FROM python:3.12

RUN mkdir -p /app/json

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY Discordbot.py /app
COPY json/items.json /app/json
COPY rustshopbot /app/rustshopbot

ENTRYPOINT [ "python" ]
CMD [ "Discordbot.py" ]
