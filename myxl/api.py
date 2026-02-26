import requests
import json
import time
from .config import BASE_API_URL, BASE_CIAM_URL, API_KEY, AX_FP_KEY, UA
from .auth import load_token, save_token
from .utils import generate_signature, generate_circle_id

def refresh_token():
    """
    Memperbarui accessToken menggunakan refreshToken.
    Mengembalikan accessToken baru jika berhasil, None jika gagal.
    """
    token_data = load_token()
    if not token_data or "refreshToken" not in token_data:
        return None
    refresh_token = token_data["refreshToken"]
    payload = {"refreshToken": refresh_token}
    timestamp = str(int(time.time() * 1000))
    body_str = json.dumps(payload, separators=(',', ':'))
    path = "/ciam/auth/refresh"
    signature = generate_signature("POST", path, body_str, timestamp)

    headers = {
        "User-Agent": UA,
        "x-api-key": API_KEY,
        "ax-fp-key": AX_FP_KEY,
        "ax-api-sig": signature,
        "x-timestamp": timestamp,
        "Content-Type": "application/json"
    }
    url = f"{BASE_CIAM_URL}{path}"
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        new_access = data.get("accessToken")
        if new_access:
            token_data["accessToken"] = new_access
            save_token(token_data)
            return new_access
    return None

def api_request(method: str, endpoint: str, data=None, params=None, retry=True):
    """
    Melakukan request ke API myXL dengan header lengkap.
    Jika mendapat 401, akan mencoba refresh token sekali.
    """
    token_data = load_token()
    if not token_data:
        raise Exception("Anda belum login. Jalankan 'myxl login' terlebih dahulu.")

    access_token = token_data.get("accessToken")
    msisdn = token_data.get("msisdn")
    device_id = token_data.get("deviceId")

    timestamp = str(int(time.time() * 1000))
    body_str = json.dumps(data, separators=(',', ':')) if data else ""
    signature = generate_signature(method.upper(), endpoint, body_str, timestamp)

    headers = {
        "User-Agent": UA,
        "x-api-key": API_KEY,
        "ax-fp-key": AX_FP_KEY,
        "ax-api-sig": signature,
        "x-timestamp": timestamp,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    if msisdn:
        headers["x-msisdn"] = msisdn
        circle_id = generate_circle_id(msisdn)
        if circle_id:
            headers["x-circle-id"] = circle_id
    if device_id:
        headers["x-device-id"] = device_id   # Mungkin diperlukan

    url = f"{BASE_API_URL}{endpoint}"
    resp = requests.request(method, url, headers=headers, json=data, params=params)

    if resp.status_code == 401 and retry:
        new_token = refresh_token()
        if new_token:
            # Coba lagi sekali dengan token baru
            return api_request(method, endpoint, data, params, retry=False)
        else:
            raise Exception("Sesi habis dan gagal memperbarui token. Silakan login ulang.")

    resp.raise_for_status()
    return resp.json()
