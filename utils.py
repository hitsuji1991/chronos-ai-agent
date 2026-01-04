"""Utility functions for data processing and visualization."""
import json
import uuid
import numpy as np
import pandas as pd
import base64
from io import StringIO, BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "DejaVu Sans"

from config import s3_client, S3_BUCKET_NAME


class NotFoundError(Exception):
    """csvファイルに必要な列が存在していない場合のエラー"""
    pass


def parse_input(inputs):
    """Parse string input to dictionary if needed."""
    if isinstance(inputs, str):
        try:
            return json.loads(inputs)
        except json.JSONDecodeError:
            return eval(inputs)
    return inputs


def process_csv_data(csv_data):
    """Process CSV data and prepare for time series prediction."""
    csv_text = base64.b64decode(csv_data).decode("utf-8")
    df = pd.read_csv(StringIO(csv_text))
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        raise NotFoundError("csvファイル内に時系列予測対象のデータが存在しません。")
    
    target_col = numeric_cols[0]
    
    # Handle item_id column
    if "item_id" in df.columns:
        item_ids = list(df["item_id"].unique())
    else:
        item_ids = ["item_a"]
        df["item_id"] = "item_a"

    print('df is {}'.format(df))
    print('target_col is {}'.format(target_col))
    print('numeric_cols is {}'.format(numeric_cols))
    print('item_ids is {}'.format(item_ids))
    
    return df, target_col, numeric_cols, item_ids


def prepare_prediction_inputs(df, target_col, numeric_cols, item_ids):
    """Prepare inputs for time series prediction."""
    inputs = []
    prediction_length = None
    
    for item_id in item_ids:
        df_item = df[df["item_id"] == item_id]
        target_data = df_item[target_col].dropna().tolist()
        
        data = {"target": target_data, "item_id": item_id}
        
        # Handle covariates
        past_cols = numeric_cols[1:] if len(numeric_cols) > 1 else []
        if len(past_cols) > 0:
            past_data = {col: df_item[col].iloc[:len(target_data)].tolist() for col in past_cols}
            data["past_covariates"] = past_data
            
            # Future covariates
            future_start = len(target_data)
            if future_start < len(df_item):
                future_data = {
                    col: df_item[col].iloc[future_start:].dropna().tolist()
                    for col in past_cols
                    if not df_item[col].iloc[future_start:].isna().all()
                }
                if future_data:
                    data["future_covariates"] = future_data
                    prediction_length = len(list(future_data.values())[0])
        
        inputs.append(data)
    
    return inputs, prediction_length


def create_forecast_plot(item_id, target_data, forecast_data):
    """Create a single forecast plot for an item."""
    plt.figure(figsize=(10, 6))
    
    # Historical data
    target_x = range(len(target_data))
    plt.plot(target_x, target_data, "o-", label="Actual", color="blue")
    
    # Forecast data
    forecast_start = len(target_data)
    forecast_x = range(forecast_start, forecast_start + len(forecast_data["mean"]))
    
    plt.plot(forecast_x, forecast_data["mean"], "s-", label="Forecast Mean", color="red")
    plt.fill_between(
        forecast_x, forecast_data["0.1"], forecast_data["0.9"], 
        alpha=0.3, color="red", label="80% Confidence Interval"
    )
    
    plt.title(f"Time Series Forecast for {item_id}")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    return plt


def save_plot_to_s3(plt_obj):
    """Save matplotlib plot to S3 and return URL."""
    buf = BytesIO()
    plt_obj.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    plt_obj.close()
    
    file_key = f"{uuid.uuid4().hex[:16]}/{uuid.uuid4().hex[:8]}.png"
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME, 
        Key=file_key, 
        Body=buf.getvalue(), 
        ContentType="image/png"
    )
    
    return f"https://{S3_BUCKET_NAME}.s3.us-west-2.amazonaws.com/{file_key}"


def generate_result_text(item_id, target_data, forecast_mean, s3_url):
    """Generate formatted result text with statistics."""
    mean_val = np.mean(target_data)
    std_val = np.std(target_data)
    
    return f"""## 予測結果

**統計情報:**
- 履歴データ平均: {round(mean_val, 2)}
- 履歴データ標準偏差: {round(std_val, 2)}
- 最新値: {target_data[-1]}

**予測値（平均）:** {[round(v, 2) for v in forecast_mean]}

**予測グラフ:**

![Sales Forecast]({s3_url})
"""
