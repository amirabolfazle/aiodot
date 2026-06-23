import asyncio
import aiohttp
import json
from pathlib import Path
from aiodot import MyDotClient

USERNAME = "SamDev"   
PASSWORD = "45737619*Mn"     
SESSION_FILE = "session.json"


async def login_and_save():
    print("Logging in...")
    
    async with aiohttp.ClientSession() as session:
        url = "https://api.mydot.one/mydot/api/v1/auth/login/"
        payload = {
            "identifier": USERNAME,
            "password": PASSWORD
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Login failed: {resp.status} - {text}")
            
            token = None
            for key, cookie in resp.cookies.items():
                if key == "__Secure-access_token":
                    token = cookie.value
                    break
            
            if not token:
                data = await resp.json()
                token = data.get("access_token")
            
            if not token:
                raise Exception("Token not found!")
            
            Path(SESSION_FILE).write_text(
                json.dumps({"token": token}, indent=2),
                encoding="utf-8"
            )
            
            print("Session saved!")
            return token


async def main():
    token = await login_and_save()
    
    async with MyDotClient(token=token, session_file=SESSION_FILE) as client:
        me = await client.get_me()
        print(f"Welcome @{me.username}")
        
        dot = await client.create_dot("Hello MyDot!")
        print(f"Post sent: {dot.url}")


if __name__ == "__main__":
    asyncio.run(main())