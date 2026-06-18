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
    # Puntuacion de 0 a 4
    score = 0
    if length >= 8:
        score += 1
    if length >= 12:
        score += 1
    if categories >= 3:
        score += 1
    if length >= 16 and categories == 4:
        score += 1
    verdict = {
        0: "Muy débil",
        1: "Débil",
        2: "Moderada",
        3: "Fuerte",
        4: "Muy fuerte",
    }.get(score, "Indeterminado")
    return {
        "score": score,
        "verdict": verdict,
        "length": length,
        "categories": categories,
    }
