# Programming Language: Python
Challenge requirement

# Python Version 3.14
At the time that this project was built, this version is a good balance between new features/stability. It is the last "stable" version.
![alt text](images/image.png)

# Package manager: UV
This choice was just because I have more experience with, but I know there are some other projects available for this purpose

# Project Structure: pyproject.toml
Following PEP 621: https://peps.python.org/pep-0621/

# Pre-commit, linting, static typing check, etc
For this project I'll try a pretty recent type checker written in Rust called ty. This choice don't have a specific reason, but just the curiosity to see how it behaves (and check if can be faster than MyPy, which was really slow in my past experiences)

# Framework
Challenge Requirement

# Database: Postgres
Has widely doc available, it is open-source and free to use

# ORM usage: SQLAlchemy + asyncpg
Since tornado is a framework to overcome C10k problem, a good pair to it is an async connection with the DB.

# Database versioning tool: Alembic
Since I'm decided to use ORM, Alembic will help me to write the db. versions. It also allow me to navigate across db versions due its "upgrade" and "downgrade" methods. 

# Design pattern: MVC-ish
Since it will be a small API, I will go by simplicity and only write 3 layers (controller, service and repository) - or something similar.

# Infra
To make the code executable in another machine easily, I'll dockerize and write a docker compose with the dependencies to run the entire system

