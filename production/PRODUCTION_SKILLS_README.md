# Production Skills: MVP/本番向け開発プラクティス

MVPと本番環境で品質と速度のバランスを保つためのSkillsをまとめたカテゴリです。

## 📋 概要

このカテゴリには、プロトタイプではなくMVP/本番フェーズで使う開発プラクティスを収録します。

## 🎯 用途

**プロジェクト固有のSkills**として、必要なものだけを`.github/skills/`にコピーして使用します。

## 📦 収録Skills

| Skill名 | 説明 | バージョン | 主な機能 |
|---------|------|------------|----------|
| [tdd-standard-practice](tdd-standard-practice/) | TDD標準プラクティス | 1.0.0 | テストリスト、Red-Green-Refactor、モック/スタブ、CI |

## 🔧 依存関係

- テストフレームワーク（pytest, NUnit, Jest等）
- CIでテストを実行できる環境

## 📖 各Skillの詳細

### 1. tdd-standard-practice

**MVP/本番でのTDDワークフロー標準化**

- テストリストの作成方法
- Red-Green-Refactorの基本サイクル
- モック/スタブの境界設計
- CI/CDでのガードレール設計

**使い方**:
```
@workspace /tdd-standard-practice MVP/本番のTDDを標準化したい
```
