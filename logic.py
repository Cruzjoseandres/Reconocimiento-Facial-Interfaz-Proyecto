import sqlite3
import numpy as np
import cv2
from datetime import datetime

class FaceAppLogic:
    def __init__(self, db_path="rostrosv2.db"):
        self.com = sqlite3.connect(db_path)
        self.cursor = self.com.cursor()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # Crear el reconocedor LBPH
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.trained = False
        self.label_map = {}
        self.crear_tabla()
        self.entrenar_modelo()

    def crear_tabla(self):
        # Tabla principal para personas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                habilitado INTEGER DEFAULT 1,
                fecha_registro TEXT,
                expirado INTEGER DEFAULT 0,
                carnet_id TEXT
            )
        ''')

        # Tabla para almacenar múltiples imágenes por persona
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS imagenes_personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                persona_id INTEGER NOT NULL,
                encoding BLOB NOT NULL,
                FOREIGN KEY (persona_id) REFERENCES personas(id)
            )
        ''')

        self.com.commit()

    def cargar_rostros(self):
        # Consulta para obtener todas las imágenes con su correspondiente nombre de persona
        self.cursor.execute('''
            SELECT p.nombre, i.encoding 
            FROM personas p 
            JOIN imagenes_personas i ON p.id = i.persona_id
        ''')

        datos = self.cursor.fetchall()
        nombres = []
        encodings = []

        for nombre, encoding_blob in datos:
            try:
                encoding = np.frombuffer(encoding_blob, dtype=np.float64)
                if len(encoding) != 10000:  # Validar que el encoding tenga el tamaño correcto
                    continue
                nombres.append(nombre)
                encodings.append(encoding)
            except Exception as e:
                print(f"Error al procesar encoding: {e}")
                continue

        return nombres, encodings

    def entrenar_modelo(self):
        """Entrena el reconocedor con los rostros almacenados en la BD"""
        nombres, encodings = self.cargar_rostros()
        if len(encodings) == 0:
            self.trained = False
            return

        # Convertir encodings a imágenes para entrenar
        faces = []
        labels = []
        label_dict = {}

        for i, (nombre, encoding) in enumerate(zip(nombres, encodings)):
            face_img = encoding.reshape(100, 100).astype(np.uint8)
            if nombre not in label_dict:
                label_dict[nombre] = len(label_dict)
            label = label_dict[nombre]
            faces.append(face_img)
            labels.append(label)

        if len(faces) > 0:
            self.recognizer.train(faces, np.array(labels))
            self.trained = True
            self.label_map = {v: k for k, v in label_dict.items()}

    def compare_faces(self, face1, face2, threshold=0.5):
        if len(face1.shape) > 2:
            face1 = cv2.cvtColor(face1, cv2.COLOR_BGR2GRAY)
        if len(face2.shape) > 2:
            face2 = cv2.cvtColor(face2, cv2.COLOR_BGR2GRAY)
        face2 = cv2.resize(face2, (face1.shape[1], face1.shape[0]))
        hist1 = cv2.calcHist([face1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([face2], [0], None, [256], [0, 256])
        cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return similarity > threshold, similarity

    def registrar_rostro(self, nombre, face_img):
        """Registrar un nuevo rostro en la BD"""
        if len(face_img.shape) > 2:
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        face_resized = cv2.resize(face_img, (100, 100))
        encoding = np.array(face_resized, dtype=np.float64).flatten()

        fecha_registro = datetime.now().strftime("%Y-%m-%d")
        carnet_id = ""  # Puedes pedirlo en otro campo si lo necesitas
        self.cursor.execute(
            "INSERT INTO personas (nombre, encoding, fecha_registro, carnet_id) VALUES (?, ?, ?, ?)",
            (nombre, encoding.tobytes(), fecha_registro, carnet_id)
        )
        self.com.commit()
        # Reentrenar el modelo con el nuevo rostro
        self.entrenar_modelo()

    def registrar_rostro_multiple(self, nombre, face_images, carnet_id=""):
        """
        Registra una persona con múltiples imágenes de su rostro
        Almacena una sola entrada en la tabla personas y múltiples imágenes en imagenes_personas
        """
        fecha_registro = datetime.now().strftime("%Y-%m-%d")

        # Primero insertamos los datos de la persona
        self.cursor.execute(
            "INSERT INTO personas (nombre, fecha_registro, carnet_id) VALUES (?, ?, ?)",
            (nombre, fecha_registro, carnet_id)
        )

        # Obtenemos el ID de la persona recién insertada
        persona_id = self.cursor.lastrowid

        # Ahora insertamos todas las imágenes para esta persona
        for face_img in face_images:
            if len(face_img.shape) > 2:
                face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            face_resized = cv2.resize(face_img, (100, 100))
            encoding = np.array(face_resized, dtype=np.float64).flatten()

            # Insertamos el encoding en la tabla de imágenes
            self.cursor.execute(
                "INSERT INTO imagenes_personas (persona_id, encoding) VALUES (?, ?)",
                (persona_id, encoding.tobytes())
            )

        # Confirmar todos los cambios en la base de datos
        self.com.commit()

        # Reentrenar el modelo con las nuevas imágenes
        self.entrenar_modelo()

    def reconocer_rostro(self, face_img, confidence_threshold=80):
        """Reconoce un rostro usando LBPH"""
        if not self.trained:
            return "Desconocido", 0

        if len(face_img.shape) > 2:
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        face_resized = cv2.resize(face_img, (100, 100))

        try:
            label, confidence = self.recognizer.predict(face_resized)
            if confidence < confidence_threshold: # Menor confianza = mejor coincidencia
                nombre = self.label_map.get(label, "Desconocido")
                return nombre, confidence
        except Exception as e:
            print(f"Error en reconocimiento: {e}")

        return "Desconocido", 0

    def obtener_info_persona(self, nombre):
        self.cursor.execute(
            "SELECT habilitado, fecha_registro, carnet_id FROM personas WHERE nombre = ?", (nombre,))
        return self.cursor.fetchone()

    def obtener_todas_personas(self):
        self.cursor.execute("SELECT nombre, habilitado, fecha_registro, carnet_id FROM personas")
        return self.cursor.fetchall()

    def verificar_fechas_expiracion(self):
        self.cursor.execute("SELECT id, fecha_registro, expirado FROM personas WHERE habilitado = 1")
        filas = self.cursor.fetchall()
        hoy = datetime.now()
        for persona_id, fecha_str, expirado in filas:
            if fecha_str:
                fecha_registro = datetime.strptime(fecha_str, "%Y-%m-%d")
                if (hoy - fecha_registro).days >= 30 and not expirado:
                    self.cursor.execute(
                        "UPDATE personas SET habilitado = 0, expirado = 1 WHERE id = ?",
                        (persona_id,)
                    )
        self.com.commit()

    def obtener_todas_personas_con_id(self):
        """Obtiene todos los registros de personas incluyendo su ID"""
        self.cursor.execute("SELECT id, nombre, habilitado, fecha_registro, carnet_id FROM personas")
        return self.cursor.fetchall()

    def registrar_rostro_con_carnet(self, nombre, face_img, carnet_id=""):
        """Registra un nuevo rostro en la BD con carnet"""
        fecha_registro = datetime.now().strftime("%Y-%m-%d")

        # Insertar datos de la persona
        self.cursor.execute(
            "INSERT INTO personas (nombre, fecha_registro, carnet_id) VALUES (?, ?, ?)",
            (nombre, fecha_registro, carnet_id)
        )

        # Obtener ID de la persona recién insertada
        persona_id = self.cursor.lastrowid

        # Procesar y guardar la imagen
        if len(face_img.shape) > 2:
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        face_resized = cv2.resize(face_img, (100, 100))
        encoding = np.array(face_resized, dtype=np.float64).flatten()

        # Insertar encoding en la tabla de imágenes
        self.cursor.execute(
            "INSERT INTO imagenes_personas (persona_id, encoding) VALUES (?, ?)",
            (persona_id, encoding.tobytes())
        )

        self.com.commit()
        # Reentrenar el modelo con el nuevo rostro
        self.entrenar_modelo()

    def actualizar_persona(self, id_persona, nombre, carnet_id=""):
        """Actualiza la información de una persona"""
        self.cursor.execute(
            "UPDATE personas SET nombre = ?, carnet_id = ? WHERE id = ?",
            (nombre, carnet_id, id_persona)
        )
        self.com.commit()
        # Actualizar el modelo si cambió el nombre
        self.entrenar_modelo()

    def eliminar_persona(self, id_persona):
        """
        Elimina a una persona de la base de datos y todas sus imágenes asociadas
        """
        # Primero eliminamos todas las imágenes asociadas a la persona
        self.cursor.execute("DELETE FROM imagenes_personas WHERE persona_id = ?", (id_persona,))

        # Luego eliminamos el registro de la persona
        self.cursor.execute("DELETE FROM personas WHERE id = ?", (id_persona,))

        # Confirmar los cambios
        self.com.commit()

        # Reentrenar el modelo
        self.entrenar_modelo()

    def cerrar(self):
        self.com.close()