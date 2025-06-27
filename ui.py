import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import cv2
from datetime import datetime, timedelta
from logic import FaceAppLogic
from admin import AdminWindow
from dashboard import UserDashboard

class FaceAppUI:
    def __init__(self, root, logic: FaceAppLogic):
        self.root = root
        self.logic = logic
        self.root.title("Sistema de Reconocimiento Facial")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f5f5f5")

        # Variables para control de dashboard
        self.user_dashboard = None
        self.dashboard_showing = False
        self.last_detected_user = None
        self.dashboard_cooldown = 0  # Evita que el dashboard se abra constantemente

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

        # Inicializar cámara con opciones robustas y reintentos
        self.cap = None
        self.camera_index = 0
        self.max_retries = 3
        self.initialize_camera()

        self.current_frame = None
        self.face_locations_actual = None

        self.admin_window = AdminWindow(self.root, self.logic, self.cap)

        self.ventana_admin = None
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        self.root.bind('<Control-a>', self.mostrar_admin)

        self.actualizar_video()

    def initialize_camera(self):
        """Intenta inicializar la cámara con reintentos y manejo de errores."""
        for attempt in range(self.max_retries):
            try:
                # Liberar cualquier instancia previa
                if self.cap is not None:
                    self.cap.release()

                # Crear una nueva instancia con configuración explícita para Windows Media Foundation
                self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_MSMF)

                if not self.cap.isOpened():
                    raise ValueError("No se puede abrir la cámara.")

                # Configurar propiedades específicas para evitar errores MSMF
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                self.cap.set(cv2.CAP_PROP_FPS, 15)  # Reducir FPS puede ayudar con la estabilidad
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

                # Verificar si podemos leer correctamente
                for check_attempt in range(3):
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        # Si la lectura fue exitosa, salimos del bucle
                        break
                    # Pequeña pausa entre intentos
                    import time
                    time.sleep(0.2)

                if not ret or frame is None:
                    raise ValueError("No se puede acceder al stream de la cámara.")

                # Configuración exitosa
                self.statusbar.config(text="Cámara lista")
                return True

            except Exception as e:
                self.statusbar.config(text=f"Error al inicializar cámara {self.camera_index}: {e}")
                print(f"Fallo al inicializar cámara {self.camera_index}: {e}")

                # Probar con la siguiente cámara
                self.camera_index = (self.camera_index + 1) % 2  # Alternar entre 0 y 1

                # Dar tiempo al sistema para liberar recursos
                import time
                time.sleep(1)

        # Si no se pudo inicializar ninguna cámara
        messagebox.showerror("Error", "No se pudo inicializar la cámara. Verifica la conexión o cierra otras aplicaciones que puedan estar usándola.")
        return False

    def actualizar_video(self):
        try:
            # Usar un mecanismo try/except más robusto
            try:
                self.logic.verificar_fechas_expiracion()

                # Verificar si la cámara está disponible
                if self.cap is None or not self.cap.isOpened():
                    self.statusbar.config(text="Cámara no disponible. Intentando reiniciar...")
                    self.initialize_camera()
                    # Si la inicialización falla, programar el siguiente intento y salir
                    if self.cap is None or not self.cap.isOpened():
                        self.root.after(2000, self.actualizar_video)
                        return

                # Intento de lectura con timeouts
                import time
                start_time = time.time()
                read_timeout = 0.5  # 500ms timeout para la lectura

                # Intentar leer frame con límite de tiempo
                ret, frame = self.cap.read()

                # Verificar si la operación tomó demasiado tiempo o falló
                if time.time() - start_time > read_timeout or not ret or frame is None:
                    # Incrementar contador de errores
                    error_count = getattr(self, 'error_count', 0) + 1
                    self.error_count = error_count

                    print(f"Error de captura #{error_count} - ret: {ret}")
                    self.statusbar.config(text=f"Problema de captura: {error_count}/3. Reintentando...")

                    # Si hay muchos errores consecutivos, forzar reinicio de cámara
                    if error_count >= 3:
                        print("Reiniciando cámara debido a errores consecutivos")
                        self.statusbar.config(text="Reiniciando dispositivo de cámara...")

                        # Liberar recursos explícitamente
                        if self.cap is not None:
                            self.cap.release()
                            self.cap = None

                        # Forzar recolección de basura para liberar recursos
                        import gc
                        gc.collect()

                        # Esperar un momento antes de reinicializar
                        time.sleep(1.0)

                        # Reintentar con parámetros diferentes
                        self.camera_index = (self.camera_index + 1) % 2
                        self.initialize_camera()
                        self.error_count = 0

                    # Esperamos más tiempo entre intentos cuando hay errores
                    self.root.after(1000, self.actualizar_video)
                    return

                # Si la lectura fue exitosa, restablecer contador de errores
                self.error_count = 0

                # Procesamiento normal de video
                display_frame = frame.copy()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detectar rostros con manejo de excepciones
                try:
                    faces = self.logic.face_cascade.detectMultiScale(
                        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                    )
                    self.face_locations_actual = faces
                except Exception as e:
                    print(f"Error en detectMultiScale: {e}")
                    faces = []

                # Mostrar información en la barra de estado
                if len(faces) > 0:
                    self.statusbar.config(text=f"Detectados {len(faces)} rostros")
                else:
                    self.statusbar.config(text="No se detectan rostros en la imagen")

                # Procesar cada rostro detectado
                for (x, y, w, h) in faces:
                    try:
                        nombre = "Desconocido"
                        color = (0, 255, 0)  # Color verde por defecto

                        # Extraer región de interés
                        face_roi = frame[y:y + h, x:x + w]

                        if face_roi.size > 0:
                            # Reconocimiento facial
                            nombre_bd, confidence = self.logic.reconocer_rostro(face_roi)

                            if nombre_bd != "Desconocido":
                                result = self.logic.obtener_info_persona(nombre_bd)
                                if result:
                                    habilitado, fecha_registro, carnet_id = result
                                    dias_restantes = "?"
                                    if fecha_registro:
                                        fecha = datetime.strptime(fecha_registro, "%Y-%m-%d")
                                        dias = 30 - (datetime.now() - fecha).days
                                        if dias <= 0:
                                            dias_restantes = 0
                                        else:
                                            dias_restantes = dias

                                    # Actualizar estado según condiciones
                                    if habilitado == 0:
                                        estado_texto = f"✘ {nombre_bd}: Acceso denegado"
                                        self.status_label.config(foreground="red")
                                        nombre = f"{nombre_bd} (DENEGADO)"
                                        color = (0, 0, 255)  # Rojo en BGR
                                    elif dias_restantes <= 5:
                                        estado_texto = f"⚠ {nombre_bd}: {dias_restantes} días restantes"
                                        self.status_label.config(foreground="orange")
                                        nombre = f"{nombre_bd} ({dias_restantes} dias)"
                                        color = (0, 165, 255)  # Naranja en BGR
                                    else:
                                        estado_texto = f"✓ {nombre_bd}: Acceso permitido ({dias_restantes} días)"
                                        self.status_label.config(foreground="green")
                                        nombre = f"{nombre_bd}"
                                        color = (0, 255, 0)  # Verde en BGR

                                    # Actualizar etiqueta de estado
                                    self.status_label.config(text=estado_texto)

                                    # Mostrar dashboard del usuario si tiene acceso permitido
                                    # Usar un cooldown para evitar abrir constantemente la ventana
                                    if habilitado == 1 and (self.dashboard_cooldown <= 0 or self.last_detected_user != nombre_bd):
                                        self.mostrar_dashboard_usuario(nombre_bd, result, face_roi)
                                        self.dashboard_cooldown = 60  # Enfriar por 60 frames (aproximadamente 2 segundos)
                                    else:
                                        self.dashboard_cooldown = max(0, self.dashboard_cooldown - 1)

                                        # Si tenemos un dashboard abierto, actualizar la foto
                                        if self.user_dashboard is not None and self.last_detected_user == nombre_bd:
                                            self.user_dashboard.update_photo(face_roi)
                            else:
                                self.status_label.config(text="⚠ Persona no reconocida", foreground="gray")
                                self.dashboard_cooldown = max(0, self.dashboard_cooldown - 1)

                        # Dibujar rectángulo alrededor del rostro
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)

                        # Añadir fondo para el texto
                        text_size = cv2.getTextSize(nombre, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)[0]
                        cv2.rectangle(display_frame, (x, y - 30), (x + text_size[0] + 10, y), color, -1)
                        cv2.putText(display_frame, nombre, (x + 5, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

                    except Exception as e:
                        print(f"Error procesando rostro: {e}")
                        continue

                # Guardar frame actual para referencia
                self.current_frame = display_frame

                # Convertir para visualización en Tkinter
                img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)

                # Redimensionar para la interfaz
                try:
                    w, h = img.size
                    target_height = 480
                    ratio = target_height / h
                    new_width = int(w * ratio)
                    img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
                except Exception as e:
                    print(f"Error al redimensionar imagen: {e}")

                # Crear PhotoImage y actualizar interfaz
                try:
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.video_label.imgtk = imgtk
                    self.video_label.configure(image=imgtk)
                except Exception as e:
                    print(f"Error al actualizar imagen en UI: {e}")

                # Programar la siguiente actualización
                if self.root.winfo_exists():
                    # Usar after_idle para evitar que se acumulen llamadas
                    self.root.after_idle(lambda: self.root.after(30, self.actualizar_video))

            except Exception as e:
                # Manejo de excepciones a nivel de ciclo de captura
                print(f"Error general en actualizar_video: {e}")
                self.statusbar.config(text=f"Error: {str(e)[:50]}...")

                # Reintentar con delay mayor
                if self.root.winfo_exists():
                    self.root.after(1500, self.actualizar_video)

        except KeyboardInterrupt:
            # Manejar explícitamente la interrupción por teclado
            print("Interrupción por teclado capturada - reintentando ciclo de video")
            if self.root.winfo_exists():
                self.root.after(2000, self.actualizar_video)

    def mostrar_admin(self, event=None):
        if not hasattr(self, 'admin_window'):
            self.admin_window = AdminWindow(self.root, self.logic, self.cap)
        self.admin_window.show()

    def registrar_rostro(self):
        nombre = self.entry_name.get().strip()
        if not nombre or nombre == "Nombre de la persona":
            messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
            return

        # Crear ventana de captura
        top = tk.Toplevel(self.root)
        top.title("Captura de Rostro")
        top.geometry("500x450")

        # Crear un marco para mostrar el progreso
        progress_frame = ttk.Frame(top)
        progress_frame.pack(pady=5)
        progress_label = ttk.Label(progress_frame, text="Buscando rostro para iniciar captura...")
        progress_label.pack()

        # Crear una barra de progreso
        progress_bar = ttk.Progressbar(top, orient="horizontal", length=300, mode="determinate", maximum=10)
        progress_bar.pack(pady=5)

        # Área de visualización de la cámara
        video_label = ttk.Label(top)
        video_label.pack(padx=10, pady=10)

        # Variables para el proceso de captura
        captured_images = []
        is_capturing = [False]
        rostro_detectado = [False]  # Para controlar si ya se detectó un rostro

        def guardar_imagenes():
            try:
                # Usar el método para registrar múltiples imágenes
                self.logic.registrar_rostro_multiple(nombre, captured_images[:10])
                messagebox.showinfo("Éxito", f"10 imágenes del rostro de {nombre} registradas correctamente.")
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el rostro: {e}")

        def actualizar_captura():
            ret, frame = self.cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.logic.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )

                frame_copia = frame.copy()

                # Si hay un rostro y no estamos capturando aún, iniciamos la captura
                if len(faces) > 0 and not is_capturing[0] and not rostro_detectado[0]:
                    is_capturing[0] = True
                    rostro_detectado[0] = True
                    progress_label.config(text="¡Rostro detectado! Capturando imágenes (0/10)")

                # Dibujar rectángulos alrededor de los rostros detectados
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame_copia, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Si estamos en modo captura y hay un rostro, capturamos la imagen
                if is_capturing[0] and len(faces) > 0:
                    x, y, w, h = faces[0]  # Capturar el primer rostro detectado
                    face_roi = frame[y:y + h, x:x + w]
                    captured_images.append(face_roi)

                    # Actualizar la barra de progreso y el texto
                    num_captured = len(captured_images)
                    progress_bar["value"] = num_captured
                    progress_label.config(text=f"Capturando imágenes ({num_captured}/10)")

                    # Señal visual de captura (rectángulo rojo)
                    cv2.rectangle(frame_copia, (x, y), (x + w, y + h), (0, 0, 255), 3)

                    if num_captured >= 10:
                        is_capturing[0] = False
                        progress_label.config(text="¡Captura completa! Guardando...")
                        # Guardar automáticamente las imágenes después de un corto retraso
                        top.after(500, guardar_imagenes)
                    else:
                        # Pequeño retraso para no tomar todas las imágenes idénticas
                        # pero lo suficientemente rápido para ser automático
                        top.after(100, actualizar_captura)
                        return

                # Mostrar la imagen en la interfaz
                img = cv2.cvtColor(frame_copia, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                video_label.imgtk = imgtk
                video_label.configure(image=imgtk)
                video_label.img = imgtk

                top.after(30, actualizar_captura)

        # Iniciar la actualización de la cámara que ahora incluye detección, captura y guardado automático
        actualizar_captura()

        # Centrar la ventana
        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f'{width}x{height}+{x}+{y}')

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

    def mostrar_dashboard_usuario(self, nombre_usuario, user_data, face_roi):
        """
        Muestra el dashboard del usuario cuando se detecta un rostro conocido

        Args:
            nombre_usuario: Nombre del usuario detectado
            user_data: Tupla con datos del usuario (habilitado, fecha_registro, carnet_id)
            face_roi: Región de interés del rostro detectado para mostrar en el dashboard
        """
        # Si ya hay un dashboard abierto para otro usuario, cerrarlo
        if self.user_dashboard is not None and self.last_detected_user != nombre_usuario:
            if hasattr(self.user_dashboard, 'window') and self.user_dashboard.window is not None:
                try:
                    self.user_dashboard.window.destroy()
                except:
                    pass
            self.user_dashboard = None
            self.dashboard_showing = False

        # Si no hay dashboard o es para otro usuario, crear uno nuevo
        if self.user_dashboard is None:
            self.user_dashboard = UserDashboard(self.root, self.logic, nombre_usuario, user_data)
            self.user_dashboard.show()
            self.dashboard_showing = True
            self.last_detected_user = nombre_usuario

        # Actualizar la foto en el dashboard si está visible
        if self.user_dashboard is not None and hasattr(self.user_dashboard, 'window'):
            if self.user_dashboard.window is not None and self.user_dashboard.window.winfo_exists():
                self.user_dashboard.update_photo(face_roi)
            else:
                # Si la ventana fue cerrada manualmente, resetear el estado
                self.user_dashboard = None
                self.dashboard_showing = False
                self.last_detected_user = None

    def cerrar_aplicacion(self):
        self.cap.release()
        self.logic.cerrar()
        self.root.quit()
