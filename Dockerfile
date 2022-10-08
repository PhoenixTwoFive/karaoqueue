FROM tiangolo/uwsgi-nginx-flask:python3.7

RUN pip install requests

RUN pip install pandas

RUN pip install Flask-BasicAuth

RUN pip install bs4

COPY ./backend /app