# Research log

> TEMPLATE: replace everything below with YOUR real notes as you learn each topic.
> Write in your own words, and include what you tried that didn't work.

## 1. Reading a TLS certificate's expiry date in Python
- **Why I needed it:**
- **Where I looked / how I judged it:** (Python `ssl` docs, etc.)
- **What didn't work:**
- **What I learned:** (`getpeercert()`, the `notAfter` format, `ssl.cert_time_to_seconds`)

## 2. Timeouts
- Why `requests` has no default timeout and what could happen without one:

## 3. Testing code that uses the network
- What mocking is, why I patched `requests.get`, what `unittest.mock.patch` does:

## 4. Exit codes
- How cron/CI uses them:

## 5. Concurrency with ThreadPoolExecutor
- Why threads help for network-bound work (vs CPU-bound):
