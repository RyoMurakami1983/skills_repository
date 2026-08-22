# Archive notice

## Status

このリポジトリは2026-08-22に開発を終了し、read-onlyの履歴としてアーカイブします。

開発は [RyoMurakami1983/happy-ai-work](https://github.com/RyoMurakami1983/happy-ai-work) で継続します。移行先はCodexデスクトップアプリとCodex CLIを主対象とし、旧leaf skill、固定agent、Copilot instructions、GitHub wrapperをそのまま移植しません。

このrepoに残る同期、インストール、skill、agentの説明は当時の履歴です。現在の導入手順として使用しないでください。

## Migrated as a redesigned Issue

| Old Issue | 移行先 | 判断 |
| --- | --- | --- |
| [#172](https://github.com/RyoMurakami1983/skills_repository/issues/172)、[#173](https://github.com/RyoMurakami1983/skills_repository/issues/173) | [happy-ai-work#8](https://github.com/RyoMurakami1983/happy-ai-work/issues/8) | Tauriの日常dev loopとWindowsの実行中binary lock診断を、package managerやアプリ名に依存しない一つのIssueへ再設計した。 |

## Fulfilled or absorbed

| Issue | 判断理由 |
| --- | --- |
| [#182](https://github.com/RyoMurakami1983/skills_repository/issues/182) | 現行のskill portfolioとskill-evalが、独立目的、実利用、near-miss、should-not-trigger、追加複雑性を含む採用・停止基準を持つ。 |
| [#175](https://github.com/RyoMurakami1983/skills_repository/issues/175)、[#174](https://github.com/RyoMurakami1983/skills_repository/issues/174) | 現行のfurikaeri、improvement-loop、happy-add-issue、github-issueに改善候補の選別とIssue intakeを再設計済み。 |
| [#142](https://github.com/RyoMurakami1983/skills_repository/issues/142) | 特殊directoryだけのleaf ruleにせず、repo instructions、README、近接docs、既存変更を先に確認する一般原則へ吸収した。 |
| [#85](https://github.com/RyoMurakami1983/skills_repository/issues/85) | 現行のTDD loopとskill-evalがfail-first、near-miss、false-positive相当のshould-not-trigger評価を扱う。 |

## Retired and not ported

| Issue | 判断理由 |
| --- | --- |
| [#181](https://github.com/RyoMurakami1983/skills_repository/issues/181) | Oracle専用leaf skillを廃止し、一般.NETとWPFの責務へ統合した。実案件で独自workflowが必要になった場合だけ再評価する。 |
| [#180](https://github.com/RyoMurakami1983/skills_repository/issues/180) | 旧skill routerとsub_skills構造を移植せず、公式skill-creatorと現行portfolioを使う。 |
| [#165](https://github.com/RyoMurakami1983/skills_repository/issues/165) | PR確認command wrapperはGitHub pluginおよびCodexのGit workflowと重複する。 |
| [#164](https://github.com/RyoMurakami1983/skills_repository/issues/164) | 毎sessionの一律環境判定は行わず、Codexのenvironment contextと対象repoのbuild contractを使う。 |
| [#127](https://github.com/RyoMurakami1983/skills_repository/issues/127) | Copilot固有のPLAN modeとinstructionsを対象とするため、Codex向けrepoへ移植しない。 |
| [#87](https://github.com/RyoMurakami1983/skills_repository/issues/87) | Copilot指摘への無条件な即時対応は採用しない。現行は指摘をcodeとtestで独立検証し、scopeと妥当性を確認する。 |
| [#86](https://github.com/RyoMurakami1983/skills_repository/issues/86) | 旧SQL todo管理を廃止し、現行のtask／Issue責務へ移行した。 |
| [#71](https://github.com/RyoMurakami1983/skills_repository/issues/71) | 対象となる旧dotnet leaf skillとtool inventoryを移植していない。 |
| [#21](https://github.com/RyoMurakami1983/skills_repository/issues/21) | PowerShellのgh wrapperを再実装せず、GitHub connectorを優先する。 |
| [#13](https://github.com/RyoMurakami1983/skills_repository/issues/13) | 独自create-skill CLIを移植せず、公式skill-creatorを使用する。 |

## Pull requests

アーカイブ判断時点でopen pull requestはありません。

## Preservation policy

commit、closed issue、docs、旧skills／agentsは移行せず、このrepoに履歴として保持します。新しいbacklogは移行先で、現在の構造とAcceptance Criteriaに合わせて新規作成します。
