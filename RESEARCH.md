# Research log

## 1. Reading a certificate's expiry date

**Why I needed it:** Websites use certificates for HTTPS. If one expires, browsers show visitors a scary warning page and most people leave.

**What I learned:** My tool connects to the site, asks it for its certificate, reads the expiry date, and works out how many days are left before the certificate expires.