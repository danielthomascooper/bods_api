from flask import Flask, request, make_response, Response
from api.bods_api import BODS_request
from api.location.responses import LocationResponse
import logging
import os
import time
import threading
from collections import OrderedDict
from typing import TypeVar, Generic, Optional

logger = logging.getLogger(__name__)

app = Flask(__name__)

CACHE_TIMEOUT = int(os.environ.get("CACHE_TIMEOUT", 15))
CACHE_MAX_SIZE = int(os.environ.get("CACHE_MAX_SIZE", 256))


def _load_api_key() -> str:
    """Load API key from environment variable or SECRET.txt fallback."""
    key = os.environ.get("BODS_API_KEY")
    if key:
        return key
    secret_path = os.path.join(os.path.dirname(__file__), "SECRET.txt")
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.readline().strip()
    raise RuntimeError(
        "BODS API key not found. Set the BODS_API_KEY environment variable "
        "or create a SECRET.txt file in the project root."
    )


API_KEY = _load_api_key()


T = TypeVar("T")


class TTLCache(Generic[T]):
    """Thread-safe LRU cache with per-entry TTL expiry."""

    def __init__(self, ttl: float, max_size: int = 256):
        self._ttl = ttl
        self._max_size = max_size
        self._store: OrderedDict[object, tuple[float, T]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key) -> Optional[T]:
        with self._lock:
            if key not in self._store:
                return None
            expiry, value = self._store[key]
            if time.monotonic() > expiry:
                del self._store[key]
                return None
            self._store.move_to_end(key)  # mark as recently used
            return value

    def set(self, key, value: T) -> None:
        with self._lock:
            expiry = time.monotonic() + self._ttl
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = (expiry, value)
            while len(self._store) > self._max_size:
                self._store.popitem(last=False)  # evict oldest/least-recently-used entry


_cache: TTLCache[Response] = TTLCache(ttl=CACHE_TIMEOUT, max_size=CACHE_MAX_SIZE)


def request_key(args):
    return frozenset(args.items())


ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")


@app.route('/locations')
def get_locations() -> Response:
    key = request_key(request.args)
    cached = _cache.get(key)
    if cached is not None:
        logger.debug("Cache hit for key %s", key)
        return cached

    logger.info("Cache miss — fetching new data")
    try:
        return_data = BODS_request(API_KEY, "location", **request.args)
    except ValueError as e:
        return make_response({"error": str(e)}, 400)
    except Exception:
        logger.exception("Upstream BODS request failed")
        return make_response({"error": "Failed to fetch data from BODS"}, 502)

    if isinstance(return_data, LocationResponse):
        body = return_data.to_json()
    elif isinstance(return_data, str):
        body = return_data
    else:
        body = str(return_data)

    response = make_response(body)
    response.headers["Content-Type"] = "application/json"
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGINS
    _cache.set(key, response)
    return response


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(debug=debug, host=host, port=port)

