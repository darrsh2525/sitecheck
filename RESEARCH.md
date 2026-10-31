# Research log

## 1. Reading a certificate's expiry date

**Why I needed it:** Websites use certificates for HTTPS. If one expires, browsers show visitors a scary warning page and most people leave.

**What I learned:** My tool connects to the site, asks it for its certificate, reads the expiry date, and works out how many days are left before the certificate expires.

## 2. Timeouts

**Why I needed it:** By default, the requests library waits forever for a website to answer. If one site never replied, my checker would freeze.

**What I tried:** I set the timeout to 0.01 seconds, which is far too short. Both sites reported timed out, and the tool did not crash.

**What I learned:** A timeout means a dead site is reported as a problem and the tool moves on to the next site.

## 3. Testing without the real internet (mocking)

**Why I needed it:** My tests should not depend on a working internet connection, because real websites can be slow, down, or change.

**What I learned:** The tests replace requests.get with a fake one that returns a pretend answer. This also lets me test things that are hard to cause on purpose, like a timeout.

## 4. Problems I hit along the way

**Terminal stuck on a ">" prompt**
- What happened: I typed a git command but forgot the closing quote, so the terminal kept waiting for me to finish the text and swallowed the next commands.
- How I fixed it: I pressed Ctrl+C to cancel, then typed the command again with both quotes.
- What I learned: a ">" prompt usually means an unclosed quote.

**GitHub rejected my password**
- What happened: when I ran git push, GitHub said "Password authentication is not supported".
- How I fixed it: I created a personal access token on GitHub (with the "repo" permission) and used it instead of my password.
- What I learned: GitHub uses tokens instead of passwords for git, because they can be limited and revoked.