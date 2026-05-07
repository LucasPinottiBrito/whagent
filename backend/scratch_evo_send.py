import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv(".env")

async def test():
    base_url = os.getenv("EVOLUTION_API_BASE_URL", "http://localhost:8080").rstrip("/")
    api_key = os.getenv("EVOLUTION_API_KEY", "p8qlNdkSEDjPDL8zObEtJEBJ")
    instance = "instancia-demo"
    phone = "5511977776666"

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{base_url}/message/sendText/{instance}",
            headers={"apikey": api_key, "Content-Type": "application/json"},
            json={"number": phone, "text": "Teste de retorno de ID da API"}
        )
        print("Status:", r.status_code)
        try:
            print("JSON:", r.json())
        except:
            print("Text:", r.text)

if __name__ == "__main__":
    asyncio.run(test())
