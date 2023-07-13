from functions import get_repos_stats
from postgres_db import PostgresDB


def main():
    db_name = input('Укажите название для базы данных: ')
    git_user_name = input('Укажите никнейм пользователя на GitHub: ')

    repo_data = get_repos_stats(git_user_name)
    postgres_db = PostgresDB(db_name)
    postgres_db.add_data(repo_data)

    print(postgres_db.get_repo_by_stats())
    json_data = postgres_db.get_json_data()

    repo_name = input('Укажите имя репозитория, чтобы получить по нему информацию: ')
    print(postgres_db.get_data_by_name(repo_name))


if __name__ == '__main__':
    main()
