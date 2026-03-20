from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class ApiClientError(RuntimeError):
    """Raised when the Streamlit UI cannot complete an API request."""


@dataclass
class ApiClient:
    base_url: str
    timeout: int = 10

    def _build_url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        try:
            response = requests.request(
                method=method,
                url=self._build_url(path),
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ApiClientError(str(exc)) from exc

        if not response.content:
            return None
        return response.json()

    def create_keyword(self, name: str) -> dict[str, Any]:
        return self._request('POST', '/keywords/', {'name': name})

    def trigger_scan(self, dataset_path: str | None = None) -> dict[str, Any]:
        payload = {'dataset_path': dataset_path} if dataset_path else {}
        return self._request('POST', '/scan/', payload)

    def list_flags(self) -> list[dict[str, Any]]:
        return self._request('GET', '/flags/')

    def update_flag_status(self, flag_id: int, status: str) -> dict[str, Any]:
        return self._request('PATCH', f'/flags/{flag_id}/', {'status': status})
