import pyrealsense2 as rs
import numpy as np
import cv2
import os
import time
import csv

# --- Configurações ---
# Ask user for folder name
output_folder = input("Enter the name for the main folder (default: realsense_data): ").strip()
if not output_folder:  # If user just pressed Enter
    output_folder = "realsense_data"
    
num_frames_to_capture = 100      # Quantidade de conjuntos de quadros para capturar

# --------------------
# USB 2.1 Resolução e FPS 
# color_width, color_height = 640, 480
# depth_width, depth_height = 640, 480
# fps = 15
# # --------------------

# USB 3.2 Resolução e FPS 
color_width, color_height = 848, 480
depth_width, depth_height = 1280, 720
fps = 30
# --------------------

# --- Criação das Pastas de Saída ---p3
rgb_folder = os.path.join(output_folder, "rgb")
depth_folder = os.path.join(output_folder, "depth")
imu_folder = os.path.join(output_folder, "imu")

os.makedirs(output_folder, exist_ok=True)
os.makedirs(rgb_folder, exist_ok=True)
os.makedirs(depth_folder, exist_ok=True)
os.makedirs(imu_folder, exist_ok=True) # Pasta para o arquivo CSV do IMU
# -----------------------------------

# --- Configuração do Pipeline RealSense ---
pipeline = rs.pipeline()
config = rs.config()

try:
    # First check if there's any device connected
    ctx = rs.context()
    devices = ctx.query_devices()
    if len(list(devices)) == 0:
        raise RuntimeError("No RealSense device detected! Please connect a RealSense camera.")

    # Start with basic configuration
    config.enable_stream(rs.stream.depth, depth_width, depth_height, rs.format.z16, fps)
    config.enable_stream(rs.stream.color, color_width, color_height, rs.format.bgr8, fps)
    config.enable_stream(rs.stream.accel, rs.format.motion_xyz32f, 100)
    config.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 200)
    
    print("Iniciando pipeline...")
    profile = pipeline.start(config)
    print("Pipeline iniciado.")

except Exception as e:
    print(f"Error: {e}")
    pipeline.stop()
    exit(1)

# Obter escala de profundidade (metros por unidade de profundidade)
# depth_sensor = profile.get_device().first_depth_sensor()
# depth_scale = depth_sensor.get_depth_scale()
# print(f"Escala de profundidade: {depth_scale}")

# Alinhador para alinhar profundidade com cor (opcional, mas útil)
align_to = rs.stream.color
align = rs.align(align_to)

frame_count = 0
last_imu_save_time = time.time()

# --- Configuração do Arquivo CSV do IMU ---
imu_csv_path = os.path.join(imu_folder, "imu_data.csv")
imu_file = open(imu_csv_path, 'w', newline='')
imu_writer = csv.writer(imu_file)
imu_writer.writerow(['timestamp', 'type', 'frame_number', 'x', 'y', 'z'])  # Header
# -----------------------------------------

try:
    print(f"Capturando {num_frames_to_capture} conjuntos de quadros...")
    while frame_count < num_frames_to_capture:
        try:
            frames = pipeline.wait_for_frames(timeout_ms=5000)
        except RuntimeError as e:
            print(f"Timeout waiting for frames: {e}")
            continue

        # Alinha o quadro de profundidade ao quadro de cor
        aligned_frames = align.process(frames)
        if not aligned_frames:
            print("Falha ao alinhar quadros. Pulando...")
            continue

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        
        # Remove these incorrect lines:
        # accel_frames = frames.get_motion_frame(rs.stream.accel)
        # gyro_frames = frames.get_motion_frame(rs.stream.gyro)

        # Verifica se temos quadros de imagem válidos
        if not depth_frame or not color_frame:
            print("Quadro de profundidade ou cor ausente. Pulando...")
            continue

        # --- Processamento e Salvamento dos Quadros de Imagem ---
        # Obter timestamp (pode ser útil, mas usaremos contador por simplicidade no nome do arquivo)
        # timestamp_ms = frames.get_timestamp()

        # Converter imagens para arrays NumPy
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data()) # Formato BGR

        # Salvar imagem colorida (BGR como está, OpenCV salva corretamente)
        color_filename = os.path.join(rgb_folder, f"frame_{frame_count:06d}.png")
        cv2.imwrite(color_filename, color_image)

        # Salvar imagem de profundidade (como PNG de 16 bits para preservar dados)
        depth_filename = os.path.join(depth_folder, f"frame_{frame_count:06d}.png")
        cv2.imwrite(depth_filename, depth_image)
        # Alternativa: Salvar como .npy (preserva tipo de dado e escala original)
        # depth_npy_filename = os.path.join(depth_folder, f"frame_{frame_count:06d}.npy")
        # np.save(depth_npy_filename, depth_image)

        print(f"Salvo: {os.path.basename(color_filename)}, {os.path.basename(depth_filename)}")
        # -------------------------------------------------------

        # --- Processamento e Salvamento dos Dados IMU ---
        for frame in frames:
            if frame.is_motion_frame():
                motion = frame.as_motion_frame()
                if motion.get_profile().stream_type() == rs.stream.accel:
                    accel_data = motion.get_motion_data()
                    timestamp = motion.get_timestamp()
                    frame_num = motion.get_frame_number()
                    imu_writer.writerow([timestamp, 'accel', frame_num, 
                                       accel_data.x, accel_data.y, accel_data.z])
                elif motion.get_profile().stream_type() == rs.stream.gyro:
                    gyro_data = motion.get_motion_data()
                    timestamp = motion.get_timestamp()
                    frame_num = motion.get_frame_number()
                    imu_writer.writerow([timestamp, 'gyro', frame_num, 
                                       gyro_data.x, gyro_data.y, gyro_data.z])
        # ----------------------------------------------

        frame_count += 1

        # Pequena pausa para evitar uso excessivo da CPU (opcional)
        # time.sleep(0.01)

finally:
    print("\nParando pipeline...")
    pipeline.stop()
    if 'imu_file' in locals():
        imu_file.close()
    print("Pipeline parado.")
    print(f"Dados salvos em: {os.path.abspath(output_folder)}")
    print(f"Total de {frame_count} conjuntos de quadros de imagem salvos.")
    if 'imu_csv_path' in locals():
        print(f"Dados IMU salvos em: {os.path.abspath(imu_csv_path)}")