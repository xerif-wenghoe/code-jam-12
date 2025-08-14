import base64

from js import document

from .aes import encrypt


async def start() -> None:
    document.title = "Code Jam 12"
    encrypted = encrypt(b"Hello, world!", b"1234567812345678")
    encrypted_b64 = base64.b64encode(encrypted).decode()
    document.body.innerHTML = f"<p>Hello, world! ({encrypted_b64})</p>"
