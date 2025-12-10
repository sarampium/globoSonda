import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from collections import deque
import threading
import os 

# Configuración
PORT = 'COM6'
BAUD = 115200
TIME_WINDOW = 180  # segundos
MAX_DATA = int(TIME_WINDOW / 3) + 5
CSV_FILENAME = "datos_globo_sonda.csv"

# Inicialización de estructuras
time_data = deque(maxlen=MAX_DATA)
lat_data = deque(maxlen=MAX_DATA)
lon_data = deque(maxlen=MAX_DATA)
alt_gps_data = deque(maxlen=MAX_DATA)
vel_kmh_data = deque(maxlen=MAX_DATA)
vel_vert_data = deque(maxlen=MAX_DATA)
hdop_data = deque(maxlen=MAX_DATA)
sat_data = deque(maxlen=MAX_DATA)
pitch_data = deque(maxlen=MAX_DATA)
roll_data = deque(maxlen=MAX_DATA)
temp_data = deque(maxlen=MAX_DATA)
hum_data = deque(maxlen=MAX_DATA)
pres_data = deque(maxlen=MAX_DATA)
alt_bme_data = deque(maxlen=MAX_DATA)
out_temp_data = deque(maxlen=MAX_DATA)
out_hum_data = deque(maxlen=MAX_DATA)

plt.style.use('seaborn-v0_8-darkgrid')
fig = plt.figure(figsize=(14, 12))
gs = fig.add_gridspec(4, 3, height_ratios=[2, 2, 2, 0.1], width_ratios=[1, 1, 1], hspace=0.60, wspace=0.32)

# Fila 0: [Altitudes][Temp/Hum][Presión]
# Fila 1: [Pitch/Roll][HDOP][Satélites]
# Fila 2: [Vel_kmh][Vel_Vertical][Temp/Hum Ext]
# Fila 3: [Cuadro de texto/logo]

ax_alt = fig.add_subplot(gs[0, 0])
ax_th = fig.add_subplot(gs[0, 1])
ax_pres = fig.add_subplot(gs[0, 2])
ax_pitchroll = fig.add_subplot(gs[1, 0])
ax_hdop = fig.add_subplot(gs[1, 1])
ax_sat = fig.add_subplot(gs[1, 2])
ax_vel = fig.add_subplot(gs[2, 0])
ax_velvert = fig.add_subplot(gs[2, 1])
ax_outhth = fig.add_subplot(gs[2, 2])  # Nuevo gráfico en espacio libre

# 1. Altitudes
line_alt_gps, = ax_alt.plot([], [], label="Altitud GPS (m)", color="tab:green")
line_alt_bme, = ax_alt.plot([], [], label="Alt. BME (m)", color="tab:purple")
ax_alt.set_ylabel("Altitud (m)", fontweight='bold')
ax_alt.set_xlabel("Tiempo (s)", fontweight='bold')
ax_alt.legend(loc='upper left')
ax_alt.set_ylim(0, 40000)
ax_alt.grid(True, linestyle=':', color='gray', alpha=0.6)

# 2. Temp & Hum
line_temp, = ax_th.plot([], [], label="Temp (°C)", color="tab:red")
line_hum, = ax_th.plot([], [], label="Hum (%)", color="tab:cyan")
ax_th.set_ylabel("Temp / Hum", fontweight='bold')
ax_th.set_xlabel("Tiempo (s)", fontweight='bold')
ax_th.legend(loc='upper left')
ax_th.set_ylim(-50, 60)
ax_th.grid(True, linestyle=':', color='gray', alpha=0.6)

# 3. Presión
line_pres, = ax_pres.plot([], [], label="Pres (hPa)", color="tab:brown", linestyle="-")
ax_pres.set_ylabel("Pres (hPa)", fontweight='bold')
ax_pres.set_xlabel("Tiempo (s)", fontweight='bold')
ax_pres.legend(loc='upper left')
ax_pres.set_ylim(100, 1100)
ax_pres.grid(True, linestyle=':', color='gray', alpha=0.6)

# 4. Pitch & Roll (horizontal)
line_pitch, = ax_pitchroll.plot([], [], label="Pitch (°)", color="tab:blue")
line_roll, = ax_pitchroll.plot([], [], label="Roll (°)", color="tab:orange")
ax_pitchroll.set_ylabel("Pitch / Roll (°)", fontweight='bold')
ax_pitchroll.set_xlabel("Tiempo (s)", fontweight='bold')
ax_pitchroll.legend(loc='upper left')
ax_pitchroll.set_ylim(-90, 90)
ax_pitchroll.grid(True, linestyle=':', color='gray', alpha=0.6)

# 5. HDOP (horizontal)
line_hdop, = ax_hdop.plot([], [], label="HDOP", color="tab:olive")
ax_hdop.set_ylabel("HDOP", fontweight='bold')
ax_hdop.set_xlabel("Tiempo (s)", fontweight='bold')
ax_hdop.legend(loc='upper left')
ax_hdop.set_ylim(0, 25)
ax_hdop.grid(True, linestyle=':', color='gray', alpha=0.6)

# 6. Satélites (horizontal)
line_sat, = ax_sat.plot([], [], label="Satélites", color="tab:pink")
ax_sat.set_ylabel("Satélites", fontweight='bold')
ax_sat.set_xlabel("Tiempo (s)", fontweight='bold')
ax_sat.legend(loc='upper left')
ax_sat.set_ylim(0, 15)
ax_sat.grid(True, linestyle=':', color='gray', alpha=0.6)

# 7. Velocidad horizontal
line_vel, = ax_vel.plot([], [], label="Velocidad (km/h)", color="tab:gray")
ax_vel.set_ylabel("Vel. (km/h)", fontweight='bold')
ax_vel.set_xlabel("Tiempo (s)", fontweight='bold')
ax_vel.legend(loc='upper left')
ax_vel.set_ylim(0, 50)
ax_vel.grid(True, linestyle=':', color='gray', alpha=0.6)

# 8. Velocidad vertical
line_velvert, = ax_velvert.plot([], [], label="Velocidad Vertical (m/s)", color="tab:blue")
ax_velvert.set_ylabel("Vel Vert (m/s)", fontweight='bold')
ax_velvert.set_xlabel("Tiempo (s)", fontweight='bold')
ax_velvert.legend(loc='upper left')
ax_velvert.set_ylim(0, 50)
ax_velvert.grid(True, linestyle=':', color='gray', alpha=0.6)

# 9. Temp y Hum Externa (nuevo gráfico)
line_out_temp, = ax_outhth.plot([], [], label="Temp Ext (°C)", color="tab:olive")
line_out_hum, = ax_outhth.plot([], [], label="Hum Ext (%)", color="tab:purple")
ax_outhth.set_ylabel("Temp Ext / Hum Ext", fontweight='bold')
ax_outhth.set_xlabel("Tiempo (s)", fontweight='bold')
ax_outhth.legend(loc='upper left')
ax_outhth.set_ylim(-50, 100)
ax_outhth.grid(True, linestyle=':', color='gray', alpha=0.6)

# Cuadro de texto para Lat, Lon, Velocidad en la posición derecha abajo
props = dict(
    boxstyle='square,pad=0.6',
    facecolor="#F4F4F4",
    edgecolor='grey',
    linewidth=1,
    alpha=0.95
)
info_text = fig.text(
    0.82, 0.06, "", 
    fontsize=12, 
    fontweight='normal', 
    color='black', 
    bbox=props, 
    va='bottom', 
    ha='left'
)  # Esquina inferior derecha

# Marca de agua / Logo
try:
    # Construye la ruta al archivo de forma segura
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, 'logo.png')
    logo_img = plt.imread(logo_path)


    logo_width = 0.30
    top_margin = 0.03
    
    # Calcula el resto para que no se deforme
    h, w, _ = logo_img.shape  # Alto y ancho en píxeles
    fig_width_in, fig_height_in = fig.get_size_inches() # Tamaño de la figura en pulgadas
    aspect_ratio = h / w
    logo_height = logo_width * (fig_width_in / fig_height_in) * aspect_ratio
    
    left_pos = 0.5 - (logo_width / 2) # Centrado horizontal
    bottom_pos = 1.0 - logo_height - top_margin # Posición vertical desde abajo
    
    ax_logo = fig.add_axes([left_pos, bottom_pos, logo_width, logo_height], frameon=False, zorder=20)
    
    ax_logo.imshow(logo_img, alpha=0.25) # Puedes ajustar la transparencia aquí
    ax_logo.axis('off') # Oculta los bordes y ticks del eje del logo

except FileNotFoundError:
    print(f"ADVERTENCIA: No se encontró el archivo 'logo.png'.")
    print("Asegúrate de que esté en la misma carpeta que tu script. El programa continuará sin logo.")
except Exception as e:
    print(f"Error al cargar el logo: {e}")

# =========================================================

def update_plot(frame):
    if len(time_data) > 0:
        t0 = time_data[0]
        times = [x - t0 for x in time_data]

        # 1. Altitudes
        line_alt_gps.set_data(times, alt_gps_data)
        line_alt_bme.set_data(times, alt_bme_data)
        ax_alt.set_xlim(max(0, times[-1] - TIME_WINDOW), times[-1] + 2)

        # 2. Temp & Hum
        line_temp.set_data(times, temp_data)
        line_hum.set_data(times, hum_data)
        ax_th.set_xlim(max(0, times[-1] - TIME_WINDOW), times[-1] + 2)

        # 3. Presión
        line_pres.set_data(times, pres_data)
        ax_pres.set_xlim(max(0, times[-1] - TIME_WINDOW), times[-1] + 2)

        # 4. Pitch & Roll
        line_pitch.set_data(times, pitch_data)
        line_roll.set_data(times, roll_data)
        ax_pitchroll.set_xlim(max(0, times[-1] - TIME_WINDOW), times[-1] + 2)

        # 5. HDOP
        line_hdop.set_data(times, hdop_data)
        ax_hdop.set_xlim(max(0, times[-1] - TIME_WINDOW), times[-1] + 2)

        # 6. Satélites
        line_sat.set_data(times, sat_data)
        ax_sat.set_xlim(max(0, times[-1] - TIME_WINDOW), times[-1] + 2)

        # 7. Velocidad horizontal
        line_vel.set_data(times, vel_kmh_data)
        ax_vel.set_xlim(max(0, times[-1] - TIME_WINDOW), times[-1] + 2)

        # 8. Velocidad vertical
        line_velvert.set_data(times, vel_vert_data)
        ax_velvert.set_xlim(max(0, times[-1] - TIME_WINDOW), times[-1] + 2)

        # 9. Temp y Hum Externa (nuevo gráfico)
        line_out_temp.set_data(times, out_temp_data)
        line_out_hum.set_data(times, out_hum_data)
        ax_outhth.set_xlim(max(0, times[-1] - TIME_WINDOW), times[-1] + 2)

        # Cuadro de texto: Lat, Lon, Vel
        info = (
            f" Lat: {lat_data[-1]:.6f}\n"
            f" Lon: {lon_data[-1]:.6f}\n"
            f" Vel: {vel_kmh_data[-1]:.2f} km/h"
        )
        info_text.set_text(info)
    return (
        line_alt_gps, line_alt_bme, line_temp, line_hum, line_pres,
        line_pitch, line_roll, line_hdop, line_sat, line_vel, line_velvert,
        line_out_temp, line_out_hum, info_text
    )

def parse_line(line):
    try:
        vals = [v.strip() for v in line.strip().split(',')]
        if len(vals) != 18:
            print("Línea descartada por columnas:", line)
            return None
        return [float(v) if v.lower() != 'nan' else np.nan for v in vals]
    except Exception as e:
        print("Error parseando línea:", line, e)
        return None

def serial_reader_thread():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Escuchando en {PORT} a {BAUD} baudios...")
        with open(CSV_FILENAME, "a", buffering=1) as csvfile:
            if csvfile.tell() == 0:
                csvfile.write("timestamp,Lat,Lon,Alt_GPS,Vel_kmh,Vel_Vertical,HDOP,Sats,Pitch,Roll,Temp,Hum,Pres,Alt_BME,out_Temp,out_Hum\n")
            while True:
                line = ser.readline().decode(errors='ignore').strip()
                if not line or not ',' in line:
                    continue
                vals = parse_line(line)
                if vals is None:
                    continue
                timestamp = pd.Timestamp.now().isoformat()
                now = pd.Timestamp.now().timestamp()
                time_data.append(now)
                lat_data.append(vals[0])
                lon_data.append(vals[1])
                alt_gps_data.append(vals[2])
                vel_kmh_data.append(vals[3])
                vel_vert_data.append(vals[4])
                hdop_data.append(vals[5])
                sat_data.append(vals[6])
                pitch_data.append(vals[7])
                roll_data.append(vals[8])
                temp_data.append(vals[9])
                hum_data.append(vals[10])
                pres_data.append(vals[11])
                alt_bme_data.append(vals[12])
                out_temp_data.append(vals[13])
                out_hum_data.append(vals[14])
                csvfile.write(f"{timestamp}," + ",".join(str(v) for v in vals) + "\n")
    except Exception as e:
        print(f"Error en el hilo de lectura serial: {e}")

def main():
    hilo_serial = threading.Thread(target=serial_reader_thread, daemon=True)
    hilo_serial.start()
    ani = animation.FuncAnimation(fig, update_plot, interval=1000, cache_frame_data=False)
    plt.show()
    print("Finalizando...")

if __name__ == "__main__":
    main()