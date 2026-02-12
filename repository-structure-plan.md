# Git管理前提のSkillsリポジトリ構造計画

**作成日**: 2026-02-12  
**ステータス**: 計画中（実装前）

---

## 📋 方針決定事項

### 1. README命名規則
- **ルート**: `README.md`（全体概要、インストール手順）
- **各カテゴリ**: `CATEGORY_SKILLS_README.md`
  - 例: `PYTHONS_SKILLS_README.md`, `DOTNETS_SKILLS_README.md`
  - 理由: 通常の`README.md`と区別、カテゴリが明確

### 2. カテゴリREADME内容
- ✅ **Skills一覧表**（名前、説明、バージョン）
- ✅ **依存関係**（Python 3.8+, .NET 8等）
- ❌ インストール方法は含めない（ルートREADMEに集約）

### 3. 配置方針

#### グローバルSkills（全プロジェクト共通）
```
~/.copilot/skills/
└── (skills/カテゴリからコピー)
    ├── skill-writing-guide/
    ├── skill-quality-validation/
    ├── skill-template-generator/
    └── skill-revision-guide/
```

#### プロジェクトSkills（プロジェクト固有）
```
.github/skills/
└── (pythons/, dotnets/, typescripts/等からコピー)
    ├── skill-fastapi-patterns/
    ├── skill-wpf-databinding/
    └── ...
```

---

## 🗂️ リポジトリ構造（最終形）

```
~/dev/skills-repository/
├── README.md (日本語)
│   ├─ 全体概要
│   ├─ インストール手順
│   │  ├─ グローバルインストール（skills/カテゴリ用）
│   │  └─ プロジェクトインストール（言語別カテゴリ用）
│   ├─ カテゴリ一覧
│   └─ 貢献方法
│
├── skills/ (Meta-Skills: グローバル用)
│   ├── SKILLS_README.md (日本語)
│   │   ├─ 4 Meta-Skills一覧
│   │   ├─ 依存関係（Python 3.8+）
│   │   └─ 用途説明
│   ├── skill-writing-guide/
│   ├── skill-quality-validation/
│   ├── skill-template-generator/
│   └── skill-revision-guide/
│
├── pythons/ (Python特化Skills: プロジェクト用)
│   ├── PYTHONS_SKILLS_README.md (日本語)
│   │   ├─ Python Skills一覧
│   │   └─ 依存関係（python>=3.8, pandas, numpy等）
│   ├── skill-pandas-analysis/
│   ├── skill-fastapi-patterns/
│   └── skill-pytest-patterns/
│
├── dotnets/ (.NET特化Skills: プロジェクト用)
│   ├── DOTNETS_SKILLS_README.md (日本語)
│   │   ├─ .NET Skills一覧
│   │   └─ 依存関係（.NET 8+, C# 12+）
│   ├── skill-wpf-databinding/
│   ├── skill-ef-core-patterns/
│   └── skill-aspnetcore-api/
│
├── typescripts/ (TypeScript特化Skills: プロジェクト用)
│   ├── TYPESCRIPTS_SKILLS_README.md (日本語)
│   │   ├─ TypeScript Skills一覧
│   │   └─ 依存関係（Node.js 18+, TypeScript 5+）
│   ├── skill-react-patterns/
│   ├── skill-nextjs-patterns/
│   └── skill-express-api/
│
└── (将来的な拡張カテゴリ)
    ├── data-engineering/ (データエンジニアリング特化)
    ├── finance/ (金融業務特化)
    ├── healthcare/ (医療業務特化)
    └── ...
```

**注**: `businesses/` は抽象度が高すぎるため、具体的なドメインごとに分割
  - 例: `finance/`, `healthcare/`, `ecommerce/`, `data-engineering/`

---

## 📝 ルートREADME.md構成（日本語）

```markdown
# GitHub Copilot Skills Collection

高品質なGitHub Copilot Agent Skillsのコレクション

## 📋 概要

このリポジトリには以下が含まれます：
- **Meta-Skills**: Skill作成支援システム（グローバル用）
- **言語別Skills**: Python, .NET, TypeScript等の専門知識（プロジェクト用）

## 🗂️ カテゴリ

| カテゴリ | 説明 | 配置先 | 詳細 |
|---------|------|--------|------|
| `skills/` | Skill作成支援（Meta-Skills） | グローバル | [SKILLS_README.md](skills/SKILLS_README.md) |
| `pythons/` | Python開発パターン | プロジェクト | [PYTHONS_SKILLS_README.md](pythons/PYTHONS_SKILLS_README.md) |
| `dotnets/` | .NET/C#開発パターン | プロジェクト | [DOTNETS_SKILLS_README.md](dotnets/DOTNETS_SKILLS_README.md) |
| `typescripts/` | TypeScript/Node.js開発パターン | プロジェクト | [TYPESCRIPTS_SKILLS_README.md](typescripts/TYPESCRIPTS_SKILLS_README.md) |

## 🚀 インストール

### グローバルインストール（全プロジェクト共通）

**Meta-Skills（Skill作成支援）をグローバルに配置**:
```bash
# Clone repository
git clone https://github.com/your-org/skills-repository.git /tmp/skills-repository

# Copy to global skills directory
mkdir -p ~/.copilot/skills
cp -r /tmp/skills-repository/skills/* ~/.copilot/skills/

# Verify
ls ~/.copilot/skills/
# skill-writing-guide/
# skill-quality-validation/
# skill-template-generator/
# skill-revision-guide/
```

### プロジェクトインストール（プロジェクト固有）

**例: Python Skillsをプロジェクトに追加**:
```bash
# Clone repository
git clone https://github.com/your-org/skills-repository.git /tmp/skills-repository

# Copy Python skills to project
mkdir -p .github/skills
cp -r /tmp/skills-repository/pythons/* .github/skills/

# Verify
ls .github/skills/
# skill-pandas-analysis/
# skill-fastapi-patterns/
# ...
```

**例: .NET Skillsをプロジェクトに追加**:
```bash
cp -r /tmp/skills-repository/dotnets/* .github/skills/
```

**複数カテゴリを同時に追加**:
```bash
# Python + TypeScript
cp -r /tmp/skills-repository/pythons/* .github/skills/
cp -r /tmp/skills-repository/typescripts/* .github/skills/
```

## 🛠️ 使い方

### Skill作成
```bash
# Meta-Skillsを使用（グローバルにインストール済みの前提）
python ~/.copilot/skills/skill-template-generator/scripts/generate_template.py
```

### 品質検証
```bash
python ~/.copilot/skills/skill-quality-validation/scripts/validate_skill.py path/to/SKILL.md
```

## 🤝 貢献

新しいSkillの追加方法：
1. 適切なカテゴリを選択（pythons/, dotnets/等）
2. `skill-template-generator`でテンプレート生成
3. `skill-quality-validation`で検証
4. Pull Request作成

## 📄 ライセンス

[MIT License](LICENSE)
```

---

## 📝 各カテゴリREADME例

### skills/SKILLS_README.md（日本語）

```markdown
# Meta-Skills: Skill作成支援システム

GitHub Copilot Agent Skillsを作成・管理するための支援システム

## 📋 収録Skills

| Skill名 | 説明 | バージョン |
|---------|------|-----------|
| skill-writing-guide | Skill執筆ガイド | 1.0.0 |
| skill-quality-validation | 55項目品質検証 | 2.0.0 |
| skill-template-generator | テンプレート自動生成 | 1.0.0 |
| skill-revision-guide | 修正・バージョン管理 | 1.0.0 |

## 🔧 依存関係

- Python 3.8+ (スクリプト実行用、オプション)
- 標準ライブラリのみ（外部パッケージ不要）

## 🎯 用途

**グローバルインストール推奨**（全プロジェクトで使用）

これらのMeta-Skillsは新しいSkillを作成・管理するためのツールです。
プロジェクト固有ではなく、開発環境全体で使用することを想定しています。

## 📚 詳細

各Skillの詳細は個別の`SKILL.md`と`references/SKILL.ja.md`を参照してください。
```

### pythons/PYTHONS_SKILLS_README.md（日本語）

```markdown
# Python Skills

Python開発に特化したSkillsコレクション

## 📋 収録Skills

| Skill名 | 説明 | 依存ライブラリ | バージョン |
|---------|------|---------------|-----------|
| skill-pandas-analysis | Pandasデータ分析パターン | pandas>=2.0, numpy | 1.0.0 |
| skill-fastapi-patterns | FastAPI APIパターン | fastapi, uvicorn | 1.0.0 |
| skill-pytest-patterns | Pytestテストパターン | pytest>=7.0 | 1.0.0 |

## 🔧 共通依存関係

- Python 3.8+ 必須
- pip 20.0+ 推奨

## 🎯 用途

**プロジェクトレベルインストール推奨**

Pythonプロジェクトで使用する専門知識を含みます。
プロジェクトごとに必要なSkillsを`.github/skills/`にコピーしてください。
```

---

## ✅ 今回実施すること（別セッションまで）

1. **現状の`~/.copilot/skills/README.md`を日本語化**
   - 4 Meta-Skillsの概要のみ
   - インストール手順は含めない（将来的にルートREADMEに記載）

2. **計画ドキュメント作成**（本ファイル）
   - Git管理前提の構造設計
   - 命名規則、配置方針の明文化

## 📌 次セッションで実施すること

1. `~/dev/`に現状をコピー
2. リポジトリ構造に再編成
3. ルートREADME.md作成（日本語、インストール手順含む）
4. 各カテゴリREADME作成（`CATEGORY_SKILLS_README.md`形式）
5. Git初期化、コミット

---

## ❓ 確認事項

1. ✅ カテゴリREADME命名: `PYTHONS_SKILLS_README.md`形式で良いか
2. ✅ 内容: Skills一覧 + 依存関係のみ（インストール手順はルートREADMEに集約）
3. ✅ skills/ = グローバル、他 = プロジェクトレベル
4. ❓ 業務特化カテゴリ名は将来検討（`businesses/`は抽象的すぎる）
5. ❓ スペル確認: "Businesses" が正しいが、この名前自体を使わない方向？

**次のアクション**: 現状のREADME.md日本語化（概要のみ）

---

**作成者**: RyoMurakami1983
