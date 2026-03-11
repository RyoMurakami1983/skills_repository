---
name: pdf
description: PDFテキスト抽出、Optical Character Recognition (OCR)、結合/分割、フォーム処理をuvベースの再現可能コマンドで実行したいときに使う。
---

## When to Use This Skill

業務ワークフローで、再実行可能な Portable Document Format (PDF) 処理が必要なときに使います。

- 請求書PDFからテキストを抽出し、後段の照合ログへ受け渡したいとき。
- スキャン報告書へOCRを実行し、分類や監査レビュー前に文字化したいとき。
- 大きな監査資料を規則的なページ範囲で分割し、部門配布したいとき。
- 署名済み付録を結合し、命名規則を守った単一成果物にしたいとき。
- フォーム入力やフラット化を行い、監査可能な処理履歴を残したいとき。
- 実行コマンドを記録し、他メンバーが同じ結果を再現できるようにしたいとき。

## Core Principles

1. **基礎を先に固める**: まず決定的なコマンドを作り、その後に速度とコストを最適化する。
2. **型で運用する**: 名前付きフローを再利用し、担当者が変わっても出力を揃える。
3. **推測より追跡性**: 根拠がない補正を避け、出典と不確実性を明示する。
4. **成果物ライフサイクル設計**: 中間ファイルと最終成果物を意図的に分離する。

## Workflow:

### Step 1 - 入出力パスと保管方針を確定する

入力、出力、保管メタ情報のパスを明示します。

```powershell
Test-Path input.pdf
```

> **Values**: 基礎と型

### Step 2 - テキストレイヤ有無を判定する

テキスト抽出を先に使います。理由は、抽出のほうが高速で元文字を保持しやすいためです。

```powershell
uv run --with pypdf==6.1.1 python scripts\extract_text.py input.pdf --output input.txt
```

> **Values**: 基礎と型 / 成長の複利

### Step 3 - 抽出経路かOCR経路を選択する

抽出結果が空、または利用困難なときだけOCRを使います。理由は、OCRの計算コストが高いためです。

```powershell
uv run --with pypdfium2==5.6.0 --with rapidocr-onnxruntime==1.4.4 --with numpy==2.4.3 python scripts\ocr_script.py input.pdf --output input.ocr.txt
```

> **Values**: ニュートラルな視点 / 余白の設計

### Step 4 - 公開と出典記録を実施する

決定的命名と再実行ログを残します。理由は、運用監査で再現性が必要になるためです。

```powershell
uv cache prune
```

> **Values**: 教える・広める / 成長の複利

### Decision Table

| 状況 | 主経路 | フォールバック | 出力サフィックス |
| --- | --- | --- | --- |
| テキストレイヤがあり品質も十分 | `extract_text.py` | 失敗ページのみOCR | `.txt` |
| テキストレイヤがない/空 | `ocr_script.py` | `--scale` を上げて再実行 | `.ocr.txt` |
| ページごとに品質が混在 | ページ単位ハイブリッド | 読取不能箇所を手動確認 | `.hybrid.txt` |

## Patterns

### Basic Pattern

#### Overview

born-digital PDF から最小構成でテキスト抽出する基本型です。

#### When to Use

抽出品質が十分で、OCRコストを増やしたくないときに使います。

#### Steps

1. ソースファイルの存在を確認する。
2. 依存バージョン固定で抽出を実行する。
3. 結果を業務フォルダへ保存し、Temp依存を避ける。

```powershell
uv run --with pypdf==6.1.1 python scripts\extract_text.py input.pdf --output input.txt
```

### Intermediate Pattern

#### Overview

抽出とOCRを判定ロジックで切り替える運用型です。

#### When to Use

文書ごと、またはページごとに品質がばらつくときに使います。

#### Steps

1. 先にテキスト抽出を実行する。
2. 結果が空、または利用困難ならOCRへ切り替える。
3. 出力ヘッダへ `text-layer` か `ocr` かを記録する。

```powershell
uv run --with pypdf==6.1.1 python scripts\extract_text.py scan.pdf --output scan.txt
uv run --with pypdfium2==5.6.0 --with rapidocr-onnxruntime==1.4.4 --with numpy==2.4.3 python scripts\ocr_script.py scan.pdf --output scan.ocr.txt
```

### Advanced Pattern

#### Overview

バッチ処理で失敗追跡と再実行性を担保する上級型です。

#### When to Use

多ファイル処理、命名統制、監査証跡の維持が必要なときに使います。

#### Steps

1. 規則的な命名でファイルを走査する。
2. ファイル単位で成功/失敗を記録する。
3. トラブルシュート用に中間成果物を保持する。

```python
from pathlib import Path
import subprocess

for pdf in sorted(Path("incoming").glob("*.pdf")):
    out = Path("outputs") / f"{pdf.stem}.txt"
    cmd = ["uv", "run", "--with", "pypdf==6.1.1", "python", "scripts\\extract_text.py", str(pdf), "--output", str(out)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] {pdf.name}: {result.stderr.strip()}")
        continue
    print(f"[OK] {pdf.name} -> {out}")
```

## Best Practices

- `--with` 依存は必ずバージョン固定する。
- OCR生データと清書版を分離保存する。
- 読取不能箇所は `[UNREADABLE: page 3 line 12]` のように明示する。
- 成果物ごとに実行コマンドを記録する。
- Use 明示ラベルで出典を常にヘッダへ書く。
- Avoid 低信頼の自動補正を黙って反映しない。
- Apply 実行ごとの決定的命名規則を運用する。
- Define バッチ前に保管ルールを先に確定する。
- Consider 監査対応可能性を標準要件として扱う。

### Why these practices work

- **Why** 決定的コマンド: 担当者差による出力揺れを減らせます。
- **Why** 出典ラベル: OCRと抽出結果の混在事故を防げます。
- **Why** 生データ分離: 根拠付きレビューを維持できます。
- **Why** 保管方針明示: 証跡の消失を防げます。
- **Why** 再実行ログ: 障害調査と監査対応を短縮できます。

### Good vs Bad Examples

❌ 悪い例: OCRの不確実な文字を、根拠なしで上書きする。

✅ 良い例: OCR原文を保持し、修正版との差分と理由を記録する。

❌ 悪い例: 最終成果物を一時フォルダだけに保存する。

✅ 良い例: 最終成果物を業務保管先へ保存し、処理メタ情報を保管する。

❌ 悪い例: 抽出失敗を検知しても、フォールバック判断を記録しない。

✅ 良い例: フォールバック判断を記録し、明確な理由付きでOCRへ切り替える。

## Common Pitfalls

- 自動処理で入力/出力パス指定を省略してしまう。
- OCR結果とテキスト抽出結果を、出典ラベルなしで混在させる。
- 元PDF更新後に古い出力を再利用してしまう。

### Fixes

- 最初の **solution** として、ファイル命名を実行ID付きに固定する。
- 次の **solution** として、抽出方式と時刻をヘッダへ残す。
- 旧版成果物を残した場合は、差し替え時に **correct** マーカーを付ける。
- 読取不能ページはプレースホルダで **fix** し、下流マッピングを維持する。

## Anti-Patterns

- 運用方針なしで `pip install` と `uv run --with` を混在させる。
- 毎回キャッシュ削除して処理時間と電力コストを増やす。
- 再現ログなしで業務成果物を配布する。

## FAQ

Q. `uv run --with` でAppDataキャッシュが作られるのは正常ですか？
A. 正常です。uvは再実行高速化のため依存キャッシュを再利用します。

Q. 常に `.venv` を作るべきですか？
A. 長期開発では `.venv`、都度処理では `--with` を使い分けます。

Q. キャッシュはいつ削除すべきですか？
A. 容量圧迫、または破損疑いがあるときだけ削除します。

## Quick Reference

| 判定 | コマンド | 理由 |
| --- | --- | --- |
| テキストレイヤあり | `python scripts\extract_text.py` | 高速で元文字を保持しやすい。 |
| テキストレイヤなし | `python scripts\ocr_script.py` | 下流処理向けの検索可能テキストを作る。 |

```powershell
# テキストレイヤ抽出
uv run --with pypdf==6.1.1 python scripts\extract_text.py input.pdf --output input.txt

# スキャンPDF OCR
uv run --with pypdfium2==5.6.0 --with rapidocr-onnxruntime==1.4.4 --with numpy==2.4.3 python scripts\ocr_script.py input.pdf --output input.ocr.txt

# キャッシュ操作
uv cache dir
uv cache prune
```

## ライセンス方針メモ

このスキルは本リポジトリ運用のために新規作成した内容です。利用・再配布の扱いはリポジトリ方針に従ってください。
