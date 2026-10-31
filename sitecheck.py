"""sitecheck - a small website health checker.

Reads a JSON config listing URLs, checks each one (status code, response
time, TLS certificate expiry) and prints a report. Exits non-zero if any
problem is found, so it can be used from cron or CI.
"""
import argparse
import json
import socket
import ssl
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

DEFAULT_TIMEOUT = 5          # seconds before we give up on a request
DEFAULT_SLOW = 2.0           # seconds; slower than this is flagged
DEFAULT_CERT_WARN_DAYS = 14  # warn if the certificate expires sooner


@dataclass
class Result:
    url: str
    status_code: int | None = None
    response_time: float | None = None
    cert_days_left: int | None = None
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def get_cert_days_left(hostname: str, port: int = 443, timeout: float = DEFAULT_TIMEOUT) -> int:
    """Connect over TLS and return the days until the certificate expires.

    Raises ssl.SSLError / OSError if the connection or verification fails.
    """
    context = ssl.create_default_context()  # verifies the cert chain + hostname
    with socket.create_connection((hostname, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls:
            cert = tls.getpeercert()
    expires = ssl.cert_time_to_seconds(cert["notAfter"])
    return int((expires - datetime.now(timezone.utc).timestamp()) // 86400)


def check_url(url: str, timeout: float = DEFAULT_TIMEOUT,
              slow_threshold: float = DEFAULT_SLOW,
              cert_warn_days: int = DEFAULT_CERT_WARN_DAYS) -> Result:
    """Check one URL. Never raises: every failure becomes a problem string."""
    result = Result(url=url)

    # --- HTTP check ---
    try:
        start = time.perf_counter()
        response = requests.get(url, timeout=timeout)
        result.response_time = round(time.perf_counter() - start, 3)
        result.status_code = response.status_code
        if response.status_code >= 400:
            result.problems.append(f"bad status {response.status_code}")
        if result.response_time > slow_threshold:
            result.problems.append(f"slow response ({result.response_time}s > {slow_threshold}s)")
    except requests.exceptions.Timeout:
        result.problems.append(f"timed out after {timeout}s")
    except requests.exceptions.SSLError as exc:
        result.problems.append(f"SSL error: {exc}")
    except requests.exceptions.ConnectionError:
        result.problems.append("connection failed (DNS error or refused)")
    except requests.exceptions.RequestException as exc:
        result.problems.append(f"request error: {exc}")

    # --- Certificate check (https only) ---
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.hostname:
        try:
            result.cert_days_left = get_cert_days_left(parsed.hostname, parsed.port or 443, timeout)
            if result.cert_days_left < 0:
                result.problems.append("certificate has expired")
            elif result.cert_days_left < cert_warn_days:
                result.problems.append(f"certificate expires in {result.cert_days_left} days")
        except (ssl.SSLError, OSError) as exc:
            # Avoid duplicating a problem already reported by the HTTP check
            if not any("SSL" in p or "connection" in p or "timed out" in p for p in result.problems):
                result.problems.append(f"certificate check failed: {exc}")
    return result


def load_config(path: str) -> dict:
    """Load and validate the JSON config. Raises ValueError with a clear message."""
    try:
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"config file not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"config is not valid JSON: {exc}")

    sites = config.get("sites")
    if not isinstance(sites, list) or not sites:
        raise ValueError('config must contain a non-empty "sites" list')
    for site in sites:
        if not isinstance(site, str) or not site.startswith(("http://", "https://")):
            raise ValueError(f"invalid URL (must start with http:// or https://): {site!r}")
    return config


def format_report(results: list[Result]) -> str:
    lines = []
    for r in results:
        status = "OK  " if r.ok else "FAIL"
        code = r.status_code if r.status_code is not None else "---"
        rt = f"{r.response_time}s" if r.response_time is not None else "---"
        cert = f"{r.cert_days_left}d" if r.cert_days_left is not None else "n/a"
        lines.append(f"[{status}] {r.url}  status={code}  time={rt}  cert={cert}")
        for problem in r.problems:
            lines.append(f"        - {problem}")
    failed = sum(not r.ok for r in results)
    lines.append(f"\n{len(results) - failed}/{len(results)} sites healthy")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check website health and TLS certificate expiry.")
    parser.add_argument("config", help="path to JSON config file")
    parser.add_argument("--json", dest="json_out", help="also write results to this JSON file")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ValueError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    timeout = config.get("timeout", DEFAULT_TIMEOUT)
    slow = config.get("slow_threshold", DEFAULT_SLOW)
    warn = config.get("cert_warn_days", DEFAULT_CERT_WARN_DAYS)

    # Checks are I/O bound (waiting on the network), so threads speed this up a lot.
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(lambda u: check_url(u, timeout, slow, warn), config["sites"]))

    print(format_report(results))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in results], f, indent=2)

    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
