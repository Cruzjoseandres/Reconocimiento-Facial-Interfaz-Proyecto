import tkinter as tk
from tkinter import messagebox, ttk
import cv2
from PIL import Image, ImageTk
from datetime import datetime


class AdminWindow:
    def __init__(self, parent, logic, cap):
        """
        Inicializa la ventana de administración

        """
        self.parent = parent
        self.logic = logic
        self.cap = cap
        self.window = None

    def show(self):
        if self.window is not None:
            self.window.destroy()

        self.window = tk.Toplevel(self.parent)
        self.window.title("Panel de Administración")
        self.window.geometry("1000x700")
        self.window.configure(bg="#f8f9fa")

        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure('TLabelframe', background='#f8f9fa')
        self.style.configure('TFrame', background='#f8f9fa')

        # Título principal
        title_frame = ttk.Frame(self.window)
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 5))

        title_label = ttk.Label(title_frame, text="Panel de Administración",
                                font=("Segoe UI", 18, "bold"))
        title_label.pack()

        subtitle_label = ttk.Label(title_frame, text="Gestión de Usuarios",
                                   font=("Segoe UI", 12))
        subtitle_label.pack(pady=(0, 10))

        # Barra de búsqueda
        search_frame = ttk.Frame(self.window)
        search_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Label(search_frame, text="Buscar:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=40, font=("Segoe UI", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)

        search_button = ttk.Button(search_frame, text="Buscar", command=self.buscar_registros)
        search_button.pack(side=tk.LEFT, padx=5)

        # Panel principal con pestañas
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Pestaña de listado
        list_tab = ttk.Frame(notebook)
        notebook.add(list_tab, text=" Listado de Usuarios ")

        # Tabla de usuarios
        table_frame = ttk.Frame(list_tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Estilo personalizado para la tabla
        self.style.configure("Treeview",
                             background="#ffffff",
                             foreground="#333333",
                             rowheight=25,
                             fieldbackground="#ffffff",
                             font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading",
                             font=("Segoe UI", 10, "bold"),
                             background="#e6e6e6")
        self.style.map("Treeview", background=[("selected", "#0078d7")])

        # Scrollbars para la tabla
        table_scroll_y = ttk.Scrollbar(table_frame)
        table_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        table_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        table_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Tabla con columnas mejoradas
        self.tree = ttk.Treeview(
            table_frame,
            columns=("id", "nombre", "estado", "dias", "carnet"),
            show="headings",
            selectmode="browse",
            yscrollcommand=table_scroll_y.set,
            xscrollcommand=table_scroll_x.set)

        self.tree.bind("<Double-1>", self.abrir_edicion)

        # Configuración de scrollbars
        table_scroll_y.config(command=self.tree.yview)
        table_scroll_x.config(command=self.tree.xview)

        # Configurar columnas
        self.tree.heading("id", text="ID", anchor=tk.W)
        self.tree.heading("nombre", text="Nombre", anchor=tk.W)
        self.tree.heading("estado", text="Estado", anchor=tk.W)
        self.tree.heading("dias", text="Días Restantes", anchor=tk.W)
        self.tree.heading("carnet", text="Carnet ID", anchor=tk.W)

        self.tree.column("id", width=50, anchor=tk.W)
        self.tree.column("nombre", width=200, anchor=tk.W)
        self.tree.column("estado", width=100, anchor=tk.W)
        self.tree.column("dias", width=120, anchor=tk.W)
        self.tree.column("carnet", width=120, anchor=tk.W)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Pestaña de edición
        edit_tab = ttk.Frame(notebook)
        notebook.add(edit_tab, text=" Editar Usuario ")

        # Panel de formulario
        form_frame = ttk.LabelFrame(edit_tab, text="Datos de Usuario", padding=15)
        form_frame.pack(fill=tk.X, expand=False, padx=10, pady=10)

        # Formulario con mejor layout
        field_frame = ttk.Frame(form_frame)
        field_frame.pack(fill=tk.X, pady=10)

        # ID (oculto) e ID visible pero no editable
        id_frame = ttk.Frame(field_frame)
        id_frame.pack(fill=tk.X, pady=5)

        ttk.Label(id_frame, text="ID:", width=15).pack(side=tk.LEFT)
        self.entry_id = ttk.Entry(id_frame, width=15, state="readonly")
        self.entry_id.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Nombre
        nombre_frame = ttk.Frame(field_frame)
        nombre_frame.pack(fill=tk.X, pady=5)

        ttk.Label(nombre_frame, text="Nombre:", width=15).pack(side=tk.LEFT)
        self.entry_nombre = ttk.Entry(nombre_frame)
        self.entry_nombre.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Carnet
        carnet_frame = ttk.Frame(field_frame)
        carnet_frame.pack(fill=tk.X, pady=5)

        ttk.Label(carnet_frame, text="Carnet ID:", width=15).pack(side=tk.LEFT)
        self.entry_carnet = ttk.Entry(carnet_frame)
        self.entry_carnet.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Botones de acción
        buttons_frame = ttk.Frame(edit_tab)
        buttons_frame.pack(fill=tk.X, pady=15, padx=10)

        # Botones con iconos (puedes añadir iconos aquí)
        self.btn_nuevo = ttk.Button(buttons_frame, text="✚ Nuevo Usuario",
                                    command=self.nuevo_registro,
                                    style="Success.TButton", width=18)
        self.btn_nuevo.pack(side=tk.LEFT, padx=5)

        self.btn_actualizar = ttk.Button(buttons_frame, text="✎ Actualizar",
                                         command=self.actualizar_registro,
                                         style="Info.TButton", width=18)
        self.btn_actualizar.pack(side=tk.LEFT, padx=5)

        self.btn_eliminar = ttk.Button(buttons_frame, text="✖ Eliminar",
                                       command=self.eliminar_registro,
                                       style="Danger.TButton", width=18)
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)

        self.btn_refrescar = ttk.Button(buttons_frame, text="↻ Refrescar",
                                        command=self.refrescar_tabla,
                                        style="Secondary.TButton", width=18)
        self.btn_refrescar.pack(side=tk.RIGHT, padx=5)

        # Estilos para botones
        self.style.configure("Success.TButton", background="#28a745", foreground="white")
        self.style.configure("Info.TButton", background="#17a2b8", foreground="white")
        self.style.configure("Danger.TButton", background="#dc3545", foreground="white")
        self.style.configure("Secondary.TButton", background="#6c757d", foreground="white")

        # Vincular evento de selección de fila
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_fila)

        # Barra de estado
        self.status_bar = ttk.Label(self.window, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Cargar datos iniciales
        self.refrescar_tabla()

        # Centrar la ventana
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def buscar_registros(self):
        # Implementar búsqueda en la tabla
        texto = self.search_entry.get().lower().strip()
        self.refrescar_tabla(filtro=texto)

    def refrescar_tabla(self, filtro=None):
        # Limpia la tabla
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Obtiene datos actualizados
        filas = self.logic.obtener_todas_personas_con_id()
        contador = 0

        for fila in filas:
            id_persona, nombre, habilitado, fecha_registro, carnet_id = fila

            # Aplicar filtro si existe
            if filtro and filtro not in str(id_persona).lower() and filtro not in nombre.lower() and \
                    (not carnet_id or filtro not in carnet_id.lower()):
                continue

            dias_restantes = "?"
            if fecha_registro:
                fecha = datetime.strptime(fecha_registro, "%Y-%m-%d")
                dias = 30 - (datetime.now() - fecha).days
                if dias <= 0:
                    dias_restantes = "Expirado"
                else:
                    dias_restantes = str(dias)

            estado = "✓ Activo" if habilitado else "✗ Deshabilitado"

            # Alternar colores de fila
            tag = "even" if contador % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(id_persona, nombre, estado, dias_restantes, carnet_id), tags=(tag,))
            contador += 1

        # Configurar colores alternados
        self.tree.tag_configure("odd", background="#f5f5f5")
        self.tree.tag_configure("even", background="#ffffff")

        # Actualizar barra de estado
        self.status_bar.config(text=f"Total de registros: {contador}")

    def seleccionar_fila(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        valores = item['values']

        if not valores or len(valores) < 5:
            return

        # Limpia y llena los campos

        self.entry_id.configure(state="normal")  # Habilitar temporalmente para editar
        self.entry_id.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_carnet.delete(0, tk.END)

        # Insertar valores asegurándose de que sean strings
        self.entry_id.insert(0, str(valores[0]))
        self.entry_nombre.insert(0, str(valores[1]))
        self.entry_carnet.insert(0, str(valores[4]) if valores[4] else "")
        self.entry_id.configure(state="readonly")

    def refrescar_tabla(self, filtro=None):
        # Limpia la tabla
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Obtiene datos actualizados
        filas = self.logic.obtener_todas_personas_con_id()
        contador = 0

        for fila in filas:
            id_persona, nombre, habilitado, fecha_registro, carnet_id = fila

            # Aplicar filtro si existe
            if filtro and filtro not in str(id_persona).lower() and filtro not in nombre.lower() and \
                    (not carnet_id or filtro not in carnet_id.lower()):
                continue

            dias_restantes = "?"
            if fecha_registro:
                fecha = datetime.strptime(fecha_registro, "%Y-%m-%d")
                dias = 30 - (datetime.now() - fecha).days
                if dias <= 0:
                    dias_restantes = "Expirado"
                else:
                    dias_restantes = str(dias)

            estado = "✓ Activo" if habilitado else "✗ Deshabilitado"

            # Alternar colores de fila
            tag = "even" if contador % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(id_persona, nombre, estado, dias_restantes, carnet_id), tags=(tag,))
            contador += 1

        # Configurar colores alternados
        self.tree.tag_configure("odd", background="#f5f5f5")
        self.tree.tag_configure("even", background="#ffffff")

        # Actualizar barra de estado
        self.status_bar.config(text=f"Total de registros: {contador}")

    def nuevo_registro(self):
        # Abre ventana para capturar nuevo rostro
        nombre = self.entry_nombre.get().strip()
        carnet_id = self.entry_carnet.get().strip()

        if not nombre:
            messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
            return

        # Capturar rostro
        top = tk.Toplevel(self.window)
        top.title("Capturar Rostro")
        top.geometry("500x400")

        # Crear un marco para mostrar el progreso
        progress_frame = ttk.Frame(top)
        progress_frame.pack(pady=5)
        progress_label = ttk.Label(progress_frame, text="Buscando rostro para iniciar captura...")
        progress_label.pack()

        # Crear una barra de progreso
        progress_bar = ttk.Progressbar(top, orient="horizontal", length=300, mode="determinate", maximum=10)
        progress_bar.pack(pady=5)

        label_video_capture = tk.Label(top)
        label_video_capture.pack(pady=10)

        # Variable para almacenar las imágenes capturadas
        captured_images = []
        is_capturing = [False]  # Usar una lista para poder modificarla en la función anidada
        rostro_detectado = [False]  # Para controlar si ya se detectó un rostro

        def guardar_imagenes():
            try:
                self.logic.registrar_rostro_multiple(nombre, captured_images[:10], carnet_id)
                messagebox.showinfo("Éxito", f"10 imágenes del rostro de {nombre} registradas correctamente.")
                top.destroy()
                self.refrescar_tabla()
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

                # Mostrar la imagen en la interfaz
                img = cv2.cvtColor(frame_copia, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                label_video_capture.imgtk = imgtk
                label_video_capture.configure(image=imgtk)
                label_video_capture.img = imgtk

                # Si estamos en modo captura y hay un rostro, capturamos la imagen
                if is_capturing[0] and len(faces) > 0:
                    x, y, w, h = faces[0]  # Capturar el primer rostro detectado
                    face_roi = frame[y:y + h, x:x + w]
                    captured_images.append(face_roi)

                    # Actualizar la barra de progreso y el texto
                    num_captured = len(captured_images)
                    progress_bar["value"] = num_captured
                    progress_label.config(text=f"Capturando imágenes ({num_captured}/10)")

                    # Señal visual de captura
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

                top.after(30, actualizar_captura)

        # Iniciar la actualización de la cámara que ahora incluye la detección, captura y guardado automático
        actualizar_captura()


    def actualizar_registro(self):
        id_persona = self.entry_id.get().strip()
        nombre = self.entry_nombre.get().strip()
        carnet_id = self.entry_carnet.get().strip()

        if not id_persona or not nombre:
            messagebox.showwarning("Advertencia", "Seleccione un registro válido.")
            return

        try:
            self.logic.actualizar_persona(id_persona, nombre, carnet_id)
            messagebox.showinfo("Éxito", "Registro actualizado correctamente.")
            self.refrescar_tabla()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el registro: {e}")

    def eliminar_registro(self):
        id_persona = self.entry_id.get().strip()

        if not id_persona:
            messagebox.showwarning("Advertencia", "Seleccione un registro válido.")
            return

        confirmacion = messagebox.askyesno("Confirmar",
                                           "¿Está seguro que desea eliminar este registro? Esta acción no se puede deshacer.")

        if confirmacion:
            try:
                self.logic.eliminar_persona(id_persona)
                messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
                self.refrescar_tabla()

                # Limpia los campos
                self.entry_id.delete(0, tk.END)
                self.entry_nombre.delete(0, tk.END)
                self.entry_carnet.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el registro: {e}")

    def abrir_edicion(self, event):
        # Asegurarse de que haya una selección
        selected = self.tree.selection()
        if not selected:
            return

        # Obtener el ítem seleccionado
        item = self.tree.item(selected[0])
        valores = item['values']

        # Seleccionar la pestaña de edición (índice 1)
        for tab in self.window.winfo_children():
            if isinstance(tab, ttk.Notebook):
                tab.select(1)  # Selecciona la segunda pestaña (índice 1)
                break

        # Cargar los datos en los campos de edición
        if valores:
            self.seleccionar_fila(event)