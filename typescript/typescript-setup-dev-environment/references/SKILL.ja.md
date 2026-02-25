---
name: typescript-setup-dev-environment
description: Set up a reproducible TypeScript dev environment with Node.js, npm, ESLint, Prettier, and Jest. Use when starting a new TypeScript project or standardizing team tooling.
metadata:
  author: RyoMurakami1983
  tags: [typescript, nodejs, npm, eslint, prettier, jest, vscode]
  invocable: false
---

# TypeScript開発環境をセットアップする

Node.js・npm・ESLint・Prettier・Jest・VSCode保存時ガードを使って、再現可能なTypeScript開発環境を構築・運用するための単一ワークフローです。

## このスキルを使うとき

このスキルは次のときに使います:
- 新しいTypeScriptプロジェクトを立ち上げ、ツールチェーンを統一したいとき
- C#やPythonの経験はあるがTypeScriptは初めてのメンバーをオンボーディングするとき
- チームメンバー間で同じTypeScript実行環境を再現したいとき
- ESLint/Prettierの競合やVSCode保存時の挙動を解決したいとき
- JavaScriptプロジェクトをTypeScript strictモードへ移行するとき

---

## Related Skills

- **`typescript-tauri-setup`** — この環境の上にTauriデスクトップアプリ機能を追加するときに使用
- **`git-initial-setup`** — 最初のコミット前にmainブランチを保護するときに使用
- **`git-commit-practices`** — 環境変更を原子的にコミットするときに使用
- **`github-pr-workflow`** — 環境変更をPR経由で反映するときに使用

---

## Dependencies

- Node.js 20+ LTS（必須）
- npm 10+（Node.jsに同梱）
- VSCode + ESLint/Prettier拡張（推奨）

---

## Core Principles

1. **単一ランタイムエントリポイント** — `npx`やnpmスクリプト経由でツールを実行し、グローバルインストールの差異を防ぐ（基礎と型）
2. **最初からstrict** — TypeScript strictモードを初日から有効化。後から厳しくするより、最初から厳しい方が楽（基礎と型）
3. **コミット前の高速フィードバック** — lint, format, testを予測可能な順序で実行（成長の複利）
4. **再現可能な依存状態** — `package-lock.json`と`npm ci`で環境を追跡（温故知新）
5. **段階的な採用** — Node.js + TypeScript + ESLint + Jestから始め、フレームワークは必要になってから（余白の設計）

---

## C# / Python経験者向けのツール対応表

TypeScriptのツールチェーンは、C#やPythonと**同じ役割を持つツールの組み合わせ**です。

| 役割 | C# | Python | TypeScript |
|------|-----|--------|-----------|
| ランタイム | .NET Runtime | Python (uv管理) | **Node.js** |
| パッケージ管理 | NuGet (.csproj) | uv (pyproject.toml) | **npm (package.json)** |
| 言語/コンパイラ | C# (csc) | Python | **TypeScript (tsc)** |
| 静的解析 | StyleCop | ruff check | **ESLint** |
| フォーマッタ | dotnet format | ruff format | **Prettier** |
| テスト | xUnit | pytest | **Jest** |
| 型チェック | コンパイラが担当 | mypy | **tsc（コンパイラが担当）** |
| ロックファイル | packages.lock.json | uv.lock | **package-lock.json** |
| クリーンインストール | dotnet restore | uv sync | **npm ci** |

**重要な違い**: C#やPythonでは型チェックとコンパイルが分かれていることがありますが、TypeScriptでは`tsc`が**型チェックとトランスパイルの両方**を担います。

---

## Workflow: TypeScript開発環境の構築と運用

### Step 1: Node.jsのインストール

Node.js LTSランタイムをインストールします。Node.jsはJavaScript/TypeScriptの実行環境で、C#における.NET RuntimeやPythonにおけるPythonインタプリタに相当します。

```powershell
# Windows (winget)
winget install OpenJS.NodeJS.LTS

# 確認
node --version
npm --version
```

**なぜNode.js?**: TypeScriptは単体では動かず、Node.js上で動作します。.NETなしでC#が動かないのと同じ関係です。

新しい開発マシンをセットアップするときに使います。

> **Values**: 基礎と型 / 継続は力

### Step 2: プロジェクトの初期化

プロジェクトのメタデータを作成し、依存関係の追跡を開始します。

```powershell
# ディレクトリ作成と初期化
mkdir my-project
cd my-project
npm init -y

# TypeScriptを開発依存として追加
npm install --save-dev typescript
```

`package.json`はC#の`.csproj`やPythonの`pyproject.toml`に相当します。プロジェクトのメタデータと依存関係を定義します。

新しいプロジェクトをゼロから始めるときに使います。

> **Values**: 基礎と型 / 余白の設計

### Step 3: TypeScriptコンパイラの設定

`tsconfig.json`をstrictモードとES Modulesで設定します。TypeScriptコンパイラ（`tsc`）は型チェッカー（mypyのような）とトランスパイラの両方の役割を果たします。

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ES2020",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**ES Modulesの重要ルール**: 相対インポートには必ず`.js`拡張子を付けます。

```typescript
// ✅ 正しい — ブラウザとNode.js ES Modulesは明示的な拡張子が必要
import { MyClass } from './MyClass.js';

// ❌ 間違い — 実行時にERR_FILE_NOT_FOUNDで失敗
import { MyClass } from './MyClass';
```

**なぜ`.js`?**: TypeScriptは`.ts`を`.js`にコンパイルしますが、import文のパスは書き換えません。実行時（ブラウザまたはNode.js）は実際の`.js`ファイルを探すため、拡張子が必要です。

プロジェクトで初めてTypeScriptを設定するときに使います。

> **Values**: 基礎と型 / ニュートラル

### Step 4: ESLintとPrettierの設定

ESLintは静的解析ツール（C#のStyleCop、PythonのRuffに相当）。Prettierはフォーマッタ（`dotnet format`、`ruff format`に相当）。

```powershell
# ESLintとTypeScriptサポート
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin

# PrettierとESLint連携
npm install --save-dev prettier eslint-config-prettier eslint-plugin-prettier
```

`.eslintrc.js`を作成:

```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier'
  ],
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module'
  },
  env: {
    node: true,
    es2020: true
  },
  rules: {
    '@typescript-eslint/explicit-function-return-type': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }]
  }
};
```

`.prettierrc`を作成:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

**なぜ2つのツール?**: ESLintは「コードの正しさ」（未使用変数、型の不整合）、Prettierは「見た目の統一」（インデント、改行）を担当。責務を分けることで設定の衝突を防ぎます。

プロジェクトのコード品質基準を確立するときに使います。

> **Values**: 基礎と型 / 成長の複利

### Step 5: Jestのセットアップ

JestはテストフレームワークでC#のxUnit、Pythonのpytestに相当します。

```powershell
npm install --save-dev jest ts-jest @types/jest
```

`jest.config.js`を作成:

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  collectCoverageFrom: ['src/**/*.ts', '!src/**/*.d.ts'],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 }
  }
};
```

`package.json`にnpmスクリプトを追加:

```json
{
  "scripts": {
    "build": "tsc",
    "lint": "eslint src/ --ext .ts",
    "format": "prettier --write src/",
    "test": "jest",
    "test:coverage": "jest --coverage"
  }
}
```

プロジェクトにテスト基盤を追加するときに使います。

> **Values**: 成長の複利 / 継続は力

### Step 6: VSCodeの設定

保存時に自動フォーマットを実行し、チーム全体で統一された編集体験を提供します。

`.vscode/settings.json`を作成:

```json
{
  "[typescript]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": "explicit"
    }
  },
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

推奨拡張機能（`.vscode/extensions.json`）:

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

チームメンバー間でエディタの挙動を統一するときに使います。

> **Values**: ニュートラル / 継続は力

### Step 7: 再現性の検証

他のマシンやCIが同じ環境を再現できることを確認します。

```powershell
# ロックファイルからクリーンインストール（dotnet restore / uv syncに相当）
npm ci

# 品質チェックを順番に実行
npm run format
npm run lint
npm run build
npm run test
```

**`package-lock.json`を必ずコミット** — これは`uv.lock`や`packages.lock.json`に相当するロックファイルです。これがないと`npm ci`は同一バージョンの依存関係を保証できません。

チームメンバーのオンボーディングやCI構築時に使います。

> **Values**: 温故知新 / 基礎と型

---

## Best Practices

- CIや新規環境では`npm ci`を使う（`npm install`ではなく）。決定論的なインストールを保証
- 品質チェックは format → lint → build → test の順序で実行
- `package-lock.json`をバージョン管理に含める
- TypeScript `strict`モードを最初から有効にする
- ES Moduleのimportには必ず`.js`拡張子を含める
- npmスクリプトをビルド・テスト・リントの単一エントリポイントにする

---

## Common Pitfalls

1. **ES Moduleインポートで`.js`拡張子が抜ける**
修正: ソースファイルが`.ts`でも、相対インポートパスには`.js`を含める。

2. **ESLintとPrettierの競合**
修正: `eslint-config-prettier`でESLintのフォーマット系ルールを無効化する。

3. **`package-lock.json`をコミットし忘れる**
修正: `.gitignore`に`package-lock.json`を追加しない。再現可能なビルドの要。

4. **グローバルインストールに頼る**
修正: `npx`またはnpmスクリプトを使う。グローバルインストールはマシン間でバージョン差異を生む。

---

## Anti-Patterns

- TypeScriptやESLintをグローバルインストール（`npm install -g`）
- 型エラーを避けるために`strict`モードを無効化
- 適切な型定義の代わりに`any`型をデフォルトの逃げ道にする
- CIで`npm ci`ではなく`npm install`を使う
- `.editorconfig`なしでタブとスペースを混在させる

---

## Quick Reference

### セットアップ

```powershell
winget install OpenJS.NodeJS.LTS
npm init -y
npm install --save-dev typescript eslint prettier jest ts-jest
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install --save-dev eslint-config-prettier eslint-plugin-prettier @types/jest
```

### 日常チェック

```powershell
npm run format
npm run lint
npm run build
npm run test
```

### Decision Table

| 状況 | アクション | 理由 |
|------|----------|------|
| 新プロジェクト | `npm init -y && npm i -D typescript` | 依存関係の追跡開始 |
| コミット前 | `npm run format && npm run lint` | レビュー前に問題検出 |
| PR前 | `npm run test` | 振る舞いの検証 |
| クローン直後 | `npm ci` | ロックファイルから再現インストール |
| CIパイプライン | `npm ci && npm run build && npm test` | フル検証 |

---

## FAQ

**Q: Node.jsではなくDenoやBunを使うべき?**
A: Node.jsは最大のエコシステムと最も安定したツール群を持っています。まずここから始め、特定の課題がある場合に代替を検討してください。

**Q: なぜ最初から`strict: true`?**
A: 後からstrictを有効にすると、コードベース全体の型エラーを一度に修正する必要があります。最初から厳しい方が楽です。

**Q: npmの代わりにyarnやpnpmは使える?**
A: はい。ワークフローは同じで、コマンドを置き換えるだけです。本スキルではNode.jsに同梱されるnpmをデフォルトとしています。

**Q: なぜTypeScriptのインポートに`.js`拡張子?**
A: TypeScriptは`.ts`を`.js`にコンパイルしますが、import文のパスは書き換えません。ランタイムは実際の`.js`ファイルを探すため、拡張子が必要です。

---

## Resources

- [Node.js documentation](https://nodejs.org/docs/latest/api/)
- [TypeScript documentation](https://www.typescriptlang.org/docs/)
- [ESLint documentation](https://eslint.org/docs/latest/)
- [Prettier documentation](https://prettier.io/docs/en/)
- [Jest documentation](https://jestjs.io/docs/getting-started)

---

## Changelog

### Version 1.0.0 (2026-02-25)
- 初版: Node.js + TypeScript + ESLint + Prettier + Jestワークフロー
