import os

# IMPORTAMOS las funciones desde cripto.py
from cripto import (
    load_public_key,
    load_private_key,
    encrypt_records_to_file,
    decrypt_records_from_file,
)

# Funcionalidades de vault
#
# IMPORTANTE: estas funciones son llamadas desde gui.py dentro de bloques
# try/except que esperan capturar errores reales. Por eso, ante cualquier
# problema, SIEMPRE se relanza una excepción (nunca se hace print + return),
# o la GUI mostraría "Éxito" aunque la operación haya fallado.


def init_empty_vault(out_file: str, public_key_path: str) -> None:
    encrypt_records_to_file({}, public_key_path, out_file)


def add_record(
    file_path: str,
    private_key_path: str,
    public_key_path: str,
    name: str,
    password: str,
    passphrase: bytes = None,
) -> None:
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"El archivo '{file_path}' no existe. Inicializa el baúl primero."
        )

    records = decrypt_records_from_file(file_path, private_key_path, passphrase)

    if name in records:
        raise ValueError(
            f"Ya existe un registro llamado '{name}'. "
            "Usa 'Modificar' si querés actualizar su contraseña."
        )

    records[name] = password
    encrypt_records_to_file(records, public_key_path, file_path)


def modify_record(
    file_path: str,
    private_key_path: str,
    passphrase: bytes,
    public_key_path: str,
    name: str,
    new_password: str,
) -> None:
    records = decrypt_records_from_file(file_path, private_key_path, passphrase)

    if name not in records:
        raise KeyError(f"No existe el registro '{name}'.")

    records[name] = new_password
    encrypt_records_to_file(records, public_key_path, file_path)


def delete_record(
    file_path: str,
    private_key_path: str,
    passphrase: bytes,
    public_key_path: str,
    name: str,
) -> None:
    records = decrypt_records_from_file(file_path, private_key_path, passphrase)

    if name not in records:
        raise KeyError(f"No existe el registro '{name}'.")

    del records[name]
    encrypt_records_to_file(records, public_key_path, file_path)