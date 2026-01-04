"""Tools for time series prediction and visualization."""
import json
from strands import tool
from config import sagemaker_runtime, ENDPOINT_NAME
from utils import (
    parse_input, process_csv_data, prepare_prediction_inputs,
    create_forecast_plot, save_plot_to_s3, generate_result_text
)


@tool
def analyze_csv(csv_data: str) -> dict:
    """添付されたCSVファイルのデータをSageMakerのエンドポイントに投げるためにデータを整形する"""
    try:
        df, target_col, numeric_cols, item_ids = process_csv_data(csv_data)
        inputs, prediction_length = prepare_prediction_inputs(df, target_col, numeric_cols, item_ids)
        
        print(f'inputs in analyze csv method is {inputs}')
        return {"inputs": inputs, "prediction_length": prediction_length}
    
    except Exception as e:
        print(f"Error in analyze_csv: {e}")
        return {"error": str(e)}


@tool
def predict_time_series(inputs: dict) -> dict:
    """Execute time series prediction using SageMaker"""
    try:
        print(f'inputs in predict_time_series is {inputs}')
        inputs = parse_input(inputs)
        print(f"inputs after parsing is {inputs}")

        payload = {
            "inputs": inputs['inputs'], 
            "parameters": {"prediction_length": inputs['prediction_length']}
        }
        print(f'payload is {payload}')

        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME, 
            ContentType="application/json", 
            Body=json.dumps(payload)
        )
        print(f"response is {response}")

        results = json.loads(response["Body"].read().decode())
        return {"inputs": inputs, "results": results}
    
    except Exception as e:
        print(f"Error in predict_time_series: {e}")
        raise e


@tool
def create_forecast_graph(prediction_result: str) -> str:
    """Create forecast visualization graph"""
    try:
        print(f"prediction_result before parsing: {prediction_result}")
        prediction_result = parse_input(prediction_result)
        print(f"prediction_result after parsing: {prediction_result}")

        inputs_data = prediction_result["inputs"]
        results = prediction_result["results"]
        
        # Handle nested inputs structure
        if isinstance(inputs_data, dict) and "inputs" in inputs_data:
            inputs_list = inputs_data["inputs"]
        else:
            inputs_list = inputs_data

        # Organize data by item_id
        input_dict = {item["item_id"]: item["target"] for item in inputs_list}
        result_dict = {item["item_id"]: item for item in results['predictions']}

        result_texts = []

        # Create separate graphs for each item_id
        for item_id in input_dict.keys():
            target_data = input_dict[item_id]
            forecast_data = result_dict[item_id]
            
            # Create and save plot
            plt_obj = create_forecast_plot(item_id, target_data, forecast_data)
            s3_url = save_plot_to_s3(plt_obj)
            
            # Generate result text
            result_text = generate_result_text(
                item_id, target_data, forecast_data["mean"], s3_url
            )
            result_texts.append(result_text)
        
        return result_texts

    except Exception as e:
        print(f"Error in create_forecast_graph: {e}")
        return str(e)
