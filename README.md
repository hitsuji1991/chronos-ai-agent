# Chronos AI Agent

時系列データの予測を行うAIエージェントです。Amazon SageMakerとAmazon Bedrockを活用して、CSVデータから自動的に時系列予測を実行し、結果を可視化します。

## 機能

- CSVデータの自動解析
- SageMakerエンドポイントを使用した時系列予測
- 予測結果の可視化グラフ生成
- S3への結果保存
- Bedrock Claude モデルによる結果考察

## 必要な環境

- Python 3.12+
- AWS アカウント（SageMaker、S3、Bedrock へのアクセス権限）
- 事前にデプロイされたSageMaker時系列予測エンドポイント

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
export SAGEMAKER_ENDPOINT_NAME="your-sagemaker-endpoint-name"
export S3_BUCKET_NAME="your-s3-bucket-name"
```

### 3. AWS認証情報の設定

AWS CLIまたは環境変数でAWS認証情報を設定してください。

## 使用方法

### ローカル実行

```bash
python main.py
```

### Docker実行

```bash
# イメージのビルド
docker build -t chronos-ai-agent .

# コンテナの実行
docker run -p 8080:8080 \
  -e SAGEMAKER_ENDPOINT_NAME="your-endpoint" \
  -e S3_BUCKET_NAME="your-bucket" \
  -e AWS_ACCESS_KEY_ID="your-key" \
  -e AWS_SECRET_ACCESS_KEY="your-secret" \
  chronos-ai-agent
```

## API仕様

エージェントは以下の形式でリクエストを受け付けます：

```json
{
  "prompt": "CSVデータを解析して時系列予測を実行してください",
  "model": {
    "modelId": "anthropic.claude-sonnet-4-20250514-v1:0"
  }
}
```

## ファイル構成

- `main.py` - メインアプリケーション
- `config.py` - 設定とAWSクライアント
- `tools.py` - 予測・可視化ツール
- `utils.py` - データ処理ユーティリティ
- `requirements.txt` - Python依存関係
- `Dockerfile` - Docker設定

## 処理フロー

1. CSVデータの解析（`analyze_csv`）
2. SageMakerでの時系列予測実行（`predict_time_series`）
3. 予測結果の可視化グラフ生成（`create_forecast_graph`）
4. Claude モデルによる結果考察

## 注意事項

- SageMakerエンドポイントが事前にデプロイされている必要があります
- S3バケットへの読み書き権限が必要です
- 対象列が明示されない場合、自動的に判断されます
