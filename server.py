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
from mcp.types import ToolAnnotations
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

GATEWAY_URL = os.environ.get("SENTINEL_GATEWAY_URL", "https://api.sentinelfleet.tech").rstrip("/")
API_KEY = os.environ.get("SENTINEL_API_KEY", "").strip()
PORT = int(os.environ.get("APIFY_CONTAINER_PORT") or os.environ.get("PORT") or "8080")

READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)

mcp = FastMCP(
    "sentinel-fleet-defi-mcp",
    stateless_http=True,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


async def _call_gateway(tool_name: str, payload: Dict[str, Any]) -> str:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "SentinelFleet-MCP-Wrapper/2.2.1",
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


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS)
async def invariant_shield_scan(
    pool_address: str,
    reserve_x: float,
    reserve_y: float,
    k_last: Optional[float] = 0.0,
) -> str:
    """Read-only AMM liquidity pool invariant check on Base Mainnet.

    Use when auditing Uniswap-style x*y=k pools for reserve manipulation or invariant drift.
    Provide pool_address (0x...), reserve_x, reserve_y, and optional prior k_last.
    Returns deterministic Decimal(78) invariant ratio, drift percentage, and risk verdict.
    """
    return await _call_gateway(
        "invariant_shield_scan",
        {
            "pool_address": pool_address,
            "reserve_x": reserve_x,
            "reserve_y": reserve_y,
            "k_last": k_last or 0.0,
        },
    )


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS)
async def oracle_divergence_circuit_breaker(
    pair_symbol: str,
    spot_price: float,
    reference_price: float,
    tolerance_bps: int = 1500,
) -> str:
    """Read-only oracle vs. on-chain DEX spot price divergence circuit breaker.

    Use before swaps, liquidations, or vault rebalances to detect oracle manipulation or stale feeds.
    Provide pair_symbol (e.g. 'ETH/USDC'), spot_price, reference_price, and tolerance_bps (default 1500 = 15%).
    Returns divergence in bps and whether the circuit breaker should trip.
    """
    return await _call_gateway(
        "oracle_divergence_circuit_breaker",
        {
            "pair_symbol": pair_symbol,
            "spot_price": spot_price,
            "reference_price": reference_price,
            "tolerance_bps": tolerance_bps,
        },
    )


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS)
async def forensic_risk_scoring(
    vault_address: str,
    total_assets: float,
    total_shares: float,
) -> str:
    """Read-only ERC-4626 and DeFi vault solvency and share-inflation forensic scorer.

    Use when evaluating vault deposits/withdrawals for first-depositor inflation or reserve deficit.
    Provide vault_address (0x...), total_assets, and total_shares.
    Returns share-to-asset ratio, anomaly flags, and deterministic forensic risk score.
    """
    return await _call_gateway(
        "forensic_risk_scoring",
        {
            "vault_address": vault_address,
            "total_assets": total_assets,
            "total_shares": total_shares,
        },
    )


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS)
async def dex_burst_volume_detector(
    tx_hash: str,
    borrow_amount_usd: float,
    reentrancy_depth: int = 1,
) -> str:
    """Read-only flash-loan burst and reentrancy depth telemetry analyzer on Base Mainnet.

    Use when inspecting suspicious transactions for flash-loan-backed price attacks or deep reentrancy.
    Provide tx_hash (0x...), borrow_amount_usd, and reentrancy_depth (default 1).
    Returns burst severity classification and recommended defensive action.
    """
    return await _call_gateway(
        "dex_burst_volume_detector",
        {
            "tx_hash": tx_hash,
            "borrow_amount_usd": borrow_amount_usd,
            "reentrancy_depth": reentrancy_depth,
        },
    )


async def health(_request):
    return JSONResponse({"status": "UP", "service": "sentinel-mcp-wrapper", "version": "2.2.1", "upstream": GATEWAY_URL})


app = mcp.streamable_http_app()
app.routes.insert(0, Route("/health", health, methods=["GET"]))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
