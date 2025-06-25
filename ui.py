import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import cv2
from datetime import datetime, timedelta
from logic import FaceAppLogic
from admin import AdminWindow

class FaceAppUI:
    def __init__(self, root, logic: FaceAppLogic):
        self.root = root
        self.logic = logic
        self.root.title("Sistema de Reconocimiento Facial")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f5f5f5")

        # Configurar estilo
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')
        self.estilo.configure('TFrame', background='#f5f5f5')
        self.estilo.configure('TLabel', background='#f5f5f5', font=('Segoe UI', 10))
        self.estilo.configure('TEntry', font=('Segoe UI', 10))
        self.estilo.configure('TButton', font=('Segoe UI', 10))

        # Marco principal con padding
        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Encabezado
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=10)

        self.title_label = ttk.Label(self.header_frame, text="SISTEMA DE CONTROL DE ACCESO",
                                     font=('Segoe UI', 24, 'bold'))
        self.title_label.pack()

        self.subtitle_label = ttk.Label(self.header_frame, text="Reconocimiento Facial",
                                        font=('Segoe UI', 14))
        self.subtitle_label.pack(pady=5)

        # Contenedor para video y panel de control
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Panel de video con borde elevado
        self.video_frame = ttk.Frame(self.content_frame, borderwidth=2, relief="ridge")
        self.video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.video_label = ttk.Label(self.video_frame, text="Inicializando cámara...")
        self.video_label.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Panel de control con pestañas
        self.control_frame = ttk.Frame(self.content_frame, width=350)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

        self.notebook = ttk.Notebook(self.control_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestaña de registro
        self.register_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.register_tab, text=" Registro ")

        ttk.Label(self.register_tab, text="Nombre de la persona:", font=('Segoe UI', 11)).pack(anchor='w', pady=(10, 5))
        self.entry_name = ttk.Entry(self.register_tab, width=30, font=('Segoe UI', 11))
        self.entry_name.pack(fill=tk.X, pady=(0, 15))

        self.button_register = ttk.Button(
            self.register_tab, text="Registrar Nuevo Rostro", command=self.registrar_rostro,
            style='Accent.TButton', width=25)
        self.estilo.configure('Accent.TButton', background='#0078d7', foreground='white')
        self.estilo.map('Accent.TButton', background=[('active', '#005fa3')])
        self.button_register.pack(pady=10)

        # Separador visual
        ttk.Separator(self.register_tab, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        # Estado de reconocimiento
        self.status_frame = ttk.LabelFrame(self.register_tab, text="Estado de Reconocimiento", padding="10")
        self.status_frame.pack(fill=tk.X, pady=10)

        self.status_label = ttk.Label(self.status_frame, text="Esperando...", font=('Segoe UI', 10, 'italic'))
        self.status_label.pack(pady=5)

        # Pestaña de administración
        self.admin_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.admin_tab, text=" Administración ")

        ttk.Label(self.admin_tab, text="Nombre para actualizar:", font=('Segoe UI', 11)).pack(anchor='w', pady=(10, 5))
        self.entry_update = ttk.Entry(self.admin_tab, width=30, font=('Segoe UI', 11))
        self.entry_update.pack(fill=tk.X, pady=(0, 10))

        # Frame para botones de acceso
        self.access_frame = ttk.Frame(self.admin_tab)
        self.access_frame.pack(fill=tk.X, pady=5)

        self.button_habilitar = ttk.Button(
            self.access_frame, text="Habilitar Acceso", command=self.habilitar_acceso,
            style='Success.TButton')
        self.estilo.configure('Success.TButton', background='#28a745', foreground='white')
        self.estilo.map('Success.TButton', background=[('active', '#218838')])
        self.button_habilitar.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)

        self.button_deshabilitar = ttk.Button(
            self.access_frame, text="Deshabilitar Acceso", command=self.deshabilitar_acceso,
            style='Danger.TButton')
        self.estilo.configure('Danger.TButton', background='#dc3545', foreground='white')
        self.estilo.map('Danger.TButton', background=[('active', '#c82333')])
        self.button_deshabilitar.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Control de días
        ttk.Separator(self.admin_tab, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        ttk.Label(self.admin_tab, text="Actualización de días:", font=('Segoe UI', 11)).pack(anchor='w', pady=(10, 5))

        self.days_frame = ttk.Frame(self.admin_tab)
        self.days_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.days_frame, text="Días:").pack(side=tk.LEFT)
        self.entry_dias = ttk.Spinbox(self.days_frame, from_=1, to=365, width=5)
        self.entry_dias.pack(side=tk.LEFT, padx=5)

        self.button_actualizar_dias = ttk.Button(
            self.admin_tab, text="Actualizar Días Disponibles",
            command=self.actualizar_dias_disponibles,
            style='Warning.TButton')
        self.estilo.configure('Warning.TButton', background='#ffc107', foreground='black')
        self.estilo.map('Warning.TButton', background=[('active', '#e0a800')])
        self.button_actualizar_dias.pack(pady=10, fill=tk.X)

        # Botón de panel administrativo completo
        ttk.Separator(self.admin_tab, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        self.button_admin = ttk.Button(
            self.admin_tab, text="Panel Administrativo Completo", command=self.mostrar_admin,
            style='Info.TButton')
        self.estilo.configure('Info.TButton', background='#17a2b8', foreground='white')
        self.estilo.map('Info.TButton', background=[('active', '#138496')])
        self.button_admin.pack(pady=10, fill=tk.X)

        # Barra de estado
        self.statusbar = ttk.Label(self.root, text="Sistema listo", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Inicializar cámara y componentes
        self.cap = cv2.VideoCapture(0)
        self.current_frame = None
        self.face_locations_actual = None

        self.admin_window = AdminWindow(self.root, self.logic, self.cap)

        self.ventana_admin = None
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        self.root.bind('<Control-a>', self.mostrar_admin)

        self.actualizar_video()

    def actualizar_video(self):
        self.logic.verificar_fechas_expiracion()
        ret, frame = self.cap.read()

        if not ret:
            self.statusbar.config(text="Error: No se puede acceder a la cámara")
            self.root.after(30, self.actualizar_video)
            return

        display_frame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.logic.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        self.face_locations_actual = faces

        # Mostrar información de reconocimiento
        if len(faces) > 0:
            self.statusbar.config(text=f"Detectados {len(faces)} rostros")
        else:
            self.statusbar.config(text="No se detectan rostros en la imagen")

        for (x, y, w, h) in faces:
            nombre = "Desconocido"
            color = (0, 255, 0)
            face_roi = frame[y:y + h, x:x + w]

            if face_roi.size > 0:
                # Usar el método de reconocimiento
                nombre_bd, confidence = self.logic.reconocer_rostro(face_roi)

                if nombre_bd != "Desconocido":
                    result = self.logic.obtener_info_persona(nombre_bd)
                    if result:
                        habilitado, fecha_registro, carnet_id = result
                        dias_restantes = "?"
                        if fecha_registro:
                            fecha = datetime.strptime(fecha_registro, "%Y-%m-%d")
                            dias_restantes = 30 - (datetime.now() - fecha).days
                            if dias_restantes <= 0:
                                dias_restantes = 0

                        # Actualizar label de estado
                        if habilitado == 0:
                            estado_texto = f"✘ {nombre_bd}: Acceso denegado"
                            self.status_label.config(foreground="red")
                            nombre = f"{nombre_bd} (DENEGADO)"
                            color = (0, 0, 255)
                        elif dias_restantes <= 5:
                            estado_texto = f"⚠ {nombre_bd}: {dias_restantes} días restantes"
                            self.status_label.config(foreground="orange")
                            nombre = f"{nombre_bd} ({dias_restantes} dias)"
                            color = (0, 165, 255)  # Naranja en BGR
                        else:
                            estado_texto = f"✓ {nombre_bd}: Acceso permitido ({dias_restantes} días)"
                            self.status_label.config(foreground="green")
                            nombre = f"{nombre_bd}"
                            color = (0, 255, 0)

                        self.status_label.config(text=estado_texto)
                else:
                    self.status_label.config(text="⚠ Persona no reconocida", foreground="gray")

            # Dibujar un rectángulo más estético con esquinas redondeadas
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)

            # Añadir fondo para el texto
            text_size = cv2.getTextSize(nombre, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)[0]
            cv2.rectangle(display_frame, (x, y - 30), (x + text_size[0] + 10, y), color, -1)
            cv2.putText(display_frame, nombre, (x + 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        self.current_frame = display_frame
        img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)

        # Ajustar el tamaño de la imagen para que quede bien en la UI
        w, h = img.size
        target_height = 480
        ratio = target_height / h
        new_width = int(w * ratio)
        img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)

        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.root.after(30, self.actualizar_video)

    def mostrar_admin(self, event=None):
        if not hasattr(self, 'admin_window'):
            self.admin_window = AdminWindow(self.root, self.logic, self.cap)
        self.admin_window.show()

    def registrar_rostro(self):
        nombre = self.entry_name.get().strip()
        if not nombre or nombre == "Nombre de la persona":
            messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
            return

        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "No se pudo capturar imagen de la cámara.")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.logic.face_cascade.detectMultiScale(gray, 1.1, 5)

        if len(faces) == 0:
            messagebox.showinfo("Info", "No se detectó ningún rostro.")
            return

        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        # Usar el nuevo método de registrar rostro
        try:
            self.logic.registrar_rostro(nombre, face_roi)
            messagebox.showinfo("Éxito", f"Rostro de {nombre} registrado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el rostro: {e}")

    def habilitar_acceso(self):
        nombre = self.entry_update.get().strip()
        if not nombre or nombre == "Nombre para actualizar":
            messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
            return
        self.logic.cursor.execute(
            "UPDATE personas SET habilitado = 1, expirado = 0 WHERE nombre = ?", (nombre,))
        self.logic.com.commit()
        messagebox.showinfo("Éxito", f"Acceso habilitado para {nombre}.")

    def deshabilitar_acceso(self):
        nombre = self.entry_update.get().strip()
        if not nombre or nombre == "Nombre para actualizar":
            messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
            return
        self.logic.cursor.execute(
            "UPDATE personas SET habilitado = 0 WHERE nombre = ?", (nombre,))
        self.logic.com.commit()
        messagebox.showinfo("Éxito", f"Acceso deshabilitado para {nombre}.")

    def actualizar_dias_disponibles(self):
        nombre = self.entry_update.get().strip()
        dias = self.entry_dias.get().strip()
        if not nombre or nombre == "Nombre para actualizar":
            messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
            return
        try:
            dias = int(dias)
            if dias < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Advertencia", "Ingrese un número de días válido.")
            return
        fecha_nueva = (datetime.now() - timedelta(days=30 - dias)).strftime("%Y-%m-%d")
        self.logic.cursor.execute(
            "UPDATE personas SET fecha_registro = ?, habilitado = 1, expirado = 0 WHERE nombre = ?",
            (fecha_nueva, nombre)
        )
        self.logic.com.commit()
        messagebox.showinfo("Éxito", f"Días disponibles actualizados para {nombre}.")




    def cerrar_aplicacion(self):
        self.cap.release()
        self.logic.cerrar()
        self.root.quit()



