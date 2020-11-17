FROM python:3.8.5

LABEL author='bulochka'

WORKDIR /var/www/web

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN CD foodgram

RUN python3 manage.py collectstatic --noinput

RUN cd /var/www/web/static && ls -la