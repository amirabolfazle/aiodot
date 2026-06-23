# ==========================================
# aiodot/auth.py
# ==========================================

"""Authentication module for MyDot.one. Token-based with session file."""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict, field

import aiohttp
import requests


@dataclass
class Session:
    """Session data saved to disk."""
    token: str = ""
    user_id: str = ""
    username: str = ""
    display_name: str = ""
    phone: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


class MyDotAuth:
    """Auth handler for MyDot.one."""

    BASE_URL = "https://api.mydot.one/mydot/api/v1"

    def __init__(self, session_file: Optional[str] = None):
        if session_file is None:
            self.session_file = Path.home() / ".mydot" / "session.json"
        else:
            self.session_file = Path(session_file)

        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.session_data = Session()
        self._loaded = False

        if self.session_file.exists():
            self._load()

    def _load(self) -> bool:
        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.session_data = Session.from_dict(data)
            self._loaded = bool(self.session_data.token)
            return True
        except Exception:
            return False

    def save(self) -> None:
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(self.session_data.to_dict(), f, indent=2, ensure_ascii=False)

    def clear(self) -> None:
        self.session_data = Session()
        if self.session_file.exists():
            self.session_file.unlink()

    # ============ Sync Login (called once during init) ============

    def login_with_token_sync(self, token: str) -> bool:
        """Sync token validation. Called once during MyDotClient init."""
        self.session_data.token = token
        resp = requests.get(
            f"{self.BASE_URL}/auth/profile/",
            cookies={"__Secure-access_token": token},
            headers=self._get_headers_sync(),
        )
        if resp.ok:
            p = resp.json()
            self.session_data.user_id = p.get("user_id", "")
            self.session_data.username = p.get("username", "")
            self.session_data.display_name = p.get("display_name", "")
            self._loaded = True
            self.save()
            print(f"✅ Token saved! @{self.username}")
            return True
        print("❌ Invalid token")
        return False

    # ============ Async Token Refresh ============

    async def refresh(self) -> bool:
        """Async token refresh using aiohttp."""
        headers = self._get_headers_async()
        headers["Cookie"] = f"__Secure-access_token={self.token}"
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.BASE_URL}/auth/token/refresh/", headers=headers, json={}) as resp:
                if resp.status == 200:
                    for key, cookie in resp.cookies.items():
                        if key == "__Secure-access_token":
                            self.session_data.token = cookie.value
                            self.save()
                            print("🔄 Token refreshed")
                            return True
        return False

    # ============ Headers ============

    def _get_headers_sync(self) -> Dict[str, str]:
        return {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://mydot.one",
            "Referer": "https://mydot.one/",
            "User-Agent": "Mozilla/5.0",
        }

    def _get_headers_async(self) -> Dict[str, str]:
        return {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://mydot.one",
            "Referer": "https://mydot.one/",
            "User-Agent": "Mozilla/5.0",
        }

    # ============ Properties ============

    @property
    def token(self) -> Optional[str]:
        return self.session_data.token

    @property
    def user_id(self) -> Optional[str]:
        return self.session_data.user_id

    @property
    def username(self) -> Optional[str]:
        return self.session_data.username

    @property
    def display_name(self) -> Optional[str]:
        return self.session_data.display_name

    @property
    def is_logged_in(self) -> bool:
        return self._loaded and bool(self.token)

    def __repr__(self) -> str:
        return f"MyDotAuth(@{self.username})" if self.username else "MyDotAuth(not logged in)"