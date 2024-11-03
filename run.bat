@echo off
docker run --rm -it -v %cd%\json\config.json:/app/json/config.json rustshopbot