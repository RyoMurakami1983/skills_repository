---
name: typescript-setup-dev-environment
description: Set up a reproducible TypeScript dev environment with Node.js, npm, ESLint, Prettier, and Jest. Use when starting a new TypeScript project or standardizing team tooling.
metadata:
  author: RyoMurakami1983
  tags: [typescript, nodejs, npm, eslint, prettier, jest, vscode]
  invocable: false
---

# Set Up a TypeScript Dev Environment

Single-workflow guide for setting up and operating a reproducible TypeScript development environment with Node.js, npm, ESLint, Prettier, Jest, and VSCode save-time guardrails.

## When to Use This Skill

Use this skill when:
- Starting a new TypeScript project and standardizing the toolchain
- Onboarding a team member who knows C# or Python but not TypeScript
- Reproducing the same TypeScript environment across machines
- Troubleshooting ESLint/Prettier conflicts or VSCode save-time behavior
- Migrating a JavaScript project to TypeScript strict mode

---

## Related Skills

- **`typescript-tauri-setup`** — Add Tauri desktop app capabilities on top of this environment
- **`git-initial-setup`** — Protect main branch before first commit
- **`git-commit-practices`** — Commit environment changes as atomic units
- **`github-pr-workflow`** — Ship setup changes through PR workflow

---

## Dependencies

- Node.js 20+ LTS (required)
- npm 10+ (bundled with Node.js)
- VSCode + ESLint/Prettier extensions (recommended)

---

## Core Principles

1. **Single runtime entrypoint** — Use `npx` or npm scripts for all tooling to avoid global install drift (基礎と型)
2. **Strict by default** — Enable TypeScript strict mode from day one; relaxing later is easy, tightening is painful (基礎と型)
3. **Fast feedback before commit** — Run lint, format, and test in a predictable sequence (成長の複利)
4. **Reproducible dependency state** — Track environment via `package-lock.json` and `npm ci` (温故知新)
5. **Incremental adoption** — Start with Node.js + TypeScript + ESLint + Jest; add frameworks only when needed (余白の設計)

---

## Tool Mapping for C# and Python Developers

The TypeScript toolchain is a **combination of tools that serve the same roles** as C# and Python tooling.

| Role | C# | Python | TypeScript |
|------|-----|--------|-----------|
| Runtime | .NET Runtime | Python (uv-managed) | **Node.js** |
| Package manager | NuGet (.csproj) | uv (pyproject.toml) | **npm (package.json)** |
| Language/compiler | C# (csc) | Python | **TypeScript (tsc)** |
| Static analyzer | StyleCop | ruff check | **ESLint** |
| Formatter | dotnet format | ruff format | **Prettier** |
| Test framework | xUnit | pytest | **Jest** |
| Type checker | Compiler handles it | mypy | **tsc (compiler handles it)** |
| Lock file | packages.lock.json | uv.lock | **package-lock.json** |
| Clean install | dotnet restore | uv sync | **npm ci** |

**Key difference**: In C# and Python, type checking and compilation may be separate concerns. In TypeScript, `tsc` handles **both type checking and transpilation**.

---

## Workflow: Set Up and Operate TypeScript Dev Environment

### Step 1: Install Node.js

Install the Node.js LTS runtime. Node.js is the JavaScript/TypeScript runtime — equivalent to .NET Runtime for C# or the Python interpreter.

```powershell
# Windows (winget)
winget install OpenJS.NodeJS.LTS

# Verify installation
node --version
npm --version
```

Use when setting up a new development machine.

> **Values**: 基礎と型 / 継続は力

### Step 2: Initialize Project

Create project metadata and establish the dependency tracking file.

```powershell
# Create project directory and initialize
mkdir my-project
cd my-project
npm init -y

# Install TypeScript as dev dependency
npm install --save-dev typescript
```

`package.json` is equivalent to `.csproj` in C# or `pyproject.toml` in Python — it defines project metadata and dependencies.

Use when starting a new project from scratch.

> **Values**: 基礎と型 / 余白の設計

### Step 3: Configure TypeScript Compiler

Set up `tsconfig.json` with strict mode and ES Modules. The TypeScript compiler (`tsc`) is both a type checker (like `mypy`) and a transpiler.

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

**ES Modules critical rule**: All relative imports must include `.js` extension.

```typescript
// ✅ Correct — browser and Node.js ES Modules require explicit extension
import { MyClass } from './MyClass.js';

// ❌ Wrong — will fail at runtime with ERR_FILE_NOT_FOUND
import { MyClass } from './MyClass';
```

Use when configuring TypeScript for the first time in a project.

> **Values**: 基礎と型 / ニュートラル

### Step 4: Set Up ESLint and Prettier

ESLint is the static analyzer (equivalent to StyleCop/Ruff). Prettier is the formatter (equivalent to `dotnet format`/`ruff format`).

```powershell
# Install ESLint with TypeScript support
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin

# Install Prettier and ESLint-Prettier integration
npm install --save-dev prettier eslint-config-prettier eslint-plugin-prettier
```

Create `.eslintrc.js`:

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

Create `.prettierrc`:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

Use when establishing code quality standards for a TypeScript project.

> **Values**: 基礎と型 / 成長の複利

### Step 5: Set Up Jest for Testing

Jest is the test framework — equivalent to xUnit for C# or pytest for Python.

```powershell
npm install --save-dev jest ts-jest @types/jest
```

Create `jest.config.js`:

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

Add npm scripts to `package.json`:

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

Use when adding test infrastructure to a TypeScript project.

> **Values**: 成長の複利 / 継続は力

### Step 6: Configure VSCode

Set up editor-level guardrails for consistent formatting on save.

Create `.vscode/settings.json`:

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

Recommended extensions (`.vscode/extensions.json`):

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

Use when standardizing editor behavior across team members.

> **Values**: ニュートラル / 継続は力

### Step 7: Verify Reproducibility

Confirm that another machine or CI can recreate the same environment.

```powershell
# Clean install from lock file (equivalent to dotnet restore / uv sync)
npm ci

# Run full quality check sequence
npm run format
npm run lint
npm run build
npm run test
```

**Commit `package-lock.json`** — this is the lock file equivalent to `uv.lock` or `packages.lock.json`. Without it, `npm ci` cannot guarantee identical dependency versions.

Use when onboarding collaborators or validating CI parity.

> **Values**: 温故知新 / 基礎と型

---

## Best Practices

- Use `npm ci` (not `npm install`) in CI and fresh environments for deterministic installs
- Run quality checks in order: format → lint → build → test
- Keep `package-lock.json` in version control
- Enable TypeScript `strict` mode from the start
- Include `.js` extensions in all ES Module imports
- Use npm scripts as the single entry point for all build/test/lint commands

---

## Common Pitfalls

1. **Missing `.js` extension in ES Module imports**
Fix: Always include `.js` in relative import paths, even though source files are `.ts`.

2. **ESLint and Prettier conflicts**
Fix: Use `eslint-config-prettier` to disable ESLint formatting rules that conflict with Prettier.

3. **Forgetting to commit `package-lock.json`**
Fix: Never add `package-lock.json` to `.gitignore`. It ensures reproducible builds.

4. **Using global installs instead of project-local**
Fix: Use `npx` or npm scripts. Global installs cause version drift across machines.

---

## Anti-Patterns

- Installing TypeScript or ESLint globally (`npm install -g`)
- Disabling `strict` mode to avoid fixing type errors
- Using `any` type as a default escape hatch instead of proper typing
- Running `npm install` in CI instead of `npm ci`
- Mixing tabs and spaces without `.editorconfig`

---

## Quick Reference

### Setup

```powershell
winget install OpenJS.NodeJS.LTS
npm init -y
npm install --save-dev typescript eslint prettier jest ts-jest
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install --save-dev eslint-config-prettier eslint-plugin-prettier @types/jest
```

### Daily checks

```powershell
npm run format
npm run lint
npm run build
npm run test
```

### Decision Table

| Situation | Action | Why |
|-----------|--------|-----|
| New project | `npm init -y && npm i -D typescript` | Establish dependency tracking |
| Before commit | `npm run format && npm run lint` | Catch issues before review |
| Before PR | `npm run test` | Validate behavior |
| Fresh clone | `npm ci` | Reproducible install from lock file |
| CI pipeline | `npm ci && npm run build && npm test` | Full validation |

---

## FAQ

**Q: Why Node.js and not Deno or Bun?**
A: Node.js has the largest ecosystem and most stable tooling. Start here; evaluate alternatives when you have specific needs they address.

**Q: Why `strict: true` from the start?**
A: Enabling strict mode later requires fixing accumulated type errors across the entire codebase. Starting strict is easier than migrating to strict.

**Q: Can I use yarn or pnpm instead of npm?**
A: Yes. The workflow is the same; replace `npm` commands accordingly. This skill uses npm as the default because it ships with Node.js.

**Q: Why `.js` extension in TypeScript imports?**
A: TypeScript compiles `.ts` to `.js` but does not rewrite import paths. The runtime (browser or Node.js) needs the actual `.js` file extension to resolve modules.

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
- Initial release: Node.js + TypeScript + ESLint + Prettier + Jest workflow
