# Skill Quality Levels

このファイルは validation の single source of truth として使います。

## Critical Checks

skill を出荷可能とみなす前に、Critical はすべて通過させます。

| ID | Check | Why it matters |
| --- | --- | --- |
| C1 | Frontmatter に `name` と `description` がある | 起動条件は parse できる metadata が前提になる。 |
| C2 | `name` がディレクトリ名と一致する | 安定した lookup には `name` と配置の整合が必要。 |
| C3 | `description` に trigger-oriented な表現（例: `こんなときに使う` / `Use when`）がある | trigger surface が曖昧だと発見性が落ちる。 |
| C4 | `## こんなときに使う` 互換のセクションがある | 起動後すぐに relevance を判断できる必要がある。 |
| C5 | 明示的な手順または route を持つ workflow / router セクションがある | 次に何をする skill なのかを agent に示す必要がある。 |
| C6 | Router skill は `## 判断表` 互換セクションを持つ | router には意図から route への明示マップが必要。 |
| C7 | Router の route が実在する `sub_skills/` ディレクトリを指す | routing 文言と filesystem 構造は一致しているべき。 |

## Recommended Checks

Recommended は、わかりやすさ・再利用性・保守性を高めるためのシグナルです。

| ID | Check | Why it matters |
| --- | --- | --- |
| R1 | 「こんなときに使う」が 3-8 個の bullet で書かれている | 少なすぎると意図空間を取り逃がし、多すぎると焦点がぼける。 |
| R2 | 各 scenario が行動ベースで書かれている | 行動ベースの bullet はユーザー意図に対応づけやすい。 |
| R3 | skill が「何を」だけでなく「なぜ」を説明している | WHY を説明する guidance のほうが応用しやすい。 |
| R4 | `## 注意点` 互換セクションがある | 失敗パターンは暗黙知にせず明示したほうが強い。 |
| R5 | main `SKILL.md` がコンパクトに保たれている | hot path は短く保ち、必要時だけ `references/` を読む形がよい。 |
| R6 | overflow detail は必要時に `references/` へ逃がす | 本文が十分コンパクトなら必須ではないが、長文化し始めたら `references/` へ分離する。 |
| R7 | 関連リソースや sibling skill への導線がある | cross-navigation は重複説明を減らす。 |
| R8 | multi-step な操作では早見表または判断表がある | 実行者には短い execution view が必要。 |
| R9 | コードやコマンド例が空でない / 壊れていない | 壊れた例は信頼をすぐ失わせる。 |
| R10 | H1 タイトルがある | 起動後に「何の skill か」を一目で掴める。 |
| R11 | Router skill は 2-7 個の sub-skill に保つ | 少なすぎる route は router 化の価値が薄く、多すぎるとノイズになる。 |
| R12 | 各 sub-skill が独自の「こんなときに使う」を持つ | sibling route の違いを局所的に判断しやすくなる。 |

## Validation Levels

| Level | Scope | Expected use |
| --- | --- | --- |
| L1 | Critical checks only | 初稿の draft gate |
| L2 | Critical + Recommended | 広く使う前の review gate |
| L3 | Governance and enterprise review | team / organization rollout |
| L4 | Behavioral eval pipeline | trigger quality を測る重要 skill |

router 固有の check は、automation 実装が後から追いつく場合でも、まずこの文書側に定義しておきます。著者が 1 つの基準を見れば済むようにするためです。
