#!/usr/bin/env python3
"""
Dependencias: pip install cryptography
Ejemplos:
  # Generar par de claves RSA
  python main.py gen-keys --private private.pem --public public.pem --passphrase "miPass"

  # Inicializar archivo vault vacío cifrado con la clave pública
  python main.py init --file vault.bin --public public.pem

  # Agregar un registro al vault (requiere la clave privada para descifrar y la pública para re-encriptar)
  python main.py add --file vault.bin --private private.pem --passphrase "miPass" --public public.pem --name "juan" --password "Secreto123!"

  # Listar registros (requiere la clave privada)
  python main.py list --file vault.bin --private private.pem --passphrase "miPass"
"""

""" import argparse  # para manejar la linea de comandos
import base64  # para convertir binario a texto y viceversa
import json  # para guardar registros como JSON
import os  # para verificar existencia de archivos
from typing import Dict, Any  # dict - diccionario, any - cualquier tipo
import secrets  # para generar contraseñas seguras y claves aleatorias
import string  # para los caracteres posibles en contraseñas
from getpass import getpass  # para pedir contraseñas de forma segura (sin mostrarlas)

# librerias de cryptography para cifrado
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
# Importamos lo que se fue a cripto.py
from cripto import *

# Importamos lo que se fue a negocio.py
from negocio import *

from utils import *


# CLI (gestionar)
def gestionar():
    parser = argparse.ArgumentParser(
        description="Vault de contraseñas cifrado (RSA + AES-GCM)"
    )
    sub = parser.add_subparsers(dest="cmd")

    # gen-keys
    gk = sub.add_parser("gen-keys", help="Generar par RSA")
    gk.add_argument("--private", required=True)
    gk.add_argument("--public", required=True)
    gk.add_argument(
        "--passphrase",
        required=False,
        help="Si se pasa, se usará para cifrar la private PEM",
    )

    # init
    it = sub.add_parser(
        "init", help="Inicializar archivo vault vacío (cifrado con la public key)"
    )
    it.add_argument("--file", required=True)
    it.add_argument("--public", required=True)

    # add
    ad = sub.add_parser("add", help="Agregar registro")
    ad.add_argument("--file", required=True)
    ad.add_argument("--private", required=True)
    ad.add_argument("--public", required=True)
    ad.add_argument("--name", required=True)
    ad.add_argument("--password", required=False)
    ad.add_argument("--passphrase", required=False)

    # list
    ls = sub.add_parser("list", help="Listar registros")
    ls.add_argument("--file", required=True)
    ls.add_argument("--private", required=True)
    ls.add_argument("--passphrase", required=False)

    # modify
    mo = sub.add_parser("modify", help="Modificar registro")
    mo.add_argument("--file", required=True)
    mo.add_argument("--private", required=True)
    mo.add_argument("--public", required=True)
    mo.add_argument("--name", required=True)
    mo.add_argument("--password", required=False)
    mo.add_argument("--passphrase", required=False)

    # delete
    de = sub.add_parser("delete", help="Eliminar registro")
    de.add_argument("--file", required=True)
    de.add_argument("--private", required=True)
    de.add_argument("--public", required=True)
    de.add_argument("--name", required=True)
    de.add_argument("--passphrase", required=False)

    # gen-pass
    gp = sub.add_parser("gen-pass", help="Generar contraseña aleatoria")
    gp.add_argument("--length", type=int, default=12)

    # check-pass
    cp = sub.add_parser("check-pass", help="Medir fortaleza de una contraseña")
    cp.add_argument("--password", required=True)

    args = parser.parse_args()

    if args.cmd == "gen-keys":
        pf = args.passphrase.encode("utf-8") if args.passphrase else None
        generate_rsa_keypair(args.private, args.public, pf)
    elif args.cmd == "init":
        init_empty_vault(args.file, args.public)
    elif args.cmd == "add":
        pw = args.password or getpass("Contraseña para el registro: ")
        pp = args.passphrase.encode("utf-8") if args.passphrase else None
        add_record(args.file, args.private, args.public, args.name, pw, pp)
    elif args.cmd == "list":
        pp = args.passphrase.encode("utf-8") if args.passphrase else None
        list_records(args.file, args.private, pp)
    elif args.cmd == "modify":
        pw = args.password or getpass("Nueva contraseña: ")
        pp = args.passphrase.encode("utf-8") if args.passphrase else None
        modify_record(args.file, args.private, pp, args.public, args.name, pw)
    elif args.cmd == "delete":
        pp = args.passphrase.encode("utf-8") if args.passphrase else None
        delete_record(args.file, args.private, pp, args.public, args.name)
    elif args.cmd == "gen-pass":
        print(generate_password(length=args.length))
    elif args.cmd == "check-pass":
        res = password_strength(args.password)
        print(f"Puntaje: {res['score']} -> {res['verdict']}")
        print(f"Largo: {res['length']}, Categorías: {res['categories']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    gestionar()
 """

#!/usr/bin/env python3
"""
Punto de entrada oficial para el Administrador de Contraseñas.
UNLaM - Grupo de 7 Integrantes
"""
from gui import arrancar_interfaz

if __name__ == "__main__":
    # Arranca el bucle visual de las ventanas
    arrancar_interfaz()