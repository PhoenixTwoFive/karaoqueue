FROM tiangolo/meinheld-gunicorn-flask:python3.9

# Currently unusable, mariadb is not available through installer for debian 12
# RUN apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db
# RUN curl -LsS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get dist-upgrade

# In the meantime, acquire the mariadb packages through apt
RUN apt-get install -y libmariadb3 libmariadb-dev

COPY ./backend/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN pip install --no-cache-dir -U meinheld

ARG SOURCE_VERSION
ENV SOURCE_VERSION ${SOURCE_VERSION:-unknown}

COPY ./backend /app