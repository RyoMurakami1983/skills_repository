---
name: dotnet
description: >
  広い .NET / C# / WPF 相談を、既存の dotnet skill や deploy workflow へ案内する薄い入口 skill。Use when: ユーザーが「dotnet」「.NET」「C#」「WPF」「EF Core」など広く言っていて、まだ具体 skill が定まっていないとき。
---
# .NET 入口 skill

`.NET` 系の相談で、まだどの具体 skill を使うべきか曖昧なときに最初に入るための薄い入口です。

この skill は `dotnet-project-structure` や `dotnet-wpf-mvvm-patterns` など既存の具体 skill を置き換えません。最初の振り分けだけを担当し、意図が明確になったら速やかに具体 skill へ委譲します。

## こんなときに使う
次のような場面で使います。
- `.NET` や `C#` の広い相談を最初に分類したいとき
- WPF アプリ関連の相談をどの WPF 系 skill に振るか判断したいとき
- solution bootstrap を project structure / DI / configuration / package management に振り分けたいとき
- EF Core、serialization、database performance を data 系 skill へ案内したいとき
- `.github/skills/` への curated deployment が必要か判断したいとき

## Decision Table

| 意図 | ルート | 何をするか |
| --- | --- | --- |
| 新しい `.NET` solution を作る・整える | `dotnet-project-structure` | まず project structure から入り、必要に応じて infra skill を追加する。 |
| 推奨 skill セットをプロジェクトへ配備したい | `dotnet-skill-deploy` | `foundation`、`wpf`、`wpf-app` などのカテゴリから必要分だけ配備する。 |
| WPF アプリを作る・改善する | `dotnet-wpf-mvvm-patterns` | まず MVVM を土台にし、その後 secure config、dialog、OCR、PDF、integration に分岐する。 |
| EF Core / serialization / DB 性能に取り組む | `dotnet-efcore-patterns`、`dotnet-serialization`、`dotnet-database-performance` | UI や bootstrap ではなく data 系の流れに留まる。 |
| テスト、snapshot、Playwright、containers を整える | `dotnet-testcontainers`、`dotnet-snapshot-testing`、`dotnet-playwright-blazor`、`dotnet-playwright-ci-caching` | testing concern ごとに絞って案内する。 |
| DI、configuration、tools、package management を扱う | `dotnet-extensions-dependency-injection`、`dotnet-extensions-configuration`、`dotnet-local-tools`、`dotnet-package-management` | アプリ機能ではなく infra / bootstrap concern として扱う。 |

## Related Skills

- **`dotnet-skill-deploy`** — `.NET` skill セットをプロジェクトに配備する
- **`dotnet-project-structure`** — 新規 solution や modernize の第一候補
- **`dotnet-wpf-mvvm-patterns`** — WPF 相談の第一候補
- **`dotnet-efcore-patterns`** — data / persistence の第一候補
- **`dotnet-testcontainers`** — testing / integration の代表ルート

## Routing Notes

- 意図が明確になったら直接 concrete skill を呼ぶ。入口 skill に留まり続けない。
- `WPF` は `.NET` の中で最も強い sub-domain だが、現時点では top-level `wpf` skill へは分離しない。
- deploy 実行は `dotnet-skill-deploy` に委譲し、この skill 自体は routing に集中する。
