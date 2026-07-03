"""Verificación final end-to-end del núcleo lógico (cripto + negocio + utils).

Ejercita el sistema real en un directorio temporal, sin tocar los archivos
del repo (private.pem / vault.bin). Sirve como evidencia de aseguramiento de
calidad y para re-verificar tras cambios.

Uso:
    python3 tests/verificacion_final.py
"""
import os, sys, json, base64, tempfile

# Permite ejecutar el script desde cualquier carpeta importando los módulos
# del proyecto (que viven en el directorio padre de tests/).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cripto, negocio, utils
from gui import NIVELES_FORTALEZA  # para chequear alineación de etiquetas

ok = 0
fail = 0

def check(nombre, cond):
    global ok, fail
    if cond:
        ok += 1
        print(f"  [PASS] {nombre}")
    else:
        fail += 1
        print(f"  [FAIL] {nombre}")

def espera_error(nombre, fn):
    """Pasa si fn() lanza una excepción."""
    global ok, fail
    try:
        fn()
    except Exception as e:
        ok += 1
        print(f"  [PASS] {nombre}  ({type(e).__name__})")
    else:
        fail += 1
        print(f"  [FAIL] {nombre}  (no lanzó excepción)")

tmp = tempfile.mkdtemp(prefix="vault_test_")
priv = os.path.join(tmp, "private.pem")
pub = os.path.join(tmp, "public.pem")
vault = os.path.join(tmp, "vault.bin")
PASS = b"clave-maestra-correcta"

print("== 1. Criptografía: round-trip y protección de clave ==")
cripto.generate_rsa_keypair(priv, pub, passphrase=PASS)
check("Se generaron private.pem y public.pem", os.path.exists(priv) and os.path.exists(pub))
negocio.init_empty_vault(vault, pub)
check("Baúl vacío descifra a {}", cripto.decrypt_records_from_file(vault, priv, PASS) == {})
espera_error("Descifrar con passphrase incorrecta falla",
             lambda: cripto.decrypt_records_from_file(vault, priv, b"incorrecta"))

print("== 2. Negocio: ABM y casos de error ==")
negocio.add_record(vault, priv, pub, "GitHub", "gh-secret", PASS)
regs = cripto.decrypt_records_from_file(vault, priv, PASS)
check("Alta: GitHub queda guardado", regs.get("GitHub") == "gh-secret")
espera_error("Alta duplicada rechazada",
             lambda: negocio.add_record(vault, priv, pub, "GitHub", "otro", PASS))
negocio.modify_record(vault, priv, PASS, pub, "GitHub", "gh-nuevo")
regs = cripto.decrypt_records_from_file(vault, priv, PASS)
check("Modificar: contraseña actualizada", regs.get("GitHub") == "gh-nuevo")
espera_error("Modificar inexistente rechazado",
             lambda: negocio.modify_record(vault, priv, PASS, pub, "NoExiste", "x"))
espera_error("Eliminar inexistente rechazado",
             lambda: negocio.delete_record(vault, priv, PASS, pub, "NoExiste"))
negocio.delete_record(vault, priv, PASS, pub, "GitHub")
regs = cripto.decrypt_records_from_file(vault, priv, PASS)
check("Eliminar: GitHub ya no está", "GitHub" not in regs)

print("== 3. Integridad: detección de manipulación (AES-GCM) ==")
negocio.add_record(vault, priv, pub, "Gmail", "correo123", PASS)
with open(vault) as f:
    cont = json.load(f)
ct = bytearray(base64.b64decode(cont["ciphertext"]))
ct[0] ^= 0x01  # alteramos un byte del texto cifrado
cont["ciphertext"] = base64.b64encode(bytes(ct)).decode()
with open(vault, "w") as f:
    json.dump(cont, f)
espera_error("Vault manipulado: el descifrado falla",
             lambda: cripto.decrypt_records_from_file(vault, priv, PASS))

print("== 4. Vault corrupto / no válido ==")
malo = os.path.join(tmp, "corrupto.bin")
with open(malo, "w") as f:
    f.write("esto no es json")
espera_error("Archivo no-JSON: ValueError claro",
             lambda: cripto.decrypt_records_from_file(malo, priv, PASS))

print("== 5. Generador de contraseñas ==")
p = utils.generate_password(length=20, use_upper=True, use_lower=True, use_digits=True, use_special=True)
check("Respeta la longitud pedida (20)", len(p) == 20)
check("Incluye mayúscula", any(c.isupper() for c in p))
check("Incluye minúscula", any(c.islower() for c in p))
check("Incluye dígito", any(c.isdigit() for c in p))
check("Incluye especial", any(not c.isalnum() for c in p))
solo_dig = utils.generate_password(length=10, use_upper=False, use_lower=False, use_digits=True, use_special=False)
check("Solo dígitos cuando se pide solo dígitos", solo_dig.isdigit() and len(solo_dig) == 10)
espera_error("Longitud < 4 rechazada", lambda: utils.generate_password(length=2))

print("== 6. Medidor de fortaleza (progresivo) ==")
casos = {
    "123Ab": (0, "Muy Débil"),          # corta con variedad -> Muy Débil
    "Ab1!": (0, "Muy Débil"),           # 4 categorías pero 4 chars
    "password": (1, "Débil"),           # 8, 1 cat
    "abcdefghijkl": (2, "Regular"),     # 12, 1 cat
    "Abcdefghij1!": (3, "Buena"),       # 12, 4 cat
    "Abcdefghijklmno1!": (4, "Excelente"),  # 17, 4 cat
}
for pw, (sc, vd) in casos.items():
    r = utils.password_strength(pw)
    check(f"'{pw}' -> {sc}/{vd}", r["score"] == sc and r["verdict"] == vd)

print("== 7. Coherencia utils <-> gui (etiquetas de fortaleza) ==")
esperado = {0: "Muy Débil", 1: "Débil", 2: "Regular", 3: "Buena", 4: "Excelente"}
for score, (label, _color) in NIVELES_FORTALEZA.items():
    check(f"score {score}: gui '{label}' == esperado '{esperado[score]}'", label == esperado[score])

print(f"\n===== RESULTADO: {ok} PASS / {fail} FAIL =====")
sys.exit(1 if fail else 0)
