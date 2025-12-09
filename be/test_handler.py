"""
Test script for Lambda handlers
Run with: python test_handler.py
"""
import json
from handler import presign, upload, ask

# Test presign endpoint
def test_presign():
    event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'filename': 'test.pdf',
            'content_type': 'application/pdf'
        })
    }
    context = {}
    
    response = presign(event, context)
    print("Presign Response:")
    print(json.dumps(json.loads(response['body']), indent=2))
    print()

# Test ask endpoint (general question)
def test_ask_general():
    event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'question': 'What is AWS Bedrock?'
        })
    }
    context = {}
    
    response = ask(event, context)
    print("Ask Response (General):")
    print(json.dumps(json.loads(response['body']), indent=2))
    print()

# Test validation
def test_validation():
    event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'filename': 'test.exe',  # Invalid file type
            'content_type': 'application/x-msdownload'
        })
    }
    context = {}
    
    response = presign(event, context)
    print("Validation Test (should fail):")
    print(json.dumps(json.loads(response['body']), indent=2))
    print()

if __name__ == '__main__':
    print("=" * 50)
    print("Testing Lambda Handlers")
    print("=" * 50)
    print()
    
    # Make sure AWS credentials are configured
    print("Note: Make sure AWS credentials are configured!")
    print()
    
    # Run tests
    test_validation()
    # test_presign()  # Uncomment to test presign
    # test_ask_general()  # Uncomment to test ask (requires Bedrock access)
