from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

print("===================================")
print("        AI CODE REVIEWER")
print("===================================")
print("Paste Python code below")
print("Type END to finish\n")

lines = []

while True:

    line = input()

    if line == "END":
        break

    lines.append(line)

code = "\n".join(lines)

prompt = f"""
You are an expert Python code reviewer.

Analyze this code:
- Find syntax errors
- Find logical bugs
- Suggest improvements
- Explain clearly

Code:
{code}
"""

try:

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print("\n===================================")
    print("         AI REVIEW RESULT")
    print("===================================\n")

    print(response.choices[0].message.content)

except Exception as e:

    print("\n❌ Error:")
    print(e)
