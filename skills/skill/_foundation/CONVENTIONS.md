# Skill Conventions

`skills/skill/` を一貫した型で保つための約束です。

## Naming

- kebab-case を使う
- top-level skill は `<context>-<verb>-<object>` を優先する
- router 配下の sub-skill は、文脈が親で補えるなら短い名前でもよい

## Frontmatter

- 必須: `name`, `description`
- 任意: `compatibility`
- `description` は trigger-oriented に書き、`こんなときに使う` 相当の表現を入れる
- `description: >` を使う場合、折り返しは句点や読点など意味の切れ目に寄せる。`こんなときに` と `使う` のように意味のまとまりを不自然に分断しない
- `compatibility` には、本当に必要なツールや runtime 制約だけを書く

## Directory Rules

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

- `SKILL.md` を正本の実行ガイドとして扱う
- `references/` には overflow docs や必要時の補助資料を置く
- `scripts/` には agent が毎回書き直すべきでない deterministic helper を置く
- `assets/` には出力に埋め込むファイルを置き、説明文書は置かない

## Router Skills

1 つの入口から、明確に異なる sub-workflow へ分岐する必要があるときだけ router を使います。

```text
router-name/
├── SKILL.md
├── sub_skills/
│   ├── route-a/
│   │   └── SKILL.md
│   └── route-b/
│       └── SKILL.md
├── _foundation/
├── scripts/
├── references/
└── assets/
```

- 親 router は `## 判断表` 互換セクションを持ち、`やりたいこと`、`ルート`、`次にやること` を明示する
- route path は `sub_skills/<name>/` を指す
- router が domain を供給できるなら、sub-skill 名は短い verb / verb-object でよい
- 共有テンプレート、規約、補助断片は router の `_foundation/` に置く
- 詳細な実行ロジックは親 router ではなく各 sub-skill に置く

## Progressive Disclosure

| Level | Content | Rule |
| --- | --- | --- |
| L1 | frontmatter | 短く、trigger-rich に保つ |
| L2 | `SKILL.md` body | hot path を短く読みやすく保つ |
| L3 | bundled resources | 必要になったときだけ読む |

## Writing Style

- MUST / NEVER を並べるより、なぜその手順が効くかを説明する
- 次の行動がすぐわかる命令形の prose を使う
- 有能なチームメイトに教えるように書く
- 大きい reference には table of contents を付ける

## Anti-Patterns

- formatter や手作業で frontmatter を機械的に折り返し、意味のまとまりを壊す
- `こんなときに使う` の trigger 句を行途中で分断し、読み手に不要な復元コストをかける
- 「短くしたい」だけを理由に、句点や意味境界より前で説明文を不自然に改行する

## Safety

- malware、exploit instructions、security bypass guidance を reusable skill として梱包しない
- 破壊的操作の前には、least surprise でリスクが見える workflow を優先する
