# ==========================================
# aiodot/__init__.py
# ==========================================

"""
aiodot - Python client for MyDot.one social platform.
Build bots, automation, and tools with ease.

License: MIT
Version: 1.0.0

Usage:
    from aiodot import MyDotClient

    client = MyDotClient(token="your_token")
    me = client.me
    dot = client.create_dot("Hello from aiodot!")
"""

from .client import MyDotClient
from .auth import MyDotAuth, Session
from .models import Dot, User, ThreadView, Notification, PaginatedResponse
from .wallet import WalletManager
from .models import Dot, User, ThreadView, Notification, PaginatedResponse, Thread, ReplyPermission

__version__ = "1.2.0"
__license__ = "MIT"
__all__ = [
    "MyDotClient",
    "MyDotAuth",
    "Session",
    "Dot",
    "User",
    "ThreadView",
    "Notification",
    "PaginatedResponse",
    "WalletManager",   
]