#!/usr/bin/env python3
"""Render project markdown to a branded PDF in the Attorney Shield palette.

Colours come from design/color-system.md and nothing else. Note the palette's
own contrast rules are obeyed here: gold is used only for rules and cover
accents, never as body text on light (2.85:1), and table headers are white on
Shield Navy (17.31:1).

Supports the markdown subset used in this repo: ATX headings, paragraphs with
**bold** / *italic* / `code` / [links](url), bullet and numbered lists, pipe
tables, fenced code blocks, blockquotes, and horizontal rules.

Typography note: the brand face is Inter, which is not installed on this
machine. Helvetica is substituted as the closest neutral grotesque. Install
Inter and register it below for exact brand type.

Usage:  md2pdf.py <input.md> <output.pdf> ["Cover subtitle"]

Requires: reportlab
"""
import re
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

# ---- Palette (design/color-system.md) -----------------------------------
SHIELD_NAVY = colors.HexColor("#0D1B2E")
DEEP_NAVY = colors.HexColor("#122440")
JUSTICE_GOLD = colors.HexColor("#C4850A")
ACTIVE_GOLD = colors.HexColor("#E8A020")
OFF_WHITE = colors.HexColor("#F5F4F0")
PURE_WHITE = colors.HexColor("#FFFFFF")
MID_NAVY = colors.HexColor("#1A3A5C")
STEEL_BLUE = colors.HexColor("#8DA8C4")
VERIFIED_GREEN = colors.HexColor("#1E7A48")
CHARCOAL = colors.HexColor("#2A2A2A")
STONE_GRAY = colors.HexColor("#6B6A60")

BODY_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"
ITALIC_FONT = "Helvetica-Oblique"
MONO_FONT = "Courier"

MARGIN = 0.85 * inch
PAGE_W, PAGE_H = LETTER

# Helvetica's WinAnsi encoding lacks these; unmapped glyphs render as black
# boxes in reportlab, so fold them to ASCII before escaping.
GLYPHS = {
    "→": "->", "←": "<-", "↔": "<->", "⇒": "=>",
    "≥": ">=", "≤": "<=", "≠": "!=", "×": "x",
    "✅": "Yes", "❌": "No", "✓": "Yes", "✔": "Yes",
    "✗": "No", "⚠": "!", "•": "-", "…": "...",
    "‑": "-", "−": "-", " ": " ", "​": "",
    "️": "", "‹": "<", "›": ">",
}


# Typographic punctuation, folded to ASCII rather than trusted to the font
# encoding. These MUST be handled explicitly: the ord() net below deletes any
# leftover non-Latin-1 char, which silently ate every em dash in the source.
PUNCT = {
    "—": " - ",   # em dash
    "–": "-",     # en dash
    "―": "-",     # horizontal bar
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "‘": "'", "’": "'", "‚": ",", "‛": "'",
    "′": "'", "″": '"',
}


def fold(t: str) -> str:
    for k, v in GLYPHS.items():
        t = t.replace(k, v)
    for k, v in PUNCT.items():
        t = t.replace(k, v)
    # Any remaining non-Latin-1 char would render as a box; drop it.
    return "".join(c if ord(c) < 0x100 else "" for c in t)


def inline(t: str) -> str:
    """Markdown inline -> reportlab intra-paragraph markup."""
    t = escape(fold(t))
    t = re.sub(r"`([^`]+)`",
               rf'<font face="{MONO_FONT}" size="8.5" color="#122440">\1</font>', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               r'<link href="\2" color="#1A3A5C"><u>\1</u></link>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", t)
    return t


# ---- Styles -------------------------------------------------------------
def styles():
    def S(name, **kw):
        kw.setdefault("fontName", BODY_FONT)
        kw.setdefault("textColor", CHARCOAL)
        kw.setdefault("alignment", TA_LEFT)
        return ParagraphStyle(name, **kw)

    return {
        "h1": S("h1", fontName=BOLD_FONT, fontSize=19, leading=23,
                textColor=SHIELD_NAVY, spaceBefore=2, spaceAfter=10),
        "h2": S("h2", fontName=BOLD_FONT, fontSize=13.5, leading=17,
                textColor=SHIELD_NAVY, spaceBefore=17, spaceAfter=7),
        "h3": S("h3", fontName=BOLD_FONT, fontSize=10.8, leading=14,
                textColor=DEEP_NAVY, spaceBefore=12, spaceAfter=5),
        "body": S("body", fontSize=9.6, leading=14.2, spaceAfter=7),
        "li": S("li", fontSize=9.6, leading=14, spaceAfter=3),
        "quote": S("quote", fontSize=9.8, leading=14.5, leftIndent=11,
                   textColor=DEEP_NAVY, fontName=BOLD_FONT,
                   spaceBefore=5, spaceAfter=9),
        "code": S("code", fontName=MONO_FONT, fontSize=8.2, leading=11.2,
                  textColor=DEEP_NAVY),
        "th": S("th", fontName=BOLD_FONT, fontSize=8.6, leading=11.4,
                textColor=PURE_WHITE),
        "td": S("td", fontSize=8.6, leading=11.4),
        "cover_eyebrow": S("ce", fontName=BOLD_FONT, fontSize=9, leading=13,
                           textColor=ACTIVE_GOLD),
        "cover_title": S("ct", fontName=BOLD_FONT, fontSize=31, leading=35,
                         textColor=PURE_WHITE),
        "cover_sub": S("cs", fontSize=11.5, leading=17, textColor=STEEL_BLUE),
        "cover_meta": S("cm", fontSize=9, leading=14, textColor=STEEL_BLUE),
        "toc1": S("toc1", fontName=BOLD_FONT, fontSize=9.8, leading=17,
                  textColor=SHIELD_NAVY),
        "toc2": S("toc2", fontSize=9.2, leading=14.5, leftIndent=14,
                  textColor=CHARCOAL),
    }


# ---- Block parsing ------------------------------------------------------
def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def build_table(rows, st, avail):
    header, body = rows[0], rows[1:]
    ncol = len(header)
    # Weight columns by longest cell so prose columns get the room, but floor
    # each column at its longest single word — otherwise a narrow column breaks
    # a header mid-word ("Rank" -> "Ra / nk").
    def longest_word(cells):
        return max([len(w) for c in cells for w in re.split(r"\s+", c)] or [1])

    weights, floors = [], []
    for i in range(ncol):
        cells = [header[i]] + [r[i] for r in body if i < len(r)]
        weights.append(max(max((len(c) for c in cells), default=1), 6))
        # ~5.6pt per char at 8.6pt Helvetica, plus 14pt cell padding.
        floors.append(longest_word(cells) * 5.6 + 14)

    total = sum(weights)
    widths = [w / total * avail for w in weights]
    widths = [max(f, w) for f, w in zip(floors, widths)]
    # Floors can overshoot the frame; rescale the slack out of the widest cols.
    if sum(widths) > avail:
        slack = sum(widths) - avail
        pool = sum(max(0, w - f) for w, f in zip(widths, floors)) or 1
        widths = [w - slack * max(0, w - f) / pool
                  for w, f in zip(widths, floors)]
    scale = avail / sum(widths)
    widths = [w * scale for w in widths]

    data = [[Paragraph(inline(c), st["th"]) for c in header]]
    for r in body:
        r = (r + [""] * ncol)[:ncol]
        data.append([Paragraph(inline(c), st["td"]) for c in r])

    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), SHIELD_NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, 0), 1.1, JUSTICE_GOLD),
        ("GRID", (0, 1), (-1, -1), 0.35, colors.HexColor("#DDDCD6")),
        ("BOX", (0, 0), (-1, -1), 0.35, colors.HexColor("#DDDCD6")),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), OFF_WHITE))
    t.setStyle(TableStyle(style))
    return t


def code_block(lines, st, avail):
    body = [[Paragraph(escape(fold(l)) or "&nbsp;", st["code"])] for l in lines]
    t = Table(body, colWidths=[avail], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), OFF_WHITE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, JUSTICE_GOLD),
    ]))
    return t


def gold_rule(avail, color=JUSTICE_GOLD, w=1.6, width_frac=1.0):
    t = Table([[""]], colWidths=[avail * width_frac], rowHeights=[0.5], hAlign="LEFT")
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), w, color)]))
    return t


def parse(md, st, avail):
    """Markdown -> flowables. Skips the leading H1 (it lives on the cover)."""
    out = []
    lines = md.split("\n")
    i, seen_h1 = 0, False

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        if not s:
            i += 1
            continue

        if s.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out += [Spacer(1, 4), code_block(buf, st, avail), Spacer(1, 9)]
            continue

        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", s):
            out += [Spacer(1, 7), gold_rule(avail, MID_NAVY, 0.6), Spacer(1, 9)]
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)", s)
        if m:
            lvl, txt = len(m.group(1)), m.group(2)
            if lvl == 1:
                if not seen_h1:          # cover carries it
                    seen_h1 = True
                    i += 1
                    continue
                out.append(Paragraph(inline(txt), st["h1"]))
            elif lvl == 2:
                out.append(KeepTogether([
                    Paragraph(inline(txt), st["h2"]),
                    gold_rule(avail, JUSTICE_GOLD, 1.2, 0.16),
                    Spacer(1, 7),
                ]))
            else:
                out.append(Paragraph(inline(txt), st["h3"]))
            i += 1
            continue

        # pipe table: header + |---| separator
        if s.startswith("|") and i + 1 < len(lines) and re.match(
                r"^\|[\s:|-]+\|?$", lines[i + 1].strip()):
            rows = [split_row(s)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            out += [Spacer(1, 3), build_table(rows, st, avail), Spacer(1, 11)]
            continue

        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(Paragraph(inline(" ".join(buf)), st["quote"]))
            continue

        if re.match(r"^([-*+]|\d+[.)])\s+", s):
            items, ordered = [], bool(re.match(r"^\d+[.)]\s", s))
            while i < len(lines):
                cur = lines[i]
                cs = cur.strip()
                m2 = re.match(r"^([-*+]|\d+[.)])\s+(.*)", cs)
                if m2 and (len(cur) - len(cur.lstrip())) < 4:
                    items.append(m2.group(2))
                    i += 1
                elif cs and not re.match(r"^(#{1,4}\s|\||```|>)", cs) and items:
                    items[-1] += " " + cs      # continuation line
                    i += 1
                else:
                    break
            out.append(ListFlowable(
                [ListItem(Paragraph(inline(x), st["li"]), leftIndent=17)
                 for x in items],
                bulletType="1" if ordered else "bullet",
                bulletColor=JUSTICE_GOLD, bulletFontName=BOLD_FONT,
                bulletFontSize=9, start="1" if ordered else None,
                leftIndent=15, spaceBefore=2, spaceAfter=9,
            ))
            continue

        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{1,4}\s|\||```|>|([-*+]|\d+[.)])\s|(-{3,}|\*{3,})$)",
                lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            out.append(Paragraph(inline(" ".join(buf)), st["body"]))
        else:
            i += 1
    return out


# ---- Document -----------------------------------------------------------
class Doc(BaseDocTemplate):
    """Adds TOC notification and cover/body page templates."""

    def __init__(self, path, title, subtitle, **kw):
        super().__init__(path, pagesize=LETTER, title=title,
                         author="Attorney Shield - ASI 2.0",
                         subject=subtitle, **kw)
        self.doc_title = title
        self.doc_subtitle = subtitle
        body = Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN,
                     PAGE_H - 2 * MARGIN - 22, id="body")
        cover = Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN,
                      PAGE_H - 2 * MARGIN, id="cover")
        self.addPageTemplates([
            PageTemplate("cover", [cover], onPage=self.draw_cover),
            PageTemplate("body", [body], onPage=self.draw_chrome),
        ])

    def draw_cover(self, c, doc):
        c.saveState()
        c.setFillColor(SHIELD_NAVY)
        c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        # Gold keyline and a deep-navy field anchoring the lower third.
        c.setFillColor(DEEP_NAVY)
        c.rect(0, 0, PAGE_W, 2.15 * inch, stroke=0, fill=1)
        c.setStrokeColor(JUSTICE_GOLD)
        c.setLineWidth(2.4)
        c.line(MARGIN, 2.15 * inch, PAGE_W - MARGIN, 2.15 * inch)

        c.setFillColor(ACTIVE_GOLD)
        c.setFont(BOLD_FONT, 9.5)
        c.drawString(MARGIN, PAGE_H - 1.35 * inch, "A T T O R N E Y   S H I E L D")
        c.setFillColor(STEEL_BLUE)
        c.setFont(BODY_FONT, 9)
        c.drawString(MARGIN, PAGE_H - 1.62 * inch, "ASI 2.0  -  Native Android & iOS")

        y = PAGE_H - 3.5 * inch
        c.setFillColor(PURE_WHITE)
        for line in self.doc_title.split("|"):
            c.setFont(BOLD_FONT, 30)
            c.drawString(MARGIN, y, line.strip())
            y -= 0.46 * inch
        c.setStrokeColor(JUSTICE_GOLD)
        c.setLineWidth(3)
        c.line(MARGIN, y + 0.16 * inch, MARGIN + 1.5 * inch, y + 0.16 * inch)

        c.setFillColor(STEEL_BLUE)
        c.setFont(BODY_FONT, 11)
        y -= 0.28 * inch
        for line in self.doc_subtitle.split("|"):
            c.drawString(MARGIN, y, line.strip())
            y -= 0.24 * inch

        c.setFillColor(STEEL_BLUE)
        c.setFont(BODY_FONT, 8.6)
        c.drawString(MARGIN, 1.55 * inch,
                     "Colour system: Attorney-Shield Color Scheme Review")
        c.drawString(MARGIN, 1.33 * inch,
                     "Repository: samson-phillip/asi-claude")
        c.setFillColor(ACTIVE_GOLD)
        c.setFont(BOLD_FONT, 8.6)
        c.drawString(MARGIN, 0.95 * inch, "DRAFT FOR APPROVAL")
        c.restoreState()

    def draw_chrome(self, c, doc):
        c.saveState()
        c.setStrokeColor(colors.HexColor("#DDDCD6"))
        c.setLineWidth(0.6)
        c.line(MARGIN, PAGE_H - MARGIN + 12, PAGE_W - MARGIN, PAGE_H - MARGIN + 12)
        c.setFont(BODY_FONT, 7.6)
        c.setFillColor(STONE_GRAY)
        c.drawString(MARGIN, PAGE_H - MARGIN + 19,
                     f"Attorney Shield  -  {self.doc_title.replace('|', ' ')}")
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - MARGIN + 19, "ASI 2.0")
        c.setStrokeColor(JUSTICE_GOLD)
        c.setLineWidth(1.1)
        c.line(MARGIN, MARGIN - 13, MARGIN + 0.5 * inch, MARGIN - 13)
        c.setFillColor(STONE_GRAY)
        c.drawRightString(PAGE_W - MARGIN, MARGIN - 16.5, f"Page {doc.page - 1}")
        c.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            sn = flowable.style.name
            if sn in ("h2", "h3"):
                self.notify("TOCEntry",
                            (0 if sn == "h2" else 1,
                             re.sub(r"<[^>]+>", "", flowable.getPlainText()),
                             self.page))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    subtitle = sys.argv[3] if len(sys.argv) > 3 else ""

    md = open(src, encoding="utf-8").read()
    m = re.search(r"^#\s+(.*)", md, re.M)
    title = fold(m.group(1)) if m else "Document"
    title = re.sub(r"^ASI 2\.0\s*[-—]\s*", "ASI 2.0|", title)

    st = styles()
    avail = PAGE_W - 2 * MARGIN
    doc = Doc(dst, title, subtitle)

    toc = TableOfContents()
    toc.levelStyles = [st["toc1"], st["toc2"]]
    toc.dotsMinLevel = 0

    # NextPageTemplate is required: templates repeat until explicitly switched,
    # so without it the navy cover paints under every page.
    story = [Spacer(1, 1), NextPageTemplate("body"), PageBreak(),
             Paragraph("Contents", st["h1"]),
             gold_rule(avail, JUSTICE_GOLD, 1.2, 0.16), Spacer(1, 13),
             toc, PageBreak()]
    story += parse(md, st, avail)

    doc.multiBuild(story)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
