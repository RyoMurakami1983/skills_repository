---
name: skill-writing-guide
description: 高品質なGitHub Copilot agentスキル執筆ガイド。SKILL.md作成時に使用する。
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
- **`skill-revision-guide`** - 既存Skillの改訂と維持

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
author: RyoMurakami1983
tags: [wpf, mvvm, ddd, csharp, dotnet]
invocable: false
license: MIT
version: 1.2.0
---
```

**フィールド指針**:
- **name**: kebab-case、フォルダ名と一致、最大64文字
- **description**: 100文字以内、"Use when..."で起動条件を明示
- **author**: システム作成スキルは`RyoMurakami1983`
- **tags**: 3-5個の技術タグ
- **invocable**: 通常は`false`

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

## アンチパターン

### 1. 1つのSkillにパターンを詰め込みすぎる

**What**: 20+パターンを含めてスキルが過大化。

**Why It's Wrong**:
- 推奨される500行制限を超える
- 内容がスキャンできない
- 段階的開示に反する

**Better Approach**: スキルを分割する。

```markdown
❌ WRONG: wpf-everything-guide (30 patterns)

✅ CORRECT:
- wpf-mvvm-fundamentals (8 patterns)
- wpf-data-binding-patterns (7 patterns)
- wpf-performance-optimization (7 patterns)
```

### 2. 起動条件が不明確なSkill

**What**: 汎用的すぎるdescription。

```yaml
❌ WRONG:
description: A helpful guide for WPF development
```

**Why It's Wrong**:
- GitHub Copilotが起動条件を判断できない
- 読者に発見されない

**Better Approach**: descriptionに"Use when..."を含める。

```yaml
✅ CORRECT:
description: Implement MVVM in WPF with dependency injection and testability. Use when building enterprise WPF applications with complex business logic.
```

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

## 変更履歴

CHANGELOG.mdに詳細を記載。直近の変更：

### Version 2.0.0 (2026-02-12)
- **Core Principles拡張**: Values統合（基礎と型、成長の複利、温故知新、継続は力、ニュートラル）
- **Pattern 8更新**: 500行推奨 + 550行許容（+10%）
- **開発哲学の統合**: Valuesとパターンを整合
- **WHY説明の強調**: 成長の複利に沿った説明追加
- **品質検証同期**: skill-quality-validation 64項目と整合

### Version 1.0.0 (2026-02-12)
- 初版リリース
- 8パターンを収録
- コード例ベストプラクティス定義
- アンチパターンと落とし穴の区別
- 段階的開示戦略を導入

<!-- 
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
