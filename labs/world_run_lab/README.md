# World Run Lab (Isolated)

This demo is isolated in this single directory.

## Run

1. Start world-runtime API in another terminal (default `http://127.0.0.1:8080`):

```bash
python3 -m api.http_server --host 127.0.0.1 --port 8080
```

2. Start this isolated lab server:

```bash
python3 labs/world_run_lab/server.py --host 127.0.0.1 --port 8090 --upstream http://127.0.0.1:8080
```

3. Open:

- `http://127.0.0.1:8090`

The UI defaults to API Base URL `/api`, which is proxied to `--upstream`.

## Files

- `index.html` - page layout
- `styles.css` - styling
- `app.js` - client orchestration + presets
- `server.py` - static server + API proxy
