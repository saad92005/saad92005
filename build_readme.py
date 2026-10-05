"""Rewrites the live sections of README.md from real GitHub data.

Run by .github/workflows/build.yml every day (and on demand). Locally:

    GITHUB_TOKEN=$(gh auth token) python build_readme.py

Only public repositories are read. Sections live between marker comments,
e.g. <!-- shipped starts --> ... <!-- shipped ends -->, so everything else in
the README is hand-written and left alone. Standard library only.
"""
import json
import os
import pathlib
import re
import urllib.request
from datetime import datetime

ROOT = pathlib.Path(__file__).parent
USER = "saad92005"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Order is the order they appear in "Projects".
FEATURED = ["thinkdesk", "omnira", "aes-app", "arabic-dialect-mt-nlp"]
SKIP_REPOS = {USER, "github-readme-stats"}
N_SHIPPED = 7


def graphql(query, variables=None):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


def day(iso):
    """Fixed dates, not "3 days ago": the README should only change when something real happens."""
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%b %-d, %Y" if os.name != "nt" else "%b %#d, %Y")


def recent_commits():
    data = graphql(
        """query($login: String!) {
          user(login: $login) {
            id
            repositories(first: 20, privacy: PUBLIC, ownerAffiliations: OWNER,
                         orderBy: {field: PUSHED_AT, direction: DESC}) {
              nodes { name url isFork defaultBranchRef { name } }
            }
          }
        }""",
        {"login": USER},
    )["user"]
    commits = []
    for repo in data["repositories"]["nodes"]:
        if repo["isFork"] or repo["name"] in SKIP_REPOS or not repo["defaultBranchRef"]:
            continue
        hist = graphql(
            """query($owner: String!, $name: String!, $branch: String!, $author: ID!) {
              repository(owner: $owner, name: $name) {
                ref(qualifiedName: $branch) { target { ... on Commit {
                  history(first: 6, author: {id: $author}) {
                    nodes { messageHeadline committedDate url }
                  }
                } } }
              }
            }""",
            {"owner": USER, "name": repo["name"], "branch": repo["defaultBranchRef"]["name"], "author": data["id"]},
        )["repository"]["ref"]["target"]["history"]["nodes"]
        for c in hist:
            msg = c["messageHeadline"]
            # Show substantive work: skip merges, docs-only and README-only commits
            if "[skip ci]" in msg or msg.lower().startswith(("merge ", "initial commit", "readme", "docs:", "docs ")):
                continue
            commits.append({"repo": repo["name"], "repo_url": repo["url"], **c})
    commits.sort(key=lambda c: c["committedDate"], reverse=True)
    return commits[:N_SHIPPED]


def featured_repos():
    fields = " ".join(
        f'{alias}: repository(owner: "{USER}", name: "{name}") '
        "{ name url description stargazerCount pushedAt primaryLanguage { name } homepageUrl }"
        for alias, name in ((f"r{i}", n) for i, n in enumerate(FEATURED))
    )
    data = graphql(f"query {{ {fields} }}")
    return [data[f"r{i}"] for i in range(len(FEATURED)) if data.get(f"r{i}")]


def esc(s):
    return s.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def short(s, n):
    s = s.strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def render_shipped(commits):
    return "\n\n".join(
        f"**[{c['repo']}]({c['repo_url']})** · [{esc(short(c['messageHeadline'], 64))}]({c['url']}) · {day(c['committedDate'])}"
        for c in commits
    )


def render_projects(repos):
    out = []
    for r in repos:
        meta = " · ".join(
            x for x in [
                r["primaryLanguage"]["name"] if r["primaryLanguage"] else None,
                f"★ {r['stargazerCount']}" if r["stargazerCount"] else None,
                f"last push {day(r['pushedAt'])}",
            ] if x
        )
        live = f" · [live]({r['homepageUrl']})" if r.get("homepageUrl") else ""
        out.append(f"**[{r['name']}]({r['url']})**{live}<br>{esc(short(r['description'] or '', 96))}<br><sub>{meta}</sub>")
    return "\n\n".join(out)


def replace_section(text, marker, content):
    pattern = re.compile(rf"(<!-- {marker} starts -->).*?(<!-- {marker} ends -->)", re.DOTALL)
    if not pattern.search(text):
        raise ValueError(f"marker '{marker}' not found in README.md")
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(2)}", text)


if __name__ == "__main__":
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = replace_section(text, "shipped", render_shipped(recent_commits()))
    text = replace_section(text, "projects", render_projects(featured_repos()))
    readme.write_text(text, encoding="utf-8")
    print("README.md rebuilt")
