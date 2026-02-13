---
name: skill-quality-validation
description: GitHub Copilot agentスキルの品質を検証する。SKILL.mdのレビュー時に使用する。
author: RyoMurakami1983
tags: [copilot, agent-skills, quality, validation, testing]
invocable: false
---

# Skill品質検証

GitHub Copilot agentスキル向けの64項目チェックリスト、スコアリング、開発哲学統合を備えた包括的品質評価システムです。

## このスキルを使うとき

以下の状況で活用してください：
- 完成したSKILL.mdを公開前にレビューして品質保証したい
- 公式の64項目基準に対してスキル品質を評価したい
- スコアと改善提案を含む詳細レポートを作成したい
- ドキュメント構造や内容の問題を特定したい
- GitHub Copilot/Claude仕様への準拠を検証したい
- コード例を含むピアレビューを徹底したい

---

## 関連スキル

- **`skill-writing-guide`** - Skill執筆のベストプラクティス
- **`skill-template-generator`** - Skillテンプレート生成
- **`skills-revise-skill`** - 検証結果に基づく修正

---

## コア原則

1. **定量評価** - 64項目チェックリストで客観評価
2. **カテゴリ別スコア** - Structure(14), Content(23), Code Quality(16), Language(11)
3. **明確な合格基準** - 各カテゴリ80%、全体80%（51/64）
4. **実行可能なフィードバック** - 具体的な失敗と改善提案
5. **継続的改善** - 90%+を目標に反復
6. **哲学の統合** - 開発Valuesと整合（基礎と型、成長の複利、温故知新、継続は力、ニュートラル）

---

## パターン1: 品質チェックの実行

### 概要

64項目チェックリストで4カテゴリの品質を評価し、ファイル長最適化、references/構造、日英対応、開発哲学の整合も確認します。

### 基本例

**クイックチェック**（手動）:
1. SKILL.mdを開く
2. YAML frontmatterに必須項目があるか確認
3. "When to Use This Skill" が最初のH2か確認
4. パターン数を数える（7-10）
5. Common PitfallsとAnti-Patternsが存在するか確認

### 使うとき

| シナリオ | アプローチ | 理由 |
|----------|------------|------|
| 公開前レビュー | 64項目の全チェック | 品質基準を保証 |
| 迅速確認 | 10項目の構造チェック | 執筆中の早期フィードバック |
| ピアレビュー | 内容 + コードチェック | 中身に集中 |
| 修正後 | 以前の失敗項目を再確認 | 修正の確認 |

### 設定例

**構造化チェックリスト**:

```markdown
## 1. Structure Check (11 items)

- [x] 1.1 SKILL.md only, no additional files
- [x] 1.2 YAML frontmatter with name/description/invocable
- [x] 1.3 Name matches directory (kebab-case)
- [x] 1.4 Description ≤ 100 chars, problem-focused
- [x] 1.5 "When to Use This Skill" is first H2 section
- [x] 1.6 "Core Principles" section exists
- [ ] 1.7 7-10 pattern sections (H2)          ← FAIL: Only 3 patterns
- [x] 1.8 "Common Pitfalls" section exists
- [x] 1.9 "Anti-Patterns" section exists
- [x] 1.10 "Quick Reference" or "Decision Tree" exists
- [x] 1.11 SKILL.md file ≤500 lines (Claude/GitHub Copilot recommendation)

**Score**: 9/11 = 82% ✅ PASS
```

---

## パターン2: 構造検証（14項目）

### 概要

ファイル構造、セクション順序、frontmatter準拠、行数最適化、references/構成、日英対応を検証します。

### 基本例

**14項目の構造チェック**:

1. **Single File**: SKILL.mdのみ（README.md, examples.md等は不可）
2. **YAML Frontmatter**: name/description/invocableを含む
3. **Name Consistency**: nameがフォルダ名と一致（kebab-case）
4. **Description Length**: 100文字以内、問題解決に焦点
5. **When to Use Position**: タイトル直後の最初のH2
6. **Core Principles**: セクションが存在
7. **Pattern Count**: 7-10個のH2パターン
8. **Common Pitfalls**: セクションが存在
9. **Anti-Patterns**: セクションが存在
10. **Quick Reference**: セクションまたはDecision Treeが存在
11. **File Length Optimization**: ≤500行推奨、≤550行は警告
12. **References Directory**: 500行超ならreferences/必須
13. **Japanese Version**（ボーナス）: `references/SKILL.ja.md`が存在
14. **References Validity**: references/内の命名規則を検証

### 使うとき

構造検証は次のタイミングで実施：
- **執筆前**: 骨格が正しいか確認
- **大規模リファクタ後**: 構造の整合性を確認
- **ピアレビュー**: 構造の準拠を素早く確認

**合格基準**: 11/14 (79%) 以上

### 設定例

**詳細ルール**:

```yaml
# Structure Check Configuration
checks:
  1.1_single_file:
    rule: "Count of *.md files in skill directory == 1"
    allow_exceptions: ["references/SKILL.ja.md", "references/*.md", "CHANGELOG.md"]
  
  1.4_description_length:
    rule: "len(frontmatter['description']) <= 100"
    severity: "warning"  # Over 100 is warning, over 150 is failure
  
  1.7_pattern_count:
    rule: "7 <= pattern_count <= 10"
    count_method: "regex: ^## Pattern \\d+:"
  
  1.11_file_length_optimization:
    rule: |
      if line_count <= 500: PASS
      elif line_count <= 550: PASS with WARNING (+10% tolerance)
      else: FAIL (require references/ structure)
    recommended: 500
    tolerance: 550
  
  1.12_references_directory:
    rule: "If line_count > 500, check references/ directory exists"
    valid_files: ["anti-patterns.md", "advanced-examples.md", "configuration.md", "SKILL.ja.md"]
    required_count: ">= 1"
  
  1.13_japanese_version:
    rule: "Check for references/SKILL.ja.md"
    bonus: true  # +1 bonus point if exists
    required: false
  
  1.14_references_validity:
    rule: "If references/ exists, validate all files are *.md"
    severity: "error"
```

---

## パターン3: 内容検証（23項目）

### 概要

"When to Use"、Core Principles、Patterns、Problem-Solution構造、Values統合、Why説明の有無を検証します。

### 基本例

**主要チェック項目**:

- **When to Use**（4項目）:
  - 5-8個の具体的シナリオ
  - 各項目が動詞で開始
  - 50-100文字以内
  - 抽象表現がない（"good code"等）

- **Patterns**（6項目）:
  - Overviewがある
  - Basic/Intermediate/Advancedの3段階
  - "When to Use"がある
  - パターン間の重複がない

- **Core Principles**（2項目）:
  - Values統合（基礎と型、成長の複利など）
  - スキル目的と整合

- **Pattern Quality**（2項目）:
  - Why説明がある
  - Progressive Disclosureが守られている

### 使うとき

内容検証は以下に必須：
- **実用性の評価**: 実行可能なガイダンスか
- **完全性の確認**: 必須サブセクションの有無
- **明確性の確認**: 具体的なシナリオか

**合格基準**: 18/23 (78%) 以上

### 設定例

**検証ルール**:

```python
# ✅ CORRECT - Validate "When to Use" scenarios
scenarios = skill.get_when_to_use_scenarios()

# Check 2.1.1: Count (5-8 scenarios)
if 5 <= len(scenarios) <= 8:
    pass  # ✅ Valid

# Check 2.1.2: Start with verb
if all(scenario.split()[0].lower() in ACTION_VERBS for scenario in scenarios):
    pass  # ✅ Valid

# Check 2.1.3: Length (50-100 chars)
if all(50 <= len(s) <= 100 for s in scenarios):
    pass  # ✅ Valid

# Check 2.1.4: No abstract phrases
if not any(phrase in s.lower() for s in scenarios for phrase in ABSTRACT_PHRASES):
    pass  # ✅ Valid

# ✅ NEW - Validate Core Principles - Values integration
core_principles = skill.get_core_principles()
DEVELOPMENT_VALUES = ['基礎と型', '成長の複利', '温故知新', '継続は力', 'ニュートラル']

# Check 2.2.1: Values integration (bonus)
values_found = any(value in core_principles for value in DEVELOPMENT_VALUES)
if values_found:
    bonus_points += 1  # +1 bonus point

# ✅ NEW - Validate Pattern Quality - Why explanations
advanced_patterns = skill.get_patterns(level='Advanced')

# Check 2.2.2: Why explanations in complex patterns
why_count = sum(1 for p in advanced_patterns if 'why' in p.lower() or '理由' in p)
if why_count >= len(advanced_patterns) * 0.5:  # At least 50%
    pass  # ✅ Valid

# ✅ NEW - Validate Progressive Disclosure
if skill.line_count > 500:
    # Check 2.2.3: Progressive Disclosure strategy
    has_references_dir = Path('references/').exists()
    advanced_in_references = any(f.name.startswith('advanced') for f in Path('references/').glob('*.md'))
    if has_references_dir and advanced_in_references:
        pass  # ✅ Valid
```

> 📚 **完全な実装**: `references/validation-examples.md` を参照  
> 📚 **失敗例**: `references/anti-patterns.md` を参照

---

## パターン4: コード品質検証（16項目）

### 概要

コンパイル可能性、段階的複雑度、マーカー一貫性、本番品質、コード例の長さ制限を検証します。

### 基本例

**主要チェック項目**:

- **Compilability**（3項目）: コードがコンパイル可能、usingあり、依存関係の明記
- **Progression**（3項目）: Simple → Advancedの順序、各段階を説明
- **Markers**（4項目）: ✅/❌の一貫使用、コメントはWHY
- **Completeness**（5項目）: DI設定、エラーハンドリング、async/await、リソース破棄
- **Code Length**（1項目）: 例は15行以内（超過はreferences/へ）

### 使うとき

コード検証で保証すること：
- コピー&ペーストで動く
- 段階的に学べる
- 本番向けパターンが示される

**合格基準**: 13/16 (81%) 以上

### 設定例

**コード品質チェック**:

```python
# ✅ CORRECT - Validate code markers and comment quality
import re

# Check 3.3.1: Validate ✅/❌ markers are used consistently
code_blocks = re.findall(r'```\w+\n(.*?)```', content, re.DOTALL)
for block in code_blocks:
    if re.search(r'\bclass\b|\bpublic\b', block):
        assert re.search(r'//\s*[✅❌]', block), "Missing ✅/❌ marker"

# Check 3.3.3: Comments explain WHY not WHAT
WHAT_PATTERNS = [r'//\s*Get\s+\w+', r'//\s*Set\s+\w+', r'//\s*Call\s+\w+']
for block in code_blocks:
    for pattern in WHAT_PATTERNS:
        assert not re.search(pattern, block), "Comment explains WHAT, should explain WHY"

# ✅ NEW - Check 3.16: Code example length limit
for block in code_blocks:
    lines = [l for l in block.split('\n') if l.strip() and not l.strip().startswith('using')]
    line_count = len(lines)
    
    if line_count <= 15:
        pass  # ✅ Valid - Inline examples are concise
    elif line_count <= 20:
        warnings.append("Code example is 16-20 lines, consider moving to references/")
    else:
        # >20 lines should be in references/advanced-examples.md
        has_advanced_ref = Path('references/advanced-examples.md').exists()
        assert has_advanced_ref, "Code example >20 lines requires references/advanced-examples.md"
```

> 📚 **完全な実装**: `references/validation-examples.md` を参照  
> 📚 **失敗例**: `references/anti-patterns.md` を参照

---

## パターン5: 言語・表現検証（11項目）

### 概要

文体、用語の一貫性、可読性、日英対応を検証します。

### 基本例

**主要チェック項目**:

- **Style**（4項目）: 能動態、短文、命令形、曖昧さの排除
- **Terminology**（3項目）: 用語統一、初出定義、略語展開
- **Scannability**（3項目）: 見出しと表の明瞭性
- **Bilingual Support**（1項目）: 英語SKILL.md + 日本語references/SKILL.ja.md（ボーナス）
- **Scannability**（3項目）: 見出し構造、表の明確さ、重要情報の強調

### 使うとき

言語検証で保証すること：
- 読みやすさと理解のしやすさ
- 技術用語の定義
- ざっと読んでも理解できる構成

**合格基準**: 9/11 (82%) 以上

### 設定例

**言語品質チェック**:

```python
# ✅ CORRECT - Validate sentence length and active voice
import re

# Check 5.1.2: Sentences ≤ 20 words
sentences = re.split(r'[.!?]\s+', text)
for sentence in sentences:
    word_count = len(sentence.split())
    assert word_count <= 20, f"Sentence too long: {word_count} words"

# Check 5.1.1: Detect passive voice
PASSIVE_INDICATORS = [r'\bis\s+\w+ed\b', r'\bwas\s+\w+ed\b', r'\bcan\s+be\s+\w+ed']
passive_count = sum(1 for s in sentences for p in PASSIVE_INDICATORS if re.search(p, s))
passive_ratio = passive_count / len(sentences)
assert passive_ratio < 0.2, f"Too much passive voice: {passive_ratio:.0%}"

# ✅ NEW - Check 5.11: Bilingual Support
has_english = Path('SKILL.md').exists()
has_japanese = Path('references/SKILL.ja.md').exists()

if has_english and has_japanese:
    bonus_points += 1  # +1 bonus point for bilingual support
elif not has_english and has_japanese:
    assert False, "Japanese-only skill - must have English SKILL.md"
# English-only is acceptable (no penalty)
```

> 📚 **完全な実装**: `references/validation-examples.md` を参照  
> 📚 **失敗例**: `references/anti-patterns.md` を参照

---

## パターン6: 品質レポート生成

### 概要

スコアと失敗項目、改善提案を含む詳細レポートを作成します。

### 基本例

**シンプルレポート**:

```markdown
# Quality Report: skill-name

**Overall**: 52/64 (81%) ✅ PASS
- Structure: 11/14 (79%) ✅
- Content: 19/23 (83%) ✅
- Code Quality: 13/16 (81%) ✅
- Language: 9/11 (82%) ✅
- Bonus Points: +1 (Japanese version)

**Critical Issues**:
- File length: 520 lines (warning: use references/ for >500)
- Missing Why explanations in Advanced patterns
```

---

## よくある落とし穴

### 1. 総合80%未満でも通してしまう

**問題**: カテゴリ80%を満たしても全体80%未満で公開される。

**解決策**: 「カテゴリ80%」と「全体80%」の両方を必須にする。

```python
# ✅ CORRECT - Strict validation
def is_passing(results: Dict[str, ValidationResult]) -> bool:
    # Check per-category threshold (80%)
    if not all(r.score >= 80 for r in results.values()):
        return False
    
    # Check overall threshold (80%, 51/64 points)
    total_passed = sum(r.passed for r in results.values())
    total_items = sum(r.total for r in results.values())
    overall_score = (total_passed / total_items) * 100
    
    return overall_score >= 80  # 51/64 = 79.7%, round to 80%
```

### 2. 文脈を無視したコード品質チェック

**問題**: チュートリアル用途でも本番エラーハンドリング不足として判定する。

**解決策**: スキル種別に応じて検証ルールを調整する。

```yaml
# In SKILL.md frontmatter
validation_profile: tutorial  # or: production, reference, quickstart

# Adjust checks based on profile
if profile == "tutorial":
    skip_checks = ["3.4.3"]  # Error handling optional for tutorials
```

### 3. 修正後の再検証をしない

**問題**: 修正で別の問題が発生しても再検証しない。

**解決策**: 変更後は必ずフル検証を再実行。

```bash
# ❌ WRONG - Fix and assume it's good
# Edit SKILL.md...
# Done!

# ✅ CORRECT - Fix and validate
# Edit SKILL.md...
python validate_skill.py --skill my-skill --full-check
```

---

## アンチパターン

### 自動化だけで人間レビューを省略する

**What**: 自動チェックのみでレビューを完結させる。

**Why It's Wrong**:
- 主観的品質（明確さ、実用性）は検知できない
- 例が実践的かを判断できない
- 微妙な不整合を見逃す

**Better Approach**: 自動チェックは基礎、最終は人間レビュー。

---

## クイックリファレンス

### 検証ワークフロー

```
1. Run structure check (14 items)
   ├─ PASS: Continue
   └─ FAIL: Fix structure issues, restart

2. Run content check (23 items)
   ├─ PASS: Continue
   └─ FAIL: Improve scenarios, patterns, Values integration

3. Run code quality check (16 items)
   ├─ PASS: Continue
   └─ FAIL: Fix code examples, add DI/error handling, shorten long examples

4. Run language check (11 items)
   ├─ PASS: Calculate overall score
   └─ FAIL: Rewrite for clarity, active voice, add Japanese version

5. Overall score ≥ 80% AND all categories ≥ 80%?
   ├─ YES: ✅ PUBLISH
   └─ NO: Review failures, iterate
```

---

### 合格基準サマリー

| カテゴリ | 項目数 | 合格基準 | 重み |
|----------|--------|----------|------|
| Structure | 14 | ≥ 11 (79%) | Critical |
| Content | 23 | ≥ 18 (78%) | High |
| Code Quality | 16 | ≥ 13 (81%) | High |
| Language | 11 | ≥ 9 (82%) | Medium |
| **Overall** | **64** | **≥ 51 (80%)** | **Required** |
| **Bonus** | **+2** | **Japanese + Values** | **Optional** |

---

## ベストプラクティスまとめ

1. **早期・高頻度で実行** - 完成後だけでなく執筆中に検証
2. **構造を最優先** - 構造エラーは他の検証を阻害
3. **自動化を活用** - .ps1/.shで繰り返し作業を簡略化
4. **重大失敗を優先** - 構造/内容 → 言語の順に修正
5. **90%+を目標** - 初回80%は許容、改訂で90%へ
6. **例外を記録** - 意図的にスキップする項目を明記
7. **最終レビューは人間** - 自動チェック + 人間レビュー
8. **変更後は再検証** - 修正で別の問題が出る前提
9. **改善を追跡** - スコアの推移を記録
10. **レポートを学習に活用** - 失敗傾向から改善
11. **references/を活用** - 500行超は詳細を移動
12. **Values統合** - Core Principlesに開発哲学を反映

---

## リソース

- **[references/anti-patterns.md](references/anti-patterns.md)** - 詳細な❌例と失敗パターン
- **[references/validation-examples.md](references/validation-examples.md)** - 検証ロジック実装例
- **[skill-writing-guide](../skill-writing-guide/SKILL.md)** - Skill執筆ガイド
- **[skills-revise-skill](../skills-revise-skill/SKILL.md)** - 修正ガイド
- **[Development Philosophy](../../.github/copilot-instructions.md)** - Valuesと規範

---

## 変更履歴

### Version 3.0.0 (2026-02-12)
- **チェックリスト拡張**: 56 → 64項目（+8）
- **行数最適化追加**: 500行推奨、550行許容
- **references/検証追加**: ディレクトリ構造の検証
- **日英対応追加**: 日本語版ボーナス
- **Values統合追加**: 開発哲学整合チェック
- **コード長制限追加**: 例は15行以内推奨
- **Progressive Disclosure追加**: >500行はreferences/へ
- **しきい値更新**: 全体85% → 80%（51/64）
- **新スクリプト**: PowerShell/Bashラッパー追加

### Version 2.0.0 (2026-02-12)
- **行数最適化**: 780行 → 335行（57%削減）
- **アンチパターン移動**: `references/anti-patterns.md`へ
- **検証ロジック簡略化**: 擬似コード化
- **56項目維持**: 既存基準を保持
- **相互参照追加**: anti-patterns/validation-examples

### Version 1.0.0 (2026-02-12)
- 初版リリース
- 56項目チェックリスト
- 4カテゴリスコアリング
- 自動検証例
- レポート生成パターン

<!-- 
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
