#!/usr/bin/env python3
"""
MCP HTTP-to-STDIO Proxy for Claude Code - Simple curl-based implementation

Usage:
    MCP_PROXY_URL=http://localhost:8000/mcp P9I_API_KEY=xxx python3 mcp_proxy_simple.py

Claude Code will communicate with this script via stdin/stdout JSON-RPC.
"""

import os
import sys
import json
import urllib.request
import urllib.error


def main():
    """Run proxy - read JSON-RPC from stdin, forward to HTTP MCP, write response to stdout."""
    url = os.getenv("MCP_PROXY_URL", "http://localhost:8000/mcp")
    auth = os.getenv("P9I_API_KEY", "")

    print(f"MCP Proxy: {url}", file=sys.stderr, flush=True)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    if auth:
        headers["X-API-Key"] = auth
        print(f"Auth: configured", file=sys.stderr, flush=True)

    # Session tracking
    session_id = None

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            line = line.strip()
            if not line:
                continue

            # Parse request
            try:
                req = json.loads(line)
                method = req.get("method", "")
                req_id = req.get("id")
            except json.JSONDecodeError as e:
                error = json.dumps({"jsonrpc": "2.0", "id": None,
                                   "error": {"code": -32700, "message": f"Parse error: {e}"}})
                print(error, flush=True)
                continue

            # Add session header if we have one
            req_headers = headers.copy()
            if session_id:
                req_headers["Mcp-Session-Id"] = session_id

            # Send to MCP server
            try:
                data = line.encode("utf-8")
                request = urllib.request.Request(url, data=data, headers=req_headers, method="POST")

                with urllib.request.urlopen(request, timeout=60) as response:
                    # Extract session ID from response headers
                    new_session = response.getheader("Mcp-Session-Id")
                    if new_session and not session_id:
                        session_id = new_session
                        print(f"Session: {session_id}", file=sys.stderr, flush=True)

                    body = response.read().decode("utf-8")

                    # Parse SSE response if present
                    for l in body.split("\n"):
                        if l.startswith("data: "):
                            print(l[6:], flush=True)
                            break
                    else:
                        # No SSE, just print the body
                        print(body, flush=True)

            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8")
                # Try to extract JSON from error response
                try:
                    error_json = json.loads(error_body)
                    print(json.dumps(error_json), flush=True)
                except:
                    error = json.dumps({"jsonrpc": "2.0", "id": req_id,
                                       "error": {"code": e.code, "message": error_body}})
                    print(error, flush=True)
            except urllib.error.URLError as e:
                error = json.dumps({"jsonrpc": "2.0", "id": req_id,
                                   "error": {"code": -32603, "message": f"Connection error: {e.reason}"}})
                print(error, flush=True)
            except Exception as e:
                error = json.dumps({"jsonrpc": "2.0", "id": req_id,
                                   "error": {"code": -32603, "message": str(e)}})
                print(error, flush=True)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr, flush=True)
            break


if __name__ == "__main__":
    main()