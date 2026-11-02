"""The only network code in Puck. Tests replace `fetch` with recorded responses."""

import json
import urllib.error
import urllib.parse
import urllib.request

from core.common.errors import PuckError

TIMEOUT = 20
MAX_BYTES = 2_000_000
AGENT = "puck/0.1 (personal study tool)"


class SourceError(PuckError):
    """A source could not be reached or returned something unusable."""


def fetch(url: str, params: dict | None = None, headers: dict | None = None) -> tuple[int, bytes, str]:
    """GET a URL. Returns (status, body, final URL). Raises SourceError when unreachable."""
    if params:
        url = f"{url}?{urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})}"
    request = urllib.request.Request(url, headers={"User-Agent": AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, response.read(MAX_BYTES), response.geturl()
    except urllib.error.HTTPError as error:
        return error.code, error.read(MAX_BYTES) if error.fp else b"", url
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise SourceError(f"Could not reach {url.split('?')[0]}: {error}") from error


def get_json(url: str, params: dict | None = None, headers: dict | None = None) -> dict:
    status, body, _ = fetch(url, params, headers)
    if status == 429:
        raise SourceError(f"{urllib.parse.urlsplit(url).netloc} is rate-limiting requests. "
                          "Wait a minute, or set its API key (see `puck sources --help`).")
    if status != 200:
        raise SourceError(f"{url.split('?')[0]} returned HTTP {status}.")
    try:
        return json.loads(body)
    except json.JSONDecodeError as error:
        raise SourceError(f"{url.split('?')[0]} did not return JSON.") from error
