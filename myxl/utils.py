import hmac
import hashlib
import json
import time
import base64
from Crypto.Cipher import AES
from .config import AX_API_SIG_KEY, CIRCLE_MSISDN_KEY

def generate_signature(method: str, path: str, body: str, timestamp: str) -> str:
    """
    Menghasilkan header ax-api-sig menggunakan HMAC-SHA256.
    - method: HTTP method (GET, POST, dll)
    - path: endpoint path (contoh: /ciam/auth/login)
    - body: string JSON dari payload (kosong jika tidak ada)
    - timestamp: millisecond timestamp
    """
    message = f"{method}:{path}:{body}:{timestamp}"
    key = AX_API_SIG_KEY.encode()
    return hmac.new(key, message.encode(), hashlib.sha256).hexdigest()

def generate_circle_id(msisdn: str) -> str | None:
    """
    Menghasilkan x-circle-id dengan mengenkripsi MSISDN menggunakan AES-ECB.
    Kunci diambil dari CIRCLE_MSISDN_KEY (hex string).
    """
    if not CIRCLE_MSISDN_KEY or not msisdn:
        return None
    try:
        key = bytes.fromhex(CIRCLE_MSISDN_KEY)
        cipher = AES.new(key, AES.MODE_ECB)

        # Padding PKCS7
        pad_len = 16 - (len(msisdn) % 16)
        padded = msisdn.encode() + bytes([pad_len] * pad_len)

        encrypted = cipher.encrypt(padded)
        return base64.b64encode(encrypted).decode()
    except Exception:
        # Jika gagal, kembalikan None (mungkin header tidak dibutuhkan)
        return None
