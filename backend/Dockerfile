# uvのバージョンを定義
ARG UV_VERSION=0.9.26

# uvのイメージをビルドステージとして定義
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

# ============================================================
# Base ステージ: 共通設定
# ============================================================
FROM python:3.14-slim AS base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/home/appuser/.cache/uv

RUN groupadd -r appuser && \
    useradd -r -g appuser -d /home/appuser -m -s /sbin/nologin -c "Application user" -u 1000 appuser

COPY --from=uv /uv /uvx /bin/

WORKDIR /app/backend
RUN chown appuser:appuser /app/backend

USER appuser

ENV PATH="/app/backend/.venv/bin:$PATH"

# ============================================================
# Development ステージ: 開発依存関係を含む
# ============================================================
FROM base AS development

# 1. 依存関係のインストール（開発依存関係を含む）
RUN --mount=type=cache,target=/home/appuser/.cache/uv,uid=1000,gid=1000 \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --group dev

# 2. アプリケーションファイルのコピー（テストを含む）
COPY --chown=appuser:appuser ./pyproject.toml ./alembic.ini /app/backend/
COPY --chown=appuser:appuser ./app /app/backend/app
COPY --chown=appuser:appuser ./scripts /app/backend/scripts
COPY --chown=appuser:appuser ./tests /app/backend/tests

# 3. プロジェクト自体をインストール
RUN --mount=type=cache,target=/home/appuser/.cache/uv,uid=1000,gid=1000 \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --group dev

CMD ["fastapi", "run", "--reload", "app/main.py"]

# ============================================================
# Production ステージ: 本番用の最小構成
# ============================================================
FROM base AS production

# 1. 依存関係のインストール（本番依存関係のみ）
RUN --mount=type=cache,target=/home/appuser/.cache/uv,uid=1000,gid=1000 \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# 2. アプリケーションファイルのコピー
COPY --chown=appuser:appuser ./pyproject.toml ./alembic.ini /app/backend/
COPY --chown=appuser:appuser ./app /app/backend/app
COPY --chown=appuser:appuser ./scripts /app/backend/scripts

# 3. プロジェクト自体をインストール
RUN --mount=type=cache,target=/home/appuser/.cache/uv,uid=1000,gid=1000 \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
