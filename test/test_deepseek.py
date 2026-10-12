from openai import OpenAI

client = OpenAI(
    api_key="sk-dde5e30f75db4e95ba8328f5078ceeec",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "user",
            "content": "اكتب جملة ترحيبية قصيرة فقط."
        }
    ],
    max_tokens=100,
)

print(response.choices[0].message.content)