import requests

GIT_TOKEN = 'YOUR-TOKEN'


def get_repos_stats(user_name: str) -> list[dict]:
    '''
    Собирает статистику по всем репозиториям пользователя,
    возвращая список, состроящий из словарей с данными о
    репозиториях
    :return: список со словарями с данными о репозиториях
    '''
    headers = {
        'Authorization': 'token ' + GIT_TOKEN
    }

    params = {
        'per_page': 100,
        'page': 1
    }

    repositories = []

    # перебирает все страницы репозиториев пользователя
    while True:
        repos_data = requests.get(
            url=f'https://api.github.com/users/{user_name}/repos',
            headers=headers,
            params=params
        ).json()

        if len(repos_data) == 0:
            break

        params['page'] += 1

        for repo in repos_data:
            repo_dict = {}

            repo_dict['name'] = repo['name']
            repo_dict['author'] = repo['owner']['login']
            repo_dict['author_url'] = repo['owner']['html_url']
            repo_dict['language'] = repo['language']
            repo_dict['stargazers_count'] = repo['stargazers_count']
            repo_dict['watchers_count'] = repo['watchers_count']
            repo_dict['forks_count'] = repo['forks_count']
            repo_dict['url'] = repo['html_url']

            repositories.append(repo_dict)

    return repositories
