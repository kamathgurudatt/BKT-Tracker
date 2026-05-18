import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

logger = logging.getLogger(__name__)
_healthcheck_server: ThreadingHTTPServer | None = None
_healthcheck_thread: threading.Thread | None = None


class WorkerHealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path not in {"/", "/health", "/health/live"}:
            self.send_error(404)
            return

        body = json.dumps({"status": "ok", "service": "worker"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        logger.info("worker_healthcheck: " + format, *args)


def _port() -> int:
    # Prefer an explicit worker port for local/docker-compose runs. Fall back to
    # Railway's PORT when the worker service is expected to expose health HTTP.
    return int(os.environ.get("WORKER_HEALTH_PORT") or os.environ.get("PORT") or "8001")


def start_background_server() -> None:
    global _healthcheck_server, _healthcheck_thread

    if _healthcheck_thread and _healthcheck_thread.is_alive():
        return

    port = _port()
    try:
        _healthcheck_server = ThreadingHTTPServer(("0.0.0.0", port), WorkerHealthHandler)
    except OSError as exc:
        logger.warning("Worker healthcheck server could not bind to port %s: %s", port, exc)
        return

    _healthcheck_thread = threading.Thread(target=_healthcheck_server.serve_forever, name="worker-healthcheck", daemon=True)
    _healthcheck_thread.start()
    logger.info("Worker healthcheck server listening on port %s", port)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", _port()), WorkerHealthHandler)
    logger.info("Worker healthcheck server listening on port %s", _port())
    server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    main()
