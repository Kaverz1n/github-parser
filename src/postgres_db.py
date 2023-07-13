import psycopg2

from config import config


class PostgresDB:
    '''
    Класс для создания базы данных
    '''
    instance = None

    def __new__(cls, *args, **kwargs) -> None:
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, db_name: str) -> None:
        self.__db_name = db_name
        self.__db_data = config()
        self.__create_db()

        self.__connection = psycopg2.connect(dbname=self.__db_name, **self.__db_data)
        self.__create_tables()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.db_name})'

    def __str__(self) -> str:
        return f'База данных {self.db_name}'

    def __create_db(self) -> None:
        '''
        Создаёт базу данных с переданным пользователем названием
        '''
        try:
            # подключение к бд postgres
            connection = psycopg2.connect(dbname='postgres', **self.__db_data)
            connection.autocommit = True

            with connection.cursor() as cursor:
                cursor.execute(f'CREATE DATABASE {self.__db_name}')

            connection.close()
        except psycopg2.errors.DuplicateDatabase:
            pass
        finally:
            connection.close()

    def __create_tables(self) -> None:
        '''
        Заполняет созданнную бд таблицами, которые создаются в последствии
        выполнения кода из файла create_tables.sql
        '''
        # подключение к созданной бд
        connection = self.__connection
        with connection.cursor() as cursor:
            # создание таблиц в базе данных
            with open('create_tables.sql', 'r', encoding='UTF-8') as sql_file:
                commands = sql_file.read()
                cursor.execute(commands)

    def add_data(self, data_list: list[dict]) -> None:
        '''
        Заполняет созданные таблицы в бд данными, собраными с
        помощью GitHub API
        :param data_list: список с данными о пользователе GitHub
        '''
        try:
            connection = self.__connection

            with connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO users(name, repos_count, url) VALUES (%s, %s, %s)',
                    (data_list[0]['author'], len(data_list), data_list[0]['author_url'])
                )
                for data in data_list:
                    cursor.execute('SELECT COUNT(*) FROM users')
                    last_user = cursor.fetchone()[0]
                    cursor.execute(
                        'INSERT INTO repositories '
                        '(title, author_id, language, stargazers_count, watchers_count, forks_count, url)'
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (data['name'], last_user, data['language'], data['stargazers_count'],
                         data['watchers_count'], data['forks_count'], data['url'])
                    )

            connection.commit()
        except IndexError:
            connection.rollback()
            print('Вы указали неверные данные!')

    def get_json_data(self) -> list:
        '''
        Получает список словарей о всех репозиториях в
        формате JSON
        :return: список словарей в формате JSON
        '''

        connection = self.__connection
        json_data = []

        with connection.cursor() as cursor:
            cursor.execute('''
            SELECT 
                repositories.title, 
                users.name,
                users.url,
                repositories.language,
                repositories.stargazers_count,
                repositories.watchers_count,
                repositories.forks_count,
                repositories.url
            FROM
                repositories
                JOIN users ON author_id = user_id
            ''')

            for data in cursor.fetchall():
                repo_dict = {}

                repo_dict['name'] = data[0]
                repo_dict['author'] = data[1]
                repo_dict['author_url'] = data[2]
                repo_dict['language'] = data[3]
                repo_dict['stargazers_count'] = data[4]
                repo_dict['watchers_count'] = data[5]
                repo_dict['forks_count'] = data[6]
                repo_dict['url'] = data[7]

                json_data.append(repo_dict)

        return json_data

    def get_data_by_name(self, repo_name: str) -> str:
        '''
        Возвращает информацию о репозитории по его названию
        :param repo_name: название репозитория
        :return: информацию о репозитории
        '''
        try:
            connection = self.__connection

            with connection.cursor() as cursor:
                query = '''
                SELECT 
                    repositories.title, 
                    users.name,
                    users.url,
                    repositories.language,
                    repositories.stargazers_count,
                    repositories.watchers_count,
                    repositories.forks_count,
                    repositories.url
                FROM
                    repositories
                    JOIN users ON author_id = user_id
                WHERE
                    title = %s
                '''
                cursor.execute(query, (repo_name,))
                data = cursor.fetchone()

            connection.commit()

            return f'Проект {data[0]} ({data[7]}) пользователя {data[1]} ({data[2]}), написанный на языке ' \
                   f'{data[3]} с количеством отметок в {data[4]}, просмотров в {data[5]} ' \
                   f'и форков {data[6]}'
        except TypeError:
            return 'Вы ввели неверные данные'

    def get_repo_by_stats(self) -> str:
        '''
        Выводит информацию о самому популярном репозитории
        пользователя
        :return: информация о самом популярном репозитории
        '''
        try:
            connection = self.__connection

            with connection.cursor() as cursor:
                cursor.execute('''
                SELECT 
                    repositories.title, 
                    users.name,
                    users.url,
                    repositories.language,
                    repositories.stargazers_count,
                    repositories.watchers_count,
                    repositories.forks_count,
                    repositories.url
                FROM
                    repositories
                    JOIN users ON author_id = user_id
                ORDER BY 
                    (stargazers_count +
                    watchers_count +
                    forks_count) DESC;
                ''')

                data = cursor.fetchone()

            connection.commit()

            return f'Проект {data[0]} ({data[7]}) пользователя {data[1]} ({data[2]}), написанный на языке ' \
                   f'{data[3]} с количеством отметок в {data[4]}, просмотров в {data[5]} ' \
                   f'и форков {data[6]}'
        except TypeError:
            return 'Вы ввели неверные данные!'

    def close_connection(self):
        '''
        Закрывает соединение с базой данных
        '''
        connection = self.__connection
        connection.close()

    @property
    def db_name(self):
        '''
        Возвращает имя базы данных
        :return: имя базы данных
        '''
        return self.__db_name
