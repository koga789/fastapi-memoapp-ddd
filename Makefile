.PHONY: help docker-build docker-up docker-watch docker-down docker-clean docker-ps test-backend

# デフォルトターゲット
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "docker-build        - Dockerイメージをビルド"
	@echo "docker-up           - バックグラウンド（デタッチモード）で起動"
	@echo "docker-watch        - 開発環境を起動（コード変更を監視）"
	@echo "docker-down         - コンテナを停止して削除"
	@echo "docker-clean        - コンテナ、イメージ、ボリュームを削除"
	@echo "docker-ps           - 実行中のコンテナを表示"
	@echo "test-backend        - バックエンドのテストを実行"

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
