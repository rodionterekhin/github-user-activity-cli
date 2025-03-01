# github-user-activity-cli
A simple project for a https://roadmap.sh/projects/github-user-activity idea

# Running from source code

This project utilizes [Poetry](https://python-poetry.org/) as a dependency manager. First of all
you should install it according to official manual.

After poetry is installed execute
```shell
poetry install
```
Wait till all the dependencies are installed, and then run

```shell
poetry run python github_activity.py
```

## PyCharm cyrillic symbols issue

In case your username folder contains cyrillic letters, PyCharm won't be able to perform
any invocations of `poetry` command. This issue can be solved by changing virtualenv
folder path in poetry configuration by

```shell
poetry config virtualenvs.path <path_to_venv_folder>
```

# Motivation

My goals behind creation of this repo:

1. Get the hang of Poetry
2. Familiarize with aiohttp and async requests
3. Deepen Pydantic knowledge
