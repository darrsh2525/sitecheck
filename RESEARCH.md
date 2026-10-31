# Research log

## 1. Reading a certificate's expiry date

**Why I needed it:** Websites use certificates for HTTPS. If one expires, browsers show visitors a scary warning page and most people leave.

**What I learned:** My tool connects to the site, asks it for its certificate, reads the expiry date, and works out how many days are left before the certificate expires.

## 2. Timeouts

**Why I needed it:** By default, the requests library waits forever for a website to answer. If one site never replied, my checker would freeze.

**What I tried:** I set the timeout to 0.01 seconds, which is far too short. Both sites reported timed out, and the tool did not crash.

**What I learned:** A timeout means a dead site is reported as a problem and the tool moves on to the next site.