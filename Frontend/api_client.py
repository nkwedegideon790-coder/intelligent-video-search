from __future__ import annotations

import os
from typing import Any, Optional

import requests


class APIError(Exception):
    def __init__(self, message: str, code: str | None = None, status: int | None = None):
        super().__init__(message)
        self.message, self.code, self.status = message, code, status


def _secret(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(name, default))
    except Exception:
        return default


def base_url() -> str:
    return _secret("INTELLIGENT_VIDEO_SEARCH_URL", "http://localhost:8000").rstrip("/")




def _request(method: str, path: str, *, timeout: float = 20, **kwargs: Any) -> Any:
    try:
        resp = requests.request(method, base_url() + path, timeout=timeout, **kwargs)
    except requests.exceptions.Timeout as exc:
        raise APIError("The request took too long. Please try again.", "timeout") from exc
    except requests.exceptions.RequestException as exc:
        raise APIError("We can't reach the ScamLens service right now. Check that the backend is running.",
                       "unreachable") from exc
    if resp.status_code >= 400:
        try:
            body = resp.json()
            raise APIError(body.get("detail") or "Something went wrong.", body.get("code"), resp.status_code)
        except ValueError:
            raise APIError("Something went wrong. Please try again.", None, resp.status_code)
    try:
        return resp.json()
    except ValueError as exc:
        raise APIError("The service returned an unreadable response.", None, resp.status_code) from exc

def health() -> dict:
    return _request("GET", "/health", timeout=6)

def stats() -> dict[str, Any]:
    return _request("GET", "/status")

def tracklogs() -> dict:
    return _request("GET", "/track_logs")

def upload_video(file):
    return _request("POST", "/upload_video", timeout=60, files={"file": (file.name, file.getvalue(), file.type)})

def process_video():
    return _request("POST", "/videos/latest/process" )