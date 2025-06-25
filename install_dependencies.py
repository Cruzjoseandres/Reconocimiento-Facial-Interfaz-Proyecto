import subprocess
import sys
import os

def install():
    print("Instalando dependencias necesarias para tkinter...")

    # Intenta instalar tkinter si está disponible a través de pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
        print("Tkinter instalado correctamente a través de pip.")
    except Exception as e:
        print(f"No se pudo instalar tkinter mediante pip: {e}")
        print("Es posible que debas instalar tkinter manualmente.")

    # Verificar la instalación de tkinter
    try:
        import tkinter
        print(f"Tkinter está instalado correctamente. Versión: {tkinter.TkVersion}")
    except ImportError as e:
        print(f"Error importando tkinter: {e}")
        print("Sugerencias para solucionar este problema:")
        print("1. Reinstalar Python asegurándote de seleccionar 'tcl/tk e IDLE' durante la instalación")
        print("2. En Windows, verifica que tcl/tk esté en tu PATH")

    print("\nComprobando otras dependencias del proyecto...")
    try:
        import cv2
        print(f"OpenCV está instalado correctamente. Versión: {cv2.__version__}")
    except ImportError:
        print("OpenCV no está instalado. Instalando...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
            print("OpenCV instalado correctamente.")
        except Exception as e:
            print(f"Error instalando OpenCV: {e}")

    try:
        from PIL import Image, ImageTk
        print(f"Pillow está instalado correctamente.")
    except ImportError:
        print("Pillow no está instalado. Instalando...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            print("Pillow instalado correctamente.")
        except Exception as e:
            print(f"Error instalando Pillow: {e}")

    print("\nInstrucciones adicionales:")
    print("Si continúas experimentando problemas con tkinter:")
    print("1. Asegúrate de que estás ejecutando el script desde un entorno virtual configurado correctamente")
    print("2. Considera reinstalar Python y seleccionar la opción 'tcl/tk e IDLE' durante la instalación")
    print("3. Si estás en Windows, verifica que la carpeta de Python y sus bibliotecas estén incluidas en la variable PATH")

if __name__ == "__main__":
    install()
