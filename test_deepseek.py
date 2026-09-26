import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.environ["NVIDIA_API_KEY"]
)

try:
    completion = client.chat.completions.create(
      model="deepseek-ai/deepseek-coder-6.7b-instruct",
      messages=[{"role":"user","content":"Say hi"}],
      timeout=10
    )
    print(completion.choices[0].message.content)
except Exception as e:
    print("Error:", e)
