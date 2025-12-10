# app.py

import csv
import json
import os
import queue
import threading
import time
from flask import Flask, render_template, Response
import pandas as pd

# Archivo de donde se buscan los datos
CSV_FILE = 'datos_globo_sonda.csv' 
START_LAT = 10.26942
START_LON = -67.94462

# Estructura de datos compartidos
REQUIRED_COLUMNS = ['Lat', 'Lon', 'Alt_GPS']
data_queue = queue.Queue()
app = Flask(__name__)

# File watcher: pone las nuevas columnas que se agregan en el CSV en una cola
def file_watcher_worker():

    print(f"[*] Iniciando el file watcher para '{CSV_FILE}'...")
    
    # Si el archivo datos_globo_sonda.csv no existe, lo crea
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(REQUIRED_COLUMNS) # Use the constant
            print(f"[*] Creado '{CSV_FILE}' con headers.")

    # Logica para encontrar indices de columnas
    column_indices = {}
    try:
        with open(CSV_FILE, 'r') as f:
            header_line = f.readline()
            if not header_line:
                print(f"[!] Error: '{CSV_FILE}' está vacío.")
                return

            headers = [h.strip() for h in header_line.strip().split(',')]
            
            # Hallar el indice de cada columna requerida
            for col in REQUIRED_COLUMNS:
                if col not in headers:
                    raise ValueError(f"Columna requerida '{col}' no fue encontrada.")
                column_indices[col] = headers.index(col)

            print(f"[*] Columnas encontradas: {column_indices}")

    except (FileNotFoundError, ValueError) as e:
        print(f"[!] Error: no se pudo iniciar el file watcher. {e}")
        print(f"[*] Asegurar que el archivo '{CSV_FILE}' existe y contienen las columnas: {REQUIRED_COLUMNS}")
        return

    # --- LOOP PRINCIPAL ---
    with open(CSV_FILE, 'r') as f:
        f.seek(0, 2) # Mover cursor hasta el final del archivo
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            # Nueva linea encontrada
            try:
                # Dividir la linea en todas sus partes
                parts = line.strip().split(',')
                
                lat_str = parts[column_indices['Lat']]
                lon_str = parts[column_indices['Lon']]
                alt_str = parts[column_indices['Alt_GPS']]

                point_data = {
                    "Lat": float(lat_str),
                    "Lon": float(lon_str),
                    "Alt_GPS": float(alt_str)
                }
                
                print(f"[+] Nuevo punto detectado: {point_data}")
                data_queue.put(point_data)

            except (ValueError, IndexError):
                # Ocurre si el archivo CSV no tiene la estructura correcta
                print(f"[!] Warning: Could not parse line, skipping: '{line.strip()}'")
                pass
            except Exception as e:
                print(f"[!] Error processing line: {e}")

# --- Servidor Web ---- 

# Tomar todos los datos iniciales
def get_initial_data():
    try:
        # Verifica que el archivo CSV de datos exista y que sí tenga puntos GPS
        if not (os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 10):
            print("[*] Archivo de datos no encontrado o no tiene datos.")
            return pd.DataFrame(columns=REQUIRED_COLUMNS)

        df = pd.read_csv(CSV_FILE)

        # Verificar que el archivo CSV tenga todas las columnas de datos esperadas
        if not all(col in df.columns for col in REQUIRED_COLUMNS):
            print(f"[!] Error: al archivo '{CSV_FILE}' le falta al menos una columna de datos.")
            print(f"    Columnas requeridas: {REQUIRED_COLUMNS}")
            print(f"    Encontradas: {list(df.columns)}")
            return pd.DataFrame(columns=REQUIRED_COLUMNS)

        # Seleccionar solamente las columnas con datos relevantes para el mapa (puntos GPS)
        return df[REQUIRED_COLUMNS].dropna().copy()

    except Exception as e:
        print(f"[!] Error leyendo la información de '{CSV_FILE}': {e}")
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

@app.route('/')
def index():

    # Renderizar el mapa inicial
    df = get_initial_data()
    
    initial_data = {
        'start_location': [START_LAT, START_LON],
        'zoom': 15,
        'historical_path': [],
        'last_point': None
    }

    if not df.empty:
        initial_data['historical_path'] = df[['Lat', 'Lon']].values.tolist()
        last_row = df.iloc[-1]
        initial_data['last_point'] = last_row.to_dict()
        initial_data['start_location'] = [last_row['Lat'], last_row['Lon']]
        initial_data['zoom'] = 17

    return render_template('map.html', initial_data=initial_data)

@app.route('/stream')
def stream():
    # Saca nuevos datos de la cola 
    def event_stream():
        while True:
            point_data = data_queue.get()
            sse_data = f"data: {json.dumps(point_data)}\n\n"
            yield sse_data
            
    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Comienza el file watcher
    watcher_thread = threading.Thread(target=file_watcher_worker, daemon=True)
    watcher_thread.start()
    
    # Correr el servidor Flask
    app.run(debug=False, port=5000, threaded=True)