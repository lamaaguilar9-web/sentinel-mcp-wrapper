# Sentinel Fleet — MCP Wrapper (MIT)

Lightweight public Model Context Protocol (MCP) wrapper for [Sentinel Fleet Technologies](https://sentinelfleet.tech) DeFi security tools on Base Mainnet, ready for **Apify** and **MCPize** autodeploy.

## Environment Variables
- `SENTINEL_GATEWAY_URL` (default: `https://api.sentinelfleet.tech`)
- `SENTINEL_API_KEY` (required secret in Apify / MCPize when platform handles billing, sent as `Authorization: Bearer <key>`)

## Tools Exposed
1. `invariant_shield_scan`
2. `oracle_divergence_circuit_breaker`
3. `forensic_risk_scoring`
4. `dex_burst_volume_detector`
