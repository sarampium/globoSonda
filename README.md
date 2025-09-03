# 🚀 Trabajo de Grado: Globo Sonda UCAB

Este repositorio contiene todo el software y la documentación necesaria para reproducir el experimento descrito en el trabajo de grado "Diseño y desarrollo de un sistema de comunicación punto a punto para cápsula de globo sonda", escrito por Jesús Serrano y Sara Pérez. El sistema está diseñado para capturar datos atmosféricos y de geolocalización, transmitirlos en tiempo real a una estación terrena a través del protocolo de comunicación LoRa, y visualizarlos en un dashboard de telemetría y un mapa interactivo.

Esta investigación tuvo como misión ser completamente de código abierto, permitiendo que estudiantes, entusiastas e investigadores puedan replicar, modificar, mejorar y expandir el alcance de este trabajo en futuras iteraciones.

 <!-- Reemplaza esto con una captura de pantalla de tu dashboard -->
 <!-- Reemplaza esto con una captura de pantalla de tu mapa -->

---

## 📋 Tabla de Contenidos
1.  [Arquitectura del Sistema](#-arquitectura-del-sistema)
2.  [Componentes del Proyecto](#-componentes-del-proyecto)
    *   [Hardware Requerido](#hardware-requerido)
    *   [Software y Librerías](#software-y-librerías)
3.  [Descripción Detallada de los Módulos](#-descripción-detallada-de-los-módulos)
    *   [1. Transmisor (Carga Útil)](#1-transmisor-carga-útil---lilygo-t-beam)
    *   [2. Receptor (Estación Terrena)](#2-receptor-estación-terrena---lora32)
    *   [3. Dashboard y Receptor de Datos](#3-dashboard-y-receptor-de-datos-python)
    *   [4. Mapa de Seguimiento Web](#4-mapa-de-seguimiento-web-flask--leaflet)
4.  [Guía de Instalación y Uso](#-guía-de-instalación-y-uso)
    *   [Paso 1: Configuración del Hardware](#paso-1-configuración-del-hardware)
    *   [Paso 2: Carga del Firmware](#paso-2-carga-del-firmware)
    *   [Paso 3: Configuración del Software de la Estación Terrena](#paso-3-configuración-del-software-de-la-estación-terrena)
    *   [Paso 4: Ejecución del Sistema](#paso-4-ejecución-del-sistema)
5.  [Estructura del Repositorio](#-estructura-del-repositorio)
6.  [Licencia](#-licencia)

---

## 🛰️ Arquitectura del Sistema

El proyecto se divide en dos partes principales: la **Carga Útil (Transmisor)** que asciende con el globo, y la **Estación Terrena (Receptor)** que recibe y procesa los datos.

1.  **Transmisor (Lilygo T-Beam)**: Recopila datos de múltiples sensores (GPS, BME280, BMI160, DHT22), los formatea en una cadena CSV y los envía a través de LoRa.
2.  **Receptor (LoRa32)**: Recibe los paquetes de datos LoRa. Actúa como un puente, enviando los datos recibidos a través del puerto serie (USB) a una computadora.
3.  **Estación Terrena (PC)**:
    *   Un script de Python (`dashboard_y_rx.py`) lee los datos del puerto serie, los muestra en un dashboard de telemetría en tiempo real (usando Matplotlib) y los guarda en un archivo `datos_globo_sonda.csv`.
    *   Otro script de Python (`mapa.py`) actúa como un servidor web (usando Flask) que monitorea el archivo CSV.
    *   Un navegador web se conecta a este servidor para mostrar la trayectoria del globo en un mapa interactivo (`map.html` con Leaflet.js), actualizándose en tiempo real.

 <!-- Reemplaza esto con un diagrama de flujo de tu sistema -->

---

## 🛠️ Componentes del Proyecto

### Hardware Requerido

**Para la Carga Útil (Transmisor):**
*   **Microcontrolador:** Lilygo T-Beam (módulo LoRa y GPS NEO-6).
*   **Sensor Ambiental Interno:** BME280 (temperatura, humedad, presión). Conectado por I2C.
*   **Unidad de Medición Inercial:** BMI160 (acelerómetro y giroscopio). Conectado por I2C.
*   **Sensor Ambiental Externo:** DHT22 (temperatura y humedad).
*   **Antena LoRa:** de alta ganancia (recomendada una antena Ground Plane).

**Para la Estación Terrena (Receptor):**
*   **Microcontrolador:** Placa de desarrollo LoRa32 (ESP32 con módulo LoRa).
*   **Computadora** para ejecutar los scripts de Python.

### Software y Librerías

**Firmware (Arduino IDE):**
*   SPI.h
*   LoRa.h by Sandeep Mistry
*   SD.h
*   Wire.h
*   Adafruit_Sensor.h
*   Adafruit_BME280.h
*   TinyGPSPlus.h by Mikal Hart
*   DHT.h by Adafruit

**Estación Terrena (Python 3):**
*   `pyserial`: Para la comunicación con el receptor.
*   `matplotlib`: Para el dashboard de telemetría.
*   `numpy`: Para cálculos numéricos.
*   `pandas`: Para la manipulación de datos y timestamps.
*   `flask`: Para el servidor web del mapa.

Puedes instalar las dependencias de Python con:
```bash
pip install pyserial matplotlib numpy pandas flask
```

---

## 🔩 Descripción Detallada de los Módulos

### 1. Transmisor (Carga Útil) - Lilygo T-Beam

Este módulo es el cerebro del globo sonda. Su función es leer todos los sensores, procesar los datos y transmitirlos.

*   **Archivo:** `transmisor.ino`
*   **Funcionalidad:**
    *   Inicializa los sensores GPS, BME280, BMI160 y DHT22.
    *   Realiza una calibración inicial del acelerómetro (BMI160) para obtener mediciones de pitch y roll más precisas.
    *   En un bucle infinito, lee los datos de todos los sensores.
    *   Calcula la velocidad vertical a partir de los cambios de altitud del GPS.
    *   Formatea todos los datos en una única cadena de texto separada por comas (CSV).
    *   Envía la cadena de datos a través del módulo LoRa cada 3 segundos.

#### Configuración de Pines (Hardware)

El código `transmisor.ino` está configurado para la placa Lilygo T-Beam. Las conexiones son las siguientes:

| Pin Lógico       | Pin Físico (ESP32) | Propósito                               | Conexión                                     |
| ---------------- | ------------------ | --------------------------------------- | -------------------------------------------- |
| **LoRa (SPI)**   |                    |                                         | **Integrado en la placa T-Beam**             |
| `LORA_SCK`       | GPIO 5             | Reloj SPI                               | Interna                                      |
| `LORA_MISO`      | GPIO 19            | MISO SPI                                | Interna                                      |
| `LORA_MOSI`      | GPIO 27            | MOSI SPI                                | Interna                                      |
| `LORA_SS`        | GPIO 18            | Chip Select LoRa                        | Interna                                      |
| `LORA_RST`       | GPIO 14            | Reset LoRa                              | Interna                                      |
| `LORA_DIO0`      | GPIO 26            | Interrupción LoRa                       | Interna                                      |
| **GPS (Serial)** |                    |                                         | **Integrado en la placa T-Beam**             |
| `GPS_RX`         | GPIO 34            | Recepción de datos del GPS              | Interna (TX del GPS -> GPIO 34 del ESP32)    |
| `GPS_TX`         | GPIO 12            | Transmisión de datos al GPS (no usado)  | Interna                                      |
| **I2C**          |                    |                                         | **Bus para sensores externos**               |
| `SDA`            | GPIO 21            | Datos I2C                               | Conectar a SDA del BME280 y BMI160           |
| `SCL`            | GPIO 22            | Reloj I2C                               | Conectar a SCL del BME280 y BMI160           |
| **DHT22**        |                    |                                         | **Sensor externo**                           |
| `DHTPIN`         | GPIO 4             | Línea de datos del DHT22                | Conectar al pin de datos del sensor DHT22    |

### 2. Receptor (Estación Terrena) - LoRa32

Este módulo actúa como un puente entre la transmisión LoRa y el ordenador. Es una solución robusta que también proporciona un respaldo de datos en una tarjeta SD.

*   **Archivo:** `receptor.ino`
*   **Funcionalidad:**
    *   Inicializa el módulo LoRa y la tarjeta SD en buses SPI separados para evitar conflictos.
    *   Escucha continuamente por paquetes de datos LoRa.
    *   Cuando recibe un paquete, lo imprime inmediatamente en el puerto serie (conectado por cable micro USB a la computadora).
    *   Simultáneamente, abre el archivo `/loradata.csv` en la tarjeta SD y añade la línea de datos recibida.

#### Configuración de Pines (Hardware)

El código `receptor.ino` utiliza dos buses SPI del ESP32: **VSPI** para el módulo LoRa y **HSPI** para la tarjeta microSD. Esto es crucial para la estabilidad.

| Pin Lógico           | Pin Físico (ESP32) | Propósito                   | Bus SPI |
| -------------------- | ------------------ | --------------------------- | ------- |
| **LoRa (VSPI)**      |                    |                             | **VSPI** |
| `LORA_SCK`           | GPIO 5             | Reloj SPI LoRa              | VSPI    |
| `LORA_MISO`          | GPIO 19            | MISO SPI LoRa               | VSPI    |
| `LORA_MOSI`          | GPIO 27            | MOSI SPI LoRa               | VSPI    |
| `LORA_SS`            | GPIO 18            | Chip Select LoRa            | VSPI    |
| `LORA_RST`           | GPIO 14            | Reset LoRa                  | -       |
| `LORA_DIO0`          | GPIO 26            | Interrupción LoRa           | -       |
| **MicroSD (HSPI)**   |                    |                             | **HSPI** |
| `SD_CS`              | GPIO 13            | Chip Select SD              | HSPI    |
| `SD_MOSI`            | GPIO 15            | MOSI SPI SD                 | HSPI    |
| `SD_MISO`            | GPIO 2             | MISO SPI SD                 | HSPI    |
| `SD_SCK`             | GPIO 14            | Reloj SPI SD                | HSPI    |

### 3. Dashboard y Receptor de Datos (Python)

Este script es el corazón de la estación terrena. Recibe, procesa, visualiza y almacena todos los datos de telemetría.

*   **Archivo:** `dashboard_y_rx.py`
*   **Funcionalidad:**
    *   Se conecta al puerto serie donde está el microcontrolador receptor (ej. `COM6`).
    *   Lee cada línea de datos que llega por el puerto serie.
    *   Añade un timestamp a cada paquete de datos y lo guarda en el archivo `datos_globo_sonda.csv`. Este es el archivo principal de registro de la misión.
    *   Mantiene un historial de los últimos datos recibidos.
    *   Actualiza una serie de gráficos en tiempo real para mostrar visualmente la telemetría: altitudes, temperaturas, presión, orientación, estado del GPS, etc.

### 4. Mapa de Seguimiento Web (Flask + Leaflet)

Este sistema proporciona una interfaz web accesible para seguir la ubicación del globo en tiempo real.

*   **Archivos:** `mapa.py`, `map.html`
*   **Funcionalidad:**
    *   `mapa.py`:
        *   Inicia un servidor web local con Flask.
        *   Monitorea el archivo `datos_globo_sonda.csv` en busca de nuevas líneas.
        *   Cuando se añade una nueva línea, lee las coordenadas y la altitud.
        *   Envía los nuevos datos a los clientes web conectados mediante Server-Sent Events (SSE), una técnica eficiente para el streaming de datos en tiempo real.
    *   `map.html`:
        *   Utiliza la librería Leaflet.js para renderizar un mapa satelital.
        *   Al cargar, dibuja la trayectoria histórica completa del globo.
        *   Se suscribe al flujo de eventos del servidor.
        *   Cada vez que recibe un nuevo punto de datos, actualiza la posición del marcador en el mapa y extiende la línea de la trayectoria en tiempo real.

---

## ⚙️ Guía de Instalación y Uso

### Paso 1: Configuración del Hardware
1.  **Transmisor:** Conecta los sensores BME280, BMI160 y DHT22 al Lilygo T-Beam siguiendo la tabla de pines especificada anteriormente. Alimenta la placa a través de su puerto USB o con una batería LiPo.

### Paso 2: Carga del Firmware
1.  Abre el **IDE de Arduino**.
2.  Instala todas las librerías necesarias mencionadas en la sección [Software y Librerías](#software-y-librerías) a través del "Gestor de Librerías".
3.  Selecciona la placa correcta en el menú `Herramientas > Placa` (ej. "TTGO LoRa32-OLED" para el T-Beam y una placa genérica "ESP32 Dev Module" para el receptor).
4.  Abre `transmisor.ino` y cárgalo en el Lilygo T-Beam.
5.  Abre `receptor.ino` y cárgalo en la placa LoRa32.

### Paso 3: Configuración del Software de la Estación Terrena
1.  Clona este repositorio en tu ordenador.
2.  Abre una terminal en la carpeta del proyecto.
3.  Instala las dependencias de Python (pyserial, matplotlib, numpy, pandas y flask).

### Paso 4: Ejecución del Sistema
1.  Conecta la placa receptora (LoRa32) a tu ordenador por cable micro USB.
2.  Identifica el puerto COM al que se conectó (ej. `COM6` en Windows, `/dev/ttyUSB0` en Linux). Actualiza la variable `PORT` en `dashboard_y_rx.py` si es necesario.
3.  **Inicia el Dashboard:** Abre un terminal y ejecuta:
    ```bash
    python dashboard_y_rx.py
    ```
    Deberías ver una ventana con gráficos que empezarán a actualizarse cuando lleguen datos.
4.  **Inicia el Servidor del Mapa:** Abre una **segunda terminal**, activa el entorno virtual y ejecuta:
    ```bash
    python mapa.py
    ```
5.  **Visualiza el Mapa:** Abre tu navegador web y ve a la dirección `http://127.0.0.1:5000`.

¡Ahora estás recibiendo y visualizando los datos de tu globo sonda en tiempo real!

---

## 📁 Estructura del Repositorio

```
.
├── transmisor.ino         # Código para la carga útil (Lilygo T-Beam)
├── receptor.ino           # Código para la estación terrena (LoRa32)
├── dashboard_y_rx.py      # Script para el dashboard y la recepción de datos serial
├── mapa.py                # Servidor web Flask para el mapa
├── templates/
│   └── map.html           # Plantilla HTML para el mapa con Leaflet.js
├── logo.png               # Logo opcional para el dashboard
└── README.md              # Esta documentación
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la **Licencia MIT**. Esto significa que eres libre de usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender copias del software. Consulta el archivo `LICENSE` para más detalles.
---

¡Gracias por tu interés en este proyecto! Si tienes alguna pregunta o sugerencia, no dudes en abrir un *Issue* en este repositorio
