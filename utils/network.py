from __future__ import annotations

import time
import requests

from config import BACKOFF_BASE_SECONDS, MAX_RETRIES, REQUEST_TIMEOUT_SECONDS


class NetworkRequestError(RuntimeError):
    pass


def request_with_retry(method: str, url: str, *, logger, **kwargs) -> requests.Response:
    timeout = kwargs.pop("timeout", REQUEST_TIMEOUT_SECONDS)
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as exc:
            last_error = exc
            logger.warning("Petición fallida (%s/%s) %s: %s", attempt, MAX_RETRIES, url, exc)
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_BASE_SECONDS * (2 ** (attempt - 1)))

    raise NetworkRequestError(f"No se pudo completar {method} {url}: {last_error}")
