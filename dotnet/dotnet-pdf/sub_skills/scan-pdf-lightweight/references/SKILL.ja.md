---
name: scan-pdf-lightweight
description: スキャンPDFを OCR 向けに軽量化する .NET 用 sub-skill。
---

# スキャンPDF軽量化 sub-skill

この sub-skill は、スキャンPDFを OCR サービスへ送る前に軽量化し、  
アップロード安定性やトークン効率を改善したいときのための型です。

ここで大事なのは、単なる「圧縮」ではなく、**OCR入力として扱いやすい PDF を安全に作る** ことです。

## この sub-skill が向く場面

- OCR へ送るスキャンPDFが重く、アップロードが不安定なとき
- ネットワーク要因で大きな request body が切断されやすいとき
- .NET アプリ内で、グレースケール化・JPEG再構成・再PDF化を行いたいとき
- DDD 構成を崩さず、画像処理を Infrastructure に閉じ込めたいとき
- 前処理が適用されたかどうかを診断ログで追えるようにしたいとき

## このリポジトリでの知見

このプロジェクトでは、OCR経路に対して以下の流れを採りました。

1. 元PDFを OCR 用チャンクへ分割
2. 各ページを rasterize
3. グレースケール化
4. JPEG で再エンコード
5. OCR用の一時PDFへ再構成
6. 元チャンクより大きくなったら前処理版を採用しない

この構成により、「軽くできるときだけ軽くする」という安全な最適化になっています。

## DDD での責務

### Domain

- `OcrPreprocessSettings` のような設定値オブジェクトを置く
- 「OCR用前処理を使う」という要求の意味だけを持つ

### Application

- `SplitIntoOcrChunks(...)` のような抽象化された要求を使う
- 画像処理の詳細やライブラリ名を知らない
- 診断イベントを組み立てて Presentation に渡す

### Infrastructure

- PDF レンダリング
- グレースケール化
- JPEG エンコード
- 一時 PDF 再構成
- サイズ比較とフォールバック
- 一時ファイル掃除

この分離を守ることで、PDF 処理の変更が Application の振る舞い説明と混ざりません。

## TDD で先に固定したいこと

- OCR 経路だけが前処理を通ること
- 前処理後サイズが元より大きいときは元PDFへ戻ること
- グレースケール出力になっていること
- 診断で「適用/スキップ」が分かること
- 最終の1枚保存や通常分割に影響しないこと

## 推奨する diagnostic 観点

最低限、以下を構造化して持つのがおすすめです。

- chunk index
- start/end page
- original size
- output size
- target DPI
- grayscale flag
- preprocessing result（適用 / スキップ）

文字列だけに埋め込むと後で再利用しづらいので、可能な限り構造化してください。

## 注意点

- 軽量化は最適化であり、正しさの本体ではない
- サイズだけを追うと OCR 精度が下がる場合がある
- `.preprocessed` のような一時ファイルは失敗時も必ず掃除する
- プロジェクト実績をベースにしても、skill 自体は再利用できる trigger に寄せる
