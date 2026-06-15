"""Pytest configuration for the iApp AI SDK test suite.

Live integration tests (files named ``test_live_*``) hit the real
``api.iapp.co.th`` and need a valid ``IAPP_API_KEY``. They are skipped
automatically when the key is not set, so the offline suite stays green in CI.
"""

import os
import json
import pytest
import requests
import iapp_ai.module_api as module_api


def pytest_collection_modifyitems(config, items):
    if os.environ.get("IAPP_API_KEY"):
        return
    skip_live = pytest.mark.skip(
        reason="live integration test — set IAPP_API_KEY to run"
    )
    for item in items:
        if "test_live_" in os.path.basename(str(item.fspath)):
            item.add_marker(skip_live)


@pytest.fixture
def mock_sdk_request(monkeypatch):
    """Replace request_sync with a mock recorder that returns configurable responses."""
    calls = []
    response_data = {"status_code": 200, "json_payload": {"status": "success", "taskGuid": "test-guid-12345"}}

    def fake_request_sync(
        method,
        url,
        *,
        apikey,
        headers=None,
        params=None,
        data=None,
        json_body=None,
        files=None,
        raise_for_error=False,
        timeout=None,
    ):
        # Close open file handles to prevent ResourceWarnings
        for item in files or []:
            if isinstance(item[1], (list, tuple)) and len(item[1]) > 1:
                handle = item[1][1]
                if hasattr(handle, "close"):
                    handle.close()
        
        calls.append({
            "method": method,
            "url": url,
            "apikey": apikey,
            "headers": headers,
            "params": params,
            "data": data,
            "json_body": json_body,
            "files": files,
            "raise_for_error": raise_for_error,
            "timeout": timeout,
        })
        
        resp = requests.Response()
        resp.status_code = response_data["status_code"]
        resp._content = json.dumps(response_data["json_payload"]).encode("utf-8")
        resp.url = url
        return resp

    monkeypatch.setattr(module_api, "request_sync", fake_request_sync)
    return {"calls": calls, "response_data": response_data}
