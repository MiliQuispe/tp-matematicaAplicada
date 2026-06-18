import json
import base64
import secrets
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from typing import Dict, Any

# Utilidades de cifrado


def generate_rsa_keypair(
    private_out: str, public_out: str, passphrase: bytes = None, bits: int = 2048
):
    """
    Genera un par de claves RSA:
    - private_out: archivo donde se guarda la clave privada
    - public_out: archivo donde se guarda la clave pública
    - passphrase: cifra la clave privada
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
    enc = (
        serialization.BestAvailableEncryption(passphrase)
        if passphrase
        else serialization.NoEncryption()
    )
    priv_pem = private_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, enc
    )
    pub_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(private_out, "wb") as f:
        f.write(priv_pem)
    with open(public_out, "wb") as f:
        f.write(pub_pem)
    print(f"Claves generadas: privada -> {private_out}, pública -> {public_out}")


def load_public_key(pem_path: str):
    # Carga la clave pública desde un archivo PEM
    with open(pem_path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def load_private_key(pem_path: str, passphrase: bytes = None):
    # Carga la clave privada desde un archivo PEM, con passphrase si se cifró
    with open(pem_path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=passphrase)


def encrypt_records_to_file(
    records: Dict[str, str], public_key_path: str, out_file: str
):
    public_key = load_public_key(public_key_path)
    plaintext = json.dumps(records, ensure_ascii=False).encode("utf-8")
    # Genera una clave AES-256 aleatoria
    aes_key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(aes_key)
    # Nonce aleatorio de 12 bytes (necesario en AES-GCM para que cada cifrado sea único)
    nonce = secrets.token_bytes(12)
    # Cifra los datos con AES-GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    # Cifra la clave AES con RSA-OAEP (solo se puede descifrar con la clave privada)
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Guardamos todo en un "contenedor" en JSON
    container = {
        "encrypted_key": base64.b64encode(encrypted_key).decode("utf-8"),
        "nonce": base64.b64encode(nonce).decode("utf-8"),
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
    }
    # Guardamos el contenedor en el archivo
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(container, f)
    print(f"Archivo cifrado guardado en {out_file}")


def decrypt_records_from_file(
    file_path: str, private_key_path: str, passphrase: bytes = None
) -> Dict[str, str]:
    # Descifra un archivo vault.
    # Primero se descifra la clave AES con RSA-OAEP y luego se usan esos datos para descifrar los registros con AES-GCM.
    with open(file_path, "r", encoding="utf-8") as f:
        container = json.load(f)
    encrypted_key = base64.b64decode(container["encrypted_key"])
    nonce = base64.b64decode(container["nonce"])
    ciphertext = base64.b64decode(container["ciphertext"])
    private_key = load_private_key(private_key_path, passphrase)

    # Descifra la clave AES
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Descifra los registros con AES-GCM
    aesgcm = AESGCM(aes_key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    return json.loads(plaintext.decode("utf-8"))
