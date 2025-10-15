"""
AWS Lambda Handler for Customer Support Agent
Serverless deployment using Mangum adapter
"""
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from mangum import Mangum
from app.main import app

# Create Lambda handler using Mangum
# Mangum adapts FastAPI/Starlette applications for AWS Lambda and API Gateway
handler = Mangum(app, lifespan="off")


def lambda_handler(event, context):
    """
    AWS Lambda entry point
    
    Args:
        event: API Gateway event data
        context: Lambda runtime information
        
    Returns:
        API Gateway compatible response
    """
    # Log incoming request
    print(f"Incoming event: {event.get('httpMethod')} {event.get('path')}")
    
    # Handle the request using Mangum
    response = handler(event, context)
    
    return response


# For local testing
if __name__ == "__main__":
    # Simulate a Lambda event
    test_event = {
        "httpMethod": "POST",
        "path": "/api/chat",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": '{"query": "What payment methods do you support?"}'
    }
    
    test_context = {}
    
    result = lambda_handler(test_event, test_context)
    print("Response:", result)
