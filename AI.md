# AI usage

**Tools used:** Claude. I asked it to suggest a project idea (a website health checker, to fit a DevOps role), and it wrote the first version of the code, the tests and the documentation templates. It also guided me through running the project, setting up git and pushing to GitHub.

**Incorrect or unhelpful suggestions:**
- Claude told me there were 11 tests, but pytest showed 13, because one test runs four times with different inputs.
- The SSL error messages are very long and hard to read.

**How I checked things:**
- I ran the tests myself (13 passed).
- I ran the tool against real sites and against deliberately broken ones (expired certificate, wrong hostname, HTTP 500 error, slow response, nonexistent domain), and checked the exit codes (0 when healthy, 1 when there are problems).
- I tested a very short timeout to see that the tool reports failures and carries on instead of crashing.