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
import ssl
import urllib.request
import urllib.error
import threading
import time


def create_ssl_context():
    """Create SSL context that bypasses certificate verification for HTTPS proxy."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def urlopen_with_ssl(request, timeout=None):
    """Make HTTP request with SSL bypass for HTTPS URLs."""
    if request.full_url.startswith("https://"):
        ctx = create_ssl_context()
        return urllib.request.urlopen(request, timeout=timeout, context=ctx)
    return urllib.request.urlopen(request, timeout=timeout)


def stream_response(response, session_store):
    """Stream SSE response line by line to stdout."""
    session_id = session_store.get("id")

    # Extract session ID from headers
    new_session = response.getheader("Mcp-Session-Id")
    if new_session and not session_id:
        session_store["id"] = new_session
        print(f"[PROXY] Session stored: {new_session}", file=sys.stderr, flush=True)

    print(f"[PROXY] Starting response stream", file=sys.stderr, flush=True)

    # Read and forward streaming data
    line_count = 0
    for line in response:
        line = line.decode("utf-8").strip()
        line_count += 1
        if line_count % 5 == 0:
            print(f"[PROXY] Read line {line_count}", file=sys.stderr, flush=True)

        if line.startswith("data: "):
            data_content = line[6:]
            print(data_content, flush=True)
        elif line.startswith("event: "):
            # Forward event line
            print(line, flush=True)

    print(f"[PROXY] Response complete, {line_count} lines", file=sys.stderr, flush=True)


def main():
    """Run proxy - read JSON-RPC from stdin, forward to HTTP MCP, write response to stdout."""
    url = os.getenv("MCP_PROXY_URL", "http://localhost:8000/mcp")
    api_key = os.getenv("P9I_API_KEY", "")

    # Extract base URL (without /mcp path) for initialize request
    base_url = url.rsplit("/mcp", 1)[0] if "/mcp" in url else url.rsplit("/", 1)[0]
    init_url = base_url if base_url else "http://localhost:8000"
    if not init_url.startswith("http"):
        init_url = "http://" + init_url

    print(f"MCP Proxy: {url}", file=sys.stderr, flush=True)
    print(f"Init URL: {init_url}", file=sys.stderr, flush=True)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"  # Both required by MCP server
    }
    if api_key:
        headers["X-API-Key"] = api_key
        print(f"Auth: configured", file=sys.stderr, flush=True)

    # Session tracking (stored in dict for thread safety)
    session_store = {"id": None}
    initialized = False

    while True:
        try:
            print("[PROXY] Waiting for request...", file=sys.stderr, flush=True)
            line = sys.stdin.readline()
            if not line:
                print("[PROXY] EOF received, exiting", file=sys.stderr, flush=True)
                break

            line = line.strip()
            if not line:
                continue

            # Parse request
            try:
                req = json.loads(line)
                method = req.get("method", "")
                req_id = req.get("id")
                print(f"[PROXY] Got request: {method}, id={req_id}", file=sys.stderr, flush=True)
            except json.JSONDecodeError as e:
                error = json.dumps({"jsonrpc": "2.0", "id": None,
                                   "error": {"code": -32700, "message": f"Parse error: {e}"}})
                print(error, flush=True)
                continue

            # For first request, MUST call initialize to get session
            if not initialized and method != "initialize":
                print("[PROXY] First request - calling initialize to get session...", file=sys.stderr, flush=True)
                init_req = json.dumps({
                    "jsonrpc": "2.0",
                    "id": 0,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "claude-code", "version": "1.0"}
                    }
                })

                req_headers = headers.copy()
                # CRITICAL: Don't set session header at all for initialize request
                # The server will create a new session if header is missing/empty
                if "Mcp-Session-Id" in req_headers:
                    del req_headers["Mcp-Session-Id"]
                # Force fresh connection by not using keep-alive
                req_headers["Connection"] = "close"

                try:
                    init_data = init_req.encode("utf-8")
                    # Use the same /mcp endpoint for initialize
                    init_request = urllib.request.Request(url, data=init_data, headers=req_headers, method="POST")
                    timeout = int(os.getenv("MCP_PROXY_TIMEOUT", "300"))
                    print(f"[PROXY] Calling initialize at {url}...", file=sys.stderr, flush=True)
                    init_response = urlopen_with_ssl(init_request, timeout=timeout)

                    # Get session from headers FIRST
                    new_session = init_response.getheader("Mcp-Session-Id")
                    if new_session:
                        session_store["id"] = new_session
                        print(f"[PROXY] Session obtained: {new_session}", file=sys.stderr, flush=True)
                        initialized = True

                    # CRITICAL: Read/drain the ENTIRE response body before making next request
                    # This is required by HTTP/1.1 to reuse the connection
                    print(f"[PROXY] Draining initialize response...", file=sys.stderr, flush=True)
                    init_response.read()  # Drain the entire body
                    print(f"[PROXY] Response drained", file=sys.stderr, flush=True)

                except Exception as e:
                    print(f"[PROXY] Initialize failed: {e}", file=sys.stderr, flush=True)

            # Add session header - but NOT for initialize (first) request
            req_headers = headers.copy()
            if method == "initialize":
                # Don't set session header for initialize - server creates new session
                print("[PROXY] Skipping session header for initialize", file=sys.stderr, flush=True)
            elif session_store["id"]:
                req_headers["Mcp-Session-Id"] = session_store["id"]
                print(f"[PROXY] Using session: {session_store['id']}", file=sys.stderr, flush=True)
            else:
                req_headers["Mcp-Session-Id"] = ""
                print("[PROXY] Using empty session", file=sys.stderr, flush=True)

            # Send to MCP server
            try:
                print(f"[PROXY] Sending to {url}...", file=sys.stderr, flush=True)
                # Ensure line is a string before encoding
                if isinstance(line, bytes):
                    data = line
                else:
                    data = line.encode("utf-8")
                request = urllib.request.Request(url, data=data, headers=req_headers, method="POST")

                # Use longer timeout for long-running requests
                timeout = int(os.getenv("MCP_PROXY_TIMEOUT", "300"))
                print(f"[PROXY] Timeout: {timeout}s", file=sys.stderr, flush=True)

                start_time = time.time()
                response = urlopen_with_ssl(request, timeout=timeout)
                elapsed = time.time() - start_time
                print(f"[PROXY] Response received in {elapsed:.1f}s", file=sys.stderr, flush=True)

                # Stream the response
                stream_response(response, session_store)

            except urllib.error.HTTPError as e:
                print(f"[PROXY] HTTP Error: {e.code} - {e.reason}", file=sys.stderr, flush=True)
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
                print(f"[PROXY] URL Error: {e.reason}", file=sys.stderr, flush=True)
                error = json.dumps({"jsonrpc": "2.0", "id": req_id,
                                   "error": {"code": -32603, "message": f"Connection error: {e.reason}"}})
                print(error, flush=True)
            except Exception as e:
                print(f"[PROXY] Exception: {e}", file=sys.stderr, flush=True)
                error = json.dumps({"jsonrpc": "2.0", "id": req_id,
                                   "error": {"code": -32603, "message": str(e)}})
                print(error, flush=True)

        except KeyboardInterrupt:
            print("[PROXY] Interrupted", file=sys.stderr, flush=True)
            break
        except Exception as e:
            print(f"[PROXY] Error: {e}", file=sys.stderr, flush=True)
            break


if __name__ == "__main__":
    main()