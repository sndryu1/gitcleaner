# gitcleaner

**溜まったローカルブランチを、安全に一括掃除。** マージ済み・上流が削除済み(`gone`)・長期間放置のブランチを一覧にし、確認してから削除します。Python 3 標準ライブラリのみ、単一ファイル。

```console
$ python gitcleaner.py --stale-days 90
  keep    main
  keep    feature/login
  delete? fix/typo  [merged]
  delete? old-spike  [upstream gone]
  delete? exp/cache  [stale (210d)]

3 candidate(s). Re-run with --delete to remove them.
```

## 安全設計
- **既定は一覧表示のみ。** `--delete` を付けない限り何も消しません
- 削除前に `[y/N]` で確認(`--yes` で省略)
- 現在のブランチ、デフォルトブランチ、`main`/`master`/`develop`/`dev`/`trunk`/`release` は常に保護
- マージ済みは `git branch -d`(安全削除)。未マージ(放置・上流削除)は **`--force` を付けない限りスキップ**

## インストール
```
pip install git+https://github.com/sndryu1/gitcleaner.git
```
(PyPI 公開後は `pip install gitcleaner`)

**実行ファイル(Python 不要):** [Releases](https://github.com/sndryu1/gitcleaner/releases) から Windows / macOS / Linux 用をダウンロード。

または単一ファイルだけ取得:
```
curl -O https://raw.githubusercontent.com/sndryu1/gitcleaner/main/gitcleaner.py
```

## 使い方
```
python gitcleaner.py [--stale-days N] [--delete] [--force] [--yes]
```
| オプション | 内容 |
|---|---|
| `--stale-days N` | N日以上更新のないブランチも候補にする |
| `--delete` | 候補を削除する(確認あり) |
| `--force` | 未マージの候補も `-D` で削除する |
| `--yes` | 確認プロンプトを省略 |

`git gc` のように常用したい場合は `alias gitclean='python /path/to/gitcleaner.py'`。

## テスト
`python -m unittest discover tests`

## License
MIT
