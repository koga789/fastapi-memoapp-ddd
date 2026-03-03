#! /usr/bin/env bash
set -e
set -x

# データベースが接続可能な状態になるまで待機
python app/tests_pre_start.py

# Pytestの実行（coverage ツール経由）
bash scripts/test.sh "$@"
