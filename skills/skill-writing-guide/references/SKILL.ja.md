---
name: skill-writing-guide
description: 高品質なGitHub Copilot agentスキル執筆ガイド。SKILL.md作成時に使用する。
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, documentation, writing-guide]
  invocable: false
---

# Skill執筆ガイド

公式仕様とベストプラクティスに従って高品質なGitHub Copilot agentスキルを作成するための包括的ガイドです。

## このスキルを使うとき

以下の状況で活用してください：
- GitHub Copilot agent向けの新しいSKILL.mdをゼロから作成するとき
- 必須構造やセクションを学びたいとき
- コード例のベストプラクティスと書式を理解したいとき
- When to UseやPatternのレイアウトを設計するとき
- 開発者向けに明確で実行可能なドキュメントを書きたいとき
- GitHub Copilot/Claude仕様への準拠を確認したいとき

---

## 関連スキル

- **`skill-template-generator`** - SKILL.mdテンプレート生成
- **`skill-quality-validation`** - Skill品質の検証とスコアリング
- **`skills-revise-skill`** - 既存Skillの改訂と維持

---

## コア原則

1. **単一ファイル原則** - すべての内容はSKILL.mdに集約し、補助ファイルを増やさない
2. **読者ファースト** - 5秒で関連性を判断できる構成にする
3. **段階的学習** - Simple → Intermediate → Advancedの順で例を提示
4. **問題→解決の順序** - 先に「なぜ」を説明する（成長の複利）
5. **実用性重視** - コピー&ペーストで動くコードを提供
6. **価値観の統合** - 開発哲学（基礎と型、継続は力、ニュートラル）と整合

---

## パターン1: YAML Frontmatter構造

### 概要

YAML frontmatterはスキルのメタデータを定義し、いつどのようにスキルが起動されるかを決定します。適切な設定は発見性に直結します。

### 基本例

```yaml
---
name: your-skill-name
description: One-line description of what problem this skill solves (100 chars max)
invocable: false
---
```

### 使うとき

| シナリオ | 設定 | 理由 |
|----------|------|------|
| 個人スキル | `invocable: false` | 多くのスキルの標準設定 |
| 明示的起動が必要 | `invocable: true` | ユーザーが明示的に呼び出せる |
| 技術特化 | `tags: [tech1, tech2]` | 発見性が向上 |

### 設定例

```yaml
---
name: skill-writing-guide
description: Guide for writing high-quality GitHub Copilot agent skills. Use when creating new SKILL.md files or structuring skill content.
author: RyoMurakami1983
tags: [copilot, agent-skills, documentation]
invocable: false
---
```

### 上級パターン（本番向け）

```yaml
---
name: wpf-mvvm-patterns
description: Implement MVVM in WPF with domain-driven design, dependency injection, and testability. Use when building enterprise WPF applications with complex business logic.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [wpf, mvvm, ddd, csharp, dotnet]
  invocable: false
---
```

**フィールド指針**:
- **name**: kebab-case、フォルダ名と一致、最大64文字
- **description**: 1024文字以内、"Use when..."で起動条件を明示
- **author**: `metadata:` 下に配置。システム作成スキルは`RyoMurakami1983`
- **tags**: `metadata:` 下に配置。3-5個の技術タグ
- **invocable**: `metadata:` 下に配置。通常は`false`
- **version**: トップレベル禁止（Changelogで管理）

---

## パターン2: "When to Use This Skill" セクション

### 概要

タイトル直後に配置する最初のH2セクションです。読者が「今の課題に関係があるか」を素早く判断できます。

### 基本例

```markdown
## When to Use This Skill

Use this skill when:
- Designing public APIs for NuGet packages
- Making changes to existing public APIs
- Planning wire format changes
```

### 使うとき

- ✅ **DO**: 5-8個の具体的で行動的なシナリオを書く
- ✅ **DO**: 各項目を動詞で開始（Designing, Implementing, Building）
- ✅ **DO**: 各項目は50-100文字以内
- ❌ **DON'T**: 抽象表現（"When you need quality code"）
- ❌ **DON'T**: 10個以上並べない

### 設定例

```markdown
## When to Use This Skill

Use this skill when:
- Building enterprise WPF applications with complex business logic
- Implementing MVVM pattern with domain-driven design
- Integrating APIs with retry/circuit breaker policies
- Setting up dependency injection in WPF projects
- Designing testable ViewModels and Services
- Managing application state across multiple views
```

### 上級パターン（本番向け）

役割ベースのシナリオを含める：

```markdown
## When to Use This Skill

Use this skill when:
- **Architects**: Designing multi-tenant WPF application architecture
- **Senior Developers**: Implementing advanced MVVM patterns with CQRS
- **Team Leads**: Reviewing pull requests for MVVM compliance
- **Junior Developers**: Learning MVVM fundamentals in WPF
- **DevOps**: Setting up CI/CD pipelines for WPF applications
```

---

## パターン3: "Core Principles" セクション

### 概要

スキルの哲学的基盤と指針を定義します。3-5個に絞って簡潔に。

### 基本例

```markdown
## Core Principles

1. **Separation of Concerns** - Views, ViewModels, and Models have distinct responsibilities
2. **Dependency Inversion** - Depend on abstractions, not concrete implementations
3. **Testability First** - Design for unit testing from day one
```

### 使うとき

- ✅ **DO**: 3-5個に制限
- ✅ **DO**: **太字名** - 短い説明（30-50文字）で記述
- ❌ **DON'T**: 長い説明は後のセクションへ

> 📚 **上級例**: `references/core-principles-examples.md` を参照

---

## パターン4: パターンセクション（7-10必須）

### 概要

各パターンは具体的なアプローチや実装戦略を示します。完成したSkillには7-10個のパターンが必要です。

### 基本例

```markdown
## Pattern 1: [Pattern Name]

### Overview
Brief explanation (2-3 sentences)

### Basic Example
```csharp
// ✅ CORRECT - Simple case
```

### When to Use
- Condition A
- Condition B

### Advanced Pattern
```csharp
// ✅ CORRECT - Production-ready
```
```

### 使うとき

段階的学習を支える構成：
1. **Overview**: 何を解決するか
2. **Basic Example**: 最小の実装
3. **When to Use**: 判断基準
4. **Advanced**: 本番向け実装

> 📚 **完全な例**: `references/pattern-examples.md` を参照

---

## パターン5: コード例のベストプラクティス

### 概要

コード例は実用的かつコンパイル可能で、段階的に複雑化します。✅/❌マーカーを一貫して使用します。

### 基本例

```csharp
// ✅ CORRECT - Async all the way
public async Task<Data> GetDataAsync()
{
    return await _client.GetAsync("/api/data");
}

// ❌ WRONG - Blocking async code
public Data GetData()
{
    return _client.GetAsync("/api/data").Result; // Deadlock risk
}
```

### 使うとき

**✅/❌マーカーの使用**:
- ✅ `// ✅ CORRECT - Reason` で良い例を示す
- ❌ `// ❌ WRONG - Reason` で悪い例を示す
- 必ず良い例と悪い例をペアで提示

**コンテキストを含める**:
- ✅ using文を含める
- ✅ DI設定を示す
- ✅ 上級例にはエラーハンドリング
- ❌ 疑似コードや"..."は使わない

> 📚 **本番向け例**: `references/advanced-examples.md` を参照

---

## パターン6: 比較表

### 概要

比較表は意思決定を素早く支援します。パターン、ツール、シナリオの比較に使用します。

### 基本例

```markdown
| Scenario | Recommendation | Why |
|----------|----------------|-----|
| Read-only data | AsNoTracking() | No change tracking overhead |
| Update entity | Tracking | Automatic change detection |
```

### 使うとき

**意思決定表**:
- 3列構成（Scenario, Recommendation, Why）
- 5-10行以内
- 推奨項目は太字

**技術比較表**:
- Tool, Type, Performance, Use Whenを含める
- 推奨ツールを太字で強調

### 設定例

```markdown
| Feature | Pattern A | Pattern B | Pattern C |
|---------|-----------|-----------|-----------|
| **Complexity** | Low | Medium | High |
| **Performance** | Good | Better | Best |
| **Maintainability** | High | Medium | Low |
| **Use Case** | Simple CRUD | Complex queries | Bulk operations |
| **Recommendation** | ✅ Start here | Scale to this | **Only if needed** |
```

---

## パターン7: アンチパターンとよくある落とし穴

### 概要

設計上の誤り（Anti-Patterns）と実装ミス（Common Pitfalls）を区別します。

### 基本例

**Common Pitfall**:
```csharp
// ❌ WRONG - Resource not disposed
var stream = File.OpenRead("file.txt");

// ✅ CORRECT - Automatically disposed
using var stream = File.OpenRead("file.txt");
```

### 使うとき

| 種類 | 焦点 | 例 |
|------|------|----|
| **Anti-Pattern** | アーキテクチャ、設計原則 | God Class, Tight Coupling |
| **Common Pitfall** | 実装ミス | Forgetting await, null refs |

> 📚 **詳細**: `references/anti-patterns.md` を参照

---

## パターン8: 500行制限の最適化

### 概要

段階的開示でSKILL.mdを500行以内に保ちつつ品質を維持します。

### コア戦略

**Progressive Disclosure**: 必須内容はSKILL.mdに、詳細はreferences/へ。

```
┌─────────────────────────────────────┐
│ SKILL.md (≤500 lines)               │
│ • ✅ Good patterns (5-15 lines)     │
│ • Basic examples                    │
│ • Simple comparisons                │
└─────────────────────────────────────┘
           ↓ references
┌─────────────────────────────────────┐
│ references/ (loaded when needed)    │
│ • ❌ Anti-pattern details           │
│ • 📚 Advanced implementations       │
│ • ⚙️ Complex configurations         │
└─────────────────────────────────────┘
```

### SKILL.mdに残すもの

✅ **残す**（高優先度）:
1. ✅マーカー付き良い例（5-15行）
2. 基本的なYAML/markdown例
3. 簡潔な比較表
4. コア原則と決定ツリー

### references/へ移すもの

📤 **移動**（低優先度）:
1. ❌詳細なアンチパターン → `references/anti-patterns.md`
2. 📚本番向け実装 → `references/advanced-examples.md`
3. ⚙️複雑な設定 → `references/configuration.md`
4. 🌏日本語版 → `references/SKILL.ja.md`

### 決定ツリー

| 質問 | 回答 | アクション |
|------|------|------------|
| コード例が15行超？ | Yes | references/へ移動を検討 |
| 基本理解に必須？ | No | references/へ移動 |
| アンチパターン？ | Yes | references/anti-patterns.mdへ |
| 上級/本番向け？ | Yes | references/advanced-examples.mdへ |
| 良い基本例？ | Yes | **SKILL.mdに残す** |

### 基本例

✅ **CORRECT - Concise good pattern**:
```yaml
---
name: wpf-databinding
description: Guide for WPF data binding patterns. Use when implementing MVVM.
---
```

> 📚 **アンチパターンと詳細例**: `references/anti-patterns.md` を参照

### 使うとき

次の条件に該当するとき：
- SKILL.mdが500行を超えている
- ✅/❌例が多い
- 本番向け実装が含まれている
- 読者の認知負荷を下げたい

---

## グッドプラクティス（Good Practices）

### 1. 「When to Use」を最初に配置して発見性を高める

**What（概要）**: "When to Use This Skill"を最初のH2セクションとして配置し、5-8個の具体的なシナリオを記載する。

**Why（なぜ良いのか）**:
- 読者が5秒以内に関連性を判断できる
- GitHub Copilotによるスキル発見性が向上する
- エージェントに明確な起動条件を提供できる
- 「ニュートラル」の価値観を実現（誰もが理解可能な形式知化）

**具体例**:
```markdown
## When to Use This Skill

Use this skill when:
- Building enterprise WPF applications with complex business logic
- Implementing MVVM pattern with dependency injection
- Designing testable ViewModels with INotifyPropertyChanged
- Setting up CI/CD pipelines for WPF applications
- Managing application state across multiple views
```

**Why（理由の詳細）**:
最初のH2セクションを「When to Use」にすることで、読者は素早くスキルの適用範囲を把握できます。これは「ニュートラル」の価値観（形式知化で誰もが理解可能）を実現します。また、GitHub Copilot AgentがSKILL.mdを読み込む際、この情報を元に適切なタイミングでスキルを提案できるようになります。

**Values（該当する価値観）**: ニュートラル（形式知化で誰もが理解可能）

---

### 2. ✅/❌マーカーを一貫して使用する

**What（概要）**: すべてのコード例に ✅ CORRECT または ❌ WRONG マーカーと簡潔な理由を付与する。

**Why（なぜ良いのか）**:
- 読者とAIエージェントの混乱を排除できる
- 良いパターンと悪いパターンを素早くスキャンできる
- 対比による学習（Contrast Learning）を強化できる
- 「基礎と型」の価値観を実現（明確なパターン提示）

**具体例**:
```csharp
// ✅ CORRECT - Async all the way（非同期を徹底）
var result = await SomeAsyncMethod();

// ❌ WRONG - Deadlock risk with .Result（.Resultはデッドロックのリスク）
var result = SomeAsyncMethod().Result;
```

```python
# ❌ WRONG - タイムアウトが短すぎる
timeout = 10

# ✅ CORRECT - 本番環境分析に基づく適切な値（2026-02-10調査）
timeout = 30  # Why: 大量データ処理時に10秒では不足。
              # 本番ログ分析により30秒が適切と判断
```

**Why（理由の詳細）**:
マーカーなしでコード例を示すと、読者やAIエージェントは「どちらが推奨されるのか？」を判断できません。これは「ニュートラル」の価値観（明確な形式知化）に反します。✅/❌マーカーを一貫して使用することで、暗黙知を形式知に変換し、誰もが正しいパターンを学べるようになります。

**Values（該当する価値観）**: 基礎と型（明確なパターン）/ 成長の複利（対比による学習）

---

### 3. 段階的開示（Progressive Disclosure）で長さを管理する

**What（概要）**: 必須のグッドパターンはSKILL.md（約500行）に保持し、詳細なアンチパターンや高度な例はreferences/に移動する。

**Why（なぜ良いのか）**:
- AIエージェントのパフォーマンスを維持（集中した内容）
- 認知負荷を軽減（素早いスキャン）
- 深掘り学習のための詳細を保持
- 「基礎と型」の価値観を実現（最小形式で最大可能性）

**具体例**:
```
SKILL.md (≤550行)               references/
├─ ✅ グッドパターン            ├─ anti-patterns.md（詳細なアンチパターン）
├─ 基本例                       ├─ advanced-examples.md（高度な実装例）
└─ コア原則                     └─ SKILL.ja.md（日本語詳細版・人間向け）
```

**Why（理由の詳細）**:
SKILL.mdはGitHub Copilot Agentが読み込むため、約500行（+10%許容で550行）に抑えるのが理想です。これによりAIエージェントの処理効率が向上し、適切なタイミングでスキルを提案できます。一方、人間向けの日本語詳細版（SKILL.ja.md）は行数制限を気にせず、Whyの説明を充実させることができます。

**保持すべき内容（SKILL.md）**:
1. ✅ グッドパターン（5-15行/パターン）
2. 基本的なYAML/Markdown例
3. シンプルな比較（✅ vs ❌、2-3行）
4. コア原則と判断ツリー

**移動すべき内容（references/）**:
1. ❌ 詳細なアンチパターンコード → `references/anti-patterns.md`
2. 📚 本番向け実装 → `references/advanced-examples.md`
3. ⚙️ 複雑な設定 → `references/configuration.md`
4. 🌏 日本語詳細版 → `SKILL.ja.md`（人間向け・行数制限なし）

**Values（該当する価値観）**: 基礎と型（最小形式で最大可能性）

---

### 4. コメントと本文で「Why（なぜ）」を説明する

**What（概要）**: 設計判断には必ず「Why」の説明を含め、「What（何をするか）」だけで終わらせない。

**Why（なぜ良いのか）**:
- 暗黙知を形式知に変換し、チーム知識の共有を促進
- 将来のメンテナが意図を理解できる
- 複利的な学習成長をサポート
- 「成長の複利」の価値観を実現（学習資産化）

**具体例**:
```python
# ❌ WRONG - Whatだけで終わる
timeout = 30

# ✅ CORRECT - Whyを説明（成長の複利）
timeout = 30  # Why: 大量データ処理時に10秒では不足。
              # 本番ログ分析により30秒が適切と判断（2026-02-10調査）
              # 理由: 計測システムから5万件/秒のデータが流入するため、
              #       バッファ確保とネットワーク遅延を考慮した値
```

```csharp
// ❌ WRONG - Whatだけ
var client = new HttpClient();
client.Timeout = TimeSpan.FromSeconds(30);

// ✅ CORRECT - Whyを説明
var client = new HttpClient();
// Why: 外部APIは平均2秒応答だが、ピーク時に10秒超えることがある（監視ログ2026-02分析）
// リトライ戦略と組み合わせて30秒でタイムアウト
client.Timeout = TimeSpan.FromSeconds(30);
```

**Why（理由の詳細）**:
「Why」の説明がないコードは、暗黙知のまま残ります。これは「ニュートラル」の価値観（形式知化）に反します。特に数値パラメータ（タイムアウト値、リトライ回数、バッファサイズ等）は、なぜその値なのかを説明することで、将来の変更時に適切な判断ができます。

また、Whyを説明することで「成長の複利」の価値観も実現できます。読者は単にコードをコピーするのではなく、判断プロセスを学び、自分の状況に応用できるようになります。

**Whyの書き方のコツ**:
1. **根拠を示す**: 「本番ログ分析」「パフォーマンステスト結果」等
2. **日付を記録**: 「2026-02-10調査」等、いつの情報か明記
3. **条件を明示**: 「大量データ処理時」等、どんな状況で必要か
4. **数値の意味**: なぜその数値なのか（平均値+余裕、ピーク時対応等）

**Values（該当する価値観）**: 成長の複利（学習資産化）/ ニュートラル（形式知化）

---

## よくある落とし穴

### 1. 単一ファイル原則の破り

**問題**: README.mdやexamples.mdなどの補助ファイルで内容が分断される。

```
❌ WRONG Structure:
skill-name/
├── SKILL.md
├── README.md          # Redundant
├── examples.md        # Should be in SKILL.md
└── guidelines.md      # Should be in SKILL.md
```

**解決策**: すべての内容をSKILL.mdに統合。500行超の場合のみ`references/`で分離。

```
✅ CORRECT Structure:
skill-name/
└── SKILL.md           # Single source of truth
```

### 2. あいまいな"When to Use"

**問題**: 抽象的なシナリオでは関連性判断ができない。

```markdown
❌ WRONG:
- When you want to write good code
- Use this for WPF applications
- Helpful for developers
```

**解決策**: 具体的で行動的なシナリオを書く。

```markdown
✅ CORRECT:
- Building enterprise WPF applications with complex business logic
- Implementing MVVM pattern with dependency injection
- Designing testable ViewModels with INotifyPropertyChanged
```

### 3. ✅/❌マーカーの欠落

**問題**: 良い例と悪い例の区別ができない。

```csharp
// UNCLEAR - Is this good or bad?
var result = SomeAsyncMethod().Result;
```

**解決策**: 明示的なマーカーを必ず付ける。

```csharp
// ❌ WRONG - Deadlock risk with .Result
var result = SomeAsyncMethod().Result;

// ✅ CORRECT - Async all the way
var result = await SomeAsyncMethod();
```

---

## アンチパターン（詳細解説）

### 1. 1つのSkillにパターンを詰め込みすぎる

**What（概要）**: 20+パターンセクションを1つのスキルに含め、圧倒的な量になってしまう。

**Why It's Wrong（なぜ間違いか）**:
1. **認知負荷の超過**: 読者が効果的にスキャンまたは吸収できない
2. **500行制限の違反**: AIエージェントの最適処理には大きすぎる
3. **段階的開示の破綻**: 複雑さを段階的に提示せず、すべてを一度にダンプする
4. **発見性の低下**: 読者が関連するパターンを素早く見つけられない

**症状（こうなっていたら要注意）**:
- SKILL.mdが1000行以上になっている
- 目次に20+のパターンセクションがある
- 読者から「圧倒される」というフィードバック
- GitHub Copilotが適切にスキルを起動できない

**具体例**:
❌ **WRONG - モノリシックなSkill**:
```markdown
# wpf-everything-guide

## Pattern 1: Basic XAML Binding
## Pattern 2: INotifyPropertyChanged
## Pattern 3: Commands
## Pattern 4: Data Templates
## Pattern 5: Control Templates
... (さらに25個のパターン)
```

✅ **CORRECT - 焦点を絞ったSkills**:
```markdown
# wpf-mvvm-fundamentals (8 patterns)
- INotifyPropertyChanged
- Commands  
- ViewModels
- 基本的なデータバインディング
- 依存性注入
- ViewModelの単体テスト
- MVVMメッセージング
- よくある落とし穴

# wpf-data-binding-patterns (7 patterns)
- OneWay vs TwoWay
- Data Templates
- Item Templates
- Value Converters
- MultiBinding
- RelativeSource
- Validation Rules
```

**Better Approach（改善策）**:
1. **関連トピックを特定**: パターンをテーマごとにグループ化
2. **複数スキルに分割**: 1つの巨大スキルではなく、2-4つの焦点を絞ったスキルを作成
3. **相互参照**: Related Skillsセクションで関連スキルをリンク
4. **7-10パターンを目標**: 各スキルを焦点を絞り、管理しやすく

**価値観への影響**:
- **「基礎と型」に違反**: 過負荷では明確な基礎構造がない
- **「ニュートラル」に違反**: 誰もが理解するには複雑すぎる

---

### 2. 起動条件が不明確なSkill

**What（概要）**: YAML frontmatterで汎用的な説明を書き、GitHub Copilotがいつスキルを起動すべきか判断できない。

**Why It's Wrong（なぜ間違いか）**:
1. **AIの発見性が低い**: GitHub Copilotがスキルの関連性を判断できない
2. **無駄な起動**: 適用できない場面でもスキルが読み込まれる
3. **ユーザーの不満**: 開発者が必要な時にスキルを見つけられない
4. **曖昧な目的**: 価値提案が不明確

**症状（こうなっていたら要注意）**:
- Descriptionに"Use when..."句がない
- Descriptionが汎用的（"helpful guide", "useful tool"等）
- 技術特化のtagsがない
- 関連性があるにもかかわらずスキルが起動されない

**具体例**:
❌ **WRONG - 曖昧な説明**:
```yaml
---
name: wpf-guide
description: A helpful guide for WPF development
tags: [wpf]
---
```

✅ **CORRECT - 具体的な起動条件**:
```yaml
---
name: wpf-mvvm-patterns
description: Implement MVVM in WPF with domain-driven design, dependency injection, and testability. Use when building enterprise WPF applications with complex business logic.
author: RyoMurakami1983
tags: [wpf, mvvm, ddd, csharp, dotnet]
invocable: false
---
```

**Better Approach（改善策）**:
1. **"Use when..."を含める**: Descriptionで起動シナリオを明示
2. **具体的に**: 技術、パターン、ユースケースを言及
3. **関連タグを追加**: 3-5個の技術焦点タグ
4. **100文字制限**: 簡潔だが情報豊富に
5. **行動指向**: 開発者が達成しようとしていることに焦点

**Description公式**:
```
[動詞] + [コア技術/パターン] + [追加コンテキスト] + "Use when" + [具体的シナリオ]
```

**価値観への影響**:
- **「ニュートラル」に違反**: 明確さの欠如が潜在的ユーザーを排除
- **「成長の複利」に違反**: 発見性が低いと学習が妨げられる

---

### 3. ✅/❌マーカーなしでコード例を混在させる

**What（概要）**: ✅ CORRECT や ❌ WRONG マーカーなしでコード例を示し、読者とAIエージェントを混乱させる。

**Why It's Wrong（なぜ間違いか）**:
1. **曖昧性**: 読者がグッドプラクティスとアンチパターンを区別できない
2. **AIの混乱**: GitHub Copilotが悪いパターンを学習して複製する可能性
3. **知識移転の失敗**: 形式知化（明示的知識移転）に違反
4. **学習効率の低下**: 対比学習には明確なラベルが必要

**症状（こうなっていたら要注意）**:
- コード例に✅/❌マーカーがない
- コメントがコードの良し悪しを説明していない
- 複数の例を推奨なしで示している
- 読者から「どのアプローチを使うべきか？」という質問が出る

**具体例**:
❌ **WRONG - ラベルなし**:
```csharp
// アプローチ1
var result = SomeAsyncMethod().Result;

// アプローチ2  
var result = await SomeAsyncMethod();
```

✅ **CORRECT - 明確なラベル**:
```csharp
// ❌ WRONG - .Resultはデッドロックのリスク
var result = SomeAsyncMethod().Result;

// ✅ CORRECT - 非同期を徹底
var result = await SomeAsyncMethod();
```

**マーカーガイドライン**:

| マーカー | 使用時 | 形式 |
|---------|--------|------|
| ✅ CORRECT | グッドプラクティス、推奨アプローチ | `// ✅ CORRECT - [簡潔な理由]` |
| ❌ WRONG | アンチパターン、避けるべきミス | `// ❌ WRONG - [何が悪いか]` |
| ⚠️ CAUTION | 動作するが制限あり | `// ⚠️ CAUTION - [制限]` |
| 📝 NOTE | 追加コンテキスト | `// 📝 NOTE - [コンテキスト]` |

**Better Approach（改善策）**:
1. **常にマーカーを使用**: すべてのコード例に✅または❌を付ける
2. **悪い例と良い例をペアに**: 間違った方法を示した後、正しい方法を示す
3. **Whyを説明**: 根拠を簡潔なコメントで含める
4. **一貫したフォーマット**: スキル全体で同じマーカースタイルを使用

**高度なパターン（複雑なシナリオ用）**:
アプローチを比較する表を使用:

```markdown
| 側面 | ❌ アンチパターン | ✅ グッドプラクティス |
|------|----------------|---------------------|
| **アプローチ** | `result = task.Result` | `result = await task` |
| **リスク** | UIスレッドでデッドロック | ブロッキングなし |
| **パフォーマンス** | スレッドをブロック | 非同期を徹底 |
| **使用ケース** | 決して使用しない | 非同期コードでは常に |
```

**価値観への影響**:
- **「ニュートラル」に違反**: 曖昧性が形式知化を妨げる
- **「成長の複利」に違反**: 対比学習の効果が低下
- **「基礎と型」に違反**: 不明確なパターンが適切な基礎を阻害

---

### 4. （追加）日本語版で詳細説明を省略する

**What（概要）**: 日本語版（SKILL.ja.md）でも英語版（SKILL.md）と同じ簡潔さを保ち、Whyの詳細説明を省略してしまう。

**Why It's Wrong（なぜ間違いか）**:
1. **学習機会の損失**: 人間向けの詳細説明で理解を深める機会を逃す
2. **暗黙知のまま**: Why（なぜ）が不明確だと、パターンの背景を理解できない
3. **「成長の複利」の未実現**: 詳細説明がないと学習資産にならない

**Better Approach（改善策）**:
- **SKILL.md（英語・AI向け）**: 簡潔に、約500行以内
- **SKILL.ja.md（日本語・人間向け）**: 詳細に、行数制限なし

**具体例**:
```markdown
## SKILL.md（英語・AI向け）
timeout = 30  # Why: Production analysis showed 10s insufficient for large datasets

## SKILL.ja.md（日本語・人間向け）
timeout = 30  # Why: 大量データ処理時に10秒では不足。
              # 本番ログ分析により30秒が適切と判断（2026-02-10調査）
              # 理由: 計測システムから5万件/秒のデータが流入するため、
              #       バッファ確保とネットワーク遅延を考慮した値
              # 根拠: 本番環境で1週間の監視ログを分析した結果、
              #       ピーク時に最大25秒かかるケースが0.1%存在
              # 対策: 30秒でタイムアウトし、リトライ戦略で再試行
```

**価値観への影響**:
- **「成長の複利」に違反**: 詳細説明がないと学習資産にならない
- **「ニュートラル」に違反**: 誰もが理解できる形式知化が不十分

---

## アンチパターンまとめ

これらのアンチパターンはスキル品質を損なう一般的なミスです：

1. **詰め込みすぎ**: 認知過負荷と500行原則の違反
2. **曖昧な起動**: 発見と適切なAI起動を妨げる
3. **ラベルなし**: 曖昧性と学習混乱を引き起こす
4. **日本語版で手抜き**: 人間向け学習機会の損失

### 改善チェックリスト

各スキル作成時に確認：

- [ ] 総行数 < 550行（500 + 10%許容）※SKILL.mdのみ
- [ ] パターン数: 7-10個（20+ではない）
- [ ] Descriptionに"Use when..."句を含む
- [ ] すべてのコード例に✅/❌マーカー
- [ ] タグが具体的で技術焦点
- [ ] 関連スキルを相互参照
- [ ] 段階的開示を適用（詳細はreferences/へ）
- [ ] 日本語版（SKILL.ja.md）でWhyを詳細に説明

### 価値観との整合

- **基礎と型**: 明確なパターン、焦点を絞ったスコープ、最小形式
- **成長の複利**: 適切なラベルと構造による効果的学習
- **ニュートラル**: 明示的な形式知化による普遍的理解
- **継続は力**: 小さく焦点を絞ったスキルは維持しやすい
- **温故知新**: 一般的なミスから学び、現代のベストプラクティスを適用

> 📚 **さらに詳細な英語版アンチパターン解説**: `references/anti-patterns.md` を参照

---

## クイックリファレンス

### Skill構成チェックリスト

- [ ] YAML frontmatter（name, description, author, tags）
- [ ] H1タイトルがSkill名と一致
- [ ] Related Skillsセクション
- [ ] "When to Use This Skill" が最初のH2（5-8シナリオ）
- [ ] Core Principles（3-5原則）
- [ ] 7-10個のPatternセクション（段階的例付き）
- [ ] Common Pitfalls（3-5項目）
- [ ] Anti-Patterns（2-4項目）
- [ ] Quick Reference または Decision Tree
- [ ] Best Practices Summary
- [ ] Resourcesセクション
- [ ] Changelog（大きい場合はCHANGELOG.mdへリンク）

### セクション執筆チェックリスト

- [ ] ✅/❌マーカーを一貫して使用
- [ ] using文とDI設定を含める
- [ ] WHYを説明し、WHATに留めない
- [ ] SKILL.mdを500行以内に保つ
- [ ] 判断支援に表を使う
- [ ] "When to Use"項目は動詞で開始
- [ ] Core Principlesは独立して簡潔に
- [ ] パターン構成: Overview → Basic → Configuration → Advanced

### コード品質チェックリスト

- [ ] すべてのコード例がコンパイル可能
- [ ] 上級例にエラーハンドリングがある
- [ ] AsyncメソッドにCancellationTokenを含む
- [ ] リソースが確実に破棄される（using）
- [ ] 適切なDI設定が示されている

---

## ベストプラクティスまとめ

1. **単一ファイル原則** - 内容はSKILL.mdに集約し分割しない
2. **起動条件を明確化** - descriptionに具体的な"Use when"を書く
3. **段階的な複雑度** - Basic → Configuration → Advancedで構成
4. **マーカー統一** - ✅/❌をすべてのコード例で使用
5. **行動的なシナリオ** - "When to Use"は動詞開始
6. **WHYを説明** - コードコメントは理由を説明
7. **7-10パターン** - 過不足なく網羅
8. **比較表を活用** - 意思決定を支援
9. **アンチパターンと落とし穴を分離** - 設計と実装を区別
10. **500行制限** - 追加情報はreferences/へ

---

## リソース

- [GitHub Copilot Agent Skills Documentation](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Claude Skills Documentation](https://claude.com/docs/skills/overview)
- [Agent Skills Specification](https://agentskills.io/specification)
- [SKILL_TEMPLATE.md](../../.copilot/docs/SKILL_TEMPLATE.md) - English template
- [SKILL_TEMPLATE.ja.md](../../.copilot/docs/SKILL_TEMPLATE.ja.md) - Japanese template

---
