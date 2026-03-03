#! /usr/bin/env sh

# 「環境構築 → DB接続待ち → テスト実行 → カバレッジ生成 → 環境削除」を行う、
# 一連のパイプラインを完結させるためのエントリーポイント

# エラーが発生した場合にスクリプトを即座に終了させる
set -e

# 実行されるコマンドをターミナルに表示する（デバッグ用）
set -x

# 1. コンテナイメージのビルド
docker compose build

# 2. 既存環境のクリーンアップ
# 以前の実行で残ったスタックやボリュームを削除し、クリーンな状態にする
docker compose down -v --remove-orphans

# 3. コンテナの起動
# バックグラウンド（-d）で全サービスを起動する
docker compose up -d

# 4. バックエンドコンテナ内でのテスト実行
# backendコンテナ内で scripts/tests-start.sh を実行し、引数（$@）を渡す
docker compose exec -T backend bash scripts/tests-start.sh "$@"

# 5. 実行後のクリーンアップ
# テスト終了後、ボリュームを含めて環境を削除する
docker compose down -v --remove-orphans
