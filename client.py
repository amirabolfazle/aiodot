from .models import Dot, User, ThreadView, Notification, PaginatedResponse, Thread, ReplyPermission
from typing import Optional, Dict, List, Any
import aiohttp
from .auth import MyDotAuth
from .wallet import WalletManager

class MyDotClient:
    BASE_URL = "https://api.mydot.one/mydot/api/v1"

    def __init__(self, token: Optional[str] = None, session_file: Optional[str] = None, auth: Optional[MyDotAuth] = None):
        if auth:
            self.auth = auth
        elif token:
            self.auth = MyDotAuth(session_file=session_file)
            self.auth.login_with_token_sync(token)
        else:
            self.auth = MyDotAuth(session_file=session_file)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()
            self._session = None

    @property
    def http(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("Use 'async with MyDotClient(...) as client:' block.")
        return self._session

    @property
    def wallet(self) -> WalletManager:
        return WalletManager(self)

    def _headers(self) -> Dict[str, str]:
        h = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://mydot.one",
            "Referer": "https://mydot.one/",
            "User-Agent": "Mozilla/5.0",
        }
        if self.auth.token:
            h["Cookie"] = f"__Secure-access_token={self.auth.token}"
        return h

    async def _get(self, path: str, params: Dict = None) -> Any:
        url = f"{self.BASE_URL}{path}"
        async with self.http.get(url, params=params, headers=self._headers()) as resp:
            if resp.status == 401 and await self.auth.refresh():
                async with self.http.get(url, params=params, headers=self._headers()) as r:
                    r.raise_for_status()
                    ct = r.content_type
                    return await r.json() if "json" in ct else await r.text()
            resp.raise_for_status()
            ct = resp.content_type
            return await resp.json() if "json" in ct else await resp.text()

    async def _post(self, path: str, json: Dict = None) -> Any:
        url = f"{self.BASE_URL}{path}"
        async with self.http.post(url, json=json, headers=self._headers()) as resp:
            if resp.status == 401 and await self.auth.refresh():
                async with self.http.post(url, json=json, headers=self._headers()) as r:
                    r.raise_for_status()
                    ct = r.content_type
                    return await r.json() if "json" in ct else await r.text()
            resp.raise_for_status()
            ct = resp.content_type
            return await resp.json() if "json" in ct else await resp.text()

    async def _patch(self, path: str, json: Dict = None) -> Any:
        url = f"{self.BASE_URL}{path}"
        async with self.http.patch(url, json=json, headers=self._headers()) as resp:
            if resp.status == 401 and await self.auth.refresh():
                async with self.http.patch(url, json=json, headers=self._headers()) as r:
                    r.raise_for_status()
                    ct = r.content_type
                    return await r.json() if "json" in ct else await r.text()
            resp.raise_for_status()
            ct = resp.content_type
            return await resp.json() if "json" in ct else await resp.text()

    async def _delete(self, path: str) -> Any:
        url = f"{self.BASE_URL}{path}"
        async with self.http.delete(url, headers=self._headers()) as resp:
            if resp.status == 401 and await self.auth.refresh():
                async with self.http.delete(url, headers=self._headers()) as r:
                    r.raise_for_status()
                    ct = r.content_type
                    return await r.json() if "json" in ct else await r.text()
            resp.raise_for_status()
            ct = resp.content_type
            return await resp.json() if "json" in ct else await resp.text()

    async def get_me(self) -> User:
        data = await self._get("/auth/profile/")
        return User.from_dict(data)

    async def update_profile(self, **kwargs) -> User:
        data = await self._patch("/auth/profile/", json=kwargs)
        return User.from_dict(data)

    async def get_profile_visibility(self) -> Dict:
        return await self._get("/auth/profile/visibility/")

    async def set_profile_visibility(self, visibility: str) -> Dict:
        return await self._patch("/auth/profile/visibility/", json={"profile_visibility": visibility})

    async def follow(self, user_id: str) -> bool:
        await self._post("/auth/follow/", json={"target_id": user_id})
        return True

    async def unfollow(self, user_id: str) -> bool:
        await self._post("/auth/unfollow/", json={"target_id": user_id})
        return True

    async def block(self, user_id: str) -> bool:
        await self._post("/auth/block/", json={"target_id": user_id})
        return True

    async def unblock(self, user_id: str) -> bool:
        await self._post("/auth/unblock/", json={"target_id": user_id})
        return True

    async def mute(self, user_id: str) -> bool:
        await self._post("/auth/mute/", json={"target_id": user_id})
        return True

    async def unmute(self, user_id: str) -> bool:
        await self._post("/auth/unmute/", json={"target_id": user_id})
        return True

    async def get_user_followers(self, username: str, page_size: int = 20) -> Dict:
        return await self._get(f"/auth/{username}/followers/", params={"page_size": page_size})

    async def get_user_following(self, username: str, page_size: int = 20) -> Dict:
        return await self._get(f"/auth/{username}/following/", params={"page_size": page_size})

    async def search_users(self, query: str) -> Any:
        return await self._get("/auth/profile/search", params={"q": query})

    async def get_dot(self, dot_id: str) -> Dot:
        data = await self._get(f"/dots/{dot_id}/")
        return Dot.from_dict(data)

    async def get_thread_view(self, dot_id: str) -> ThreadView:
        data = await self._get(f"/dots/{dot_id}/thread-view/")
        return ThreadView.from_dict(data)

    async def get_replies(self, dot_id: str, page: int = 1, limit: int = 20) -> Dict:
        return await self._get(f"/dots/{dot_id}/replies/", params={"page": page, "limit": limit})

    async def get_reposts(self, dot_id: str) -> Dict:
        return await self._get(f"/dots/{dot_id}/reposts/")

    async def get_quotes(self, dot_id: str) -> Dict:
        return await self._get(f"/dots/{dot_id}/quotes/")

    async def get_dot_likes(self, dot_id: str) -> Any:
        return await self._get(f"/dots/{dot_id}/likes/")

    async def get_user_dots(self, user_id: str, dot_type: str = "dot,quote,repost", limit: int = 20) -> Dict:
        return await self._get(f"/dots/user/{user_id}/", params={"dot_type": dot_type, "limit": limit})

    async def get_user_replies(self, user_id: str) -> Dict:
        return await self._get(f"/dots/user/{user_id}/", params={"dot_type": "reply"})

    async def get_user_likes(self, user_id: str) -> Dict:
        return await self._get(f"/dots/user/{user_id}/activity/", params={"action_type": "like"})

    async def create_dot(self, content: str, dot_type: str = "dot", reply_to: str = None,
                         repost_of: str = None, quote_of: str = None,
                         media_ids: List[str] = None, reply_permission: str = "everyone") -> Dot:
        body = {k: v for k, v in {
            "dot_type": dot_type, "content": content,
            "reply_to": reply_to, "repost_of": repost_of, "quote_of": quote_of,
            "media_ids": media_ids or [], "reply_permission": reply_permission
        }.items() if v is not None}
        data = await self._post("/dots/", json=body)
        return Dot.from_dict(data)

    async def reply(self, dot_id: str, content: str, media_ids: List[str] = None, reply_permission: str = "everyone") -> Dot:
        return await self.create_dot(content=content, dot_type="reply", reply_to=dot_id, media_ids=media_ids, reply_permission=reply_permission)

    async def repost(self, dot_id: str, media_ids: List[str] = None) -> Dot:
        return await self.create_dot(content="", dot_type="repost", repost_of=dot_id, media_ids=media_ids)

    async def quote(self, dot_id: str, content: str, media_ids: List[str] = None, reply_permission: str = "everyone") -> Dot:
        return await self.create_dot(content=content, dot_type="quote", quote_of=dot_id, media_ids=media_ids, reply_permission=reply_permission)

    async def like(self, dot_id: str) -> bool:
        await self._post(f"/dots/{dot_id}/like/")
        return True

    async def unlike(self, dot_id: str) -> bool:
        await self._delete(f"/dots/{dot_id}/like/")
        return True

    async def bookmark(self, dot_id: str) -> bool:
        await self._post(f"/dots/{dot_id}/bookmark/")
        return True

    async def unbookmark(self, dot_id: str) -> bool:
        await self._delete(f"/dots/{dot_id}/bookmark/")
        return True

    async def edit_dot(self, dot_id: str, content: str) -> Dot:
        data = await self._patch(f"/dots/{dot_id}/", json={"content": content})
        return Dot.from_dict(data)

    async def delete_dot(self, dot_id: str) -> bool:
        await self._delete(f"/dots/{dot_id}/")
        return True

    async def explore_users_suggestions(self, limit: int = 20, cursor: str = None) -> Dict[str, Any]:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._get("/feed/suggestions/follow/", params=params)

    async def get_topic_dots(self, topic_id: str, limit: int = 20, cursor: str = None) -> Dict[str, Any]:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._get(f"/topics/{topic_id}/dots/", params=params)

    async def undo_repost(self, dot_id: str) -> bool:
        await self._delete(f"/posts/{dot_id}/unrepost/")
        return True

    async def get_repost_users(self, dot_id: str, limit: int = 20, cursor: str = None) -> Dict[str, Any]:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._get(f"/posts/{dot_id}/reposts/", params=params)

    async def get_quote_users(self, dot_id: str, limit: int = 20, cursor: str = None) -> Dict[str, Any]:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._get(f"/posts/{dot_id}/quotes/", params=params)

    async def get_reposts_and_quotes(self, dot_id: str, limit: int = 20) -> Dict[str, Any]:
        import asyncio
        reposts, quotes = await asyncio.gather(
            self.get_repost_users(dot_id, limit=limit),
            self.get_quote_users(dot_id, limit=limit)
        )
        return {
            "reposts": reposts.get("results", []),
            "quotes": quotes.get("results", []),
            "reposts_cursor": reposts.get("next"),
            "quotes_cursor": quotes.get("next")
        }

    async def set_reply_permission(self, dot_id: str, permission: str) -> bool:
        valid_permissions = ["everyone", "following", "mentioned", "nobody"]
        if permission not in valid_permissions:
            raise ValueError(f"permission must be one of {valid_permissions}")
        await self._patch(f"/posts/{dot_id}/permissions/", json={"reply_permission": permission})
        return True

    async def set_audience(self, audience_id: str) -> bool:
        await self._post("/posts/audience/", json={"audience_id": audience_id})
        return True

    async def get_composer_state(self) -> Dict[str, Any]:
        return await self._get("/composer/state/")

    async def reset_composer(self) -> bool:
        await self._post("/composer/reset/")
        return True

    async def add_thread(self, content: str = "", media_ids: List[str] = None) -> Dict[str, Any]:
        body = {"content": content}
        if media_ids:
            body["media_ids"] = media_ids
        return await self._post("/composer/thread/", json=body)

    async def remove_thread(self, index: int) -> bool:
        await self._delete(f"/composer/thread/{index}/")
        return True

    async def create_threads(self, post_id: str, threads_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post(f"/posts/{post_id}/threads/", json=threads_data)

    async def get_threads(self, post_id: str) -> Dict[str, Any]:
        return await self._get(f"/posts/{post_id}/threads/")

    async def get_threads_by_url(self, url: str) -> Dict[str, Any]:
        return await self._get(url)

    async def get_threads_view(self, post_id: str) -> Dict[str, Any]:
        return await self._get(f"/posts/{post_id}/threads/view/")

    async def create_wallet(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("/wallet/create/", json=data)

    async def get_wallet_list(self) -> List[Dict[str, Any]]:
        data = await self._get("/wallet/list/")
        return data.get("results", []) if isinstance(data, dict) else data

    async def get_transaction_list(self, wallet_id: str) -> List[Dict[str, Any]]:
        data = await self._get(f"/wallet/transactions/{wallet_id}/")
        return data.get("results", []) if isinstance(data, dict) else data

    async def get_wallet_by_id(self, wallet_id: str) -> Dict[str, Any]:
        return await self._get(f"/wallet/{wallet_id}/")

    async def toggle_wallet_default(self, wallet_id: str) -> None:
        await self._post(f"/wallet/toggle/{wallet_id}/")