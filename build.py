"""Render Jinja templates to static HTML in public/ for Cloudflare Pages."""
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
OUT = ROOT / "public"

ROUTES = {"landing": "/", "issue_001": "/issues/001"}
PAGES = {"landing.html": "index.html", "issue_001.html": "issues/001.html"}


def url_for(endpoint, filename=None, **_):
    if endpoint == "static":
        return f"/static/{filename}"
    return ROUTES[endpoint]


shutil.rmtree(OUT, ignore_errors=True)
env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True)
env.globals["url_for"] = url_for

for tpl, dest in PAGES.items():
    path = OUT / dest
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(env.get_template(tpl).render(), encoding="utf-8")

shutil.copytree(ROOT / "static", OUT / "static")
(OUT / "favicon.ico").write_bytes((ROOT / "static/favicon.ico").read_bytes())
print(f"built {len(PAGES)} pages -> {OUT}")
