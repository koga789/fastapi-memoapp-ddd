#!/usr/bin/env bash

set -e
set -x

# テストの実行
# テスト中にアプリケーションのどの行が実行されたかを詳細に記録
coverage run -m pytest tests/

# カバレッジレポートを表示
# テスト完了後、コンソール上に各ファイルごとのカバレッジ率（％）をテキスト形式で出力
coverage report

# HTMLレポートの生成
# スクリプト実行時に渡された引数をレポートのタイトルとして反映する
coverage html --title "${@-coverage}"
