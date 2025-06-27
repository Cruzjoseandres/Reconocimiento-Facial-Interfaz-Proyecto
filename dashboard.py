import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import cv2
from PIL import Image, ImageTk

class UserDashboard:
    def __init__(self, parent, logic, user_name, user_data):
        """
        Inicializa la ventana de dashboard del usuario

        Args:
            parent: Ventana padre (root)
            logic: Instancia de FaceAppLogic
            user_name: Nombre del usuario detectado
            user_data: Tupla con los datos del usuario (habilitado, fecha_registro, carnet_id)
        """
        self.parent = parent
        self.logic = logic
        self.user_name = user_name
        self.habilitado, self.fecha_registro, self.carnet_id = user_data

        self.window = None
        self.current_frame = None

    def show(self):
        """Muestra la ventana de dashboard del usuario"""
        if self.window is not None:
            self.window.destroy()

        self.window = tk.Toplevel(self.parent)
        self.window.title(f"Dashboard - {self.user_name}")
        self.window.geometry("800x600")
        self.window.configure(bg="#f8f9fa")

        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure('TFrame', background='#f8f9fa')
        self.style.configure('TLabel', background='#f8f9fa')
        self.style.configure('TButton', background='#007bff')
        self.style.configure('Header.TLabel', font=("Segoe UI", 16, "bold"), background='#f8f9fa')
        self.style.configure('Subheader.TLabel', font=("Segoe UI", 12, "bold"), background='#f8f9fa')
        self.style.configure('Info.TLabel', font=("Segoe UI", 11), background='#f8f9fa')
        self.style.configure('Accent.TButton', font=('Segoe UI', 11, 'bold'))

        # Panel principal con pestañas
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Pestaña Mis Datos
        self.tab_datos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_datos, text=" Mis Datos ")

        # Pestaña Renovar Días
        self.tab_renovar = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_renovar, text=" Renovar Días ")

        # Configurar contenido de las pestañas
        self._setup_datos_tab()
        self._setup_renovar_tab()

        # Centrar la ventana
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def _setup_datos_tab(self):
        """Configura la pestaña de Mis Datos con campos editables"""
        # Header
        header_frame = ttk.Frame(self.tab_datos)
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Label(header_frame, text=f"Bienvenido/a, {self.user_name}", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header_frame, text="Edite sus datos personales y guarde los cambios", style="Info.TLabel").pack(anchor="w", pady=5)

        # Marco para datos personales
        data_frame = ttk.LabelFrame(self.tab_datos, text="Información Personal")
        data_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Formulario para editar datos
        form_frame = ttk.Frame(data_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Nombre
        ttk.Label(form_frame, text="Nombre:", style="Subheader.TLabel").grid(row=0, column=0, sticky="w", pady=10)
        self.entry_nombre = ttk.Entry(form_frame, width=40, font=("Segoe UI", 10))
        self.entry_nombre.grid(row=0, column=1, sticky="w", padx=20, pady=10)
        self.entry_nombre.insert(0, self.user_name)

        # Carnet ID
        ttk.Label(form_frame, text="ID de Carnet:", style="Subheader.TLabel").grid(row=1, column=0, sticky="w", pady=10)
        self.entry_carnet = ttk.Entry(form_frame, width=40, font=("Segoe UI", 10))
        self.entry_carnet.grid(row=1, column=1, sticky="w", padx=20, pady=10)
        self.entry_carnet.insert(0, self.carnet_id if self.carnet_id else "")

        # Estado
        ttk.Label(form_frame, text="Estado:", style="Subheader.TLabel").grid(row=2, column=0, sticky="w", pady=10)
        estado = "Activo" if self.habilitado else "Desactivado"
        color = "green" if self.habilitado else "red"
        estado_label = ttk.Label(form_frame, text=estado, style="Info.TLabel")
        estado_label.grid(row=2, column=1, sticky="w", padx=20, pady=10)
        estado_label.configure(foreground=color)

        # Fecha de registro
        ttk.Label(form_frame, text="Fecha de registro:", style="Subheader.TLabel").grid(row=3, column=0, sticky="w", pady=10)
        fecha_label = ttk.Label(form_frame, text=self.fecha_registro if self.fecha_registro else "No registrado", style="Info.TLabel")
        fecha_label.grid(row=3, column=1, sticky="w", padx=20, pady=10)

        # Días restantes
        ttk.Label(form_frame, text="Días restantes:", style="Subheader.TLabel").grid(row=4, column=0, sticky="w", pady=10)
        dias_restantes = 0
        if self.fecha_registro:
            fecha = datetime.strptime(self.fecha_registro, "%Y-%m-%d")
            dias = 30 - (datetime.now() - fecha).days
            if dias > 0:
                dias_restantes = dias

        dias_label = ttk.Label(form_frame, text=str(dias_restantes), style="Info.TLabel")
        dias_label.grid(row=4, column=1, sticky="w", padx=20, pady=10)

        if dias_restantes <= 5:
            dias_label.configure(foreground="orange")

        # Botón para guardar cambios
        save_button = ttk.Button(form_frame, text="Guardar Cambios",
                              command=self._guardar_datos_personales,
                              style='Accent.TButton')
        save_button.grid(row=5, column=0, columnspan=2, pady=20)

        # Configurar columnas
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=3)

    def _guardar_datos_personales(self):
        """Guarda los datos personales editados en la base de datos"""
        try:
            nuevo_nombre = self.entry_nombre.get().strip()
            nuevo_carnet = self.entry_carnet.get().strip()

            if not nuevo_nombre:
                messagebox.showwarning("Advertencia", "El nombre no puede estar vacío")
                return

            # Obtener el ID del usuario actual
            self.logic.cursor.execute(
                "SELECT id FROM personas WHERE nombre = ?", (self.user_name,)
            )
            result = self.logic.cursor.fetchone()

            if not result:
                messagebox.showerror("Error", "No se pudo encontrar el usuario en la base de datos")
                return

            user_id = result[0]

            # Actualizar en la base de datos
            self.logic.cursor.execute(
                "UPDATE personas SET nombre = ?, carnet_id = ? WHERE id = ?",
                (nuevo_nombre, nuevo_carnet, user_id)
            )
            self.logic.com.commit()

            # Si cambió el nombre, actualizar la variable local
            old_name = self.user_name
            if nuevo_nombre != self.user_name:
                self.user_name = nuevo_nombre
                self.window.title(f"Dashboard - {self.user_name}")

            # Actualizar datos locales
            self.carnet_id = nuevo_carnet

            # Reconstruir la pestaña con los datos actualizados
            for widget in self.tab_datos.winfo_children():
                widget.destroy()

            self._setup_datos_tab()

            # Re-entrenar el modelo si cambió el nombre
            if nuevo_nombre != old_name:
                self.logic.entrenar_modelo()

            messagebox.showinfo("Éxito", "Datos personales actualizados correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los cambios: {e}")

    def _setup_renovar_tab(self):
        """Configura la pestaña de Renovar Días"""
        # Header
        header_frame = ttk.Frame(self.tab_renovar)
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Label(header_frame, text="Renovar suscripción", style="Header.TLabel").pack(anchor="w")

        # Contenido
        content_frame = ttk.Frame(self.tab_renovar)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Explicación
        info_text = (
            "Al renovar su suscripción, se añadirán 30 días adicionales a su cuenta.\n\n"
            "Si su cuenta está vencida, se reactivará automáticamente."
        )

        info_label = ttk.Label(content_frame, text=info_text, wraplength=600, justify="left", style="Info.TLabel")
        info_label.pack(anchor="w", pady=20)

        # Calcular fecha de vencimiento actual y nueva
        fecha_actual = "No disponible"
        fecha_nueva = "No disponible"

        if self.fecha_registro:
            fecha = datetime.strptime(self.fecha_registro, "%Y-%m-%d")
            fecha_vencimiento = fecha + timedelta(days=30)
            fecha_actual = fecha_vencimiento.strftime("%d/%m/%Y")

            fecha_nueva_dt = fecha_vencimiento + timedelta(days=30)
            fecha_nueva = fecha_nueva_dt.strftime("%d/%m/%Y")

        # Mostrar fechas
        dates_frame = ttk.Frame(content_frame)
        dates_frame.pack(fill=tk.X, pady=20)

        ttk.Label(dates_frame, text="Fecha de vencimiento actual:", style="Subheader.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Label(dates_frame, text=fecha_actual, style="Info.TLabel").grid(row=0, column=1, sticky="w", padx=20, pady=5)

        ttk.Label(dates_frame, text="Nueva fecha de vencimiento:", style="Subheader.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Label(dates_frame, text=fecha_nueva, style="Info.TLabel").grid(row=1, column=1, sticky="w", padx=20, pady=5)

        # Botón de renovación
        renew_button = ttk.Button(content_frame, text="Renovar por 30 días",
                               command=self._renovar_suscripcion,
                               style='Accent.TButton')
        renew_button.pack(pady=30)

    def _renovar_suscripcion(self):
        """Renueva la suscripción del usuario por 30 días"""
        try:
            # Actualizar fecha de registro sumando 30 días
            if self.fecha_registro:
                fecha_actual = datetime.strptime(self.fecha_registro, "%Y-%m-%d")
                dias_restantes = max(0, 30 - (datetime.now() - fecha_actual).days)
                # La nueva fecha es la actual más los días restantes (si hay) más 30 días adicionales
                nueva_fecha = datetime.now() - timedelta(days=30) + timedelta(days=dias_restantes + 30)
            else:
                nueva_fecha = datetime.now()

            # Actualizar en la base de datos
            nueva_fecha_str = nueva_fecha.strftime("%Y-%m-%d")
            self.logic.cursor.execute(
                "UPDATE personas SET fecha_registro = ?, habilitado = 1, expirado = 0 WHERE nombre = ?",
                (nueva_fecha_str, self.user_name)
            )
            self.logic.com.commit()

            # Actualizar datos locales
            self.fecha_registro = nueva_fecha_str
            self.habilitado = 1

            # Reconstruir las pestañas con los datos actualizados
            for widget in self.tab_datos.winfo_children():
                widget.destroy()
            for widget in self.tab_renovar.winfo_children():
                widget.destroy()

            self._setup_datos_tab()
            self._setup_renovar_tab()

            messagebox.showinfo("Éxito", "Suscripción renovada con éxito por 30 días adicionales.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo renovar la suscripción: {e}")

    def update_photo(self, face_img):
        # Esta función ya no se utiliza pero la dejamos por compatibilidad
        pass
