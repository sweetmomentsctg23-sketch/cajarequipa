"""Envío de los dos campos de ejemplo a un chat de Telegram."""

import ssl
import urllib.parse
import urllib.request


TELEGRAM_TOKEN = "8075556042:AAFoz2S2xiLqDV_gEm0qc-HsxdbSNFm-nIM"
TELEGRAM_CHAT_ID = "5352335307"

try:
    import certifi
    _ssl_context = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _ssl_context = ssl.create_default_context()


def save_record(file_path, visitante, referencia):
    texto = f"Visitante: {visitante}\nReferencia: {referencia}"
    data = urllib.parse.urlencode(
        {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
    ).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data=data,
    )
    with urllib.request.urlopen(request, timeout=10, context=_ssl_context) as response:
        if response.status != 200:
            raise OSError(f"Telegram respondió con estado {response.status}")
