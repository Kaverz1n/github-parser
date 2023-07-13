CREATE TABLE IF NOT EXISTS users
(
    user_id serial,
    name varchar(39),
    repos_count smallint,
    url text,

    CONSTRAINT pk_users_user_id PRIMARY KEY(user_id)
);

CREATE TABLE IF NOT EXISTS repositories
(
    repo_id serial,
    title varchar(100),
    author_id smallint,
    language varchar(20),
    stargazers_count int,
    watchers_count int,
    forks_count int,
    url text,

    CONSTRAINT pk_repositories_repo_id PRIMARY KEY(repo_id),
    CONSTRAINT fk_repositories_author_id FOREIGN KEY(author_id) REFERENCES users(user_id)
);