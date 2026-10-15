# 改善ステップ 0〜13

番号はユーザー提示の順序。公式READMEの見出し番号ではない。スコアは書籍Ruby実装・計測環境の参考値。下記の検証観点は、このスキルで段階的に作業するための補足である。

公式サンプル・スコア:
https://github.com/tatsujin-web-performance/tatsujin-web-performance/blob/v1/appendix-A/README.md

SQL:
https://github.com/tatsujin-web-performance/tatsujin-web-performance/tree/v1/appendix-A/private-isu/webapp/sql

| 番号 | 変更と範囲 | 主な確認 | 参考スコア |
|---|---|---|---:|
| 0 | ベンチ、アクセスログ、MySQLスローログで現状を計測 | 対象・初期化範囲・実行条件・エラー・負荷 | — |
| 1 | `comments(post_id, created_at DESC)` | 既存索引との重複、投稿別一覧・件数の実行計画 | — |
| 2 | Unicorn workerを4に増やす | 有効worker数とメモリ、DB接続数。別ランタイムは実装に応じて判断 | 約15,000 |
| 3 | CSS・JSなどをnginxから配信しexpiresを設定 | root/aliasと権限、MIME、アプリを経由しないこと | 約17,000 |
| 4 | 新規画像をファイル保存。既存画像は初回DB取得時にファイル化し、以後nginx配信 | 未生成時のアプリfallback、新規・既存画像、同時取得、初期化後の古い画像 | 約22,000 |
| 5 | postsとusersをJOIN、`users.del_flg = 0` をSQLへ移し、新着順で20件取得 | 削除ユーザー除外後のLIMIT、投稿者情報、画面ごとの件数・順序 | 約90,000 |
| 6 | `posts(created_at DESC)` | ORDER BYとLIMITの実行計画、同等索引の有無 | — |
| 7 | Rubyの毎回のprepare/executeをmysql2-cs-bindのxqueryへ | 値のバインド・戻り値・依存追加。文字列連結でSQLを組まない | 約110,000 |
| 8 | `comments(user_id)` | プロフィールのコメント件数集計の実行計画 | — |
| 9 | 投稿別コメント件数・一覧をMemcachedへ。コメント投稿者はJOIN | 更新・削除・初期化時の整合性、miss、TTL、一覧順序、既存の全件表示用途 | 約180,000 |
| 10 | 必要なクエリへSTRAIGHT_JOIN/FORCE INDEX | 対象環境の実行計画と測定で有効性を確認。効果がなければ無理に導入しない | 約200,000 |
| 11 | openssl外部コマンドをライブラリへ | 入力バイト列・改行・ハッシュ表現の同一性、既存ユーザーのログイン | 約240,000 |
| 12 | slow log停止、binlog無効化、`innodb_flush_log_at_trx_commit = 2` | 練習環境の耐久性・復旧条件、対応する設定名、再起動後の有効値 | 約255,000 |
| 13 | Memcachedのgetをget_multiへ | missの補完・空結果・キー対応・表示順序・通信回数 | 約300,000 |

## 適用時の注意

- 1/6/8: MySQLのバージョンごとに降順索引の対応が異なる。公式DDLを盲目的に実行せず、現在の定義と実行計画を確認する。
- 4: 初期化で投稿IDが再利用される場合、前回の画像を配信しない仕組みが必要。初期化時の削除は、このアプリが生成したファイルだけを対象にする。
- 5: 先にLIMITしアプリ側で削除ユーザーを除くと件数が不足する。投稿とユーザーの同名カラムの衝突や、プロフィールなど別の一覧条件を維持する。
- 9/13: キャッシュキーと更新・無効化の経路をソースで追う。専用か不明なMemcachedにflush_allを実行しない。初期化後も古い値が残らないようにする。
- 12: binlog停止や同期緩和は耐久性と復旧能力を変える。対象が破棄可能な専用練習DBであること、レプリケーションや保持要件がないことを確認する。不明なら該当変更前に確認する。ファイル全体のコピーで認証設定などを持ち込まない。計測済みログを保存してから停止する。

## 公式の変更差分

対象ステップの差分を開き、現在の実装に必要な部分だけ移す。

- 2: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/83a57020b2e205c8a7d6163ee3c58fed361f6605
- 3: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/9f34d0bd90146a050cc4c7e13d5c89743c7f77be
- 4（アプリ）: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/907c70b3f7e722068fd3462445d8cee8efb27a76
- 4（nginx）: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/a49eb2dfd307ffe7a85eb9cfbcae3912e8427f0d
- 5: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/7f73caf78e714e982b9f24478e0919b8e50af2b6
- 7: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/57592ee2681fc3551ab810932b1706fc775aac43
- 9: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/8de837130c50186ce5cd08b560552cd97a1e9b34
- 10: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/8bf1580d4542dd7e4c798dcc6c6aead6cd0bd339
- 11: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/8f3b4a8839a3583a8abd2bde0cea2e2bfa2f8c20
- 12: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/ecabb326243b04fb5e7e669d034ad2eeb6297474
- 13: https://github.com/tatsujin-web-performance/tatsujin-web-performance/commit/ca092dc1e02f7b3b0d79c96b1271bf0dbd4bb5b9

MySQL設定:
https://github.com/tatsujin-web-performance/tatsujin-web-performance/blob/v1/appendix-A/private-isu/webapp/etc/my.cnf
