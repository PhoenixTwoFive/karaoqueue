FROM tiangolo/uwsgi-nginx-flask:python3.10

COPY ./backend /app

RUN pip install -r /app/requirements.txt