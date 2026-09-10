#!/usr/bin/env python3
"""Export a compiled markdown draft to docx, pdf, latex or html.

Standard library only (shells out to pandoc/weasyprint if installed; installs
nothing itself). Detects available conversion engines at runtime and fails
with the exact install command for this OS when none is available, rather
than a Python traceback.

    export.py <draft.md> --format docx -o out.docx
    export.py <draft.md> --format pdf  -o out.pdf  [--bibliography refs.bib --csl apa.csl]
    export.py <draft.md> --format latex -o out.tex
    export.py <draft.md> --format html -o out.html
    export.py --check              # report what this machine can produce

PDF strategy: pandoc with a LaTeX engine (xelatex/pdflatex) if one is
installed, otherwise pandoc with --pdf-engine=weasyprint (needs the
`weasyprint` Python package on PATH), otherwise fail with install commands
for both pandoc and a PDF engine.
"""
import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

FORMATS = ("docx", "pdf", "latex", "html")

PANDOC_INSTALL = {
    "Darwin": "brew install pandoc",
    "Linux": "sudo apt-get update && sudo apt-get install -y pandoc",
}
LATEX_INSTALL = {
    "Darwin": "brew install --cask mactex-no-gui   (or: brew install --cask basictex)",
    "Linux": "sudo apt-get install -y texlive-xetex",
}
WEASYPRINT_INSTALL = {
    "Darwin": "pip install weasyprint   (also needs: brew install pango)",
    "Linux": "pip install weasyprint   (also needs: sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0)",
}


def _os_name():
    return platform.system()  # "Darwin", "Linux", "Windows"


def _install_hint(table):
    os_name = _os_name()
    if os_name in table:
        return table[os_name]
    return " / ".join(f"{k}: {v}" for k, v in table.items())


def detect_engines():
    """Return a dict describing what this machine can produce."""
    pandoc = shutil.which("pandoc")
    xelatex = shutil.which("xelatex")
    pdflatex = shutil.which("pdflatex")
    weasyprint = shutil.which("weasyprint")

    pdf_engine = None
    if pandoc and xelatex:
        pdf_engine = "xelatex"
    elif pandoc and pdflatex:
        pdf_engine = "pdflatex"
    elif pandoc and weasyprint:
        pdf_engine = "weasyprint"

    return {
        "pandoc": bool(pandoc),
        "pandoc_path": pandoc,
        "xelatex": bool(xelatex),
        "pdflatex": bool(pdflatex),
        "weasyprint": bool(weasyprint),
        "can_docx": bool(pandoc),
        "can_latex": bool(pandoc),
        "can_html": bool(pandoc),
        "can_pdf": bool(pdf_engine),
        "pdf_engine": pdf_engine,
    }


def _run(cmd, timeout=120):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as e:
        return 127, "", str(e)
    except subprocess.TimeoutExpired as e:
        return 124, "", f"Timed out after {timeout}s: {e}"
    return result.returncode, result.stdout, result.stderr


class ExportError(Exception):
    pass


def export_docx(src, out, engines):
    if not engines["pandoc"]:
        raise ExportError(_missing_pandoc_message())
    code, _, err = _run(["pandoc", str(src), "-o", str(out)])
    if code != 0:
        raise ExportError(f"pandoc failed (exit {code}):\n{err.strip()}")


def export_latex(src, out, engines):
    if not engines["pandoc"]:
        raise ExportError(_missing_pandoc_message())
    code, _, err = _run(["pandoc", str(src), "-o", str(out)])
    if code != 0:
        raise ExportError(f"pandoc failed (exit {code}):\n{err.strip()}")


def _document_title(src):
    """The paper's own title: its first level-1 heading, outside code fences.

    `pandoc -s` with no title metadata falls back to the source filename, so a
    finished paper exported to HTML arrived titled "final" in the browser tab
    and in every search result and link preview that reads that element. The
    title is the one piece of metadata the document already carries, and
    nothing else in the pipeline records it.
    """
    try:
        with open(src, encoding="utf-8") as handle:
            in_fence = False
            for line in handle:
                if line.lstrip().startswith(("```", "~~~")):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                stripped = line.strip()
                if stripped.startswith("# "):
                    return stripped[2:].strip() or None
    except OSError:
        return None
    return None


def _title_metadata(src):
    title = _document_title(src)
    return ["--metadata", f"title={title}"] if title else []


def export_html(src, out, engines):
    if not engines["pandoc"]:
        raise ExportError(_missing_pandoc_message())
    cmd = ["pandoc", str(src), "-s"] + _title_metadata(src) + ["-o", str(out)]
    code, _, err = _run(cmd)
    if code != 0:
        raise ExportError(f"pandoc failed (exit {code}):\n{err.strip()}")


def export_pdf(src, out, engines):
    if not engines["pandoc"]:
        raise ExportError(_missing_pandoc_message())
    if not engines["pdf_engine"]:
        raise ExportError(
            "No PDF engine available. pandoc is installed but needs either a "
            "LaTeX engine or weasyprint to produce a PDF.\n"
            f"Install a LaTeX engine:\n  {_install_hint(LATEX_INSTALL)}\n"
            f"or install weasyprint:\n  {_install_hint(WEASYPRINT_INSTALL)}"
        )
    cmd = ["pandoc", str(src), f"--pdf-engine={engines['pdf_engine']}", "-o", str(out)]
    code, _, err = _run(cmd, timeout=180)
    if code != 0:
        raise ExportError(f"pandoc --pdf-engine={engines['pdf_engine']} failed (exit {code}):\n{err.strip()}")


def _missing_pandoc_message():
    return (
        "pandoc is not installed. It is required for every export format.\n"
        f"Install it with:\n  {_install_hint(PANDOC_INSTALL)}"
    )


EXPORTERS = {
    "docx": export_docx,
    "latex": export_latex,
    "html": export_html,
    "pdf": export_pdf,
}


def export(src_path, out_path, fmt, bibliography=None, csl=None):
    engines = detect_engines()
    if fmt not in EXPORTERS:
        raise ExportError(f"Unsupported format '{fmt}'. Choose from: {', '.join(FORMATS)}")

    extra = []
    if bibliography:
        if not Path(bibliography).exists():
            raise ExportError(f"Bibliography file not found: {bibliography}")
        extra += [f"--bibliography={bibliography}", "--citeproc"]
    if csl:
        if not Path(csl).exists():
            raise ExportError(f"CSL style file not found: {csl}")
        extra += [f"--csl={csl}"]

    if extra:
        _export_with_extra_args(src_path, out_path, fmt, engines, extra)
    else:
        EXPORTERS[fmt](src_path, out_path, engines)


def _export_with_extra_args(src, out, fmt, engines, extra):
    if not engines["pandoc"]:
        raise ExportError(_missing_pandoc_message())
    cmd = ["pandoc", str(src)] + extra
    if fmt == "pdf":
        if not engines["pdf_engine"]:
            raise ExportError(
                "No PDF engine available. pandoc is installed but needs either a "
                "LaTeX engine or weasyprint to produce a PDF.\n"
                f"Install a LaTeX engine:\n  {_install_hint(LATEX_INSTALL)}\n"
                f"or install weasyprint:\n  {_install_hint(WEASYPRINT_INSTALL)}"
            )
        cmd.append(f"--pdf-engine={engines['pdf_engine']}")
    elif fmt == "html":
        cmd.append("-s")
        cmd += _title_metadata(src)
    cmd += ["-o", str(out)]
    code, _, err = _run(cmd, timeout=180)
    if code != 0:
        raise ExportError(f"pandoc failed (exit {code}):\n{err.strip()}")


def _print_check(engines):
    print(f"OS: {_os_name()}")
    print(f"pandoc:     {'yes (' + engines['pandoc_path'] + ')' if engines['pandoc'] else 'NOT FOUND'}")
    print(f"xelatex:    {'yes' if engines['xelatex'] else 'no'}")
    print(f"pdflatex:   {'yes' if engines['pdflatex'] else 'no'}")
    print(f"weasyprint: {'yes' if engines['weasyprint'] else 'no'}")
    print()
    print(f"docx:  {'OK' if engines['can_docx'] else 'unavailable, ' + PANDOC_INSTALL.get(_os_name(), _install_hint(PANDOC_INSTALL))}")
    print(f"latex: {'OK' if engines['can_latex'] else 'unavailable, ' + PANDOC_INSTALL.get(_os_name(), _install_hint(PANDOC_INSTALL))}")
    print(f"html:  {'OK' if engines['can_html'] else 'unavailable, ' + PANDOC_INSTALL.get(_os_name(), _install_hint(PANDOC_INSTALL))}")
    if engines["can_pdf"]:
        print(f"pdf:   OK (via pandoc --pdf-engine={engines['pdf_engine']})")
    else:
        print("pdf:   unavailable")
        if not engines["pandoc"]:
            print(f"       install pandoc: {_install_hint(PANDOC_INSTALL)}")
        else:
            print(f"       install a LaTeX engine: {_install_hint(LATEX_INSTALL)}")
            print(f"       or install weasyprint: {_install_hint(WEASYPRINT_INSTALL)}")


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="export.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("draft", nargs="?", help="Path to the compiled draft markdown file")
    parser.add_argument("--format", choices=FORMATS, help="Output format")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--bibliography", help="BibTeX file for pandoc --citeproc rendering")
    parser.add_argument("--csl", help="CSL style file for pandoc citation rendering")
    parser.add_argument("--check", action="store_true",
                         help="Report what this machine can produce and exit (no conversion)")
    return parser


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.check:
        _print_check(detect_engines())
        return 0

    if not args.draft or not args.format or not args.output:
        parser.print_help()
        return 2

    draft_path = Path(args.draft)
    if not draft_path.exists():
        print(f"Error: draft not found: {args.draft}", file=sys.stderr)
        return 1

    try:
        export(draft_path, Path(args.output), args.format,
               bibliography=args.bibliography, csl=args.csl)
    except ExportError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Exported {args.draft} -> {args.output} ({args.format})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
