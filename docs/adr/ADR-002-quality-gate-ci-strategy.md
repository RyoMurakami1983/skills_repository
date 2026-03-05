# ADR-002: 品質ゲートCI導入判断と横展開戦略

## ステータス

Accepted

## 日付

2026-03-04

## コンテキスト

private リポジトリの固有名詞（プロジェクト名・クライアント名等）がそのまま public リポジトリ（skills_repository）に混入する事案が発生した（Issue #97）。

原因は、private リポジトリで作成したドキュメントを匿名化せずに public リポジトリへコピーしたことにある。  
`knowledge-capture` スキルの匿名化ゲートを強化（PR #99）したが、それは人間の判断に依存する「検知後対処」の仕組みに過ぎなかった。  
根本対策として、PR 時点で自動的に問題を検出する CI ゲートの設置が必要であると判断した。

## 決定

**gitleaks（必須）+ textlint（任意）の2層品質ゲートを採用し、PR 時点でのブロックを実現する。**

- **gitleaks**: シークレット・固有名詞候補を PR 差分単位でスキャン（GitHub Actions `gitleaks-action@v2` 利用）
- **textlint**: Markdown の無効制御文字・空セクションを検出（Node.js ベース、任意適用）
- **detect-secrets**: 将来の強化オプション（現時点では未導入）

## 検討した選択肢

### Design A（採用）: gitleaks + textlint の2層ゲート

- **概要**: gitleaks でシークレット検出、textlint で Markdown 品質チェックを行う2層構成
- **メリット**:
  - PR 時点で自動ブロック — 人間の判断に依存しない
  - gitleaks は言語・リポジトリ種別に非依存（汎用性が高い）
  - textlint は任意適用 — Markdown 量が少ないリポジトリはオプトイン不要
  - `.gitleaks.toml` の allowlist でドキュメント例示文字列の誤検知を制御可能
  - `github-repo-template` に組み込むことで新規リポジトリへの自動展開が可能
- **デメリット**:
  - Node.js 依存が追加される（textlint）
  - allowlist の初期チューニングが必要

### Design B（不採用）: detect-secrets のみ

- **概要**: Python ベースの detect-secrets で統一
- **メリット**:
  - Python 依存のみ — このリポジトリは uv/Python 環境が既にある
- **デメリット**:
  - Markdown の品質チェック機能がない
  - gitleaks に比べてコミュニティ採用率が低く、allowlist 管理が煩雑

### Design C（不採用）: pre-commit フックのみ

- **概要**: `.pre-commit-config.yaml` でローカル実行のみ
- **デメリット**:
  - ローカル未設定のメンバーや AI エージェントによるコミットをブロックできない
  - CI ゲートなしではメインブランチへの混入を防げない

## 結果

### Positive

- **PR 時点での自動ブロック**: gitleaks が差分スキャンし、シークレット候補を即検出
- **汎用性**: gitleaks は言語・技術スタック非依存で全リポジトリに適用可能
- **横展開の仕組み化**: `github-quality-gate-setup` スキル（PR #101）と `github-repo-template` リポジトリで新規リポジトリへの自動展開を実現
- **低ノイズ設計**: `.gitleaks.toml` allowlist で例示文字列の誤検知を防止

### Negative

- **Node.js 依存追加**: textlint 利用時に `npm install` が必要
- **allowlist 初期コスト**: 導入直後は誤検知が発生するため `.gitleaks.toml` の調整が必要

## 決定基準

- **Fail Fast**: PR 段階でブロックし、main への混入を防ぐ（継続は力）
- **低ノイズ**: allowlist と任意適用 textlint で誤検知を抑制（余白の設計）
- **汎用性**: 言語・技術スタック非依存の gitleaks をコアとして採用（ニュートラルな視点）
- **横展開容易性**: スキル化・テンプレート化で他リポジトリへ自動展開（成長の複利）

## 横展開手順

既存リポジトリへの適用は `github-quality-gate-setup` スキルを参照。

### 新規リポジトリ

1. [`github-repo-template`](https://github.com/RyoMurakami1983/github-repo-template) をテンプレートとして使用
2. gitleaks + textlint は初期設定済みで自動適用される

### 既存リポジトリ

1. `github-quality-gate-setup` スキルを呼び出す
2. `scripts/quality.yml`、`.gitleaks.toml`、`.textlintrc.json`、`package.json` を配置
3. Branch Protection の「Require status checks」に `textlint` と `gitleaks` を追加

## ツール役割分担

| ツール | 役割 | 適用タイミング | 必須/任意 |
|--------|------|--------------|----------|
| gitleaks | シークレット・固有名詞候補の検出 | PR 差分スキャン（CI） | **必須** |
| textlint | Markdown 品質チェック（無効文字・空セクション） | PR 差分（CI） | 任意（Markdown 多用リポジトリ推奨） |
| detect-secrets | より詳細なシークレット分類 | 将来の強化オプション | 将来 |
| knowledge-capture | 人間による匿名化判断（ゲート） | コミット前（手動） | 推奨 |

## 今後の類似判断チェックリスト

品質ゲートの導入・拡張を検討する際は以下の基準で評価する：

- [ ] CI ゲートなしの場合、誰がミスしてもブロックできるか？
- [ ] 採用ツールは言語・技術スタック非依存か、または適用範囲が明確か？
- [ ] allowlist / 設定ファイルで誤検知を抑制できるか？
- [ ] スキル化・テンプレート化で他リポジトリへ横展開できるか？

## 関連

- Issue #97: private リポジトリ固有名詞の漏洩報告
- PR #99: knowledge-capture スキルへの匿名化ゲート追加（短期対策）
- PR #100: textlint + gitleaks の品質ゲートCI追加（恒久対策）
- PR #101: `github-quality-gate-setup` スキル追加
- [ADR-001](./ADR-001-dotnet-security-foundation-extraction.md): .NET WPF セキュリティ基盤の独立スキル抽出
