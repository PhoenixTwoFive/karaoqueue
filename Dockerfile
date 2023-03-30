FROM tiangolo/meinheld-gunicorn-flask:python3.9

RUN apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db
RUN curl -LsS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get dist-upgrade

COPY ./backend/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./backend /app