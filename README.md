# object-detection-app

DETR (Facebook DETR) を使ったシンプルな物体検出 API + フロントエンド（FastAPI）。

<div align="center">
<p align="center">
    <img src="https://github.com/Ryo-Kawanami/object_detection_app_uv/blob/main/assets/showcase.png"/>
<p>
</div>

## 概要

- FastAPI サーバーが Hugging Face Transformers の DETR モデルを読み込み、アップロード画像に対して物体検出を行う。
- シンプルなブラウザ UI（static/index.html）で画像アップロード → 検出結果を重ねて表示。

## 主要ファイル

- `main.py` — FastAPI アプリケーション（/detect エンドポイント、静的ファイル配信）
- `static/index.html` — フロントエンド UI
- `pyproject.toml` — 依存管理
- `Dockerfile` — コンテナ化用

## 前提条件

- Python 3.12 以上
- 仮想環境の利用を推奨

## セットアップ（ローカル）

1. uvのインストール

https://docs.astral.sh/uv/getting-started/installation/

2. 起動

```

uv run uvicorn main:app --reload

```

ブラウザで http://127.0.0.1:8000/ を開く。

## API

- POST /detect
- form-data: `file` (画像)
- クエリパラメータ: `threshold`（0.5〜1.0、既定 0.9）
- レスポンス: JSON（filename, detections）
- detection: { label, score, box: { xmin, ymin, xmax, ymax } }

curl の例：

```

curl -F "file=@test.jpg" "http://127.0.0.1:8000/detect?threshold=0.85"

```

## Docker

ビルドと実行：

```

docker build -t object-detection-app .
docker run -p 8000:8000 object-detection-app

```

## 注意点

- Transformers がモデルをダウンロードする際、HF Hub のレート制限があります。頻繁にダウンロードする場合は環境変数 `HF_TOKEN` を設定してください。
- 起動時に大きなモデルをトップレベルで読み込むとリローダやサブプロセスで問題が出ることがあります。`@app.on_event("startup")` で遅延ロードすることを推奨します（`main.py` 内のモデル読み込みを startup に移す方法を検討してください）。
- Mac の CPU 環境では推論が遅いです。GPU を使う場合は PyTorch を CUDA 対応でインストールしてください。

## 開発 / テスト

- dev 依存は `pyproject.toml` の dependency-groups に記載（pytest, ruff など）。
- ユニットテスト追加や CI 導入は自由に行ってください。

## ライセンス

プロジェクトに合わせて適切なライセンスを追加してください。
