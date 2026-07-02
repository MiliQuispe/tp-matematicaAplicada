#!/usr/bin/env python3
"""
Administrador de Contraseñas — UNLaM
Punto de entrada oficial de la aplicación (interfaz gráfica).

Ejecutar desde la carpeta del proyecto:
    python3 main.py

Dependencias:
    pip install cryptography        # cifrado RSA / AES-GCM
    sudo apt install python3-tk     # interfaz gráfica (Linux/WSL)
"""
from gui import arrancar_interfaz

if __name__ == "__main__":
    # Arranca el bucle visual de las ventanas
    arrancar_interfaz()
