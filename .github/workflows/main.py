import os
import re
import sys
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# beartype opzionale
try:
    from beartype import beartype as _beartype
except Exception:
    def _beartype(func):
        return func

BEARTYPE_ENABLED = os.getenv("BEARTYPE_ENABLE", "1") != "0"
def maybe_beartype(func):
    return _beartype(func) if BEARTYPE_ENABLED else func

SRC_DIR = Path("src")
OUTPUT_DIR = Path("output")
MAX_DEPTH = 2
SECTION_ORDER = ["PB", "RTB", "Candidatura", "Diario Di Bordo"]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

@maybe_beartype
def format_filename(filename: str) -> str:
    name, _ = os.path.splitext(filename)
    return name.replace("_", " ")

@maybe_beartype
def cleanup_source_pdf(src_dir: Path = SRC_DIR) -> None:
    patterns = (".pdf", ".log", ".aux", ".fls", ".fdb_latexmk", ".synctex.gz", ".toc", ".snm", ".nav")
    for root, _dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(patterns):
                try:
                    os.remove(os.path.join(root, file))
                except Exception:
                    pass

@maybe_beartype
def compile_tex_to_pdf(src_dir: Path = SRC_DIR, output_dir: Path = OUTPUT_DIR, max_depth: Optional[int] = MAX_DEPTH) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tex_files = [p for p in src_dir.rglob("*.tex") if p.is_file()]

    for tex_file in tex_files:
        tex_dir = tex_file.parent
        tex_name = tex_file.name
        try:
            logger.info(f"Compiling {tex_file}...")
            res = subprocess.run(
                ["latexmk", "-pdf", "-interaction=nonstopmode", "-f", tex_name],
                cwd=str(tex_dir),
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            if res.returncode != 0:
                logger.warning(f"latexmk failed for {tex_file}: {res.stderr.strip()}")
                continue

            pdf_name = tex_file.stem + ".pdf"
            pdf_path = tex_dir / pdf_name
            if pdf_path.exists():
                relative_parts = tex_dir.relative_to(src_dir).parts
                if max_depth is not None and len(relative_parts) > max_depth:
                    relative_parts = relative_parts[:max_depth]
                dest_dir = output_dir.joinpath(*relative_parts)
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(pdf_path, dest_dir / pdf_name)
        except Exception as e:
            logger.exception(f"Error processing {tex_file}: {e}")

    cleanup_source_pdf(src_dir)

@maybe_beartype
def build_tree(path: Path, depth: int = 0, max_depth: Optional[int] = MAX_DEPTH) -> Dict[str, Any]:
    node: Dict[str, Any] = {}
    if not path.exists() or not path.is_dir():
        return {}

    pdfs = sorted([f for f in path.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"], key=lambda x: x.name.lower())
    if pdfs:
        node["_files"] = [(format_filename(f.name), str(f.relative_to(OUTPUT_DIR))) for f in pdfs]

    for d in sorted([d for d in path.iterdir() if d.is_dir()]):
        if max_depth is not None and depth + 1 > max_depth:
            continue
        child = build_tree(d, depth + 1, max_depth)
        if child:
            node[d.name] = child
    return node

@maybe_beartype
def generate_html(node: Dict[str, Any], level: int = 2, indent: int = 0) -> str:
    html_lines: List[str] = []
    space = "    " * indent
    sorted_keys = sorted(node.keys(), key=lambda k: (SECTION_ORDER.index(k) if k in SECTION_ORDER else 1000, k.lower()))
    for key in sorted_keys:
        if key == "_files":
            for name, path in node["_files"]:
                tag = f"h{min(level,4)}"
                html_lines.append(f'{space}<{tag}><a href="{path}" target="_blank">{name}</a></{tag}>')
        else:
            tag = f"h{min(level,4)}"
            html_lines.append(f'{space}<{tag}>{key}</{tag}>')
            html_lines.append(generate_html(node[key], level + 1, indent + 1))
    return "\n".join(html_lines)

@maybe_beartype
def update_index_html(output_index_path: Path = OUTPUT_DIR / "index.html") -> None:
    output_index_path.parent.mkdir(parents=True, exist_ok=True)
    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head><meta charset='UTF-8'><title>Documenti</title></head>",
        "<body>",
        "<h1>Documenti Generati</h1>"
    ]
    tree = build_tree(OUTPUT_DIR)
    html_lines.append(generate_html(tree))
    html_lines.append("</body></html>")
    output_index_path.write_text("\n".join(html_lines), encoding="utf-8")
    logger.info(f"{output_index_path} updated successfully")

def main():
    compile_tex_to_pdf()
    update_index_html()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Errore durante la build: {e}")
        sys.exit(1)
