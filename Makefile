.PHONY: help docker-build docker-up docker-up-dev docker-up-prod docker-down docker-logs docker-restart docker-shell docker-clean docker-rebuild docker-ps docker-health

# デフォルトターゲット
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "docker-build        - Dockerイメージをビルド"
	@echo "docker-up           - 開発環境を起動"
	@echo "docker-up-dev       - 開発環境を起動（ログ表示）"
	@echo "docker-up-prod      - 本番環境を起動"
	@echo "docker-down         - コンテナを停止して削除"
	@echo "docker-logs         - ログを表示"
	@echo "docker-restart      - コンテナを再起動"
	@echo "docker-shell        - コンテナ内でシェルを起動"
	@echo "docker-clean        - コンテナ、イメージ、ボリュームを削除"
	@echo "docker-rebuild      - イメージを再ビルドして起動"
	@echo "docker-ps           - 実行中のコンテナを表示"
	@echo "docker-health       - ヘルスチェックの状態を確認"

# Docker関連コマンド

docker-build: ## Dockerイメージをビルド
	docker compose build

docker-up: ## バックグラウンド（デタッチモード）で起動
	docker compose up -d

docker-watch: ## 開発環境を起動（コード変更を監視）
	docker compose watch

docker-down: ## コンテナを停止して削除
	docker compose down -v --remove-orphans

docker-clean: ## コンテナ、イメージ、ボリュームを削除
	docker compose down -v --rmi local

docker-ps: ## 実行中のコンテナを表示
	docker compose ps


# テスト関連コマンド

test-backend: ## バックエンドのテストを実行
	bash scripts/test.sh -x
