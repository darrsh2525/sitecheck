# sitecheck

A small command-line website health checker, written in Python.

## What it is and why
Given a list of URLs, `sitecheck` checks that each site responds, how fast it responds,
and how many days remain on its TLS certificate. I chose it because monitoring and
expiring certificates are everyday DevOps problems (an expired cert is a classic outage).

## How to run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.example.json config.json     # edit the list of sites
python sitecheck.py config.json
python sitecheck.py config.json --json results.json   # also save JSON
```
Run the tests with `python -m pytest`.

Config options (all but `sites` optional): `timeout` (s), `slow_threshold` (s), `cert_warn_days`.

Exit codes: `0` all healthy, `1` at least one problem, `2` config error.
This lets cron or a CI job react to failures.

## How it works
1. `load_config` reads and validates the JSON file.
2. `check_url` makes an HTTP GET with a timeout, timing it, then (for https) opens a TLS
   connection with `ssl`/`socket` and reads the certificate's `notAfter` date.
3. Every failure (timeout, DNS error, bad cert) is caught and recorded as a problem
   instead of crashing the program.
4. Sites are checked concurrently with a thread pool, since the work is network waiting.
5. `format_report` prints the results; the exit code reflects overall health.

## Testing
Network calls are mocked with `unittest.mock`, so tests are fast and deterministic.

## What I'd improve with more time
- Retries before declaring a site down, to avoid false alarms
- Alerting (Slack/email) and a GitHub Actions workflow running the tests
- Check specific content on the page, not just the status code
- Dockerfile for easy scheduled runs
