FROM python:3.12

RUN mkdir -p /app/json

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY Discordbot.py /app
COPY cogs /app/cogs
COPY gateway /app/gateway
COPY command /app/command
COPY json/items.json /app/json

