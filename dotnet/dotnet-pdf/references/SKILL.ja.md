---
name: dotnet-pdf
description: .NET の PDF 関連要求を適切な skill や sub-skill に振り分けるルーター。
---

# dotnet-pdf ルーター

`dotnet-pdf` は、.NET における PDF 関連要求の入口を 1 つにまとめるためのルーターです。  
目的は「全部を 1 skill に書く」ことではなく、PDF の知見を同じ家系に集めながら、実装ガイド自体は小さな sub-skill に分けることです。

## この構造を採る理由

- PDF は「プレビュー」「OCR入力最適化」「分割」「トリミング」のように要求の形がかなり異なります。
- これらを 1 つの巨大 skill にまとめると、trigger がぼやけて発火しにくくなります。
- 一方で完全にバラバラにすると、PDF の共通文脈が散らばって再利用しにくくなります。

そのため、`dotnet-pdf` は **薄いルーター** にして、個別の実装 guidance は `sub_skills/` 配下へ寄せます。

## 現時点での位置づけ

- WPF の PDF 表示は、すでに `dotnet-wpf-pdf-preview` があるため再実装しません。
- OCR 全体フローは `dotnet-ocr-matching-workflow` があるため、`dotnet-pdf` はそれを置き換えません。
- `dotnet-pdf` が最初に扱う新しい価値は、**スキャンPDFの軽量化** です。

## 初回サブスキル

- `scan-pdf-lightweight`

この名前を推奨する理由は、JPEG品質や DPI、グレースケールなどの**手段**ではなく、  
「OCR入力用PDFを軽くして安定させる」という**狙い**を表せるためです。

## ルーティングの考え方

| 要求 | 行き先 |
| --- | --- |
| WPF で PDF を表示したい | `dotnet-wpf-pdf-preview` |
| OCR入力用のスキャンPDFを軽くしたい | `sub_skills/scan-pdf-lightweight` |
| OCR全体のワークフローを組みたい | `dotnet-ocr-matching-workflow` |
| 今後の PDF 分割・トリミング・正規化を追加したい | `dotnet-pdf` 配下に新規 sub-skill |

## 拡張方針

将来的に以下のような sub-skill を追加できます。

- `scan-pdf-crop`
- `scan-pdf-split`
- `scan-pdf-ocr-input`

ただし、既存 skill と役割が重なるなら、新規追加より **参照** を優先してください。

## 注意点

- router に具体的なコード例を書きすぎない
- project 固有の事情は references で補足し、本体は再利用できる粒度を保つ
- PDF 家系の skill を増やすときも、trigger が 1 つに絞れる単位で切る
