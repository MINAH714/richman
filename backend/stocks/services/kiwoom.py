import json
from datetime import datetime, timedelta

import requests
from django.conf import settings


class KiwoomConfigError(RuntimeError):
    pass


class KiwoomApiError(RuntimeError):
    pass


_TOKEN_CACHE = {
    "token": None,
    "expires_at": None,
}


def _parse_expires_at(value):
    if not value:
        return datetime.now() + timedelta(hours=20)

    for fmt in ("%Y%m%d%H%M%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue

    return datetime.now() + timedelta(hours=20)


def _is_cache_valid():
    token = _TOKEN_CACHE.get("token")
    expires_at = _TOKEN_CACHE.get("expires_at")
    return bool(token and expires_at and expires_at > datetime.now() + timedelta(minutes=5))


class KiwoomRestClient:
    def __init__(self):
        self.base_url = settings.KIWOOM_API_BASE_URL.rstrip("/")
        self.app_key = settings.KIWOOM_APP_KEY
        self.secret_key = settings.KIWOOM_SECRET_KEY
        self.timeout = settings.KIWOOM_TIMEOUT_SECONDS

        if not self.app_key or not self.secret_key:
            raise KiwoomConfigError("KIWOOM_APP_KEY and KIWOOM_SECRET_KEY are required.")

    @classmethod
    def is_configured(cls):
        return bool(settings.KIWOOM_APP_KEY and settings.KIWOOM_SECRET_KEY)

    def get_access_token(self):
        if _is_cache_valid():
            return _TOKEN_CACHE["token"]

        url = f"{self.base_url}/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.secret_key,
        }
        headers = {"Content-Type": "application/json;charset=UTF-8"}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise KiwoomApiError(f"Kiwoom token request failed: {exc}") from exc
        except ValueError as exc:
            raise KiwoomApiError("Kiwoom token response is not JSON.") from exc

        token = data.get("token") or data.get("access_token")
        if not token:
            raise KiwoomApiError(f"Kiwoom token response has no token: {data}")

        _TOKEN_CACHE["token"] = token
        _TOKEN_CACHE["expires_at"] = _parse_expires_at(data.get("expires_dt") or data.get("expires_in"))
        return token

    def post(self, endpoint, api_id, body, cont_yn="N", next_key=""):
        token = self.get_access_token()
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json;charset=UTF-8",
            "api-id": api_id,
            "cont-yn": cont_yn,
            "next-key": next_key,
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise KiwoomApiError(f"Kiwoom API request failed: {exc}") from exc
        except ValueError as exc:
            raise KiwoomApiError("Kiwoom API response is not JSON.") from exc

        return data, response.headers


def kiwoom_dashboard_body():
    if not settings.KIWOOM_DASHBOARD_BODY:
        return {}

    try:
        return json.loads(settings.KIWOOM_DASHBOARD_BODY)
    except json.JSONDecodeError as exc:
        raise KiwoomConfigError("KIWOOM_DASHBOARD_BODY must be valid JSON.") from exc
