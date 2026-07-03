import string
import secrets
from typing import Dict, Any


# Generador y medidor - objetivo secundario
def generate_password(
    length: int = 12, use_upper=True, use_lower=True, use_digits=True, use_special=True
) -> str:
    # Genera una contraseña aleatoria segura
    if length < 4:
        raise ValueError("Length mínimo 4")
    pools = []
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_digits:
        pools.append(string.digits)
    if use_special:
        pools.append("!@#$%^&*()-_=+[]{};:,.<>/?")
    # Garantiza al menos un carácter de cada tipo seleccionado
    pwd = [secrets.choice(pool) for pool in pools]
    allchars = "".join(pools)
    while len(pwd) < length:
        pwd.append(secrets.choice(allchars))
    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)


def password_strength(password: str) -> Dict[str, Any]:
    # Evalua fortaleza de una contraseña: largo y diversidad de caracteres
    length = len(password)
    categories = sum(
        [
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        ]
    )
    # Puntuacion de 0 a 4, estrictamente progresiva: cada nivel exige lo del
    # anterior, de modo que una contraseña corta nunca sube por diversidad.
    if length < 8:
        score = 0
    elif length < 12:
        score = 1
    elif categories < 3:              # longitud >= 12
        score = 2
    elif length < 16 or categories < 4:  # >= 12 y >= 3 categorias
        score = 3
    else:                            # >= 16 y las 4 categorias
        score = 4
    verdict = {
        0: "Muy Débil",
        1: "Débil",
        2: "Regular",
        3: "Buena",
        4: "Excelente",
    }.get(score, "Indeterminado")
    return {
        "score": score,
        "verdict": verdict,
        "length": length,
        "categories": categories,
    }
