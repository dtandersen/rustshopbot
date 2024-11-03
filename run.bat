@REM docker build -t rustshopbot .
rem docker run --rm -it -v %cd%\json\config.json:/app/json/config.json rustshopbot bash
docker run --rm -it -v %cd%\json\config.json:/app/json/config.json rustshopbot python Discordbot.py