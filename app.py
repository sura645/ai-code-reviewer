from google import genai
from google.genai.errors import ClientError
from dotenv import load_dotenv
import os
import time
import re

# Load environment variables
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Retry function
def generate_content_with_retry(client, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"\n🔄 Attempt {attempt + 1}/{max_retries}")
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response

        except ClientError as e:
            # FIX 1: Use e.code instead of e.status_code for the new SDK
            if e.code == 429:
                error_msg = str(e)
                
                # FIX 2: Catch daily cap exhaustions so you don't wait fruitlessly
                if "free_tier_requests" in error_msg or "per_day" in error_msg:
                    print("\n🛑 Daily Free Tier Quota is completely exhausted!")
                    print("💡 Waiting won't help right now. Please try again tomorrow or upgrade to Pay-As-You-Go.")
                    raise RuntimeError("Daily API quota limit hit.")

                # Handle short term minute-by-minute rate limits
                wait_match = re.search(
                    r"Please retry in (\d+\.\d+)s",
                    error_msg
                )
                wait_time = (
                    float(wait_match.group(1))
                    if wait_match
                    else 40.0
                )

                print("\n🛑 API Minute-Rate limit exceeded")
                print(f"⏳ Waiting {wait_time:.2f} seconds before retry...")
                time.sleep(wait_time + 1)
            else:
                print("\n❌ API Error")
                print(e)
                raise e

    raise RuntimeError("Failed after maximum retries.")


# Application UI
print("===================================")
print("        AI CODE REVIEWER")
print("===================================")
print("Paste Python code below")
print("Type END to finish\n")

# Read multiline input
lines = []
while True:
    line = input()
    if line == "END":
        break
    lines.append(line)

# Combine all code
code = "\n".join(lines)

# Ensure user actually entered code before wasting an API call
if not code.strip():
    print("\n❌ No code provided to review. Exiting.")
    exit()

# Prompt
prompt = f"""
You are an expert Python code reviewer.

Analyze the following Python code.

Tasks:
1. Find syntax errors
2. Find logical bugs
3. Suggest improvements
4. Explain clearly
5. Show corrected code if possible

Python Code:
{code}
"""

try:
    # Generate AI response
    response = generate_content_with_retry(
        client,
        prompt
    )

    print("\n===================================")
    print("         AI REVIEW RESULT")
    print("===================================\n")
    print(response.text)

except Exception as e:
    print("\n❌ Application Error Stopped Execution")