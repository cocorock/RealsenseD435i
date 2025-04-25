import sys

print("--- Verificando instalação das bibliotecas ---")

libraries_ok = True
missing_libraries = []

# 1. Verificar pyrealsense2
try:
    import pyrealsense2 as rs
    print("[ OK ] pyrealsense2 importado com sucesso.")
    # Opcional: Tentar listar dispositivos para um teste mais profundo
    try:
        ctx = rs.context()
        if len(ctx.query_devices()) == 0:
            print("   (Aviso: Nenhuma câmera RealSense detectada, mas a biblioteca está instalada)")
        else:
             print(f"   (Info: {len(ctx.query_devices())} dispositivo(s) RealSense detectado(s))")
    except Exception as e:
        print(f"   (Erro ao acessar contexto RealSense: {e})")

except ImportError:
    print("[FALHA] pyrealsense2 não encontrado.")
    missing_libraries.append("pyrealsense2")
    libraries_ok = False
except Exception as e:
    print(f"[ERRO] Erro inesperado ao importar/usar pyrealsense2: {e}")
    libraries_ok = False


# 2. Verificar OpenCV (cv2)
try:
    import cv2
    print(f"[ OK ] OpenCV (cv2) importado com sucesso. Versão: {cv2.__version__}")
except ImportError:
    print("[FALHA] OpenCV (cv2) não encontrado.")
    missing_libraries.append("opencv-python") # O nome do pacote pip é opencv-python
    libraries_ok = False
except Exception as e:
    print(f"[ERRO] Erro inesperado ao importar cv2: {e}")
    libraries_ok = False

# 3. Verificar NumPy
try:
    import numpy as np
    print(f"[ OK ] NumPy importado com sucesso. Versão: {np.__version__}")
except ImportError:
    print("[FALHA] NumPy não encontrado.")
    missing_libraries.append("numpy")
    libraries_ok = False
except Exception as e:
    print(f"[ERRO] Erro inesperado ao importar numpy: {e}")
    libraries_ok = False

print("\n--- Verificação Concluída ---")

if libraries_ok:
    print("Todas as bibliotecas necessárias parecem estar instaladas corretamente!")
else:
    print("Algumas bibliotecas estão faltando ou causaram erro.")
    print("Bibliotecas com problemas:", ", ".join(missing_libraries))
    print("\nTente instalá-las usando pip:")
    if "pyrealsense2" in missing_libraries:
        print("   pip install pyrealsense2")
    if "opencv-python" in missing_libraries:
        print("   pip install opencv-python")
    if "numpy" in missing_libraries:
        print("   pip install numpy")

print(f"\nUsando Python: {sys.version}")
print(f"Localização do executável Python: {sys.executable}")