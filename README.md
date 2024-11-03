# Pairing

The bot must be paired with Rust+ on each server.

https://github.com/liamcottle/rustplus.js#pairing

```
ns.bat
fnm use --install-if-missing 20
npx @liamcottle/rustplus.js fcm-register
npx @liamcottle/rustplus.js fcm-listen
```

Add `playerToken` to `config.json`.

# Run bot

With Python

```
python Discordbot.py
```

With Docker

```
docker run --rm -it -v %cd%\json\config.json:/app/json/config.json rustshopbot python Discordbot.py
```

 # References

 * Forked from [vending](https://github.com/Gnomeslayer/vending) by Gnomeslayer
 * [Rust+.py](https://github.com/olijeffers0n/rustplus)
