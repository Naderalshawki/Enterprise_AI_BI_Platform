
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load .env from the current project directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not api_key:
    raise RuntimeError(
        f"GROQ_API_KEY not found. Check this file: {env_path}"
    )

print(f"Testing Groq model: {model}")

client = Groq(
    api_key=api_key,
    timeout=30.0,
    max_retries=0,
)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: GROQ_OK",
            }
        ],
        temperature=0,
        max_tokens=256,
    )

    print("SUCCESS:", response.choices[0].message.content)

except Exception as exc:print("Response ID:", response.id)
print("Finish reason:", response.choices[0].finish_reason)
print("Message:", repr(response.choices[0].message))
print("Usage:", response.usage)