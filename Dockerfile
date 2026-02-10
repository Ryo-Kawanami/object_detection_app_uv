# uvがプリインストールされた軽量イメージを使用
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# 依存関係ファイルのコピー
COPY pyproject.toml uv.lock ./

# 依存関係のインストール (lockファイル通りにインストール)
# システム環境にインストールすることで仮想環境のアクティベートを省略
RUN uv sync --frozen --no-cache

# アプリケーションコードのコピー
COPY main.py .
# 実行
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]