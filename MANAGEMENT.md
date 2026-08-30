# ローカルのスキル管理

自作スキルの編集元はこのリポジトリです。GitHubのURLは
`https://github.com/sorafujitani/skills.git` のままです。

| 種類 | 実体 | 更新元 |
| --- | --- | --- |
| 単独の自作スキル | このリポジトリの `<name>/` | このリポジトリで編集 |
| 外部スキル | `~/.codex/skills/<name>/` | Codexのskill-installer |
| 他プロダクトが管理する導入済みスキル | `~/.codex/skills/<name>/` | そのプロダクトの導入手順 |
| 別リポジトリで開発するスキル | 所有プロジェクトのスキルフォルダ | 所有プロジェクトで編集 |

`~/.agents/skills` と `~/.claude/skills` にはリンクだけを置きます。
自作スキルには `~/.codex/skills` にも互換リンクを置きます。各入口は同じ実体を
参照するため、コピー同期は不要です。Codexの実際の一覧で重複がないことも検査します。
プラグインのキャッシュと `.system` は各インストーラーに任せます。

ローカルの管理台帳は `~/.codex/skill-management.json` です。外部スキルの出自、
導入時点の内容ハッシュ、参照先を記録します。過去のlockファイルは証拠として保持しますが、
今後の追加は下記の操作に揃えます。移行した既存スキルには導入commitが不明なものもあり、
ハッシュは導入元の検証ではなく、移行後のローカル変更検知に使います。

## 一覧・検査

```sh
python3 scripts/manage_skills.py list
python3 scripts/manage_skills.py list --kind personal
python3 scripts/manage_skills.py list --kind external
python3 scripts/manage_skills.py check
python3 scripts/manage_skills.py link
```

`link` は不足したリンクだけを作り、実体フォルダや異なるリンク先は上書きしません。
`check` は未登録のスキル、重複した実体、リンク切れを検出します。
`list` の `modified` は移行・導入時点から内容が変わった外部パッケージを示します。

## 自作スキルを追加

Codexのskill-creatorに、このリポジトリの `<name>/` を作成先として指定します。
指定を省略すると `.codex/skills` に実体が作られるため、作成先は必ず明示します。
`reflect`・`meditate` などから作成する場合も同じです。

初期化スクリプトを使う場合:

```sh
python3 ~/.codex/skills/.system/skill-creator/scripts/init_skill.py my-skill \
  --path ~/ghq/github.com/sorafujitani/skills
```

初期化後にSKILL.mdを仕上げ、必要な補助ファイルを揃えて検証します。
その後、このリポジトリを作業ディレクトリとして登録・参照検査まで行います。

```sh
python3 scripts/manage_skills.py register my-skill --kind personal --path ./my-skill
python3 scripts/manage_skills.py check
```

`--kind personal` はこのリポジトリ直下の実体だけを受け付けます。誤って
`.codex/skills` などに作った場合は、既存の同名スキルと差分を調べ、内容を保護して
正しい編集元へ移してから登録します。上書きで解決しないでください。

プロジェクト専用スキル、プラグイン内スキル、専用生成ツールが管理するartifact templateは
この個人ライブラリへの集約対象ではありません。各ツールの配置・登録仕様を維持します。
組み込みのskill-creatorやプラグインキャッシュ自体は変更しません。

公開済みスキルの更新も、このリポジトリのファイルを直接編集します。
リンク経由の編集も同じファイルに反映されます。新しいスキルを公開するときだけ、内容と
対象ファイルを確認してコミット・pushします。移行時の未追跡ファイルは未公開です。

## 外部スキルを追加

```sh
python3 scripts/manage_skills.py install example-skill \
  --repo owner/repository --path skills/example-skill --ref COMMIT_SHA
```

この操作はCodexに同梱されたskill-installerを呼び、出自を記録してリンクを作ります。
スキルの内容は実行しません。可能なら不変のcommit SHAを指定してください。
既存の同名スキルは上書きしません。

自動更新は行いません。更新時はまず出自とローカル差分を調べ、新版を別の場所に取得して
比較します。独自修正を保持できると確認してから置き換え、台帳のrefとbaselineHashを更新します。
出自未確認のスキルを名前だけで外部から再インストールしないでください。

## 互換性と復元

従来の `.claude/skills` / `.agents/skills` / `.codex/skills` のパスはリンクで維持します。
スキルが使う別のデータフォルダ・会話ログは移動しません。
`pr:gen-linear` はClaude側の互換名として `pr-gen-linear` と同じ実体を指します。

移行前の全フォルダ、両Gitリポジトリの `.git`、ステージ済み・未ステージ差分と
実際のCodex一覧は、管理台帳の `backup` に示したフォルダに保存しています。
旧Gitのステージ済み5ファイルは、移行後のリポジトリにも同じ内容で引き継ぎました。
復元は現在の変更も退避してから行い、旧スナップショットで新しい作業を上書きしないでください。
