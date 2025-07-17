from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
response = client.responses.create(
    model="gpt-4.1",
    input="Ý nghĩa cuộc sống là gì?"
)

print(response.output_text)
