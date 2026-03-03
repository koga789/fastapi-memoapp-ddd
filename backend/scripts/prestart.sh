#! /usr/bin/env bash

set -e
set -x

# データベースの疎通を確認
python app/backend_pre_start.py

# マイグレーションの適用
alembic upgrade head
