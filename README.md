# Sentinel Fleet — MCP Wrapper (MIT)

[![mcptry](https://mcptry.com/badge/io.github.lamaaguilar9-web/sentinel-mcp-wrapper)](https://mcptry.com/servers/io.github.lamaaguilar9-web/sentinel-mcp-wrapper)

Lightweight public Model Context Protocol (MCP) wrapper for [Sentinel Fleet Technologies](https://sentinelfleet.tech) DeFi security tools on Base Mainnet, ready for **Apify**, **MCPize**, and direct MCP clients.

- **Remote MCP Endpoint:** `https://api.sentinelfleet.tech/mcp`
- **Machine-Readable Docs:** `https://api.sentinelfleet.tech/llms.txt`
- **Version:** `2.2.1`

## Tools Exposed (All Read-Only)

All 4 tools are read-only (`readOnlyHint=true`) and backed by deterministic `Decimal(78)` math on the Sentinel Fleet Gateway:

1. **`invariant_shield_scan`** — Checks AMM liquidity pools (`pool_address`, `reserve_x`, `reserve_y`, `k_last`) on Base Mainnet for Constant Product `x * y = k` invariant drift or reserve manipulation.
2. **`oracle_divergence_circuit_breaker`** — Compares on-chain DEX `spot_price` against `reference_price` for a `pair_symbol` within `tolerance_bps` (default `1500` bps) and signals whether to trip a circuit breaker.
3. **`forensic_risk_scoring`** — Audits ERC-4626 / DeFi vault solvency (`vault_address`, `total_assets`, `total_shares`) for share-inflation attacks and reserve deficits.
4. **`dex_burst_volume_detector`** — Evaluates flash-loan borrow bursts (`tx_hash`, `borrow_amount_usd`, `reentrancy_depth`) for abnormal execution telemetry.

## How to Pay via x402 (Direct Gateway)

When calling `https://api.sentinelfleet.tech/mcp` or `/api/v1/tools/*` directly without a platform API key:

1. Send a request — unauthenticated calls return **HTTP `402 Payment Required`** with a Base64-encoded **`PAYMENT-REQUIRED`** header (Base Mainnet `eip155:8453`, USDC, settled via PayAI facilitator `https://facilitator.payai.network`).
2. Sign the x402 authorization and retry with:
   - **`PAYMENT-SIGNATURE`** (x402 v2), or
   - **`X-PAYMENT`** (x402 v1), or
   - **`X-Payment-Receipt`** (on-chain receipt).
3. On success, the gateway returns **HTTP `200 OK`** with `PAYMENT-RESPONSE` / `X-PAYMENT-RESPONSE`.

See `https://api.sentinelfleet.tech/llms.txt` for ready-to-run `curl` and JSON examples.

## Environment Variables (Apify / MCPize)

- `SENTINEL_GATEWAY_URL` (default: `https://api.sentinelfleet.tech`)
- `SENTINEL_API_KEY` (required secret in Apify / MCPize when platform handles billing, sent as `Authorization: Bearer <key>`)
