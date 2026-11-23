#!/usr/bin/env python3
"""
Sentinel Fleet Technologies — Lightweight Public MCP Wrapper (MIT)
Proxies MCP tool calls to https://api.sentinelfleet.tech using platform
Bearer authentication (SENTINEL_API_KEY) for Apify & MCPize deployments.
"""

import json
import os
from typing import Any, Dict, Optional

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

GATEWAY_URL = os.environ.get("SENTINEL_GATEWAY_URL", "https://api.sentinelfleet.tech").rstrip("/")
API_KEY = os.environ.get("SENTINEL_API_KEY", "").strip()
PORT = int(os.environ.get("APIFY_CONTAINER_PORT") or os.environ.get("PORT") or "8080")

mcp = FastMCP(
    "sentinel-fleet-defi-mcp",
    stateless_http=True,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


async def _call_gateway(tool_name: str, payload: Dict[str, Any]) -> str:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "SentinelFleet-MCP-Wrapper/1.0",
    }
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    url = f"{GATEWAY_URL}/api/v1/tools/{tool_name}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 402:
            return json.dumps({
                "error": "Upstream HTTP 402 Payment Required",
                "hint": "Set SENTINEL_API_KEY in platform environment variables for pre-paid/platform-billed access.",
                "details": resp.json(),
            }, indent=2)
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)


@mcp.tool()
async def invariant_shield_scan(
    pool_address: str,
    reserve_x: float,
    reserve_y: float,
    k_last: Optional[float] = 0.0,
) -> str:
    """Scans AMM liquidity pools on Base Mainnet to verify Constant Product invariant k = x * y."""
    return await _call_gateway(
        "invariant_shield_scan",
        {
            "pool_address": pool_address,
            "reserve_x": reserve_x,
            "reserve_y": reserve_y,
            "k_last": k_last or 0.0,
        },
    )


@mcp.tool()
async def oracle_divergence_circuit_breaker(
    pair_symbol: str,
    spot_price: float,
    reference_price: float,
    tolerance_bps: int = 1500,
) -> str:
    """Evaluates price divergence between on-chain spot DEX pool prices and reference oracle feeds."""
    return await _call_gateway(
        "oracle_divergence_circuit_breaker",
        {
            "pair_symbol": pair_symbol,
            "spot_price": spot_price,
            "reference_price": reference_price,
            "tolerance_bps": tolerance_bps,
        },
    )


@mcp.tool()
async def forensic_risk_scoring(
    vault_address: str,
    total_assets: float,
    total_shares: float,
) -> str:
    """Evaluates ERC-4626 / DeFi vault reserve solvency and share-inflation risk."""
    return await _call_gateway(
        "forensic_risk_scoring",
        {
            "vault_address": vault_address,
            "total_assets": total_assets,
            "total_shares": total_shares,
        },
    )


@mcp.tool()
async def dex_burst_volume_detector(
    tx_hash: str,
    borrow_amount_usd: float,
    reentrancy_depth: int = 1,
) -> str:
    """Analyzes flashloan borrow bursts and reentrancy depth telemetry on Base Mainnet."""
    return await _call_gateway(
        "dex_burst_volume_detector",
        {
            "tx_hash": tx_hash,
            "borrow_amount_usd": borrow_amount_usd,
            "reentrancy_depth": reentrancy_depth,
        },
    )


async def health(_request):
    return JSONResponse({"status": "UP", "service": "sentinel-mcp-wrapper", "upstream": GATEWAY_URL})


app = mcp.streamable_http_app()
app.routes.insert(0, Route("/health", health, methods=["GET"]))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
