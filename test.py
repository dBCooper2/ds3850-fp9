import os
from dotenv import load_dotenv
import openai
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_openai_connection():
    # Load and verify API key
    load_dotenv(override=True)
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("No API key found in environment variables")
        return False
        
    # Clean the API key - remove any whitespace or quotes
    api_key = api_key.strip().replace('"', '').replace("'", '')
    
    # Verify API key format
    if not api_key.startswith(('sk-', 'org-')):
        print("API key appears to be in incorrect format")
        print(f"API key should start with 'sk-' or 'org-'")
        return False

    try:
        print("\nAttempting API connection...")
        client = openai.OpenAI(
            api_key=api_key,
            timeout=30.0,  # Increase timeout
            max_retries=0  # Disable automatic retries
        )
        
        # Add delay before request
        time.sleep(1)
        
        print("Sending test request...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello"}
            ],
            max_tokens=10,
            temperature=0.7
        )
        
        print("Response received!")
        print(f"Content: {response.choices[0].message.content}")
        return True
        
    except openai.RateLimitError as e:
        print(f"\nRate Limit Error: {str(e)}")
        print("\nPossible solutions:")
        print("1. Check your API key billing status")
        print("2. Verify API key permissions")
        print("3. Check usage limits at platform.openai.com/account/billing")
        return False
        
    except openai.AuthenticationError as e:
        print(f"\nAuthentication Error: {str(e)}")
        print("Please verify your API key is correct and active")
        return False
        
    except openai.APIError as e:
        print(f"\nAPI Error: {str(e)}")
        return False
        
    except Exception as e:
        print(f"\nUnexpected error: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    print("OpenAI API Test")
    print("--------------")
    
    # Print environment info
    print(f"OpenAI version: {openai.__version__}")
    
    # Test the connection
    success = test_openai_connection()
    
    if not success:
        print("\nTroubleshooting steps:")
        print("1. Verify your API key at: https://platform.openai.com/api-keys")
        print("2. Check billing status at: https://platform.openai.com/account/billing")
        print("3. Verify you have usage available at: https://platform.openai.com/usage")
        print("4. Try creating a new API key and updating your .env file")