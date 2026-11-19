#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""雪奈稿件字面提醒（v3.1，2026-11-19：加入同篇自我重複提醒）

用法：python method/verify_prose.py <稿件.md> [更多稿件 ...]
所有命中只供人工閱讀定位，不自動判錯，不提供文學品質 PASS/FAIL。
字形也可能出現在引文或專名，需看上下文。成功分析退出 0；讀取或編碼錯誤退出 2。
舊版密度門檻僅作搜尋線索，不是風格配額；無需清空提醒。
自我重複提醒只抓身體反應、比喻起手與近距離描寫片語；道具名、專名與數字多半已排除，刻意呼應可保留。
"""

import collections
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HAN = re.compile(r"[一-鿿]")

# ---------- 字面線索（不是禁用詞表） ----------
# 1. 破折號／補述解釋尾巴：「——那是……」「──這是……」（容許中間空白）
DASH_EXPLAIN = re.compile(r"(?:——|──|—|－－)\s*(?:那是|這是|那正是|這正是|對於|作為|因為|源自|來自)")

# 2. AI 套句（片語層級）
AI_CLICHES = [
    "嘴角勾起一抹", "勾起一抹玩味", "玩味的弧度", "空氣彷彿瞬間凝固", "空氣彷彿凝固",
    "空氣在這一刻凝固", "空氣瞬間凝固", "眼中閃過一絲", "眸中閃過一絲", "不易察覺的精光",
    "時間彷彿在這一刻靜止", "時間彷彿靜止", "彷彿過了一個世紀", "一抹難以言喻",
    "心中五味雜陳", "嘴角微微上揚", "露出意味深長的笑", "宛如初中生",
]

# 3. 簡體字（常見且台灣不用的字形）
SIMPLIFIED = set("们这说时来对为过还没让发现开关门间问么个觉见长车东头点动进当爱实电话应该样学钟钱级给军边乐经结远运钢铁视频软网络质盘标")  # 只放簡體專用字形

# ---------- 提醒 ----------
# 4. 比喻詞：同一段兩個以上，或全文密度偏高
SIMILE = re.compile(r"宛如|如同|彷彿|仿佛|好似|猶如|恍如")

# 5. 標籤複讀（雪奈常被反覆貼的外觀與數值標籤；每 3,000 字超過門檻就提醒）
LABELS = {
    "月光銀": 2, "淡紫": 2, "小虎牙": 1, "呆毛": 1, "雙馬尾": 4, "異色": 1,
    "三十八公斤": 1, "38公斤": 1, "38kg": 1, "149公分": 1, "149cm": 1,
    "腰肢": 1, "絕對領域": 0, "長睫毛": 1, "纖細": 3, "嬌小": 2,
}

# 6. 宣讀強度與廉價驚訝
AWE = ["怪物", "不可名狀", "瞳孔驟縮", "瞳孔猛地收縮", "瞳孔收縮", "神明般",
       "難以置信", "魂飛魄散", "呆若木雞", "倒吸一口涼氣", "驚心動魄", "華麗絕倫", "令人窒息"]

# 7. 總結旁白
SUMMARY = ["這代表", "這意味著", "這就是她", "這便是", "這不僅", "這一刻她明白", "她終於明白",
           "最溫暖的一頓飯", "毫無疑問", "不言而喻"]

# 7b.「不是 X，是 Y」句式（AI 常用的翻轉宣告；自然中文也會用，只列提醒）
NOT_X_BUT_Y = re.compile(r"不是[^，。！？「」]{1,14}[，,]\s*(?:而)?是")

# 8. 講義腔術語（旁白出現時提醒；角色台詞裡的專業用語不一定要改）
JARGON = ["迷走神經", "乳酸", "轉動慣量", "生物阻抗", "平滑肌", "頸動脈竇", "角動量守恆", "動量守恆", "神經遞質"]

# 9. 同篇自我重複（閱讀審稿最常逐條手抓的近距離重複；只定位，不判錯）
HAN_RUN = re.compile(r"[一-鿿]+")
REPEAT_FUNC = set("的了是在不一他她我你們著這那就也有和與把被說地得都還又再要會能而但並才從向對到上下中裡個些來去過")
REPEAT_NUM = set("零一二三四五六七八九十百千萬兩第半幾")
REPEAT_MARK = set("著了過起出進回下上住開往朝在把被得地")  # 片語需含動作、方位或體貌標記，藉此略過道具名與專名
BODY_PARTS = ["喉結", "嘴角", "唇角", "嘴唇", "呆毛", "眉心", "眉頭", "眉梢", "指尖", "指節", "指腹",
              "肩線", "肩膀", "睫毛", "眼神", "視線", "目光", "呼吸", "心跳", "耳根", "耳尖", "臉頰",
              "下顎", "下巴", "掌心", "手指", "拳頭", "瞳孔", "背脊", "脊背", "膝蓋", "腳步", "嗓音",
              "喉嚨", "鼻尖", "額頭", "腕骨", "手腕", "髮梢"]
SIMILE_LEAD = re.compile(r"像是|彷彿|宛如|如同|猶如|好似|(?<![好想影圖畫肖偶錄攝映頭雕佛])像")
REPEAT_WINDOW = 20  # 近距離：兩處相隔不超過幾個正文行
REPEAT_SHOW = 12    # 每類最多列出幾筆


def is_dialogue(line: str) -> bool:
    s = line.strip()
    return s.startswith("「") or s.startswith("『")


def body_lines(text: str):
    """略過 markdown 標題、引言與分隔線，只回傳正文行（含行號）。"""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(">") or set(s) <= {"-", "*", "_"}:
            continue
        out.append((i, line))
    return out


def snippet(line: str, start: int, width: int = 28) -> str:
    a = max(0, start - width // 2)
    return line[a:a + width].strip().replace("\n", " ")


def repeated_body_reactions(lines):
    """同一身體部位後接同一動作，例：喉結猛地滾動／喉結劇烈滾動。回傳 (部位, [動作], [行號])。"""
    hits = collections.defaultdict(set)
    for no, line in lines:
        for part in BODY_PARTS:
            for m in re.finditer(part, line):
                run = HAN_RUN.match(line, m.end())
                tail = run.group()[:6] if run else ""
                for k in range(len(tail) - 1):
                    gram = tail[k:k + 2]
                    if gram[0] in REPEAT_FUNC or gram[1] in REPEAT_FUNC or gram in BODY_PARTS:
                        continue
                    hits[(part, gram)].add(no)
    grouped = collections.defaultdict(list)
    for (part, gram), nos in hits.items():
        if len(nos) >= 2:
            grouped[(part, tuple(sorted(nos)))].append(gram)
    return sorted(((part, grams, list(nos)) for (part, nos), grams in grouped.items()), key=lambda x: x[2][0])


def repeated_simile_leads(lines):
    """同一比喻詞後接同一字起手，例：像截鋼樁／像截被砍斷的木樁。回傳 (起手, [行號])。"""
    hits = collections.defaultdict(set)
    for no, line in lines:
        for m in SIMILE_LEAD.finditer(line):
            ch = line[m.end():m.end() + 1]
            if ch and HAN_RUN.fullmatch(ch) and ch not in REPEAT_FUNC and ch not in "是隻個某":
                hits[m.group() + ch].add(no)
    return sorted(((lead, sorted(nos)) for lead, nos in hits.items() if len(nos) >= 2), key=lambda x: x[1][0])


def near_repeated_phrases(lines, window: int = REPEAT_WINDOW, min_len: int = 5, max_len: int = 16):
    """相隔不遠又原樣出現的描寫片語。出現超過三次（多為專名或刻意母題）、含數字、
    不含動作／方位標記（多為道具名）或只出現在台詞裡的不列。回傳 (片語, [行號])。"""
    order = {no: i for i, (no, _) in enumerate(lines)}
    dialogue = {no for no, line in lines if is_dialogue(line)}
    pos = collections.defaultdict(list)
    for no, line in lines:
        for run in HAN_RUN.findall(line):
            for size in range(min_len, min(max_len, len(run)) + 1):
                for k in range(len(run) - size + 1):
                    pos[run[k:k + size]].append(no)
    cand = {}
    for gram, nos in pos.items():
        uniq = sorted(set(nos))
        if len(uniq) < 2 or len(nos) > 3:
            continue
        if set(gram) & REPEAT_NUM or not set(gram) & REPEAT_MARK:
            continue
        if all(no in dialogue for no in uniq):
            continue
        if any(order[b] - order[a] <= window for a, b in zip(uniq, uniq[1:])):
            cand[gram] = uniq
    kept = []
    for gram in sorted(cand, key=len, reverse=True):
        if not any(gram in longer for longer in kept):
            kept.append(gram)
    return sorted(((gram, cand[gram]) for gram in kept), key=lambda x: x[1][0])


def analyze(path: str) -> int:
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    lines = body_lines(text)
    body = "\n".join(l for _, l in lines)
    han = len(HAN.findall(body))
    per3k = max(han / 3000, 1e-9)

    warn = []

    for no, line in lines:
        for m in DASH_EXPLAIN.finditer(line):
            warn.append(f"第 {no} 行 可能的補述「{m.group()}」：…{snippet(line, m.start())}…")
        for c in AI_CLICHES:
            for m in re.finditer(re.escape(c), line):
                warn.append(f"第 {no} 行 常見片語「{c}」：…{snippet(line, m.start())}…")
        bad = sorted({ch for ch in line if ch in SIMPLIFIED})
        if bad:
            warn.append(f"第 {no} 行 疑似簡體字 {''.join(bad)}")

    # 比喻密度
    total_sim = 0
    for no, line in lines:
        hits = SIMILE.findall(line)
        total_sim += len(hits)
        if len(hits) >= 2:
            warn.append(f"第 {no} 行 同一段 {len(hits)} 個比喻詞（{'、'.join(hits)}）")
    if han and total_sim / (han / 1000) > 1.0:
        warn.append(f"全文比喻詞 {total_sim} 個，約每千字 {total_sim / (han / 1000):.1f} 個（僅供定位，依本篇風格判斷）")

    # 標籤複讀
    for lab, limit in LABELS.items():
        n = body.count(lab)
        if n > limit * per3k and n > limit:
            where = [str(no) for no, l in lines if lab in l][:6]
            warn.append(f"標籤「{lab}」出現 {n} 次（約每 3,000 字 {n / per3k:.1f} 次）：第 {'、'.join(where)} 行")

    # 宣讀強度、總結旁白、講義腔
    for group, words, only_narration in (("宣讀強度", AWE, False), ("總結旁白", SUMMARY, True), ("講義腔", JARGON, True)):
        for no, line in lines:
            if only_narration and is_dialogue(line):
                continue
            for w in words:
                if w in line:
                    warn.append(f"第 {no} 行 {group}「{w}」：…{snippet(line, line.find(w))}…")

    for no, line in lines:
        if is_dialogue(line):
            continue
        for m in NOT_X_BUT_Y.finditer(line):
            warn.append(f"第 {no} 行「不是…，是…」句式：…{snippet(line, m.start(), 34)}…")

    # 短行比例（範文精讀：短行過密容易變成每拍宣布結果的預告片節奏）
    narr = [l for _, l in lines if not is_dialogue(l)]
    if len(narr) >= 20:
        short = sum(1 for l in narr if len(HAN.findall(l)) <= 20)
        ratio = short / len(narr)
        if ratio > 0.7:
            warn.append(f"不超過 20 字的敘述行佔 {ratio:.0%}（{short}/{len(narr)}），檢查是否一句一行")

    # 同篇自我重複
    def nums(nos):
        return "、".join(str(n) for n in nos)
    groups = (
        [f"身體反應重複「{part}」後接「{'／'.join(sorted(grams))}」：第 {nums(nos)} 行"
         for part, grams, nos in repeated_body_reactions(lines)],
        [f"比喻起手重複「{lead}…」：第 {nums(nos)} 行" for lead, nos in repeated_simile_leads(lines)],
        [f"近距離重複片語「{gram}」：第 {nums(nos)} 行" for gram, nos in near_repeated_phrases(lines)],
    )
    for items in groups:
        warn.extend(items[:REPEAT_SHOW])
        if len(items) > REPEAT_SHOW:
            warn.append(f"……同類重複另有 {len(items) - REPEAT_SHOW} 處未列出")

    print("=" * 64)
    print(f"{os.path.basename(path)}｜漢字 {han} 字｜正文行 {len(lines)}")
    print("=" * 64)
    print(f"[閱讀提醒] {len(warn)} 處（命中不代表錯誤）")
    for item in warn:
        print("  - " + item)
    print("結果：字面掃描完成；是否修改由上下文與讀感決定。\n")
    return 0



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    try:
        codes = [analyze(p) for p in sys.argv[1:]]
        sys.exit(max(codes))
    except (OSError, UnicodeError) as exc:
        print(f"無法讀取稿件：{exc}", file=sys.stderr)
        sys.exit(2)
