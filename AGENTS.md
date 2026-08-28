# BlazerGames — Base44 dev environment

## What this is
A pure static HTML/CSS/JS games collection (no build step, no backend, no database).
Served directly by nginx from the bind-mounted repo root.

## Running
```
docker compose -f docker-compose.base44.yml up -d
```
Serves on host port 3000. Edits to static files appear on refresh (no live-reload
server; call `reload_preview` after changes if needed).

## Gotcha
The repo root dir must be world-traversable (`chmod 755 .`) — nginx's worker runs as
a non-root user and returns 403 if it can't traverse the mount root.

## Verify
```
curl -sf http://localhost:3000/                       # homepage
curl -sf http://localhost:3000/games/2048/            # a game page
curl -sf -H "Host: external-preview.example.com" http://localhost:3000/  # external host
```
