#!/usr/bin/env python3
"""
MCP HTTP-to-STDIO Proxy for Claude Code - Streaming SSE support

Usage:
    MCP_PROXY_URL=http://localhost:8000/mcp P9I_API_KEY=xxx python3 mcp_proxy_simple.py

Claude Code will communicate with this script via stdin/stdout JSON-RPC.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import threading


def stream_response(response, session_store):
    """Stream SSE response line by line to stdout."""
    session_id = session_store.get("id")

    # Extract session ID from headers
    new_session = response.getheader("Mcp-Session-Id")
    if new_session and not session_id:
        session_store["id"] = new_session
        print(f"Session: {new_session}", file=sys.stderr, flush=True)

    # Read and forward streaming data
    for line in response:
        line = line.decode("utf-8").strip()
        if line.startswith("data: "):
            print(line[6:], flush=True)
        elif line.startswith("event: "):
            # Forward event line
            print(line, flush=True)


def main():
    """Run proxy - read JSON-RPC from stdin, forward to HTTP MCP, write response to stdout."""
    url = os.getenv("MCP_PROXY_URL", "http://localhost:8000/mcp")
    api_key = os.getenv("P9I_API_KEY", "")

    print(f"MCP Proxy: {url}", file=sys.stderr, flush=True)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"  # Both required by MCP server
    }
    if api_key:
        headers["X-API-Key"] = api_key
        print(f"Auth: configured", file=sys.stderr, flush=True)

    # Session tracking (stored in dict for thread safety)
    session_store = {"id": None}

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
            if session_store["id"]:
                req_headers["Mcp-Session-Id"] = session_store["id"]

            # Send to MCP server
            try:
                data = line.encode("utf-8")
                request = urllib.request.Request(url, data=data, headers=req_headers, method="POST")

                # Use longer timeout for long-running requests
                timeout = int(os.getenv("MCP_PROXY_TIMEOUT", "120"))
                response = urllib.request.urlopen(request, timeout=timeout)

                # Stream the response
                stream_response(response, session_store)

            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8")
                # Try to extract JSON from error response
                try:
                    error_json = json.loads(error_body)
                    print(json.dumps(error_json), flush=True)
                except:
                    error = json.dumps({"jsonrpc": "2.0", "id": req_id,
                                       "error": {"code": e.code, "message": error_body[:500]}})
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