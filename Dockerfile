FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN mkdir /logs

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN apk update && apk add --no-cache sox imagemagick ffmpeg
                                         
COPY . /app/

EXPOSE 8000
