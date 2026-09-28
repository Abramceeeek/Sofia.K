"""Make the study papers from the Markdown sources (D106).

- `study-info.pdf`: the consent form, then the privacy notice. Sent in the WhatsApp chat with `/consent`.
- `test-d-landing/privacy.html`: the public privacy page. The study's WhatsApp number is left out (D106):
  sign-ups get it in the chat.

HTML comments in the Markdown are internal notes and are dropped. Run from the repo root with the Brain's
environment (it has reportlab):  brain/.venv/bin/python validation/make_study_pdf.py
"""
from __future__ import annotations

import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
NUMBER = "+44 7771 477717"
PUBLIC_NUMBER_TEXT = "which they get when they sign up"


def blocks(md: str) -> list[tuple[str, object]]:
    """A small Markdown reader: headings, paragraphs, bullet lists and tables; enough for these two files."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    out: list[tuple[str, object]] = []
    para: list[str] = []
    items: list[str] = []
    rows: list[list[str]] = []

    def flush():
        nonlocal para, items, rows
        if para:
            out.append(("p", " ".join(para)))
        if items:
            out.append(("ul", items))
        if rows:
            out.append(("table", rows))
        para, items, rows = [], [], []

    for line in md.splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            out.append((f"h{level}", s[level:].strip()))
        elif s.startswith("|"):
            if para or items:
                flush()
            cells = [c.strip() for c in s.strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                rows.append(cells)
        elif s.startswith("- "):
            if para or rows:
                flush()
            items.append(s[2:])
        elif items and line.startswith("  "):
            items[-1] += " " + s
        else:
            if items or rows:
                flush()
            para.append(s)
    flush()
    return out


def inline_html(text: str) -> str:
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
    return re.sub(r"`(.+?)`", r"\1", t)


def public(md: str) -> str:
    out = md.replace(f", {NUMBER}", f", {PUBLIC_NUMBER_TEXT}")
    assert NUMBER not in out, "the WhatsApp number must not reach the public page"
    return out


def write_html(md: str, path: Path) -> None:
    body = []
    for kind, val in blocks(public(md)):
        if kind.startswith("h"):
            body.append(f"<{kind}>{inline_html(val)}</{kind}>")
        elif kind == "p":
            body.append(f"<p>{inline_html(val)}</p>")
        elif kind == "ul":
            body.append("<ul>" + "".join(f"<li>{inline_html(x)}</li>" for x in val) + "</ul>")
        else:
            head, *rest = val
            trs = ["<tr>" + "".join(f"<th>{inline_html(c)}</th>" for c in head) + "</tr>"]
            trs += ["<tr>" + "".join(f"<td>{inline_html(c)}</td>" for c in r) + "</tr>" for r in rest]
            body.append("<table>\n" + "\n".join(trs) + "\n</table>")
    page = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Privacy notice</title>
<style>
  :root {{ --bg:#fbfaf7; --ink:#1d1d1b; --line:#e2dfd6; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg:#151514; --ink:#efede7; --line:#34332f; }} }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif; }}
  main {{ max-width:720px; margin:0 auto; padding:32px 16px 56px; }}
  table {{ border-collapse:collapse; width:100%; margin:8px 0 16px; display:block; overflow-x:auto; }}
  th, td {{ border:1px solid var(--line); padding:8px; text-align:left; vertical-align:top; }}
</style>
</head>
<body><main>
<!-- Generated from validation/privacy-notice.md by validation/make_study_pdf.py. Edit the Markdown, then rerun. -->
{chr(10).join(body)}
<p><a href="index.html">Back</a></p>
</main></body></html>
"""
    path.write_text(page, encoding="utf-8")


def write_pdf(sources: list[str], path: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    st = getSampleStyleSheet()
    small = st["BodyText"].clone("small", fontSize=8.5, leading=11)
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                            topMargin=14 * mm, bottomMargin=14 * mm, title="Days out that fit you: study information")
    width = A4[0] - 32 * mm
    flow = []
    for n, md in enumerate(sources):
        if n:
            flow.append(PageBreak())
        for kind, val in blocks(md):
            if kind == "h1":
                flow.append(Paragraph(inline_html(val), st["Title"]))
            elif kind.startswith("h"):
                flow.append(Paragraph(inline_html(val), st["Heading3"]))
            elif kind == "p":
                flow.append(Paragraph(inline_html(val), st["BodyText"]))
            elif kind == "ul":
                flow += [Paragraph(inline_html(x), st["BodyText"], bulletText="•") for x in val]
            else:
                cols = len(val[0])
                data = [[Paragraph(inline_html(c), small) for c in r] for r in val]
                t = Table(data, colWidths=[width / cols] * cols, repeatRows=1)
                t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                                       ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                                       ("VALIGN", (0, 0), (-1, -1), "TOP")]))
                flow += [Spacer(1, 2 * mm), t, Spacer(1, 3 * mm)]
    doc.build(flow)


def main() -> None:
    consent = (HERE / "consent-form.md").read_text(encoding="utf-8")
    notice = (HERE / "privacy-notice.md").read_text(encoding="utf-8")
    write_pdf([consent, notice], HERE / "study-info.pdf")
    write_html(notice, HERE / "test-d-landing" / "privacy.html")
    print("wrote validation/study-info.pdf and validation/test-d-landing/privacy.html")


if __name__ == "__main__":
    main()
