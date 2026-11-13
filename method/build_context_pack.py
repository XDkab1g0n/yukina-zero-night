#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""設定摘錄包產生器（2026-11-09）

用法：
    python3 method/build_context_pack.py <spec 檔> <輸出資料夾>

spec 檔每行一段摘錄，欄位用「|」分隔，路徑以雪奈資料夾為根；# 開頭為註解：
    current_canon.md|1|581|0–6 章：定位、核心、外觀、人格、對話、生活面向、銀色幽靈
    world/角色/角色_黑岩真希.md|1|9999|全文

輸出 context_pack_1.md、context_pack_2.md……每份不超過 MAX_BYTES，
避免單次讀取超過上限；段落不會被切開。內容一律原文照錄，標明出處與行號。
"""

import os
import sys

MAX_BYTES = 40_000
HEADER = (
    "# 設定摘錄包{part}\n\n"
    "> 依 `method/LOOP.md` 製作。以下全部是原文摘錄，未改寫；每段標明來源檔與行號。人物以這裡為準。\n"
    "> 摘錄包是用來校準的，不是素材庫：不要照抄裡面的形容詞、語錄與互動條目，也不要為了證明讀過而把設定寫進正文。\n"
    "> 需要包外資訊時，可以讀雪奈資料夾的原檔，並在附註寫明。\n"
)


def main(spec_path: str, out_dir: str) -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    blocks = []
    with open(spec_path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            path, a, b, desc = [x.strip() for x in line.split("|", 3)]
            with open(os.path.join(root, path), encoding="utf-8") as src:
                lines = src.read().split("\n")
            a, b = int(a), min(int(b), len(lines))
            body = "\n".join(lines[a - 1:b]).strip()
            blocks.append(f"---\n\n## 【{path}｜第 {a}–{b} 行｜{desc}】\n\n{body}\n")

    parts, cur = [], ""
    for blk in blocks:
        if cur and len((cur + blk).encode("utf-8")) > MAX_BYTES:
            parts.append(cur)
            cur = ""
        cur += blk + "\n"
    if cur:
        parts.append(cur)

    os.makedirs(out_dir, exist_ok=True)
    n = len(parts)
    for i, body in enumerate(parts, 1):
        tag = f"（{i}／{n}）" if n > 1 else ""
        out = os.path.join(out_dir, f"context_pack_{i}.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write(HEADER.format(part=tag) + "\n" + body)
        print(f"{out}  {os.path.getsize(out):,} bytes")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
