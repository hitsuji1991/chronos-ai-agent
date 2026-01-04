#!/usr/bin/env python3
"""Time series forecasting agent using SageMaker and Bedrock."""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from config import SYSTEM_PROMPT
from tools import analyze_csv, predict_time_series, create_forecast_graph

app = BedrockAgentCoreApp()

@app.entrypoint
async def entrypoint(payload):
    """Time series forecasting agent"""
    print("payload received:", payload)

    model_id = payload.get("model", {}).get("modelId", "anthropic.claude-sonnet-4-20250514-v1:0")

    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        tools=[analyze_csv, predict_time_series, create_forecast_graph],
        model=BedrockModel(model_id=model_id),
    )
    
    message = payload.get("prompt", "")
    async for msg in agent.stream_async(message):
        yield msg


if __name__ == "__main__":
    app.run()
