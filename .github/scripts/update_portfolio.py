"""Refreshes the live GitHub-derived numbers on the portfolio (index.html), nothing else.

Only touches values wrapped in a marker like: <span data-auto="fixed">9</span>
Everything else on the page (prose, project facts, hours) is left exactly as written.

Markers currently owned:
- fixed: distinct other-people's repos where a bug I reported was closed as completed (fixed)

Runs in GitHub Actions with the built-in GITHUB_TOKEN. Stdlib only.
"""
import json, os, re, urllib.parse, urllib.request

ME = "Timothymycompc"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def search(q):
    url = "https://api.github.com/search/issues?" + urllib.parse.urlencode({"q": q, "per_page": 100})
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "portfolio-stats",
                                               **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def repo_of(i):
    return i["repository_url"].split("/repos/", 1)[1]


fixed = search(f'author:{ME} type:issue -user:{ME} is:closed reason:completed "version 1"')
values = {"fixed": str(len({repo_of(i) for i in fixed["items"]}))}

p = "index.html"
s = open(p).read()
for key, val in values.items():
    s = re.sub(rf'(data-auto="{key}">)\d+(<)', rf'\g<1>{val}\g<2>', s)
open(p, "w").write(s)
print({k: v for k, v in values.items()})
