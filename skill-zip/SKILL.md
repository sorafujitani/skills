---
name: skill-zip
description: ローカルのAgent Skillを、SKILL.mdと補助ファイルを含むZIPにまとめる。スキルのZIP化やファイルでの受け渡しを明示的に依頼されたときに使う。
disable-model-invocation: true
---

# Skill ZIP

スキルのフォルダ全体をZIP化する。内容や設定は変更せず、公開・アップロードは行わない。

1. 指定されたスキルの `SKILL.md` のパスからソースフォルダを特定する。
   名前だけなら `~/.agents/skills/<name>/` を使う。リンクは編集元の実体を参照する。
2. 次のスクリプトでZIPを作成する。

   ```sh
   bash ~/.agents/skills/skill-zip/scripts/zip_skill.sh <name> [<source-dir>] [<output-path>]
   ```

   省略時の出力先は `~/Downloads/<name>.zip`。既存の出力ファイルを置き換えるため、
   依頼の対象でないファイルと衝突する場合は別の出力名を選ぶ。
3. `unzip -l` で `<name>/SKILL.md` と必要なscripts・referencesが含まれることを確認する。
4. 作成したZIPへのリンクを提示する。特定アプリへのインポート方法も求められた場合は、
   対象アプリの現在の手順を確認して案内する。

ZIP内にホームディレクトリを指すリンクを残さず、実ファイルとして格納する。
