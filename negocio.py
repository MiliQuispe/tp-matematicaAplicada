import os
import json
from typing import Dict, Any

# IMPORTAMOS las funciones desde cripto.py
from cripto import (
    load_public_key,
    load_private_key,
    encrypt_records_to_file,
    decrypt_records_from_file,
)

# Funcionalidades de vault
def init_empty_vault(out_file: str, public_key_path: str):
    encrypt_records_to_file({}, public_key_path, out_file)


def add_record(
    file_path: str,
    private_key_path: str,
    public_key_path: str,
    name: str,
    password: str,
    passphrase: bytes = None,
):
    if not os.path.exists(file_path):
        print("Archivo no existe. Crea uno primero con init.")
        return
    try:
        records = decrypt_records_from_file(file_path, private_key_path, passphrase)
    except Exception as e:
        print("Error al descifrar archivo:", e)
        return
    records[name] = password
    encrypt_records_to_file(records, public_key_path, file_path)
    print(f"Registro agregado: {name}")


def modify_record(
    file_path: str,
    private_key_path: str,
    passphrase: bytes,
    public_key_path: str,
    name: str,
    new_password: str,
):
    try:
        records = decrypt_records_from_file(file_path, private_key_path, passphrase)
    except Exception as e:
        print("Error al descifrar para modificar:", e)
        return
        
    if name not in records:
        print("No existe el registro:", name)
        return
    records[name] = new_password
    encrypt_records_to_file(records, public_key_path, file_path)
    print("Registro modificado.")


def delete_record(
    file_path: str,
    private_key_path: str,
    passphrase: bytes,
    public_key_path: str,
    name: str,
):
    try:
        records = decrypt_records_from_file(file_path, private_key_path, passphrase)
    except Exception as e:
        print("Error al descifrar para eliminar:", e)
        return
        
    if name not in records:
        print("No existe el registro:", name)
        return
    del records[name]
    encrypt_records_to_file(records, public_key_path, file_path)
    print("Registro eliminado.")


def list_records(file_path: str, private_key_path: str, passphrase: bytes = None):
    try:
        records = decrypt_records_from_file(file_path, private_key_path, passphrase)
    except Exception as e:
        print("Error al descifrar para listar:", e)
        return
        
    if not records:
        print("(vacío)")
        return
    for k, v in records.items():
        print(f"{k} - {v}")