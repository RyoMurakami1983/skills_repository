---
name: tdd-standard-practice
description: MVP/本番向けにTDDを標準化する。テストリストとRed-Green-Refactorで安全に進める。
author: RyoMurakami1983
tags: [tdd, testing, workflow, ci, quality]
invocable: false
version: 1.0.0
---

# TDD標準プラクティス（MVP/本番）

Minimum Viable Product (MVP) と本番環境で、速度と品質のバランスを保つためのTest-Driven Development (TDD)ワークフローを標準化します。

**テストリスト**: これから実装する振る舞いを1件ずつ列挙した短いリスト。  
**Red-Green-Refactor**: 失敗テスト -> 最小実装 -> 整理を繰り返す基本サイクル。  
**開発者テスト**: 実装者自身が自動テストで振る舞いを検証する考え方。

Progression: Simple -> Intermediate -> Advanced は段階的にフィードバックの精度を高めます。  
Reason: フィードバックが短いほど不安が減り、変更の安全性が上がります。

## このスキルを使うとき

以下の状況で活用してください：
- MVP/本番で回帰を避けたい機能を安全に実装したいとき
- コアロジック変更でユーザー影響を守りたいとき
- 大規模リファクタの安全性を短いテストで確保したいとき
- 生成AIコードを手元の自動テストで検証したいとき
- チームでTDDの手順とRed-Greenルールを揃えたいとき
- 不具合の流出を減らし、リリースを安定させたいとき

## 関連スキル

- **`skill-git-commit-practices`** - 小さな変更を安全にコミット
- **`skill-git-review-standards`** - レビューでテスト証跡を確認
- **`skill-issue-intake`** - テスト負債をIssue化

---

## 依存関係

- 単体テストフレームワーク（pytest, NUnit, Jest等）
- ローカルで素早く回るテスト実行環境
- Continuous Integration (CI)でテストを回すパイプライン

---

## コア原則

1. **テストリスト優先** - 実装前に振る舞いを明確化（基礎と型）
2. **一歩ずつ進む** - Red -> Green -> Refactorの順序厳守（継続は力）
3. **振る舞い中心** - 公開APIやユーザー視点を基準にする（ニュートラル）
4. **開発者テスト** - フィードバックを最短化（成長の複利）
5. **学びと整理** - テスト結果から設計を磨く（温故知新）

---

## パターン1: テストリストを作る

### 概要

振る舞いを短いリストにして、1件ずつ確実に進めます。

### 基本例

```text
# ✅ CORRECT - 1件ずつ選ぶ
テストリスト:
- 空メールは拒否
- 正しいメールは通す
次の1件: 空メールは拒否

# ❌ WRONG - 一度に複数を狙う
テストリスト:
- 空メールは拒否
- 正しいメールは通す
- 大文字小文字を正規化
次の1件: 全部まとめて
```

### 中級例

- リスクと影響度で優先度を付ける
- 完了にチェックを付ける

### 上級例

```markdown
## テストリスト（PR説明）
- [x] 空メールは拒否
- [ ] 正しいメールは通す
- [ ] 大文字小文字を正規化
```

### 使うとき

- 機能開発やバグ修正の開始時
- 要件がまだ曖昧なとき

**Why**: 先にリスト化すると、抜け漏れを防ぎ「次の1手」を迷わず決められます。  
**Values**: 基礎と型 / 成長の複利

---

## パターン2: Red-Green-Refactorの徹底

### 概要

最短サイクルで失敗 -> 成功 -> 整理を繰り返します。

### 基本例

```python
from decimal import Decimal

# Red
def test_price_with_tax():
    assert price_with_tax(Decimal("100.00")) == Decimal("110.00")
```

```python
from decimal import Decimal

# Green
def price_with_tax(amount: Decimal) -> Decimal:
    return (amount * Decimal("1.1")).quantize(Decimal("1.00"))
```

### 中級例

- テストが通ったら重複を削除
- 10分以内の短いサイクルを維持

### 上級例

- Greenごとにコミット
- リファクタ用のチェックリストを持つ

### 使うとき

- テストリストの各項目すべて

**Why**: 小さなサイクルは不安とバグの発生源を最小化します。  
**Values**: 継続は力 / 成長の複利

---

## パターン3: テストファーストは小さく

### 概要

1つの失敗テストで次の振る舞いを定義します。

### 基本例

```python
def test_empty_email_is_invalid():
    assert is_valid_email("") is False
```

### 中級例

- 1テスト1アサーションで意図を明確化
- 1テストで複数失敗を出さない

### 上級例

- 基本ケースが通ってからパラメータ化

### 使うとき

- 振る舞いがシンプルで明確なとき

**Why**: 1件だけ失敗させると、次に書くコードが自明になります。  
**Values**: 基礎と型 / 継続は力

---

## パターン4: 公開振る舞いを先にテスト

### 概要

内部実装ではなく、外から見える結果をテストします。

### 基本例

```python
result = invoice.total_with_tax()
assert result == 110
```

### 中級例

- 内部ヘルパーではなく公開APIをテスト
- テスト名にユーザー意図を書く

### 上級例

- サービス境界の契約テストを追加

### 使うとき

- 内部構造を整理するとき
- 他チームに公開するAPIを作るとき

**Why**: 振る舞いテストはリファクタに強く、長期的な資産になります。  
**Values**: ニュートラル / 成長の複利

---

## パターン5: 境界だけモック/スタブ

### 概要

外部依存を隔離し、ドメイン内部は実物で検証します。

### 基本例

```python
# ✅ CORRECT - 境界だけモック
gateway = FakePaymentGateway()
service = BillingService(gateway)

# ❌ WRONG - ドメイン内部をモック
pricing = MockPriceCalculator()
service = BillingServiceWithMock(pricing)
```

### 中級例

- DBやキューはインメモリのFakeを使う
- モック対象はネットワークや時間に限定

### 上級例

```csharp
// ✅ CORRECT - DIでテスト用差し替え
using Microsoft.Extensions.DependencyInjection;

var services = new ServiceCollection();
services.AddSingleton<IPaymentGateway, FakePaymentGateway>();
services.AddSingleton<BillingService>();
```

```csharp
// ❌ WRONG - テストで依存を直書き
var service = new BillingService(new PaymentGateway());
```

- ドメイン内部はモック禁止ルールを定める

### 使うとき

- テストが遅い、または不安定なとき

**Why**: 境界だけモックにすると、テストの信頼性と速度を両立できます。  
**Values**: 基礎と型 / ニュートラル

---

## パターン6: Greenのあとにリファクタ

### 概要

テストが通ってから整理し、必ず再実行します。

### 基本例

- 先に全テストを通す
- Green後に重複を削除

### 中級例

- 振る舞い変更を伴わない抽出に限定
- 30分以内の整理で止める

### 上級例

- 自動リファクタを活用し、各ステップで再実行

### 使うとき

- Greenが確認できた直後

**Why**: Green後の整理は安全に設計を改善できます。  
**Values**: 温故知新 / 継続は力

---

## パターン7: CIをガードレールにする

### 概要

赤いビルドを見える化し、マージを止めます。

### 基本例

```yaml
# .github/workflows/tests.yml
name: tests
on: [push, pull_request]
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
```

### 中級例

- テスト成功をマージ条件にする
- Redのままでは次へ進めない

### 上級例

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-q"
```

ファイル: appsettings.json

```json
{
  "Testing": {
    "FastFail": true
  }
}
```

- ユニットと統合を分離して段階実行
- mainのカバレッジ閾値を固定

### 使うとき

- 本番に出るリポジトリすべて

**Why**: CIは個人の良い習慣をチームの安全装置に変えます。  
**Values**: 成長の複利 / 継続は力

---

## パターン8: バグは回帰テストにする

### 概要

不具合を再現するテストを書いてから修正します。

### 基本例

```python
def test_discount_rounding_bug():
    assert apply_discount(100, 0.1) == 90
```

### 中級例

- 修正前にテストリストへ追加
- テスト名にIssue IDを入れる

### 上級例

```python
from pathlib import Path

def load_fixture(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Fixture missing: {path}") from exc
```

- リリースノートに「バグ学習メモ」を残す

### 使うとき

- 本番不具合の修正時

**Why**: 回帰テストが再発防止の最短ルートになります。  
**Values**: 温故知新 / 成長の複利

---

## ベストプラクティス

- テストは高速に保ち、遅い検証は統合側へ移す
- 失敗テストは常に1件だけ
- テスト名に振る舞いを明記
- リファクタ前に必ず全体を通す
- Greenのあとにコミット
- テストリストを計画時に見直す

---

## よくある落とし穴

- 失敗テストを複数書いてしまう  
  Fix: 1件ずつ終わらせる。
- Green前に整理してしまう  
  Fix: 必ずGreenのあとに整理する。
- モックが多すぎて意味が薄い  
  Fix: 境界だけモックに限定する。

---

## アンチパターン

- 実装後にテストを書く
- 内部ロジックまで過剰にモックする
- テストリストを省略して実装に入る
- 1テストで複数の振る舞いを混ぜる

---

## FAQ

**Q: プロトタイプにもTDDを使うべき？**  
A: プロトタイプは軽量で十分です。本スキルはMVP/本番向けの標準化を想定しています。

**Q: テストリストはどれくらい書く？**  
A: 短く保ち、順番を頻繁に入れ替えます。次の1手が明確なら十分です。

**Q: レガシーコードでもTDDできる？**  
A: 可能です。まずは現状を固定する特性テストから始めます。

---

## クイックリファレンス

| 手順 | アクション | 出力 |
|------|------------|------|
| 1 | テストリスト作成 | 次の1件が決まる |
| 2 | 失敗テストを書く | Red |
| 3 | 最小実装 | Green |
| 4 | リファクタ | 整理されたコード |
| 5 | コミットとプッシュ | CIが検証 |

```text
テストリスト -> Red -> Green -> Refactor -> Commit
```

---

## Resources

- Kent Beck, "Test-Driven Development by Example"
- T-Wada: テストリストとRed-Green-Refactorのワークフロー

---

## Changelog

### Version 1.0.0 (2026-02-13)

- 初版リリース
- テストリスト、Red-Green-Refactor、CI、モック運用を整理
