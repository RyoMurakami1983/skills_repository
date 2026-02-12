---
name: skill-git-japanese-practices
description: Git workflow guide with Japanese commit messages and GitHub Flow. Provides patterns for Conventional Commits, atomic commits, and effective code reviews.
author: RyoMurakami1983
tags: [git, github-flow, conventional-commits, japanese, team-practices]
invocable: false
version: 1.0.0
---

# Git Japanese Practices

A Git workflow guide embodying **Fundamentals & Patterns / Compounding Growth**. Maximize team productivity and learning assets with Japanese commit messages and GitHub Flow.

## Related Skills

- **`skill-writing-guide`** - Best practices for skill writing
- **`skill-quality-validation`** - 55-item quality validation
- **`skill-template-generator`** - Automatic template generation
- **`skill-revision-guide`** - Revision and version management

## When to Use This Skill

Use this skill when:

- Introducing Conventional Commits format to your team
- Writing clear commit messages in Japanese
- Establishing GitHub Flow branch strategy
- Learning atomic commit practices
- Building code review culture
- Achieving consistent Git workflow across teams
- Leveraging commit history as a "learning asset"

**When NOT to use**:
- Personal projects where history management is unnecessary
- Established Git workflows with no room for change

---

## Core Principles

This skill is designed based on Ryo Murakami's development philosophy:

### 1. Fundamentals & Patterns: Unlocking Maximum Potential with Minimal Form

Adopting **Conventional Commits** as a minimal form enables the entire team to create unified commit history. Patterns enable speed; fundamentals enable infinite applications.

### 2. Compounding Growth: Commit History as Learning Assets

Clear commit messages are gifts to your future self and team members. Commit history tells "why changes were made," accelerating team-wide growth.

### 3. Tacit to Explicit: Patterns Anyone Can Use

Converting personal experience (tacit knowledge) into patterns like **Conventional Commits** and **GitHub Flow** (explicit knowledge) enables reproduction by anyone and autonomous team growth.

### 4. Consistency is Power: Accumulating Small Commits

Rather than massive commits, accumulating **atomic commits** (focused on single changes) improves long-term maintainability and quality.

### 5. Learning from the Past: Culture of Learning from Commit History

Good commit history serves as project historiography. Utilize `git log` and `git blame` to connect past wisdom with new technologies.

---

## Pattern 1: Conventional Commits Format

### Overview

Conventional Commits is a convention that gives commit messages consistent structure. This "pattern" dramatically improves change understanding, automation, and team collaboration.

### Basic Format

```
<type>: <subject>

<body>

<footer>
```

### Type List

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature | `feat: ユーザー認証機能を追加` (Add user authentication) |
| `fix` | Bug fix | `fix: ログイン時のセッションタイムアウト問題を修正` (Fix session timeout on login) |
| `docs` | Documentation update | `docs: READMEにインストール手順を追加` (Add installation steps to README) |
| `test` | Add/modify tests | `test: ユーザー登録のE2Eテストを追加` (Add E2E test for user registration) |
| `refactor` | Code improvement (not feature/fix) | `refactor: ユーザーサービスを関数型に書き換え` (Refactor user service to functional style) |
| `chore` | Build process/dependency updates | `chore: Python 3.12にアップグレード` (Upgrade to Python 3.12) |

### Basic Example: Simple Commit

```bash
git commit -m "feat: パスワードリセット機能を追加"
# (Add password reset feature)
```

**Why this format?**
- Instantly recognizable as "new feature"
- Quick understanding of change types via `git log --oneline`
- Enables automation tools (CHANGELOG generation, etc.)

### Intermediate Example: Commit with Body

```bash
git commit -m "fix: CSVインポート時の文字化け問題を修正
# (Fix character encoding issue in CSV import)

- Shift_JISエンコーディングを明示的に指定
  (Explicitly specify Shift_JIS encoding)
- BOM付きUTF-8にも対応
  (Support UTF-8 with BOM)
- エラーハンドリングを追加
  (Add error handling)

Why: ユーザーから文字化け報告が3件あり、緊急対応が必要だったため
(Three user reports of garbled text required urgent response)"
```

**Key Points**:
- **List specific changes in body**
- **Specify Why** to convey context to future self and team
- **Articulating tacit knowledge**: Clear reasons instead of "just because"

### Advanced Example: Scope and Breaking Change

```bash
git commit -m "feat(auth)!: JWT認証をOAuth2.0に移行
# (Migrate from JWT to OAuth2.0)

- JWTトークン発行ロジックを削除
  (Remove JWT token issuance logic)
- OAuth2.0認可コードフローを実装
  (Implement OAuth2.0 authorization code flow)
- 既存のAPIエンドポイント /api/auth/* を変更
  (Modify existing API endpoints /api/auth/*)

BREAKING CHANGE: /api/auth/login エンドポイントが /api/oauth/authorize に変更されました。
クライアント側の変更が必要です。
(BREAKING CHANGE: /api/auth/login endpoint changed to /api/oauth/authorize. Client-side changes required.)

Why: セキュリティ強化とサードパーティ認証対応のため
(For security enhancement and third-party authentication support)"
```

**Key Points**:
- **Scope** (`auth`) clarifies change range
- **`!` mark** warns of Breaking Change
- **BREAKING CHANGE** section details impact

### When to Use Scope?

| Project Scale | Scope Recommendation | Reason |
|--------------|---------------------|--------|
| Small (1-2 people) | Low | High overhead |
| Medium (3-10 people) | Medium | Effective with clear modules |
| Large (10+ people) | High | Change range identification critical |

**Examples**: `feat(api):`, `fix(ui):`, `test(database):`

### Relationship with Atomic Commits

Conventional Commits shows true value when combined with **atomic commits** (discussed later):

```bash
# Bad: Multiple changes in one commit
git commit -m "feat: 認証機能追加とUI改善とテスト追加"
# (Add auth feature, UI improvements, and tests)

# Good: Split changes
git commit -m "feat: JWT認証機能を追加" # (Add JWT auth)
git commit -m "refactor: ログインUIのレイアウトを改善" # (Improve login UI layout)
git commit -m "test: 認証フローのE2Eテストを追加" # (Add E2E test for auth flow)
```

---

## Pattern 2: GitHub Flow in Practice

### Overview

GitHub Flow is a simple yet powerful branch strategy. Built on three pillars: **main branch always deployable**, **feature additions on branches**, **review via Pull Requests**.

### Basic Flow

```
1. Create new branch from main
2. Accumulate commits
3. Create Pull Request
4. Code review
5. Merge to main
6. Deploy immediately (or deployable state)
```

### Branch Naming Convention

Prefixes leveraging Conventional Commits types:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New feature development | `feature/user-authentication` |
| `fix/` | Bug fixes | `fix/csv-encoding-issue` |
| `refactor/` | Code improvements | `refactor/extract-user-service` |
| `docs/` | Documentation updates | `docs/update-api-reference` |
| `test/` | Test additions | `test/add-e2e-login-test` |
| `chore/` | Environment/dependency updates | `chore/upgrade-python-312` |

### Basic Example: Feature Addition Flow

```bash
# 1. Get latest from main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/password-reset

# 3. Develop and commit (atomically)
git add src/auth/password_reset.py
git commit -m "feat: パスワードリセット機能の基本実装"
# (Basic implementation of password reset)

git add src/api/routes/auth.py
git commit -m "feat: パスワードリセットAPIエンドポイントを追加"
# (Add password reset API endpoint)

git add tests/test_password_reset.py
git commit -m "test: パスワードリセット機能のテストを追加"
# (Add tests for password reset feature)

# 4. Push to remote
git push origin feature/password-reset

# 5. Create Pull Request on GitHub
```

### Pull Request Best Practices

#### Title

Use Conventional Commits format:

```
feat: パスワードリセット機能を追加
(Add password reset feature)
```

#### Description Template

```markdown
## Changes

- Implement password reset feature
- Email-based confirmation code generation
- Token expiration management (24 hours)

## Why This Change is Needed

Many users requested password recovery functionality.
Reduces support workload and improves user experience.

## Impact Scope

- New API endpoint: `POST /api/auth/reset-password`
- New database table: `password_reset_tokens`
- Environment variables added: `EMAIL_SMTP_SERVER`, `EMAIL_FROM`

## Testing

- [ ] Unit tests (pytest)
- [ ] E2E tests
- [ ] Manual testing (email sending confirmation)

## Screenshots

(Add if UI changes are involved)

## Checklist

- [ ] Ready for code review
- [ ] Documentation updated
- [ ] Tests passing
```

### Code Review Mindset

#### Reviewer Side

✅ **Constructive Feedback**:
```markdown
# Good example
"Excellent error handling!
One suggestion: adding retry logic for timeouts
would make this even more robust."

# Bad example
"No error handling. Fix it."
```

✅ **Focus on Code** (not personal attacks):
```markdown
# Good example
"This function is 70 lines and getting complex.
Splitting into smaller functions would improve testability."

# Bad example
"Your code is always too long."
```

#### Author Side

✅ **Welcome Feedback as Learning Opportunity**:
```markdown
# Reply to review comment example
"Thank you for the suggestion!
Added retry logic with exponential backoff.
This pattern seems useful in other places too."
```

✅ **Clearly Explain Reasons and Impact**:
Always include "Why" in PR descriptions and commit messages.

### Merge Strategies

| Strategy | Use Case | Benefits | Drawbacks |
|----------|----------|----------|-----------|
| **Squash and merge** | Consolidate feature branch commits | Clean main history | Loses detailed commit history |
| **Merge commit** | Preserve all commits | Complete history preservation | Main history becomes complex |
| **Rebase and merge** | Maintain linear history | Clean and linear | Conflict resolution can be difficult |

**Recommendations**:
- **Small to medium projects**: Squash and merge (simple history)
- **Large projects**: Follow team policy (usually Merge commit)

---

## Pattern 3: Effective Japanese Commit Messages

### Overview

Japanese commit messages have the powerful advantage that all team members can understand in their native language. However, without being "clear and descriptive," history loses value.

### Basic Template

```
<type>: <Concise description without subject>

- Change detail 1
- Change detail 2
- Change detail 3

Why: <Why this change was necessary>
```

### Good vs Bad Examples

| Bad Example | Good Example | Reason |
|-------------|--------------|--------|
| `fix: バグ修正` (Bug fix) | `fix: CSVインポート時のShift_JISエンコーディングエラーを修正` | Specifies concrete problem |
| `feat: 機能追加` (Add feature) | `feat: ユーザープロフィール編集機能を追加` | Clarifies what feature |
| `update` | `refactor: ユーザー認証ロジックを関数型に書き換え` | Type and specificity |
| `fix: いろいろ修正` (Fix various) | Split into 3 independent commits | Atomic commits |

### Subject Handling

Japanese allows omitting subjects, but **verbs must be clear**:

```bash
# Good (concise)
git commit -m "feat: ログイン機能を追加"
# (Add login feature)

# Verbose (subject unnecessary)
git commit -m "feat: システムにログイン機能を追加する"
# (Add login feature to system)

# Ambiguous (no verb)
git commit -m "feat: ログイン機能"
# (Login feature)
```

### Importance of Explaining Why

From **Fundamentals & Patterns / Compounding Growth** perspective, "why" is the most valuable learning asset:

```bash
# Bad: No Why
git commit -m "fix: タイムアウトを30秒に変更"
# (Change timeout to 30 seconds)

# Good: Specify Why
git commit -m "fix: API呼び出しタイムアウトを10秒→30秒に変更
# (Change API call timeout from 10s to 30s)

Why: 大量データ処理時に10秒では不足し、タイムアウトエラーが頻発していたため。
本番環境のログ分析により30秒が適切と判断。
(10 seconds insufficient for large data processing, causing frequent timeout errors.
Production log analysis determined 30 seconds appropriate.)"
```

Six months later, anyone viewing this change (including your future self) immediately understands "why 30 seconds?"

### Emoji Usage (Optional)

Depending on team culture, emojis can visualize types:

```bash
✨ feat: New feature
🐛 fix: Bug fix
📝 docs: Documentation
🧪 test: Testing
♻️ refactor: Refactoring
🔧 chore: Chores
```

**Note**: Emojis improve visibility but verify compatibility with automation tools.

---

## Pattern 4: Atomic Commits

### Overview

**Atomic commits** focus on "single logical changes." The principle of 1 commit = 1 responsibility makes review, revert, and debugging dramatically easier.

### Why Atomic Commits Matter

| Benefit | Description |
|---------|-------------|
| **Easy to review** | Small commits enable quick understanding of changes |
| **Easy to revert** | Safely undo only problematic commits |
| **Easy to debug** | `git bisect` identifies bug-introducing commits |
| **Readable history** | `git log` functions as a "story" |

### Bad Example: Massive Commit

```bash
git commit -m "feat: ユーザー機能とAPI改善とテスト追加"
# (Add user features, API improvements, and tests)

# Changed files
# src/user/models.py
# src/user/services.py
# src/api/routes.py
# src/api/middleware.py
# tests/test_user.py
# tests/test_api.py
# docs/API.md
```

**Problems**:
- Mixed responsibilities (user features + API improvements + tests + docs)
- Cannot revert partially
- Confuses reviewers

### Good Example: Atomically Split

```bash
# Commit 1
git add src/user/models.py
git commit -m "feat: Userモデルにプロフィール画像フィールドを追加"
# (Add profile image field to User model)

# Commit 2
git add src/user/services.py
git commit -m "feat: プロフィール画像アップロード機能を実装"
# (Implement profile image upload functionality)

# Commit 3
git add src/api/routes.py
git commit -m "feat: プロフィール画像アップロードAPIエンドポイントを追加"
# (Add profile image upload API endpoint)

# Commit 4
git add src/api/middleware.py
git commit -m "refactor: API認証ミドルウェアのエラーハンドリングを改善"
# (Improve error handling in API auth middleware)

# Commit 5
git add tests/test_user.py
git commit -m "test: プロフィール画像アップロード機能のテストを追加"
# (Add tests for profile image upload)

# Commit 6
git add docs/API.md
git commit -m "docs: プロフィール画像APIのドキュメントを追加"
# (Add documentation for profile image API)
```

**Benefits**:
- Each commit is independent
- Commit 4 (API improvement) can be moved to separate PR
- Reviewers can understand progressively

### Criteria for Commit Splitting

**Conditions to combine into one commit**:
- [ ] Change has a single logical purpose
- [ ] Changed files are around 1-3
- [ ] Lines changed are ≤50 (guideline)

**Signs to split**:
- [ ] "and" appears in description ("Add X and Y")
- [ ] Spans different modules/layers
- [ ] Commit message exceeds 3 lines

### Leveraging git add -p

Partial staging to split changes within files:

```bash
# Stage only part of file
git add -p src/user/services.py

# Interactive selection
# y: stage this change
# n: skip
# s: split into smaller chunks
# q: quit

git commit -m "feat: ユーザーサービスにバリデーション追加"
# (Add validation to user service)

# Separate commit for remaining changes
git add src/user/services.py
git commit -m "refactor: ユーザーサービスのエラーメッセージを改善"
# (Improve error messages in user service)
```

---

## Best Practices

### 1. Accumulate Small Commits (Consistency is Power)

Daily development awareness:
- 1 feature = 3-5 commits, not 1 commit
- Review changes with `git diff` before committing
- Exclude unrelated changes (debug prints, etc.)

### 2. Make Commit History a Learning Asset (Compounding Growth)

Good commit history is team knowledge base:
- `git log --oneline --graph` for overall picture
- `git blame` to investigate "why this code exists"
- `git show <commit>` to review past decision reasoning

### 3. Share Patterns Across Team (Fundamentals & Patterns)

Create `.github/pull_request_template.md`:

```markdown
## Changes

## Why This Change is Needed

## Impact Scope

## Testing

- [ ] Unit tests
- [ ] E2E tests

## Checklist

- [ ] Committed in Conventional Commits format
- [ ] Split into atomic commits
- [ ] Documentation updated
```

### 4. Pre-Commit Checklist

```bash
# 1. Review changes
git diff

# 2. Check status
git status

# 3. Exclude unrelated changes
git restore <file>  # or git checkout <file>

# 4. Commit in Conventional Commits format
git commit -m "feat: ..."

# 5. Verify commit message
git log -1
```

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Vague Messages

```bash
# Bad
git commit -m "update"
git commit -m "fix"
git commit -m "WIP"

# Good
git commit -m "docs: READMEのインストール手順を更新"
# (Update installation steps in README)
git commit -m "fix: ログイン時のNullPointerExceptionを修正"
# (Fix NullPointerException during login)
# WIP temporarily OK, but must squash or rewrite before PR
```

### ❌ Anti-Pattern 2: Direct Commits to main

```bash
# Bad
git checkout main
git commit -m "feat: 新機能" # (New feature)
git push origin main

# Good
git checkout -b feature/new-feature
git commit -m "feat: 新機能" # (New feature)
git push origin feature/new-feature
# Create Pull Request for review
```

### ❌ Anti-Pattern 3: Massive Pull Requests

```bash
# Bad
# 50 files, 2000 lines in one PR

# Good
# Split features progressively
# PR1: Model definitions (5 files, 200 lines)
# PR2: Service implementation (3 files, 150 lines)
# PR3: API endpoints (2 files, 100 lines)
# PR4: UI implementation (10 files, 300 lines)
```

**Principle**: Aim for ≤300 lines per PR

### ❌ Anti-Pattern 4: Force Push Abuse After Commits

```bash
# Dangerous: force push to shared branch
git push -f origin main  # Absolutely forbidden

# Safe: only on your feature branch
git push -f origin feature/my-work  # OK before PR merge
```

**Rules**:
- `git push -f` to main branch is prohibited
- Force push to shared branches requires prior notification

---

## Philosophy Alignment Table

| Git Practice | Corresponding Values | Description |
|-------------|---------------------|-------------|
| Conventional Commits | **Fundamentals & Patterns** | Maximum potential with minimal form. Patterns enable speed |
| Atomic Commits | **Fundamentals & Patterns** / **Compounding Growth** | Accumulate small commits for long-term quality |
| Japanese Messages | **Neutral** | Universal usability. Understandable in native language |
| GitHub Flow | **Fundamentals & Patterns** / **Compounding Growth** | Simple pattern for consistent team workflow |
| Specifying Why | **Articulating Tacit Knowledge** | Convert "just because" to "clear reasoning" |
| Code Review | **Consistency is Power** / **Compounding Growth** | Joy of teaching and learning. Feedback as learning opportunity |
| Commit History = Learning Asset | **Learning from Past** | Connecting past wisdom with new technologies |

---

## FAQ

### Q1: Japanese or English commit messages—which is better?

**A**: Depends on team situation.

| Case | Recommendation | Reason |
|------|---------------|--------|
| Japanese-only team | **Japanese** | Clear communication in native language |
| International team | English | Common language |
| OSS project | English | For global contributors |

This skill assumes **Japanese commit messages**, but Conventional Commits format is language-independent, so same principles apply to English.

### Q2: I made a mistake in my commit. What should I do?

**A**: Solutions vary by situation.

```bash
# Case 1: Fix most recent commit message
git commit --amend -m "fix: 正しいメッセージ" # (Correct message)

# Case 2: Add file to most recent commit
git add forgotten_file.py
git commit --amend --no-edit

# Case 3: Modify past commits (not yet pushed)
git rebase -i HEAD~3  # Interactive edit of past 3 commits

# Case 4: Already pushed (your branch)
git commit --amend
git push -f origin feature/my-branch

# Case 5: Already merged to main
# → Fix with new commit (don't use revert/amend)
git revert <commit-hash>
```

### Q3: Is Conventional Commits scope mandatory?

**A**: No, it's optional.

- **Small projects**: No scope needed
- **Medium-large projects**: Scope is helpful
- **Monorepos**: Scope recommended (`feat(frontend):`, `fix(backend):`)

Start without scope; introduce when you feel the need.

### Q4: How many commits should one PR contain?

**A**: **1-10 commits** is a guideline.

| Commit Count | Assessment | Recommended Action |
|-------------|-----------|-------------------|
| 1-3 | ✅ Ideal | Merge as-is |
| 4-10 | ✅ Good | Verify each commit is atomic |
| 11-20 | ⚠️ Many | Consider splitting PR |
| 21+ | ❌ Too many | Must split |

### Q5: Are "WIP" commits acceptable?

**A**: Acceptable during development, cleanup required before PR.

```bash
# During development (personal branch)
git commit -m "WIP: 認証機能の途中" # (Auth feature in progress) - OK

# Cleanup before PR creation via squash or rebase
git rebase -i HEAD~5
# Combine WIP commits and rewrite to proper message

# Final commit
git commit -m "feat: JWT認証機能を実装" # (Implement JWT auth)
```

### Q6: Tips for keeping Git history clean?

**A**: Make these habits:

1. **Commit frequently during development** (WIP OK)
2. **Organize history before PR creation** (`git rebase -i`)
3. **Separate commits for review fixes** (preserve history)
4. **Squash when merging** (keep main clean)

```bash
# Development flow example
git commit -m "WIP: モデル追加" # (Add model)
git commit -m "WIP: サービス実装" # (Implement service)
git commit -m "WIP: テスト追加" # (Add tests)

# Before PR creation
git rebase -i HEAD~3
# → Combine 3 commits into one, organize message

# Final commit
"feat: ユーザープロフィール編集機能を実装"
# (Implement user profile edit feature)
```

---

## Summary

What you can master with this skill:

✅ **Conventional Commits format** for consistent commit messages  
✅ **GitHub Flow** for simple yet powerful branch strategy  
✅ **Atomic commits** for easy-to-review, easy-to-revert history  
✅ **Effective Japanese messages** creating assets understandable by entire team  
✅ **Code review culture** for continuous learning and growth  
✅ **Philosophy alignment** realizing Fundamentals & Patterns, Compounding Growth

**Fundamentals enable infinite applications. Patterns enable speed.**

Transform commit history into "learning assets" and build an environment where the entire team grows autonomously.

---

**Author**: RyoMurakami1983  
**Version**: 1.0.0  
**License**: MIT
