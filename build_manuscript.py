#!/usr/bin/env python3
"""
Build manuscript artefacts from manuscript.md without external dependencies.
Outputs: manuscript.html, manuscript.pdf
"""
from pathlib import Path
import re, html

MD_PATH = Path("manuscript.md")
HTML_PATH = Path("manuscript.html")
PDF_PATH = Path("manuscript.pdf")

def md_to_html(md: str) -> str:
    out=["<html><head><meta charset='utf-8'><title>Manuscript</title></head><body>"]
    lines=md.splitlines()
    in_table=False
    table=[]
    def flush_table():
        nonlocal in_table, table
        if in_table:
            out.append("<pre>"+html.escape("\n".join(table))+"</pre>")
            out.append("<br/>")
            in_table=False
            table=[]
    for line in lines:
        if line.startswith("|") and "|" in line[1:]:
            in_table=True
            table.append(line)
            continue
        else:
            flush_table()
        m=re.match(r'^(#+)\s+(.*)$', line)
        if m:
            level=min(len(m.group(1)),6)
            out.append(f"<h{level}>{html.escape(m.group(2))}</h{level}>")
            continue
        if line.strip()=="":
            out.append("<br/>")
        else:
            out.append(f"<p>{html.escape(line)}</p>")
    flush_table()
    out.append("</body></html>")
    return "\n".join(out)

def md_to_pdf(md: str, out_path: Path) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph as RLParagraph, Spacer, Preformatted
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    styles=getSampleStyleSheet()
    hstyles={1:styles['Heading1'],2:styles['Heading2'],3:styles['Heading3'],4:styles['Heading4']}
    body=styles['BodyText']
    mono=ParagraphStyle('Mono', parent=styles['Code'], fontName='Courier', fontSize=8, leading=9)
    docpdf=SimpleDocTemplate(str(out_path), pagesize=letter, leftMargin=1*inch, rightMargin=1*inch, topMargin=0.8*inch, bottomMargin=0.8*inch)
    story=[]
    lines=md.splitlines()
    in_table=False
    table=[]
    for line in lines:
        if line.startswith("|") and "|" in line[1:]:
            in_table=True
            table.append(line)
            continue
        if in_table:
            story.append(Preformatted("\n".join(table), mono))
            story.append(Spacer(1,0.12*inch))
            table=[]
            in_table=False
        m=re.match(r'^(#+)\s+(.*)$', line)
        if m:
            lvl=min(len(m.group(1)),4)
            story.append(RLParagraph(html.escape(m.group(2)), hstyles.get(lvl, styles['Heading4'])))
            story.append(Spacer(1,0.12*inch))
            continue
        if line.strip()=="":
            story.append(Spacer(1,0.12*inch))
        else:
            story.append(RLParagraph(html.escape(line), body))
            story.append(Spacer(1,0.08*inch))
    if in_table and table:
        story.append(Preformatted("\n".join(table), mono))
    docpdf.build(story)

def main():
    md = MD_PATH.read_text(encoding="utf-8")
    HTML_PATH.write_text(md_to_html(md), encoding="utf-8")
    md_to_pdf(md, PDF_PATH)
    print("Wrote", HTML_PATH, "and", PDF_PATH)

if __name__ == "__main__":
    main()
