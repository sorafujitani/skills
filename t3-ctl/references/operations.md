# 操作と状態の仕様

この仕様はControllerが行う選択・送信・確認を揃えるもの。T3 APIのトランザクションや、作業内容の正しさを保証する仕組みではない。

## プロジェクト選択

スキル実体のディレクトリを基準に実行する。Python標準ライブラリだけを使い、T3への書込みは行わない。

```sh
python3 scripts/control.py select-project < routing.json
```

入力例:

```json
{
  "scope": "current_project",
  "current_project_id": "project-a",
  "target": {"workspace_root": "/absolute/path/to/repo"},
  "projects": [{"id": "project-a", "title": "app", "workspaceRoot": "/absolute/path/to/repo"}]
}
```

- `projects` は対象環境の `t3_project_list` の全ページを合わせた配列。環境を混ぜない。重複IDがあれば一覧を取り直す。
- `target` は指定・裏付けのある条件だけを渡す。`project_id`、`workspace_root`、`repository_key`、`title` に対応し、複数指定は全条件の一致を要求する。指定が矛盾していても弱い条件へフォールバックしない。
- パスは対象マシンで確認した絶対パスを使う。別マシンのパスをローカルのrealpathで変換しない。
- `target` を省略した `current_project` は現在のプロジェクトを選ぶ。`cross_project` で対象なしなら確認を求める。
- `select` は一意な一致、`clarify` は未一致または複数一致。`verify_folder` は未登録の指定パスなので、フォルダの存在と登録許可を確認し、一覧を再確認してから登録する。新しいフォルダやGitリポジトリを自動作成する指示ではない。
- 登録時は `workspaceRoot` を明示する。応答が失われた場合はパスで一覧を照合し、既に登録されていればそのIDを使う。

## 作業場所と送信方法

| 状況 | 操作 |
|---|---|
| ユーザーが作業場所・baseを指定 | その指定を使う |
| 新規の独立したGit編集 | `workspaceStrategy.type=worktree`。remoteの既定ブランチから開始し `startFromOrigin=true`。remoteなしならローカル既定ブランチ |
| 未公開コミットに依存 | そのローカルbaseを使い `startFromOrigin=false` |
| 未コミット変更に依存 | その変更がある既存作業場所を確認し、所有者と競合しない形で担当へ渡す。worktreeに変更がコピーされるとは考えない |
| 読取りのみ、または非Gitフォルダでの作業 | 明示したroot。編集なら同じ対象の並行書込みを避ける |
| 既存担当への追加作業 | `t3_thread_send` の `mode=queue` |
| 実行中の作業への訂正を今反映する必要がある | `mode=steer`。開始し直す必要がある場合だけ明示許可の範囲でrestart |

モデルは指定を優先し、指定なしなら継承する。新規launchでのみworkspaceを指定する。既存スレッドの場所が違う場合は勝手に切り替えず、新担当または明示的な引継ぎを選ぶ。担当が稼働中か不明な場合は、先に現在の状態を読む。

## 操作IDと再送

```sh
python3 scripts/control.py operation-key < operation-input.json
```

入力例:

```json
{
  "environment_id": "environment-a",
  "controller_id": "original-controller-thread",
  "request_id": "original-user-message",
  "assignment_id": "a1",
  "revision": 1,
  "operation": "launch",
  "payload": {"projectId": "project-a", "title": "Task", "message": "The complete assignment"}
}
```

出力は `clientRequestId` と `payload_sha256`。IDは本文の要約ではなく、依頼・担当・revision・操作の組から生成する。同じJSONはキーの並び順が変わっても同じ結果になる。

1. IDを発行し、入力全体と出力を操作ファイルへ保存する。初回は既存ファイルを上書きしない。同じIDの保存済みファイルがあればhashと引数を比較する。
2. 保存したpayloadに `clientRequestId` を追加してツールへ渡す。
3. 返却された環境・project・thread・run・taskのID、リンク、deliveryを操作ファイルへ追記する。非対応のフィールドは捏造しない。
4. 応答不明なら状態を `dispatch_unknown` にする。元の保存済み引数とIDで再送できることを最新のツール定義で確認する。確認できない操作は、対象スレッドの状態・受信メッセージを照合してから判断する。毎回新しいIDを作らない。
5. 同じIDなのにpayloadのhashが違えば送信しない。意図的な依頼の修正・追加指示はrevisionを増やす。依頼の意味が変わっていない通信再試行ではrevisionを増やさない。

Controllerが交代しても、保存済みのcontroller ID・操作ID・引数を使う。新スレッドから再実行した場合の重複排除の範囲はAPI依存なので、IDだけで一度限りの実行を保証せず、先に受領記録と実際のスレッドを照合する。

## 状態と次の操作

| 状態 | 根拠 | 次の操作 |
|---|---|---|
| `needs_input` | 対象・権限・前提を確定できない | 必要な情報だけ確認。明確な独立作業は進めてよい |
| `prepared` | 対象と送信内容を保存済み | 保存した操作を送信 |
| `dispatch_unknown` | 送信の成否が不明 | 受領を照合。同じ操作の安全な再送以外は保留 |
| `running` | 対応runの起動・キュー投入を確認 | 通知または有限のblocking wait。`next` の指示が最優先 |
| `waiting_input` | 担当から質問・承認要求 | 許可範囲内の回答を返す。ユーザーだけが判断できる点は確認 |
| `reviewing` | 対応runが終了し、結果を取得 | 下記の完了条件を確認 |
| `failed` / `cancelled` | ツール上の失敗・取消し | 原因と残作業を確認。自動的に代替担当を作らない |
| `completed` | 完了条件と検証が揃い、未完了の子作業なし | ユーザーへ報告後、進行中一覧から外す |

`idle`、runの `completed`、waitのタイムアウトだけでは依頼を `completed` にしない。通知は依頼ID・担当・revision・run IDを照合する。古いrunや重複通知で現在の状態を上書きしない。照合できない通知は、保存済み担当を読んで確かめる。

完了確認は、依頼時に番号を付けた各条件について成果物と検証結果があるか、不合格・未実施・未解決事項が完了を妨げないか、子の作業が残っていないかを確認する。未完了の条件は具体的な追加指示として同じ担当へ送り、revisionを更新する。未検証を成功とみなさない。

通常スレッドは完了・失敗・判断待ちの報告でControllerを起動する。担当からの報告待ちでターンを終える場合は待機中と伝え、完了とは報告しない。delegateは `next` を守り、通常スレッドの報告手段でその待機規則を迂回しない。PRの待機は現在のPR監視ルールに従う。

## 状態の保存と交代

既定の保存先は `~/.local/state/t3-ctl/<project-id>/<control-id>/`。IDの各値はURL percent-encodingなどで安全な1パス要素にする。control-idは最初のControllerのIDで固定し、別マシンへ移る場合は保存先を明示的に引き継ぐ。状態をリポジトリへcommitしない。

- `ACTIVE.md`: 現在のControllerリンク・対象範囲・依頼ごとの目的、完了条件、担当リンク、状態、次の操作、操作ファイルへの参照。
- `operations/<clientRequestId>.json`: 送信前の引数とhash、送信後の受領記録。完了後も最小限の記録を残し、再送・再開時の照合に使う。全件を会話へ読み込まない。

依頼・担当・revisionをキーとして更新する。単独のControllerだけが書き込み、担当は短い報告を返す。交代時は旧Controllerの更新を止め、一覧と必要な操作記録を読み、稼働中の担当の状態を確認して報告先を変更する。過去の `ACTIVE.md` しかない場合は実際の担当からIDを補う。過去の操作が記録されていないことを、新規実行してよい根拠にしない。
