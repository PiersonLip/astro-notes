"""Better BibTeX JSON-RPC helpers (Zotero must be running)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

BBT_RPC = "http://127.0.0.1:23119/better-bibtex/json-rpc"


def bbt_call(method: str, params: list | str | dict) -> object | None:
    payload = json.dumps(
        {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    ).encode()
    req = urllib.request.Request(
        BBT_RPC,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None
    if data.get("error"):
        return None
    return data.get("result")


def selected_items() -> list[dict]:
    """Return BBT search results for the current Zotero selection."""
    keys = bbt_call("item.citationkey", ["selected"])
    if not keys or not isinstance(keys, dict):
        return []
    citekeys = list(keys.values())
    if not citekeys:
        return []
    items: list[dict] = []
    for ck in citekeys:
        found = bbt_call("item.search", [ck])
        if isinstance(found, list) and found:
            items.append(found[0])
    return items


def selected_citekey_and_title() -> tuple[str, str] | None:
    """First selected library item → (cite_key, title)."""
    items = selected_items()
    if not items:
        return None
    if len(items) > 1:
        print("Note: multiple items selected; using the first.", flush=True)
    item = items[0]
    cite_key = item.get("citation-key") or item.get("citationKey") or ""
    title = item.get("title") or ""
    if not cite_key:
        return None
    return cite_key, title
