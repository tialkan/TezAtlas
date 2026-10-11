"""
tools/latex_converter.py — TezAtlas Markdown → LaTeX Dönüştürücüsü

Guided Writing Mode'un Markdown taslak çıktısını seçilen LaTeX şablonuna dönüştürür.
Kullanım:
    python3 tools/latex_converter.py draft/ --output build/ --template thesis_yok
    python3 tools/latex_converter.py draft/introduction.md --output build/ --template article_apa7
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Mapping: document heading depth → LaTeX command per template class
# ---------------------------------------------------------------------------

HEADING_MAP: dict[str, dict[int, str]] = {
    "thesis": {1: "chapter", 2: "section", 3: "subsection", 4: "subsubsection"},
    "article": {1: "section", 2: "subsection", 3: "subsubsection", 4: "paragraph"},
    "conference": {1: "section", 2: "subsection", 3: "subsubsection", 4: "paragraph"},
}

TEMPLATE_CLASS_MAP: dict[str, str] = {
    "thesis_yok": "thesis",
    "thesis_generic": "thesis",
    "article_apa7": "article",
    "article_ieee": "article",
    "article_chicago": "article",
    "conference_acm": "conference",
    "generic": "article",
}

# ---------------------------------------------------------------------------
# Minimal preamble templates (generated if template file missing)
# ---------------------------------------------------------------------------

PREAMBLES: dict[str, str] = {
    "thesis_yok": r"""\documentclass[12pt,a4paper]{report}
\usepackage[top=3cm,bottom=2.5cm,left=3.5cm,right=2.5cm]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{setspace}
\onehalfspacing
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{graphicx}
\usepackage{booktabs}
""",
    "thesis_generic": r"""\documentclass[12pt,a4paper]{report}
\usepackage[margin=2.5cm]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{doublespace}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{graphicx}
\usepackage{booktabs}
""",
    "article_apa7": r"""\documentclass[man,12pt]{apa7}
\usepackage[utf8]{inputenc}
\usepackage[american]{babel}
\usepackage{csquotes}
\usepackage[style=apa,backend=biber]{biblatex}
\addbibresource{references.bib}
""",
    "article_ieee": r"""\documentclass[conference]{IEEEtran}
\usepackage[utf8]{inputenc}
\usepackage{cite}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}
""",
    "article_chicago": r"""\documentclass[12pt,a4paper]{article}
\usepackage[margin=2.5cm]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[notes,backend=biber]{biblatex-chicago}
\addbibresource{references.bib}
""",
    "conference_acm": r"""\documentclass[sigconf]{acmart}
\usepackage[utf8]{inputenc}
""",
    "generic": r"""\documentclass[12pt,a4paper]{article}
\usepackage[margin=2.5cm]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{graphicx}
\usepackage{booktabs}
""",
}


# ---------------------------------------------------------------------------
# Conversion helpers
# ---------------------------------------------------------------------------

def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters (outside of already-converted commands)."""
    # Only escape characters that are not part of LaTeX commands
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("^", r"\^{}"),
        ("~", r"\textasciitilde{}"),
        ("<", r"\textless{}"),
        (">", r"\textgreater{}"),
    ]
    for char, escaped in replacements:
        text = text.replace(char, escaped)
    return text


def _convert_inline(text: str) -> str:
    """Convert inline Markdown to LaTeX inline commands."""
    # Bold: **text** or __text__
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"__(.+?)__", r"\\textbf{\1}", text)
    # Italic: *text* or _text_
    text = re.sub(r"\*(.+?)\*", r"\\textit{\1}", text)
    text = re.sub(r"(?<![\\])_(.+?)_", r"\\textit{\1}", text)
    # Inline code: `code`
    text = re.sub(r"`(.+?)`", r"\\texttt{\1}", text)
    # Citation with page: [@key, p. 45] → \cite[p.~45]{key}
    text = re.sub(
        r"\[@([^\],]+),\s*p\.\s*(\d+)\]",
        r"\\cite[p.~\2]{\1}",
        text,
    )
    # Citation: [@key] → \cite{key}
    text = re.sub(r"\[@([^\]]+)\]", r"\\cite{\1}", text)
    # Footnote reference: [^1] → will be resolved in block pass
    return text


def _convert_block(lines: list[str], doc_class: str) -> list[str]:
    """Convert a list of Markdown lines to LaTeX lines."""
    heading_map = HEADING_MAP.get(doc_class, HEADING_MAP["article"])
    output: list[str] = []
    i = 0
    in_code = False
    in_blockquote = False
    footnote_defs: dict[str, str] = {}

    # First pass: collect footnote definitions
    for line in lines:
        m = re.match(r"^\[\^(\w+)\]:\s*(.+)$", line)
        if m:
            footnote_defs[m.group(1)] = m.group(2)

    while i < len(lines):
        line = lines[i]

        # Skip footnote definition lines
        if re.match(r"^\[\^(\w+)\]:\s*", line):
            i += 1
            continue

        # Code block fence
        if line.startswith("```"):
            if not in_code:
                in_code = True
                output.append(r"\begin{verbatim}")
            else:
                in_code = False
                output.append(r"\end{verbatim}")
            i += 1
            continue

        if in_code:
            output.append(line)
            i += 1
            continue

        # Horizontal rule → \clearpage
        if re.match(r"^---+$", line.strip()):
            output.append(r"\clearpage")
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            level = len(m.group(1))
            title = _convert_inline(m.group(2).strip())
            cmd = heading_map.get(level, "paragraph")
            output.append(f"\\{cmd}{{{title}}}")
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            if not in_blockquote:
                output.append(r"\begin{quote}")
                in_blockquote = True
            content = _convert_inline(line[2:])
            # Inline footnote refs [^1]
            content = re.sub(
                r"\[\^(\w+)\]",
                lambda m2: f"\\footnote{{{footnote_defs.get(m2.group(1), m2.group(1))}}}",
                content,
            )
            output.append(content)
            i += 1
            # Check if next line is still blockquote
            if i >= len(lines) or not lines[i].startswith("> "):
                output.append(r"\end{quote}")
                in_blockquote = False
            continue

        # Unordered list item
        if re.match(r"^[-*+]\s+", line):
            # Collect all consecutive list items
            output.append(r"\begin{itemize}")
            while i < len(lines) and re.match(r"^[-*+]\s+", lines[i]):
                item = _convert_inline(re.sub(r"^[-*+]\s+", "", lines[i]))
                output.append(f"  \\item {item}")
                i += 1
            output.append(r"\end{itemize}")
            continue

        # Ordered list item
        if re.match(r"^\d+\.\s+", line):
            output.append(r"\begin{enumerate}")
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                item = _convert_inline(re.sub(r"^\d+\.\s+", "", lines[i]))
                output.append(f"  \\item {item}")
                i += 1
            output.append(r"\end{enumerate}")
            continue

        # Image: ![caption](path)
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", line.strip())
        if m:
            caption = _convert_inline(m.group(1))
            path = m.group(2)
            output.append(r"\begin{figure}[htbp]")
            output.append(r"  \centering")
            output.append(f"  \\includegraphics[width=0.8\\textwidth]{{{path}}}")
            output.append(f"  \\caption{{{caption}}}")
            output.append(r"\end{figure}")
            i += 1
            continue

        # Markdown table (pipe-delimited)
        if "|" in line and re.match(r"^\|", line.strip()):
            # Collect table rows
            table_lines: list[str] = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1
            output.extend(_convert_table(table_lines))
            continue

        # Empty line → paragraph break
        if line.strip() == "":
            output.append("")
            i += 1
            continue

        # Normal paragraph line — convert inline, resolve footnote refs
        converted = _convert_inline(line)
        converted = re.sub(
            r"\[\^(\w+)\]",
            lambda m2: f"\\footnote{{{footnote_defs.get(m2.group(1), m2.group(1))}}}",
            converted,
        )
        output.append(converted)
        i += 1

    return output


def _convert_table(table_lines: list[str]) -> list[str]:
    """Convert pipe-delimited Markdown table to LaTeX tabular."""
    output: list[str] = []
    rows: list[list[str]] = []
    for line in table_lines:
        # Skip separator rows (---|---)
        if re.match(r"^\|[-| :]+\|$", line.strip()):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return output

    col_count = len(rows[0])
    col_spec = "l" * col_count

    output.append(r"\begin{table}[htbp]")
    output.append(r"  \centering")
    output.append(f"  \\begin{{tabular}}{{{col_spec}}}")
    output.append(r"    \toprule")

    for idx, row in enumerate(rows):
        cells_latex = [_convert_inline(c) for c in row]
        row_str = " & ".join(cells_latex) + r" \\"
        output.append(f"    {row_str}")
        if idx == 0:
            output.append(r"    \midrule")

    output.append(r"    \bottomrule")
    output.append(r"  \end{tabular}")
    output.append(r"\end{table}")
    return output


def convert_file(
    md_path: Path,
    doc_class: str,
) -> str:
    """Convert a single Markdown file to a LaTeX body string."""
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    body_lines = _convert_block(lines, doc_class)
    return "\n".join(body_lines)


def assemble_document(
    body: str,
    template: str,
    title: str = "Academic Document",
    author: str = "Author",
    bib_file: Optional[str] = "references.bib",
) -> str:
    """Wrap body in a full LaTeX document with preamble and bibliography."""
    preamble = PREAMBLES.get(template, PREAMBLES["generic"])

    # Choose bibliography command based on template
    if "biblatex" in preamble or "biblatex-chicago" in preamble:
        bib_cmd = r"\printbibliography"
    else:
        bib_cmd = (
            f"\\bibliographystyle{{apalike}}\n\\bibliography{{{bib_file or 'references'}}}"
        )

    doc_class = TEMPLATE_CLASS_MAP.get(template, "article")
    begin_doc = r"\begin{document}"
    end_doc = r"\end{document}"

    if doc_class == "thesis":
        front = f"\\title{{{title}}}\n\\author{{{author}}}\n\\date{{\\today}}\n\\maketitle\n\\tableofcontents\n\\newpage\n"
    else:
        front = f"\\title{{{title}}}\n\\author{{{author}}}\n\\date{{\\today}}\n\\maketitle\n"

    return f"{preamble}\n{begin_doc}\n{front}\n{body}\n\n{bib_cmd}\n{end_doc}\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="TezAtlas Markdown → LaTeX converter"
    )
    parser.add_argument(
        "input",
        help="Markdown file or directory of .md files",
    )
    parser.add_argument(
        "--output", "-o",
        default="build",
        help="Output directory (default: build/)",
    )
    parser.add_argument(
        "--template", "-t",
        default="generic",
        choices=list(PREAMBLES.keys()),
        help="LaTeX template name (default: generic)",
    )
    parser.add_argument(
        "--title",
        default="Academic Document",
        help="Document title",
    )
    parser.add_argument(
        "--author",
        default="Author",
        help="Author name",
    )
    parser.add_argument(
        "--assemble",
        action="store_true",
        default=True,
        help="Wrap output in full LaTeX document (default: True)",
    )
    parser.add_argument(
        "--body-only",
        action="store_true",
        help="Output body only, no preamble",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc_class = TEMPLATE_CLASS_MAP.get(args.template, "article")

    if input_path.is_file():
        md_files = [input_path]
    elif input_path.is_dir():
        md_files = sorted(input_path.glob("*.md"))
    else:
        print(f"Error: {input_path} not found.", file=sys.stderr)
        return 1

    if not md_files:
        print(f"No .md files found in {input_path}", file=sys.stderr)
        return 1

    # Convert and concatenate all files
    body_parts: list[str] = []
    for md_file in md_files:
        body_parts.append(f"% === {md_file.name} ===\n")
        body_parts.append(convert_file(md_file, doc_class))
        body_parts.append("\n\n")

    body = "".join(body_parts)

    if args.body_only:
        out_file = output_dir / "body.tex"
        out_file.write_text(body, encoding="utf-8")
        print(f"Body written to {out_file}")
    else:
        full_doc = assemble_document(
            body,
            template=args.template,
            title=args.title,
            author=args.author,
        )
        out_file = output_dir / "main.tex"
        out_file.write_text(full_doc, encoding="utf-8")
        print(f"LaTeX document written to {out_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
