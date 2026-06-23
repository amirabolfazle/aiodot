# ==========================================
# aiodot/wallet.py
# ==========================================

"""Wallet management module for MyDot.one."""

from typing import Dict, List, Any


class WalletManager:
    """Manage user wallets on MyDot.one."""

    def __init__(self, client):
        self.client = client

    async def create_wallet(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new wallet."""
        return await self.client._post("/wallet/create/", json=data)

    async def get_wallet_list(self) -> List[Dict[str, Any]]:
        """Get list of all wallets."""
        return await self.client._get("/wallet/list/")

    async def get_transactions(self, wallet_id: str) -> List[Dict[str, Any]]:
        """Get transactions for a specific wallet."""
        return await self.client._get(f"/wallet/transactions/{wallet_id}/")

    async def get_wallet_by_id(self, wallet_id: str) -> Dict[str, Any]:
        """Get wallet details by ID."""
        return await self.client._get(f"/wallet/{wallet_id}/")

    async def toggle_default_wallet(self, wallet_id: str) -> None:
        """Toggle a wallet as default."""
        await self.client._post(f"/wallet/toggle/{wallet_id}/", json={})