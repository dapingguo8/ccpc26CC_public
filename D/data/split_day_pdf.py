#!/usr/bin/env python3
"""把一整天的题面 PDF 按单题切分，自动跳过封面/目录页与「刻意留白」页。

识别方式:
    * 每道题的第一页含有 "X . 题目名 .时 .间 .限 .制： N 秒" 这样的表头；
    * 第一道题之前的页面（封面 + 目录）整页丢弃；
    * 含 "刻意留白" 的页面整页丢弃；
    * 其余可疑的短页面只告警、不删除。

输出命名（--naming）:
    letter-dir     A-matrix.pdf      （默认，字母 + 题目目录名）
    letter-title   A-又一道纸笔问题.pdf （字母 + 中文标题）
    dir            matrix.pdf

用法:
    python split_day_pdf.py --pdf D:\\git\\ccpc26CC\\statements\\ccpcx\\day1.pdf --repo D:\\git\\ccpc26CC
    python split_day_pdf.py --pdf ... --out <目录> --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from pypdf import PdfReader, PdfWriter

TITLE_RE = re.compile(r"([A-Z]) \. (.+?) \.时 \.间 \.限 \.制： ([0-9.]+) 秒")
BLANK_MARK = "刻意留白"
SHORT_PAGE = 60
BAD_CHARS = '<>:"/\\|?*'


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def safe_name(name: str) -> str:
    cleaned = "".join("_" if ch in BAD_CHARS else ch for ch in name).strip()
    return cleaned or "problem"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="按单题切分题面 PDF（跳过封面/目录与刻意留白页）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--pdf", required=True, help="要切分的整卷 PDF")
    parser.add_argument("--out", default=None, help="输出目录（默认: <pdf 所在目录>/split）")
    parser.add_argument("--repo", default=".", help="仓库根，用于把中文标题映射到题目目录名")
    parser.add_argument("--day", default="day1", help="题目目录所在的一级目录名（默认: day1）")
    parser.add_argument(
        "--naming",
        choices=("letter-dir", "letter-title", "dir"),
        default="letter-dir",
        help="输出文件名风格（默认: letter-dir）",
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印切分方案，不写文件")
    return parser.parse_args(argv)


def load_title_map(repo: Path, day: str) -> dict[str, str]:
    """题目标题（中文、英文、或 "中文 / English"）-> 题目目录名。"""
    mapping: dict[str, str] = {}
    day_path = repo / day
    if not day_path.is_dir():
        return mapping
    for problem_dir in sorted(p for p in day_path.iterdir() if p.is_dir()):
        conf_path = problem_dir / "conf.yaml"
        if not conf_path.is_file():
            continue
        try:
            conf = yaml.safe_load(conf_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        title = conf.get("title") or {}
        zh = title.get("zh-cn")
        en = title.get("en")
        for value in (zh, en):
            if value:
                mapping[normalize(str(value))] = problem_dir.name
        if zh and en:
            mapping[normalize("%s / %s" % (zh, en))] = problem_dir.name
    return mapping


def resolve_title(title: str, mapping: dict[str, str]) -> tuple[str | None, str]:
    """返回 (题目目录名, 用于文件名的标题片段)。整份标题对不上时按 " / " 拆开逐段匹配。"""
    full = normalize(title)
    if full in mapping:
        return mapping[full], full.split(" / ")[0]
    for part in (p.strip() for p in full.split("/")):
        if part and part in mapping:
            return mapping[part], part
    return None, full.split(" / ")[0]


def scan(reader: PdfReader):
    """返回 (problems, dropped, suspicious)，problems = [(letter, title, time, [页号])]。"""
    problems: list[dict] = []
    dropped: list[tuple[int, str]] = []
    suspicious: list[tuple[int, int]] = []
    pending: list[int] = []
    started = False

    for index, page in enumerate(reader.pages):
        number = index + 1  # 1-based，与页脚「第 N 页 共 M 页」一致
        text = normalize(page.extract_text() or "")
        match = TITLE_RE.search(text)

        if match:
            problems.append(
                {
                    "letter": match.group(1),
                    "title": match.group(2).strip(),
                    "time": match.group(3),
                    "pages": [number],
                }
            )
            started = True
            pending = []
            continue

        if not started:
            dropped.append((number, "封面/目录"))
            continue

        if BLANK_MARK in text:
            dropped.append((number, "刻意留白"))
            continue

        if len(text) < SHORT_PAGE:
            suspicious.append((number, len(text)))

        problems[-1]["pages"].append(number)

    return problems, dropped, suspicious


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.is_file():
        print(f"找不到 PDF: {pdf_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.out).resolve() if args.out else pdf_path.parent / "split"
    reader = PdfReader(str(pdf_path))
    problems, dropped, suspicious = scan(reader)
    if not problems:
        print("没有识别到任何题目页，检查标题格式", file=sys.stderr)
        return 1

    title_map = load_title_map(Path(args.repo).resolve(), args.day)
    print(f"源文件: {pdf_path}（共 {len(reader.pages)} 页）")
    print(f"输出到: {out_dir}")
    print()

    total_pages = 0
    used_names: set[str] = set()
    written = 0
    for idx, problem in enumerate(problems):
        letter, title, time_limit = problem["letter"], problem["title"], problem["time"]
        pages = problem["pages"]
        slug, display = resolve_title(title, title_map)
        if slug is None:
            hint = "  （conf.yaml 里没找到同名标题，用 PDF 标题做文件名）"
        else:
            hint = ""
        fallback = safe_name(display or title)

        if args.naming == "letter-title":
            stem = f"{letter}-{fallback}"
        elif args.naming == "dir":
            stem = slug or fallback
        elif slug and slug.lower() != letter.lower():
            stem = f"{letter}-{slug}"
        else:
            stem = f"{letter}-{fallback}"

        if stem in used_names:
            stem += f"-{idx + 1}"
        used_names.add(stem)

        span = f"{pages[0]}-{pages[-1]}" if len(pages) > 1 else str(pages[0])
        print(f"{letter}  {title}  时限 {time_limit} 秒  第 {span} 页（{len(pages)} 页） -> {stem}.pdf{hint}")

        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            writer = PdfWriter()
            for number in pages:
                writer.add_page(reader.pages[number - 1])
            with open(out_dir / f"{stem}.pdf", "wb") as handle:
                writer.write(handle)
            written += 1
        total_pages += len(pages)

    print()
    print(
        "%s %d 个题目，共 %d 页；丢弃 %d 页（%s）"
        % (
            "待切分" if args.dry_run else "已写出",
            len(problems),
            total_pages,
            len(dropped),
            "，".join(f"第 {n} 页 {why}" for n, why in dropped) or "无",
        )
    )
    if suspicious:
        print("可疑的短页面（已保留，请人工确认是否该丢）: " + ", ".join(
            f"第 {n} 页（{length} 字）" for n, length in suspicious
        ))
    if not args.dry_run:
        print(f"实际写出 {written} 个 PDF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
