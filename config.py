"""Configuration settings for the time series forecasting agent."""
import os
import boto3
from botocore.config import Config

# Environment variables
ENDPOINT_NAME = os.environ.get("SAGEMAKER_ENDPOINT_NAME")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
REGION = "us-west-2"

# AWS clients
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name=REGION)
s3_client = boto3.client(
    "s3", 
    region_name=REGION, 
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"})
)

# System prompt
SYSTEM_PROMPT = """あなたは与えられたデータを解析して、SageMakerにアクセスして時系列予測を実行し、結果を考察するエージェントです。

必須手順:
1. analyze_csvツールでCSVデータを解析
2. predict_time_seriesツールで予測を実行
3. create_forecast_graphツールが返すMarkdown形式の結果（このツールは履歴データと予測結果を可視化したグラフ画像を必ず生成します）をそのまま出力
4. 予測結果について考察を追加

重要: create_forecast_graphツールの出力には必ずグラフ画像が含まれています。![Sales Forecast]({s3_url}) です。entrypointの関数からフロントエンドにグラフ画像のS3 URIをMarkdownの形式で絶対に返却してください。

質問者が対象列を明示しなかった場合は自分で判断してtarget列を指定してください。"""
