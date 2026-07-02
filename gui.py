import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os

# Vinculamos con tus módulos de lógica
import negocio
import utils

# ======================================================================
# SISTEMA DE DISEÑO — "Bóveda digital"
# Paleta y tipografía pensadas para transmitir seguridad, no decoración:
#   - Fondo casi negro (consola nocturna) con capas de profundidad.
#   - Un único acento vivo (verde-menta) reservado para "seguro / acción
#     principal". Ámbar solo para bloqueado. Rojo solo para peligro.
#   - Tipografía monoespaciada (Consolas) para todo lo que es un dato
#     sensible (contraseñas, tabla, badges) — distingue visualmente
#     "interfaz" de "dato criptográfico".
# ======================================================================

COLOR_BG = "#0B1220"          # fondo base de la ventana
COLOR_PANEL = "#131C2E"       # barras / header
COLOR_CARD = "#182236"        # tarjetas, inputs, filas de tabla
COLOR_BORDER = "#263449"

COLOR_ACCENT = "#23D5AB"      # verde-menta: seguro / acción principal
COLOR_ACCENT_HOVER = "#33E6BC"
COLOR_ACCENT_DARK = "#159873"
COLOR_ACCENT_SOFT = "#0F2E28"

COLOR_DANGER = "#E5484D"
COLOR_DANGER_HOVER = "#F16065"

COLOR_WARNING = "#F5A623"
COLOR_WARNING_SOFT = "#3A2E12"

COLOR_NEUTRAL = "#3A4A63"
COLOR_NEUTRAL_HOVER = "#46597A"

COLOR_TEXT = "#EAF0F6"
COLOR_TEXT_MUTED = "#8996A9"
COLOR_TEXT_DIM = "#5C6B80"

FONT_TITLE = ("Segoe UI Semibold", 18)
FONT_SUBTITLE = ("Segoe UI", 9)
FONT_SECTION = ("Segoe UI Semibold", 11)
FONT_BODY = ("Segoe UI", 10)
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_LABEL = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 10)
FONT_MONO_BOLD = ("Consolas", 10, "bold")
FONT_BADGE = ("Consolas", 9, "bold")


def crear_boton(parent, text, command, bg=COLOR_NEUTRAL, hover=None, fg=COLOR_TEXT,
                 font=FONT_BODY_BOLD, width=None, padx=14, pady=8):
    """Botón plano con hover, coherente con la paleta de seguridad."""
    hover = hover or bg
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=hover,
        activeforeground=fg,
        font=font,
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=padx,
        pady=pady,
        width=width,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def crear_entry(parent, textvariable=None, show=None, width=28, font=FONT_MONO):
    entry = tk.Entry(
        parent,
        textvariable=textvariable,
        show=show,
        width=width,
        font=font,
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        insertbackground=COLOR_ACCENT,
        relief="flat",
        highlightthickness=1,
        highlightbackground=COLOR_BORDER,
        highlightcolor=COLOR_ACCENT,
    )
    return entry


def crear_indicador_fortaleza(parent, sv_password):
    """Label que se actualiza solo, mostrando la fortaleza de la
    contraseña vinculada a `sv_password` (usa utils.password_strength)."""
    lbl_fortaleza = tk.Label(
        parent, text="Fortaleza: -", fg=COLOR_TEXT_DIM, bg=COLOR_BG,
        font=("Segoe UI", 9, "italic"),
    )

    def verificar_fortaleza(*args):
        pwd = sv_password.get()
        if not pwd:
            lbl_fortaleza.config(text="Fortaleza: -", fg=COLOR_TEXT_DIM)
            return

        res = utils.password_strength(pwd)
        score = res["score"]

        if score == 0:
            lbl_fortaleza.config(text="Fortaleza: Muy Débil", fg=COLOR_DANGER)
        elif score == 1:
            lbl_fortaleza.config(text="Fortaleza: Débil", fg="#F1834D")
        elif score == 2:
            lbl_fortaleza.config(text="Fortaleza: Regular", fg=COLOR_WARNING)
        elif score == 3:
            lbl_fortaleza.config(text="Fortaleza: Buena", fg=COLOR_ACCENT_DARK)
        elif score == 4:
            lbl_fortaleza.config(text="Fortaleza: Excelente", fg=COLOR_ACCENT)

    sv_password.trace_add("write", verificar_fortaleza)
    return lbl_fortaleza


def crear_tarjeta(parent, titulo):
    """Tarjeta con borde sutil (en vez de bloques de color plano)."""
    outer = tk.Frame(parent, bg=COLOR_BORDER)
    outer.pack(fill=tk.X, pady=10)
    inner = tk.Frame(outer, bg=COLOR_PANEL, padx=20, pady=18)
    inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

    tk.Label(
        inner, text=titulo, font=FONT_SECTION, fg=COLOR_ACCENT, bg=COLOR_PANEL,
    ).pack(anchor="w", pady=(0, 12))
    return inner


def estilizar_toplevel(win, titulo, ancho, alto):
    win.title(titulo)
    win.geometry(f"{ancho}x{alto}")
    win.configure(bg=COLOR_BG)
    win.grab_set()
    return win


class AdminContrasenasGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UNLaM · Vault — Administrador Seguro de Contraseñas")
        self.root.geometry("980x620")
        self.root.minsize(820, 540)
        self.root.configure(bg=COLOR_BG)

        self.ruta_privada = tk.StringVar()
        self.ruta_publica = tk.StringVar()
        self.ruta_baul = tk.StringVar()

        # Guardamos la contraseña maestra una vez validada, para no pedirla
        # de nuevo en cada operación dentro de la vista del baúl.
        self.master_password = ""

        # Las contraseñas reales viven solo en memoria, nunca en la tabla
        # visible: la Treeview muestra un valor enmascarado y este diccionario
        # es la única fuente de verdad para operaciones (ej. Modificar).
        self.registros_actuales = {}

        self._configurar_estilos_ttk()
        self._crear_header()

        # Contenedor que aloja ambas vistas superpuestas
        self.contenedor = tk.Frame(self.root, bg=COLOR_BG)
        self.contenedor.pack(fill=tk.BOTH, expand=True)
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.vista_inicio = tk.Frame(self.contenedor, bg=COLOR_BG)
        self.vista_baul = tk.Frame(self.contenedor, bg=COLOR_BG)

        for vista in (self.vista_inicio, self.vista_baul):
            vista.grid(row=0, column=0, sticky="nsew")

        self.setup_vista_inicio()
        self.setup_vista_baul()

        self.mostrar_inicio()

    # ------------------------------------------------------------------
    # ESTILOS GLOBALES (ttk) Y HEADER
    # ------------------------------------------------------------------
    def _configurar_estilos_ttk(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=COLOR_CARD,
            fieldbackground=COLOR_CARD,
            foreground=COLOR_TEXT,
            font=FONT_MONO,
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=COLOR_PANEL,
            foreground=COLOR_ACCENT,
            font=FONT_BODY_BOLD,
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "Treeview.Heading",
            background=[("active", COLOR_PANEL)],
        )
        style.map(
            "Treeview",
            background=[("selected", COLOR_ACCENT_DARK)],
            foreground=[("selected", "#04120E")],
        )
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    def _crear_header(self):
        header = tk.Frame(self.root, bg=COLOR_PANEL, height=64)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        bloque_izq = tk.Frame(header, bg=COLOR_PANEL)
        bloque_izq.pack(side=tk.LEFT, padx=20)

        bloque_titulo = tk.Frame(bloque_izq, bg=COLOR_PANEL)
        bloque_titulo.pack(side=tk.LEFT)
        tk.Label(
            bloque_titulo, text="UNLaM · VAULT", font=FONT_TITLE, fg=COLOR_TEXT, bg=COLOR_PANEL,
        ).pack(anchor="w")
        tk.Label(
            bloque_titulo,
            text="Administrador seguro de contraseñas",
            font=FONT_SUBTITLE,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_PANEL,
        ).pack(anchor="w")

        # Badge de estado: refleja el estado REAL de la sesión, no decora.
        self.badge_estado = tk.Label(
            header,
            text="BLOQUEADO",
            font=FONT_BADGE,
            fg=COLOR_WARNING,
            bg=COLOR_WARNING_SOFT,
            padx=14,
            pady=6,
        )
        self.badge_estado.pack(side=tk.RIGHT, padx=20)

    def _actualizar_badge(self, activo: bool):
        if activo:
            self.badge_estado.config(
                text="SESION ACTIVA", fg=COLOR_ACCENT, bg=COLOR_ACCENT_SOFT
            )
        else:
            self.badge_estado.config(
                text="BLOQUEADO", fg=COLOR_WARNING, bg=COLOR_WARNING_SOFT
            )

    # ------------------------------------------------------------------
    # NAVEGACIÓN ENTRE VISTAS
    # ------------------------------------------------------------------
    def mostrar_inicio(self):
        self._actualizar_badge(activo=False)
        self.vista_inicio.tkraise()

    def mostrar_baul(self):
        self._actualizar_badge(activo=True)
        self.vista_baul.tkraise()

    # ------------------------------------------------------------------
    # VISTA 1: INICIO
    # ------------------------------------------------------------------
    def setup_vista_inicio(self):
        contenedor_centrado = tk.Frame(self.vista_inicio, bg=COLOR_BG, width=440)
        contenedor_centrado.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            contenedor_centrado,
            text="Desbloqueá tu bóveda",
            font=("Segoe UI Semibold", 15),
            fg=COLOR_TEXT,
            bg=COLOR_BG,
        ).pack(pady=(0, 4))
        tk.Label(
            contenedor_centrado,
            text="Tus contraseñas permanecen cifradas hasta que accedas.",
            font=FONT_SUBTITLE,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_BG,
        ).pack(pady=(0, 16))

        # --- Bloque: acceder con archivos existentes ---
        panel_existente = crear_tarjeta(contenedor_centrado, "Acceder a un baul existente")

        crear_boton(
            panel_existente, "Seleccionar clave privada (.pem)", self.seleccionar_privada,
            bg=COLOR_NEUTRAL, hover=COLOR_NEUTRAL_HOVER,
        ).pack(fill=tk.X, pady=(0, 4))
        tk.Label(
            panel_existente, textvariable=self.ruta_privada, fg=COLOR_TEXT_DIM, bg=COLOR_PANEL,
            font=("Consolas", 8), wraplength=380, justify="left",
        ).pack(anchor="w", pady=(0, 10))

        crear_boton(
            panel_existente, "Seleccionar baúl (.bin)", self.seleccionar_baul,
            bg=COLOR_NEUTRAL, hover=COLOR_NEUTRAL_HOVER,
        ).pack(fill=tk.X, pady=(0, 4))
        tk.Label(
            panel_existente, textvariable=self.ruta_baul, fg=COLOR_TEXT_DIM, bg=COLOR_PANEL,
            font=("Consolas", 8), wraplength=380, justify="left",
        ).pack(anchor="w", pady=(0, 14))

        tk.Label(
            panel_existente, text="CONTRASEÑA MAESTRA", font=("Segoe UI", 8, "bold"),
            fg=COLOR_TEXT_MUTED, bg=COLOR_PANEL,
        ).pack(anchor="w", pady=(0, 4))
        self.entry_master_inicio = crear_entry(panel_existente, show="•", width=34)
        self.entry_master_inicio.pack(fill=tk.X, ipady=4, pady=(0, 14))
        self.entry_master_inicio.bind("<Return>", lambda e: self.acceder_al_baul())

        crear_boton(
            panel_existente, "Desencriptar y acceder", self.acceder_al_baul,
            bg=COLOR_ACCENT_DARK, hover=COLOR_ACCENT, fg="#04120E",
        ).pack(fill=tk.X)

        # --- Bloque: inicializar sistema nuevo ---
        panel_nuevo = crear_tarjeta(contenedor_centrado, "¿Primera vez?")
        tk.Label(
            panel_nuevo,
            text="Generamos tu par de claves y un baúl vacío, listos para usar.",
            font=FONT_LABEL,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_PANEL,
            wraplength=380,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))
        crear_boton(
            panel_nuevo, "Inicializar sistema nuevo", self.ventana_inicializar,
            bg=COLOR_ACCENT_DARK, hover=COLOR_ACCENT, fg="#04120E",
        ).pack(fill=tk.X)

    # --- FUNCIONES DE SELECCIÓN ---
    def seleccionar_privada(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar private.pem", filetypes=[("PEM files", "*.pem")]
        )
        if ruta:
            self.ruta_privada.set(ruta)

    def seleccionar_baul(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar vault.bin", filetypes=[("Binary files", "*.bin")]
        )
        if ruta:
            self.ruta_baul.set(ruta)

    def acceder_al_baul(self):
        """Valida la contraseña maestra desde la vista de Inicio y,
        si es correcta, navega a la vista del Baúl con los registros cargados."""
        if not self.ruta_baul.get() or not self.ruta_privada.get():
            messagebox.showerror(
                "Error", "Selecciona el baúl y tu clave privada."
            )
            return
        passphrase_str = self.entry_master_inicio.get()
        if not passphrase_str:
            messagebox.showwarning("Atención", "Ingresa la contraseña maestra.")
            return

        if not self.listar_registros(passphrase_str):
            return  # error ya mostrado dentro de listar_registros

        self.master_password = passphrase_str
        self.lbl_baul_actual.config(text=f"Baul: {self.ruta_baul.get()}")
        self.mostrar_baul()

    def ventana_inicializar(self):
        win = estilizar_toplevel(tk.Toplevel(self.root), "Inicializar Sistema", 420, 300)

        tk.Label(
            win, text="Crear clave maestra", font=FONT_SECTION, fg=COLOR_TEXT, bg=COLOR_BG,
        ).pack(pady=(20, 4))
        tk.Label(
            win, text="Se usará para proteger private.pem y vault.bin",
            font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_BG,
        ).pack(pady=(0, 14))

        sv_password_nueva = tk.StringVar()
        entry_pass = crear_entry(win, textvariable=sv_password_nueva, show="•", width=30)
        entry_pass.pack(ipady=4, pady=5)

        crear_indicador_fortaleza(win, sv_password_nueva).pack(pady=(0, 4))

        def procesar_inicializacion():
            password = entry_pass.get()
            res = utils.password_strength(password)

            if res["score"] < 3:
                faltantes = []
                if res["length"] < 12:
                    faltantes.append("al menos 12 caracteres")
                if res["categories"] < 3:
                    faltantes.append(
                        "3 tipos de caracteres (mayúsculas, minúsculas, números o símbolos)"
                    )
                detalle = "Te falta: " + " y ".join(faltantes)
                messagebox.showerror(
                    "Contraseña maestra débil",
                    "La clave maestra protege TODO tu baúl, tiene que ser fuerte.\n\n"
                    f"Fortaleza actual: {res['verdict']}.\n{detalle}\n\n"
                    "Ingresa otra contraseña que llegue al menos a fortaleza 'Buena'.",
                )
                entry_pass.delete(0, tk.END)
                entry_pass.focus_set()
                return

            # La inicialización es un evento único ("Día Cero"): si ya existen
            # archivos de un baúl anterior, avisamos antes de sobrescribirlos
            # para no borrar las contraseñas guardadas sin que el usuario lo sepa.
            existentes = [
                f for f in ("private.pem", "public.pem", "vault.bin") if os.path.exists(f)
            ]
            if existentes and not messagebox.askyesno(
                "Ya existe un baúl",
                "Se detectaron archivos de un baúl anterior:\n"
                f"  {', '.join(existentes)}\n\n"
                "Si continuás se SOBRESCRIBIRÁN y perderás el acceso a las "
                "contraseñas ya guardadas.\n\n¿Querés continuar de todas formas?",
            ):
                return

            from cripto import generate_rsa_keypair

            try:
                generate_rsa_keypair(
                    "private.pem", "public.pem", password.encode("utf-8")
                )
                negocio.init_empty_vault("vault.bin", "public.pem")
                self.ruta_privada.set(os.path.abspath("private.pem"))
                self.ruta_publica.set(os.path.abspath("public.pem"))
                self.ruta_baul.set(os.path.abspath("vault.bin"))
                self.entry_master_inicio.delete(0, tk.END)
                self.entry_master_inicio.insert(0, password)
                messagebox.showinfo("Éxito", "Archivos generados automáticamente.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        crear_boton(
            win, "Generar archivos blindados", procesar_inicializacion,
            bg=COLOR_ACCENT_DARK, hover=COLOR_ACCENT, fg="#04120E", width=28,
        ).pack(pady=24)

    # ------------------------------------------------------------------
    # VISTA 2: ARCHIVO DE CONTRASEÑAS (BAÚL)
    # ------------------------------------------------------------------
    def setup_vista_baul(self):
        # Barra superior
        barra_superior = tk.Frame(self.vista_baul, bg=COLOR_BG)
        barra_superior.pack(fill=tk.X, padx=16, pady=(16, 8))

        crear_boton(
            barra_superior, "Cerrar sesion", self.cerrar_sesion,
            bg=COLOR_NEUTRAL, hover=COLOR_NEUTRAL_HOVER, font=FONT_LABEL, padx=10, pady=6,
        ).pack(side=tk.LEFT)

        self.lbl_baul_actual = tk.Label(
            barra_superior, text="Baul: -", fg=COLOR_TEXT_MUTED, bg=COLOR_BG, font=("Consolas", 9),
        )
        self.lbl_baul_actual.pack(side=tk.LEFT, padx=16)

        crear_boton(
            barra_superior, "Agregar credencial", self.ventana_agregar,
            bg=COLOR_ACCENT_DARK, hover=COLOR_ACCENT, fg="#04120E", font=FONT_LABEL, padx=12, pady=6,
        ).pack(side=tk.RIGHT)
        crear_boton(
            barra_superior, "Refrescar", lambda: self.listar_registros(self.master_password),
            bg=COLOR_NEUTRAL, hover=COLOR_NEUTRAL_HOVER, font=FONT_LABEL, padx=10, pady=6,
        ).pack(side=tk.RIGHT, padx=8)

        # Tabla dinámica de registros (envuelta en tarjeta con borde sutil)
        borde_tabla = tk.Frame(self.vista_baul, bg=COLOR_BORDER)
        borde_tabla.pack(fill=tk.BOTH, expand=True, padx=16)
        panel_tabla = tk.Frame(borde_tabla, bg=COLOR_CARD)
        panel_tabla.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.tabla = ttk.Treeview(
            panel_tabla, columns=("Servicio", "Contraseña"), show="headings"
        )
        self.tabla.heading("Servicio", text="SITIO / SERVICIO")
        self.tabla.heading("Contraseña", text="CONTRASEÑA PROTEGIDA")
        self.tabla.column("Servicio", width=260)
        self.tabla.column("Contraseña", width=260)
        self.tabla.pack(fill=tk.BOTH, expand=True)

        # Barra inferior: Modificar y Eliminar
        barra_inferior = tk.Frame(self.vista_baul, bg=COLOR_BG)
        barra_inferior.pack(fill=tk.X, padx=16, pady=16)

        crear_boton(
            barra_inferior, "Modificar seleccionado", self.ventana_modificar,
            bg=COLOR_NEUTRAL, hover=COLOR_NEUTRAL_HOVER,
        ).pack(side=tk.LEFT, padx=(0, 8))
        crear_boton(
            barra_inferior, "Eliminar seleccionado", self.ejecutar_eliminar,
            bg=COLOR_DANGER, hover=COLOR_DANGER_HOVER,
        ).pack(side=tk.LEFT)

    def cerrar_sesion(self):
        """Limpia el estado sensible y vuelve a la vista de Inicio."""
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.master_password = ""
        self.registros_actuales = {}
        self.entry_master_inicio.delete(0, tk.END)
        self.mostrar_inicio()

    def listar_registros(self, passphrase_str=None):
        """Descifra y carga los registros en la tabla.
        Devuelve True si tuvo éxito, False si hubo error."""
        if passphrase_str is None:
            passphrase_str = self.master_password

        if not self.ruta_baul.get() or not self.ruta_privada.get():
            messagebox.showerror(
                "Error", "Selecciona el baúl y tu clave privada."
            )
            return False
        if not passphrase_str:
            messagebox.showwarning("Atención", "Ingresa la contraseña maestra.")
            return False

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            from cripto import decrypt_records_from_file

            records = decrypt_records_from_file(
                self.ruta_baul.get(),
                self.ruta_privada.get(),
                passphrase_str.encode("utf-8"),
            )
            self.registros_actuales = records or {}
            if not records:
                return True
            for servicio in records:
                self.tabla.insert("", tk.END, values=(servicio, "••••••••"))
            return True
        except Exception:
            messagebox.showerror(
                "Error Criptográfico", "Contraseña maestra incorrecta o archivo dañado."
            )
            return False

    def ventana_agregar(self):
        if not self.ruta_baul.get() or not self.ruta_privada.get():
            messagebox.showerror("Error", "Configura los archivos del panel izquierdo.")
            return

        if not self.master_password:
            messagebox.showwarning("Aviso", "Debes acceder al baúl con la Contraseña Maestra primero.")
            return

        win = estilizar_toplevel(tk.Toplevel(self.root), "Nuevo Registro", 420, 340)

        tk.Label(win, text="Nuevo registro", font=FONT_SECTION, fg=COLOR_TEXT, bg=COLOR_BG).pack(pady=(20, 14))

        tk.Label(win, text="NOMBRE DEL SERVICIO", font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_BG).pack(anchor="w", padx=40)
        entry_name = crear_entry(win, width=34, font=FONT_BODY)
        entry_name.pack(ipady=4, pady=(2, 14), padx=40, fill=tk.X)

        # sv_password escucha los cambios del input
        sv_password = tk.StringVar()
        tk.Label(win, text="CONTRASEÑA", font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_BG).pack(anchor="w", padx=40)
        entry_key = crear_entry(win, textvariable=sv_password, width=34)
        entry_key.pack(ipady=4, pady=(2, 4), padx=40, fill=tk.X)

        # Label que indica el nivel de fortaleza de la contraseña (reutilizable)
        crear_indicador_fortaleza(win, sv_password).pack(anchor="w", padx=40, pady=(0, 10))

        def auto_generar():
            clave_segura = utils.generate_password(length=14)
            entry_key.delete(0, tk.END)
            entry_key.insert(0, clave_segura)

        crear_boton(
            win, "Generar segura", auto_generar,
            bg=COLOR_NEUTRAL, hover=COLOR_NEUTRAL_HOVER, font=FONT_LABEL, padx=10, pady=6,
        ).pack(pady=(0, 10))

        def registrar():
            name = entry_name.get()
            pwd = entry_key.get()
            if not name or not pwd:
                messagebox.showerror("Error", "Completa todos los campos.")
                return
            try:
                negocio.add_record(
                    self.ruta_baul.get(),
                    self.ruta_privada.get(),
                    "public.pem",
                    name,
                    pwd,
                    self.master_password.encode("utf-8"),
                )
                messagebox.showinfo("Éxito", f"Registro '{name}' guardado.")
                win.destroy()
                self.listar_registros()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        crear_boton(
            win, "Guardar en el baul", registrar,
            bg=COLOR_ACCENT_DARK, hover=COLOR_ACCENT, fg="#04120E", width=26,
        ).pack(pady=6)

    def ventana_modificar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Selecciona una fila de la tabla para modificar."
            )
            return

        item_data = self.tabla.item(seleccion[0], "values")
        servicio_nombre = item_data[0]
        password_actual = self.registros_actuales.get(servicio_nombre, "")

        win = estilizar_toplevel(tk.Toplevel(self.root), f"Modificar · {servicio_nombre}", 420, 260)

        tk.Label(win, text="Modificar contraseña", font=FONT_SECTION, fg=COLOR_TEXT, bg=COLOR_BG).pack(pady=(20, 4))
        tk.Label(win, text=servicio_nombre, font=FONT_MONO_BOLD, fg=COLOR_ACCENT, bg=COLOR_BG).pack(pady=(0, 14))

        entry_nueva_key = crear_entry(win, width=30)
        entry_nueva_key.pack(ipady=4, pady=5)
        entry_nueva_key.insert(0, password_actual)

        def confirmar_modificacion():
            nueva_pwd = entry_nueva_key.get()
            if not nueva_pwd:
                messagebox.showerror("Error", "Completa los campos.")
                return
            try:
                negocio.modify_record(
                    self.ruta_baul.get(),
                    self.ruta_privada.get(),
                    self.master_password.encode("utf-8"),
                    "public.pem",
                    servicio_nombre,
                    nueva_pwd,
                )
                messagebox.showinfo("Éxito", "Registro modificado correctamente.")
                win.destroy()
                self.listar_registros()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        crear_boton(
            win, "Actualizar contraseña", confirmar_modificacion,
            bg=COLOR_ACCENT_DARK, hover=COLOR_ACCENT, fg="#04120E", width=26,
        ).pack(pady=20)

    def ejecutar_eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Selecciona una fila de la tabla para eliminar."
            )
            return

        item_data = self.tabla.item(seleccion[0], "values")
        servicio_nombre = item_data[0]

        if not self.master_password:
            messagebox.showerror(
                "Error", "Debes haber accedido al baúl con la contraseña maestra."
            )
            return

        if messagebox.askyesno(
            "Confirmar",
            f"¿Estás seguro de que deseas eliminar el registro de '{servicio_nombre}'?",
        ):
            try:
                negocio.delete_record(
                    self.ruta_baul.get(),
                    self.ruta_privada.get(),
                    self.master_password.encode("utf-8"),
                    "public.pem",
                    servicio_nombre,
                )
                messagebox.showinfo("Éxito", "Registro eliminado.")
                self.listar_registros()
            except Exception as e:
                messagebox.showerror("Error", str(e))


def arrancar_interfaz():
    root = tk.Tk()
    app = AdminContrasenasGUI(root)
    root.mainloop()