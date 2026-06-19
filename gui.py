import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os

# Vinculamos con tus módulos de lógica
import negocio
import utils


class AdminContrasenasGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UNLaM - Administrador Seguro de Contraseñas")
        self.root.geometry("900x550")  # Le damos un toque más de ancho
        self.root.configure(bg="#2c3e50")

        self.ruta_privada = tk.StringVar()
        self.ruta_publica = tk.StringVar()
        self.ruta_baul = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        # PANEL LATERAL: Gestión de Llaves y Baúl
        panel_lateral = tk.Frame(self.root, bg="#34495e", width=250)
        panel_lateral.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Label(
            panel_lateral,
            text="CONFIGURACIÓN INICIAL",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#34495e",
        ).pack(pady=10)

        tk.Button(
            panel_lateral,
            text="Seleccionar Clave Privada",
            command=self.seleccionar_privada,
            bg="#7f8c8d",
            fg="white",
        ).pack(fill=tk.X, padx=10, pady=5)
        tk.Label(
            panel_lateral,
            textvariable=self.ruta_privada,
            fg="#bdc3c7",
            bg="#34495e",
            font=("Arial", 8),
            wraplength=220,
        ).pack(pady=2)

        tk.Button(
            panel_lateral,
            text="Seleccionar Baúl (.bin)",
            command=self.seleccionar_baul,
            bg="#7f8c8d",
            fg="white",
        ).pack(fill=tk.X, padx=10, pady=5)
        tk.Label(
            panel_lateral,
            textvariable=self.ruta_baul,
            fg="#bdc3c7",
            bg="#34495e",
            font=("Arial", 8),
            wraplength=220,
        ).pack(pady=2)

        tk.Frame(panel_lateral, height=2, bd=1, bg="#2c3e50").pack(
            fill=tk.X, padx=10, pady=10
        )

        tk.Label(panel_lateral, text="¿Primera vez?", fg="white", bg="#34495e").pack()
        tk.Button(
            panel_lateral,
            text="🔑 Inicializar Sistema Nuevo",
            command=self.ventana_inicializar,
            bg="#27ae60",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(fill=tk.X, padx=10, pady=5)

        # PANEL PRINCIPAL
        panel_principal = tk.Frame(self.root, bg="#2c3e50")
        panel_principal.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Barra superior (Se arregló el empaquetado para que no aplaste el botón)
        barra_superior = tk.Frame(panel_principal, bg="#2c3e50")
        barra_superior.pack(fill=tk.X, pady=5)

        tk.Label(
            barra_superior, text="Contraseña Maestra:", fg="white", bg="#2c3e50"
        ).pack(side=tk.LEFT, padx=5)
        self.entry_master = tk.Entry(barra_superior, show="*", width=18)
        self.entry_master.pack(side=tk.LEFT, padx=5)

        tk.Button(
            barra_superior,
            text="Desencriptar y Listar",
            command=self.listar_registros,
            bg="#2980b9",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            barra_superior,
            text="Agregar Credencial",
            command=self.ventana_agregar,
            bg="#e67e22",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(side=tk.RIGHT, padx=10)

        # Tabla dinámica de registros
        self.tabla = ttk.Treeview(
            panel_principal, columns=("Servicio", "Contraseña"), show="headings"
        )
        self.tabla.heading("Servicio", text="Sitio / Servicio / Aplicación")
        self.tabla.heading("Contraseña", text="Contraseña Protegida")
        self.tabla.column("Servicio", width=200)
        self.tabla.column("Contraseña", width=200)
        self.tabla.pack(fill=tk.BOTH, expand=True, pady=5)

        # BARRA INFERIOR: Botones de Gestión (Modificar y Eliminar)
        barra_inferior = tk.Frame(panel_principal, bg="#2c3e50")
        barra_inferior.pack(fill=tk.X, pady=10)

        tk.Button(
            barra_inferior,
            text="✏️ Modificar Seleccionado",
            command=self.ventana_modificar,
            bg="#d35400",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            barra_inferior,
            text="🗑️ Eliminar Seleccionado",
            command=self.ejecutar_eliminar,
            bg="#c0392b",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(side=tk.LEFT, padx=5)

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

    def listar_registros(self):
        if not self.ruta_baul.get() or not self.ruta_privada.get():
            messagebox.showerror(
                "Error", "Selecciona el baúl y tu clave privada en el panel izquierdo."
            )
            return
        passphrase_str = self.entry_master.get()
        if not passphrase_str:
            messagebox.showwarning("Atención", "Ingresa la contraseña maestra.")
            return

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            from cripto import decrypt_records_from_file

            records = decrypt_records_from_file(
                self.ruta_baul.get(),
                self.ruta_privada.get(),
                passphrase_str.encode("utf-8"),
            )
            if not records:
                return
            for servicio, clave in records.items():
                self.tabla.insert("", tk.END, values=(servicio, clave))
        except Exception as e:
            messagebox.showerror(
                "Error Criptográfico", "Contraseña maestra incorrecta o archivo dañado."
            )

    def ventana_inicializar(self):
        win = tk.Toplevel(self.root)
        win.title("Inicializar Sistema")
        win.geometry("400x230")
        win.grab_set()

        tk.Label(
            win,
            text="Crear Clave Maestra para los archivos:",
            font=("Arial", 10, "bold"),
        ).pack(pady=10)
        entry_pass = tk.Entry(win, show="*", width=30)
        entry_pass.pack(pady=5)

        def procesar_inicializacion():
            password = entry_pass.get()
            if len(password) < 4:
                messagebox.showerror("Error", "Mínimo 4 caracteres.")
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
                messagebox.showinfo("Éxito", "Archivos generados automáticamente.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(
            win,
            text="🚀 Generar Archivos Blindados",
            command=procesar_inicializacion,
            bg="#27ae60",
            fg="white",
        ).pack(pady=20)

    def ventana_agregar(self):
        if not self.ruta_baul.get() or not self.ruta_privada.get():
            messagebox.showerror("Error", "Configura los archivos del panel izquierdo.")
            return
        win = tk.Toplevel(self.root)
        win.title("Nuevo Registro")
        win.geometry("400x280")
        win.grab_set()

        tk.Label(win, text="Nombre del Servicio:").pack(pady=5)
        entry_name = tk.Entry(win, width=30)
        entry_name.pack(pady=5)

        tk.Label(win, text="Contraseña:").pack(pady=5)
        entry_key = tk.Entry(win, width=30)
        entry_key.pack(pady=5)

        def auto_generar():
            clave_segura = utils.generate_password(length=14)
            entry_key.delete(0, tk.END)
            entry_key.insert(0, clave_segura)

        tk.Button(
            win,
            text="⚡ Generar Segura",
            command=auto_generar,
            bg="#9b59b6",
            fg="white",
        ).pack(pady=5)

        def registrar():
            name = entry_name.get()
            pwd = entry_key.get()
            master = self.entry_master.get()
            if not name or not pwd or not master:
                messagebox.showerror("Error", "Completa todos los campos.")
                return
            try:
                negocio.add_record(
                    self.ruta_baul.get(),
                    self.ruta_privada.get(),
                    "public.pem",
                    name,
                    pwd,
                    master.encode("utf-8"),
                )
                messagebox.showinfo("Éxito", f"Registro '{name}' guardado.")
                win.destroy()
                self.listar_registros()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(
            win,
            text="💾 Guardar en el Baúl",
            command=registrar,
            bg="#e67e22",
            fg="white",
        ).pack(pady=15)

    # --- NUEVA FUNCIÓN: MODIFICAR REGISTRO ---
    def ventana_modificar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Selecciona una fila de la tabla para modificar."
            )
            return

        # Obtenemos los datos de la fila seleccionada
        item_data = self.tabla.item(seleccion[0], "values")
        servicio_nombre = item_data[0]

        win = tk.Toplevel(self.root)
        win.title(f"Modificar - {servicio_nombre}")
        win.geometry("400x200")
        win.grab_set()

        tk.Label(win, text=f"Nueva contraseña para {servicio_nombre}:").pack(pady=15)
        entry_nueva_key = tk.Entry(win, width=30)
        entry_nueva_key.pack(pady=5)
        entry_nueva_key.insert(
            0, item_data[1]
        )  # Carga la clave actual para editar rápido

        def confirmar_modificacion():
            nueva_pwd = entry_nueva_key.get()
            master = self.entry_master.get()
            if not nueva_pwd or not master:
                messagebox.showerror("Error", "Completa los campos.")
                return
            try:
                # Conectamos con negocio.py
                negocio.modify_record(
                    self.ruta_baul.get(),
                    self.ruta_privada.get(),
                    master.encode("utf-8"),
                    "public.pem",
                    servicio_nombre,
                    nueva_pwd,
                )
                messagebox.showinfo("Éxito", "Registro modificado correctamente.")
                win.destroy()
                self.listar_registros()  # Recarga la tabla
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(
            win,
            text="✏️ Actualizar Contraseña",
            command=confirmar_modificacion,
            bg="#d35400",
            fg="white",
        ).pack(pady=15)

    # --- NUEVA FUNCIÓN: ELIMINAR REGISTRO ---
    def ejecutar_eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Selecciona una fila de la tabla para eliminar."
            )
            return

        item_data = self.tabla.item(seleccion[0], "values")
        servicio_nombre = item_data[0]
        master = self.entry_master.get()

        if not master:
            messagebox.showerror(
                "Error", "Ingresa la contraseña maestra para validar la eliminación."
            )
            return

        # Pregunta de confirmación al usuario
        if messagebox.askyesno(
            "Confirmar",
            f"¿Estás seguro de que deseas eliminar el registro de '{servicio_nombre}'?",
        ):
            try:
                # Conectamos con negocio.py
                negocio.delete_record(
                    self.ruta_baul.get(),
                    self.ruta_privada.get(),
                    master.encode("utf-8"),
                    "public.pem",
                    servicio_nombre,
                )
                messagebox.showinfo("Éxito", "Registro eliminado.")
                self.listar_registros()  # Recarga la tabla
            except Exception as e:
                messagebox.showerror("Error", str(e))


def arrancar_interfaz():
    root = tk.Tk()
    app = AdminContrasenasGUI(root)
    root.mainloop()
