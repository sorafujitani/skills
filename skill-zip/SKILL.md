---
name: skill-zip
description: "ローカルの Claude Code skill ディレクトリを ZIP に固めて、Claude Desktop アプリ (consumer 版、Settings から Customize から Skills) のアップロード用ファイルとして書き出す。Claude Code CLI と異なり Claude Desktop は ~/.claude/skills/ を読まず ZIP アップロード方式のため、その橋渡しを提供する。プロンプトに skill 名を含めて呼ぶ (例 — 「graph-think-map を zip 化して」「Claude Desktop 用に doc-prerequisite-knowledge を package して」「skill を Desktop アプリに upload できる形にして」)。出力 default は ~/Downloads/{name}.zip。"
---

# Skill Zip

ローカルの skill ディレクトリを Claude Desktop アップロード用 ZIP に固める。

## 背景

| 環境 | skill 配布方法 |
|------|----------------|
| Claude Code CLI / IDE 拡張 | `~/.claude/skills/<name>/SKILL.md` を直接読む |
| Claude Desktop アプリ (consumer 版) | Settings > Customize > Skills で **ZIP をアップロード** |

このスキルは前者の skill を後者の形式に変換するだけの薄いラッパー。

## ワークフロー

進捗チェックリスト (応答にコピーして進捗管理):

```
- [ ] Step 1: ユーザーの要求から skill 名を抽出
- [ ] Step 2: skill ソースディレクトリを特定
- [ ] Step 3: zip_skill.sh で ZIP 化
- [ ] Step 4: 出力パスと Claude Desktop へのインポート手順を案内
```

### Step 1: skill 名を抽出

ユーザーの自然言語から skill 名を取り出す。複数候補があれば 1 つだけ確認質問する。

入力に skill 名が含まれない場合は、`~/.claude/skills/` の listing から候補を提示して選んでもらう。

### Step 2: ソースディレクトリを特定

優先順位:
1. `~/.claude/skills/<name>/` (personal skill)
2. プロジェクト直下 `.claude/skills/<name>/` (project-local skill)

両方にある場合は personal を default、ユーザーに 1 行確認。
どこにも無い場合は「skill が見つかりません」と返し、似た名前の候補を一覧する。

### Step 3: ZIP 化

```bash
~/.claude/skills/skill-zip/scripts/zip_skill.sh <name> [<source-dir>] [<output-path>]
```

引数:
- `<name>` (必須): skill 名 (ZIP root ディレクトリ名と filename に使う)
- `<source-dir>` (省略時): `~/.claude/skills/<name>`
- `<output-path>` (省略時): `~/Downloads/<name>.zip`

スクリプトの保証:
- ZIP の root には `<name>/` だけが入る (skill 標準形式)。Desktop はこれを期待する
- `.DS_Store` / `__pycache__` / `*.pyc` を自動除外
- 既存の同名 ZIP は上書き
- `SKILL.md` が存在しない場合は exit 1

### Step 4: 案内

ZIP 出力に成功したら、以下のテンプレで返す:

```
✅ {output-path} を作成しました ({size}, {file-count} files)

Claude Desktop でのインポート手順:
1. Claude Desktop を開く
2. Settings > Customize > Skills
3. 上記 ZIP をドラッグ&ドロップ (または "Add skill" で選択)
4. 反映確認: 新規チャットで /<name> を呼ぶか、トリガー文を投げる
```

Optional: `unzip -l <out>` で中身を簡易表示しても良い (ノードのリスト感を伝える)。

## やらないこと

- skill の中身を勝手に書き換えない (frontmatter 修正、不要ファイル削除等は別 skill / 手動)
- Claude Desktop の起動・操作はしない (ZIP を作るだけ)
- skill validation はこの skill の責務ではない (`package_skill.py` 等を別途使う)

## 品質チェックリスト

```
- [ ] 出力 ZIP の root に <name>/ が 1 つだけ含まれる (root に SKILL.md が直接出ない)
- [ ] junk files (.DS_Store / __pycache__) が除外されている
- [ ] 出力パスをユーザーに明示した
- [ ] Claude Desktop へのインポート手順を案内した
```
