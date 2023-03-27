FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./backend /app

RUN pip install -r /app/requirements.txt