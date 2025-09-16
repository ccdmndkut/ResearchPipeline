"""
Test OpenAI API connection (simplified)
"""
import asyncio
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv('.env')

async def test_openai():
    """Test OpenAI API connection"""

    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key or api_key == 'sk-xxxxx':
        print("[ERROR] No valid OpenAI API key found in .env file")
        print("Please ensure OPENAI_API_KEY is set in .env file")
        return False

    print(f"[OK] API Key found: {api_key[:7]}...{api_key[-4:]}")

    # Initialize OpenAI client
    client = openai.AsyncOpenAI(api_key=api_key)

    try:
        print("\nTesting OpenAI API connection...")

        # Simple test call
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using cheaper model for test
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, API is working!' in exactly 5 words."}
            ],
            max_tokens=50,
            temperature=0
        )

        result = response.choices[0].message.content
        print(f"[OK] Response: {result}")

        # Test with a research-related query
        print("\nTesting research query expansion...")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Expand the search query with related terms for academic search. Reply with comma-separated terms only."},
                {"role": "user", "content": "machine learning"}
            ],
            max_tokens=100,
            temperature=0.3
        )

        expanded = response.choices[0].message.content
        print(f"[OK] Query expansion: {expanded}")

        print("\n[SUCCESS] OpenAI API is working correctly!")
        print("Model: gpt-3.5-turbo")
        print(f"Usage: {response.usage}")
        return True

    except openai.AuthenticationError as e:
        print(f"\n[AUTH ERROR] {e}")
        print("Please check your API key is valid")
        return False

    except openai.RateLimitError as e:
        print(f"\n[RATE LIMIT] {e}")
        print("API key is valid but you've hit rate limits")
        return False

    except openai.APIError as e:
        print(f"\n[API ERROR] {e}")
        return False

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_openai())