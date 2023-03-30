FROM tiangolo/uwsgi-nginx-flask:python3.10

RUN apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db
RUN curl -LsS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get dist-upgrade

COPY ./backend /app

RUN pip install -r /app/requirements.txt