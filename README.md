# Rust Shop Bot

A Discord bot that lists items for sale in Rust player shops.

# Configuration 

## Pairing

The bot must be paired with Rust+ on each server. Please refer to [liamcottle's guide](https://github.com/liamcottle/rustplus.js#pairing).

```
ns.bat
fnm use --install-if-missing 20
npx @liamcottle/rustplus.js fcm-register
npx @liamcottle/rustplus.js fcm-listen
```

Add `playerToken` to `json/config.json`. The `playerId` is the Steam ID 64.

```
"servers": [
    {
        "name": "My Awesome Server",
        "ip": "127.0.0.1",
        "playerId": "76561198100000000",
        "playerToken": "1234000000",
        "port": "28017"
    }
],

```

## Running the bot

**With Python**

Clone the repository and run `Discordbot.py` with Python.

```
python Discordbot.py
```

**With Docker**

```
# Linux
docker run --rm -it -v $(pwd)\json\config.json:/app/json/config.json ghcr.io/dtandersen/rustshopbot

# Docker Desktop
docker run --rm -it -v %cd%\json\config.json:/app/json/config.json ghcr.io/dtandersen/rustshopbot
```

**On Kubernetes with Helm**

Update `values.yaml` with your settings. There must be a `config` volume that has `config.json` in it.

```
image:
  pullPolicy: Always
resources:
  limits:
    cpu: 100m
    memory: 256Mi
volumes:
- name: config
  nfs:
    server: 10.0.0.100
    path: /export/apps/rustshopbot
```

Now install the Helm chart.

```
helm install rustshopbot charts/rustshopbot -f values.yaml
helm upgrade rustshopbot charts/rustshopbot -f values.yaml
helm uninstall rustshopbot
```

 # References

 * Forked from [vending](https://github.com/Gnomeslayer/vending) by Gnomeslayer
 * [Rust+.py](https://github.com/olijeffers0n/rustplus)
