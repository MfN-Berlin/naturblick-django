FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN mkdir /logs

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN apk update && apk add --no-cache sox imagemagick ffmpeg && apk add gettext
                                         
COPY . /app/

RUN mkdir -p /app/web/locale/dels/LC_MESSAGES && ln -s /app/web/locale/de/LC_MESSAGES/django.po /app/web/locale/dels/LC_MESSAGES/django.po

EXPOSE 8000
