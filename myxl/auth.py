import requests
import json
import uuid
import time
from pathlib import Path
from .config import BASE_CIAM_URL, API_KEY, AX_FP_KEY, UA
from .utils import generate_signature, generate_circle_id

TOKEN_FILE = Path.home() / ".myxl" / "token.json"

def ensure_token_dir():
    """Pastikan direktori penyimpanan token ada."""
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

def save_token(data: dict):
    """Simpan token ke file."""
    ensure_token_dir()
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_token() -> dict | None:
    """Baca token dari file, jika ada."""
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return None

def delete_token():
    """Hapus file token."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()

def request_otp(msisdn: str):
    """
    Kirim OTP ke nomor XL.
    Mengembalikan tuple (refId, deviceId)
    """
    device_id = str(uuid.uuid4())
    payload = {
        "msisdn": msisdn,
        "deviceId": device_id,
        "deviceToken": "dummy_fcm_token"   # Bisa disesuaikan jika diperlukan
    }
    timestamp = str(int(time.time() * 1000))
    body_str = json.dumps(payload, separators=(',', ':'))
    path = "/ciam/auth/login"
    signature = generate_signature("POST", path, body_str, timestamp)

    headers = {
        "User-Agent": UA,
        "x-api-key": API_KEY,
        "ax-fp-key": AX_FP_KEY,
        "ax-api-sig": signature,
        "x-timestamp": timestamp,
        "Content-Type": "application/json"
    }
    # Tambahkan x-circle-id jika ada
    circle_id = generate_circle_id(msisdn)
    if circle_id:
        headers["x-circle-id"] = circle_id

    url = f"{BASE_CIAM_URL}{path}"
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    ref_id = data.get("refId")   # Sesuaikan dengan response asli
    return ref_id, device_id

def verify_otp(msisdn: str, otp: str, ref_id: str, device_id: str):
    """
    Verifikasi OTP untuk mendapatkan access token & refresh token.
    Mengembalikan dictionary token.
    """
    payload = {
        "msisdn": msisdn,
        "otp": otp,
        "refId": ref_id,
        "deviceId": device_id
    }
    timestamp = str(int(time.time() * 1000))
    body_str = json.dumps(payload, separators=(',', ':'))
    path = "/ciam/auth/login/verify"
    signature = generate_signature("POST", path, body_str, timestamp)

    headers = {
        "User-Agent": UA,
        "x-api-key": API_KEY,
        "ax-fp-key": AX_FP_KEY,
        "ax-api-sig": signature,
        "x-timestamp": timestamp,
        "Content-Type": "application/json"
    }
    circle_id = generate_circle_id(msisdn)
    if circle_id:
        headers["x-circle-id"] = circle_id

    url = f"{BASE_CIAM_URL}{path}"
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    # Asumsi response: { "accessToken": "...", "refreshToken": "...", "msisdn": "..." }
    return data
