FROM python:3.12

RUN mkdir -p /app/json

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY cogs /app/cogs
COPY json/items.json /app/json
COPY Discordbot.py /app

