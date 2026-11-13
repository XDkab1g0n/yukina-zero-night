# 雪奈／ZERO NIGHT 原世界線

這個儲存庫放《雪奈／ZERO NIGHT》原世界線的全部材料：人物正典、各時期與配角設定、寫作指南、多代理寫作流程、範文與正文。**任何 AI 先讀這份 README**，再照下面的表取用檔案。主角是朔夜雪奈；未指定時期時，一律寫十八歲、高三開學後的現在篇。

## 專案入口與維護位置

- 唯一持續維護來源：[XDkab1g0n/yukina-zero-night](https://github.com/XDkab1g0n/yukina-zero-night)，分支 `main`，入口為根目錄 `README.md`。
- ChatGPT、Claude 與其他 AI 的專案來源都應指向本儲存庫根目錄；設定權責與多代理寫作流程仍依本 README。
- 舊工作區的《雪奈》資料保留為移轉快照，後續正典、方法學、正文與工作紀錄只更新本儲存庫。
- 公開版保留 `workshop/` 草稿、審稿與計票紀錄，排除 `mapping_PRIVATE.md` 匿名對照表及 Python 編譯快取。新的匿名對照表僅在本地或私人工作區保存，不提交公開儲存庫。
- 本儲存庫以全新 Git 歷史建立。移轉範圍與檢查紀錄見 [MIGRATION.md](MIGRATION.md)。

## 誰說了算

| 問題 | 依據 |
|---|---|
| 世界的普遍環境：年代、新東京、科技、社會、異能、權力結構 | `world/世界觀_核心設定_v0.5.md`（現在篇在 2080 年代，具體年份未定） |
| 十八歲雪奈是誰、能做到什麼 | `current_canon.md`（v17.8.2d；舊的 v17.7 已過時） |
| 前傳、回憶、其他時期的雪奈 | `world/雪奈/` 的對應時期檔；各時期的能力、裝備、關係與所知要分清 |
| 配角、組織制度、場所空間、道具 | `world/` 的原始檔：制度看組織檔，空間看地點檔 |
| 怎麼寫得好看 | `WRITING_GUIDE.md`（v2） |
| 多代理怎麼分工、怎麼選稿 | `method/LOOP.md` |

其他文件裡的順帶描寫，不能覆蓋原始設定。遇到矛盾，先確認時期與文件定位；無法裁決時直接指出，不要默默拼合。

## 依任務讀什麼

| 要做的事 | 動筆前完整讀 | 視需要再讀 |
|---|---|---|
| 寫現在篇的新故事 | `current_canon.md`、`WRITING_GUIDE.md`、`source_guide.md`、`world/世界觀_核心設定_v0.5.md` | `source_guide.md` 指到的 world 檔；找手感讀 `examples/selected_examples.md` |
| 寫前傳或回憶 | 對應時期檔、`world/雪奈/雪奈_歷史事件索引.md`、`WRITING_GUIDE.md` | 該時期出場人物的檔 |
| 續寫（「繼續」「接著寫」） | `stories/<題目>.md` 的最後一段；該篇開頭註明的工作資料夾（`workshop/<YYYYMMDD>_<題目>/`）裡有 `ledger.md` 就一起讀；再加上面的必讀 | 該篇開頭的新創元素說明 |
| 沒給方向，要 AI 自己出題 | `method/proposer_prompt.md`、`method/idea_log.md`（不得重複的題目與慣性元素） | 出好的任務卡一律先交 Charles 審 |
| 用多代理寫，或要完整一篇 | `method/LOOP.md`（三級：輕量／標準／完整，預設標準）、`method/writer_prompt.md`、`method/reader_prompt.md` | `method/iteration_log.md`（流程為什麼長這樣、實測用量） |
| 審稿、評一篇稿 | `WRITING_GUIDE.md`、`method/reader_prompt.md` | 失敗稿病理：`examples/examples_editorial_analysis.md`、`examples/loop_benchmark_shinagawa.md` |
| 設計新配角或對手 | `templates/character_sheet.md`、`WRITING_GUIDE.md`〈設定留在水面下〉 | 相關組織檔 |
| 回答設定問題 | `current_canon.md` 與相關 world 檔 | `world/雪奈/雪奈_歷史事件索引.md` |

**閱讀紀律**：核心人物的對應時期設定要完整讀過；長檔分段讀到底，回傳被截斷的部分不算讀過。搜尋片段、記憶與這份 README 都不能代替全文。同一段連續創作中，已完整讀過且沒更新的檔可以沿用。**唯一例外**是多代理流程裡的寫手：他們讀主控用原文摘錄做成的設定摘錄包，由讀完整正典的讀者把關（見 `method/LOOP.md`）。

## 檔案地圖

```
README.md                 這份入口
current_canon.md          十八歲正篇正典 v17.8.2d
WRITING_GUIDE.md          寫作指南 v2：最高標準、因果骨架、冰山法則與六種堆砌、戰鬥、視角節奏、範文心得、動筆流程與重讀清單
source_guide.md           world/ 各檔的導覽：裡面有什麼、什麼時候讀
world/
  世界觀_核心設定_v0.5.md  2080 年代新東京的世界常識與制度
  雪奈/                   各時期雪奈、雪人二十一歲、歷史事件索引、〈請帶路〉分幕腳本
  角色/                   奏、琉璃、潔西卡、小夜、夏音、雪人、真希、巖本、靜流、神代椿
  組織/                   銜尾蛇、八咫烏
  地點/                   朔夜宅邸、神山高中、神諭、鴉巢、夢菓
  道具/                   夜巡者
method/
  LOOP.md                 多代理寫作流程 v2：三級制；標準級＝摘錄包、3 寫手整篇競稿、編輯兼正典＋冷讀者、原寫手修訂、超過 5% 複審
  proposer_prompt.md      出題者提示詞：沒給方向時出題寫任務卡、替三位寫手出攪局
  idea_log.md             歷史出題紀錄：寫過的題目、慣性元素、用過的攪局
  writer_prompt.md        寫手提示詞模板
  reader_prompt.md        讀者提示詞模板（標準級 E／C、完整級 R1／R2／R3、複審版、全篇驗收版）
  build_context_pack.py   依範圍清單原文摘錄設定，自動切成每份不超過 4 萬 bytes 的摘錄包
  verify_prose.py         表層快檢：解釋尾巴、套句、簡體字、比喻與標籤密度、宣讀強度、總結旁白
  iteration_log.md        方法學的驗證與修訂紀錄
examples/
  selected_examples.md         12 組範文精選片段（原文）
  full_examples_archive.md     11 篇範文與對照稿全文（約 41 萬字元，需要時才讀）
  examples_editorial_analysis.md  逐篇精讀：好在哪裡、失敗稿怎麼走偏
  loop_benchmark_shinagawa.md  品川五輪競稿實測正文與逐輪標註（第四輪是反面教材）
stories/                  定稿正文，一篇一檔；開頭列出該篇新創、不升格正典的元素
workshop/                 多代理循環的工作檔（草稿、審稿、計票），不是正文
templates/character_sheet.md  新角色設定卡模板
```

## 共同規則

- **封裝**：《黑色子彈》世界線（含獨立主設定與風見澪）與〈相遇之前〉系列不屬於原世界線，不引用其中的人物、事件或設定。
- **新創與正典分開**：新故事可以直接創造委託、敵人、場所與傳聞，但不會因此改寫核心身世、能力或長期關係。傳聞、受訪者說法與旁觀者誤解，要和作者採用的設定分清楚。
- **續寫**：接對話中正在寫的那一篇；對話裡沒有，就接 `stories/` 裡開頭標明「連載中」的那一篇（不只一篇或沒有時，先問 Charles 是哪一篇）。從停點沿指定情境接下去，不重新設計設定。
- **交付**：繁體中文、台灣用語。直接交付正文；構思、戰術分析、審稿與工作筆記留在幕後（多代理時放 `workshop/`），Charles 要求才給。要完整一篇或指定篇幅時，交付完整而且真的有發展的作品；高解析度連載不必硬塞結局。
- **存檔**：定稿正文放 `stories/`；在 claude.ai 專案裡寫的稿，也同步一份到這裡，讓兩邊的 AI 都看得到。寫不進 repo 的工作階段先存成專案文件 `雪奈正文/<題目>.md`；下一個能寫入 repo 的工作階段，把它補進 `stories/` 與 `method/idea_log.md`。

## 已知缺口

- 世界觀 Q26「學校如何安排異能與義體學生」仍未定；新東京重建的起因與更名年份、國際集團名稱、各區生活成本等也還沒展開（見世界觀第 10 節）。需要時當作該篇新創處理，不升格成世界設定。
