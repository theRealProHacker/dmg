import pathlib

from mistune import HTMLRenderer, create_markdown
from mistune.toc import render_toc_ul

from data import input_conversion_map

input_map = (
    '<ul id="con-list">'
    + "".join(f"<li>{k} → {v}</li>" for k, v in input_conversion_map.items())
    + "</ul>"
)


def render_toc(toc):
    html = render_toc_ul(toc)
    html = html[0:3] + ' id="toc" class="navbar-nav"' + html[3:]
    return html.replace("<a ", '<a class="nav-link" ')


class CustomRenderer(HTMLRenderer):
    def __init__(self, escape=True):
        super().__init__(escape)
        self.toc = []

    def heading(self, text: str, level: int, **attrs) -> str:
        if "id" not in attrs:
            slug = "-".join(
                text.lower().replace("(", "").replace(")", "").strip().split()
            )
            attrs["id"] = slug
        self.toc.append((level, attrs["id"], text))
        return super().heading(text, level, **attrs)


with open(pathlib.Path(__file__).resolve().parent / "book.md", encoding="utf-8") as f:
    markdown = f.read()

md = create_markdown(renderer=CustomRenderer(escape=False))
content = md(markdown).replace("input_map", input_map)
toc_html = render_toc(md.renderer.toc)
