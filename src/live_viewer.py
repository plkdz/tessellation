#!/usr/bin/env python3
"""Small live Canvas viewer for tiling search states."""

from __future__ import annotations

import json
import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable


StatePayload = dict[str, Any]
PayloadBuilder = Callable[[int], StatePayload]


HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tessellation Live</title>
  <style>
    html, body {
      width: 100%;
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: #f7f5ef;
      color: #1b1f23;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    canvas {
      display: block;
      width: 100vw;
      height: 100vh;
    }
    #status {
      position: fixed;
      left: 16px;
      top: 14px;
      padding: 8px 10px;
      border: 1px solid rgba(0, 0, 0, 0.12);
      border-radius: 6px;
      background: rgba(247, 245, 239, 0.88);
      font-size: 13px;
      line-height: 1.35;
      backdrop-filter: blur(8px);
      pointer-events: none;
    }
  </style>
</head>
<body>
  <canvas id="view"></canvas>
  <div id="status">等待搜索状态...</div>
  <script>
    const canvas = document.getElementById("view");
    const status = document.getElementById("status");
    const context = canvas.getContext("2d");

    let state = null;
    let previousKeys = new Map();
    let birthTimes = new Map();
    let targetCamera = { x: 0, y: 0, scale: 1 };
    let camera = { x: 0, y: 0, scale: 1 };

    function resizeCanvas() {
      const ratio = Math.max(1, window.devicePixelRatio || 1);
      const width = Math.floor(window.innerWidth * ratio);
      const height = Math.floor(window.innerHeight * ratio);
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
        return true;
      }
      return false;
    }

    function tileKey(tile) {
      return tile.points.map(([x, y]) => `${x.toFixed(6)},${y.toFixed(6)}`).join(";");
    }

    function updateBirthTimes(tiles) {
      const nextKeys = new Map();
      const now = performance.now();
      tiles.forEach((tile, index) => {
        const key = tileKey(tile);
        nextKeys.set(index, key);
        if (previousKeys.get(index) !== key) {
          birthTimes.set(index, now);
        }
      });
      for (const index of birthTimes.keys()) {
        if (index >= tiles.length) {
          birthTimes.delete(index);
        }
      }
      previousKeys = nextKeys;
    }

    function updateCamera() {
      if (!state || state.tiles.length === 0) {
        return;
      }
      let minX = Infinity;
      let minY = Infinity;
      let maxX = -Infinity;
      let maxY = -Infinity;
      for (const tile of state.tiles) {
        for (const [x, y] of tile.points) {
          minX = Math.min(minX, x);
          minY = Math.min(minY, y);
          maxX = Math.max(maxX, x);
          maxY = Math.max(maxY, y);
        }
      }
      const pad = 1.2;
      const worldWidth = Math.max(1e-9, maxX - minX + 2 * pad);
      const worldHeight = Math.max(1e-9, maxY - minY + 2 * pad);
      const scale = 0.82 * Math.min(canvas.width / worldWidth, canvas.height / worldHeight);
      targetCamera = {
        x: (minX + maxX) / 2,
        y: (minY + maxY) / 2,
        scale,
      };
      if (camera.scale === 1 && previousKeys.size <= 1) {
        camera = { ...targetCamera };
      }
    }

    function screenPoint(point) {
      return [
        canvas.width / 2 + (point[0] - camera.x) * camera.scale,
        canvas.height / 2 - (point[1] - camera.y) * camera.scale,
      ];
    }

    function draw() {
      if (resizeCanvas()) {
        updateCamera();
      }
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.fillStyle = "#f7f5ef";
      context.fillRect(0, 0, canvas.width, canvas.height);

      camera.x += (targetCamera.x - camera.x) * 0.06;
      camera.y += (targetCamera.y - camera.y) * 0.06;
      camera.scale += (targetCamera.scale - camera.scale) * 0.06;

      if (state) {
        const now = performance.now();
        state.tiles.forEach((tile, index) => {
          const points = tile.points.map(screenPoint);
          const age = Math.max(0, now - (birthTimes.get(index) || now));
          const flash = Math.max(0, 1 - age / 900);
          context.beginPath();
          context.moveTo(points[0][0], points[0][1]);
          for (const point of points.slice(1)) {
            context.lineTo(point[0], point[1]);
          }
          context.closePath();
          context.fillStyle = tile.reflected
            ? `rgba(${Math.round(120 + 70 * flash)}, ${Math.round(154 - 20 * flash)}, ${Math.round(196 - 35 * flash)}, 0.66)`
            : `rgba(${Math.round(217 + 25 * flash)}, ${Math.round(180 - 60 * flash)}, ${Math.round(135 - 45 * flash)}, 0.66)`;
          context.strokeStyle = "rgba(23, 32, 42, 0.86)";
          context.lineWidth = Math.max(1.2, Math.min(2.4, camera.scale * 0.018));
          context.fill();
          context.stroke();
        });
      }

      requestAnimationFrame(draw);
    }

    const events = new EventSource("/events");
    events.onmessage = (event) => {
      state = JSON.parse(event.data);
      updateBirthTimes(state.tiles);
      updateCamera();
      status.textContent = `step ${state.step} / tiles ${state.tiles.length}`;
    };
    events.onerror = () => {
      status.textContent = state
        ? `连接中断，最后 step ${state.step} / tiles ${state.tiles.length}`
        : "等待实时流...";
    };

    window.addEventListener("resize", updateCamera);
    draw();
  </script>
</body>
</html>
"""


class LiveViewer:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self._clients: list[queue.Queue[str]] = []
        self._lock = threading.Lock()
        self._latest: str | None = None
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def url(self) -> str:
        if self._server is None:
            return f"http://{self.host}:{self.port}/"
        host, port = self._server.server_address
        return f"http://{host}:{port}/"

    def start(self) -> None:
        server = ThreadingHTTPServer((self.host, self.port), self._make_handler())
        self._server = server
        self._thread = threading.Thread(target=server.serve_forever, name="live-viewer", daemon=True)
        self._thread.start()

    def publish(self, payload: StatePayload) -> None:
        message = json.dumps(payload, separators=(",", ":"))
        with self._lock:
            self._latest = message
            clients = tuple(self._clients)
        for client in clients:
            self._put_latest(client, message)

    def close(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()

    def _add_client(self) -> queue.Queue[str]:
        client: queue.Queue[str] = queue.Queue(maxsize=1)
        with self._lock:
            self._clients.append(client)
            latest = self._latest
        if latest is not None:
            self._put_latest(client, latest)
        return client

    def _remove_client(self, client: queue.Queue[str]) -> None:
        with self._lock:
            if client in self._clients:
                self._clients.remove(client)

    def _put_latest(self, client: queue.Queue[str], message: str) -> None:
        try:
            client.put_nowait(message)
        except queue.Full:
            try:
                client.get_nowait()
            except queue.Empty:
                pass
            client.put_nowait(message)

    def _make_handler(self) -> type[BaseHTTPRequestHandler]:
        viewer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                return

            def do_GET(self) -> None:
                if self.path == "/" or self.path.startswith("/?"):
                    self._send_html()
                    return
                if self.path == "/events":
                    self._send_events()
                    return
                self.send_error(404)

            def _send_html(self) -> None:
                body = HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

            def _send_events(self) -> None:
                client = viewer._add_client()
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                try:
                    self.wfile.write(b": connected\n\n")
                    self.wfile.flush()
                    while True:
                        try:
                            message = client.get(timeout=15.0)
                            self.wfile.write(f"data: {message}\n\n".encode("utf-8"))
                        except queue.Empty:
                            self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
                except OSError:
                    pass
                finally:
                    viewer._remove_client(client)

        return Handler
