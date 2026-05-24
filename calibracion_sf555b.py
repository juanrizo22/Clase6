"""
Calibración SF555B con micrófono USB en Raspberry Pi.
Compara la lectura del ESP32 (vía Serial) con el micrófono USB de referencia.
"""

import sounddevice as sd
import numpy as np
import serial
import time
import sys

SAMPLE_RATE = 44100
BLOCK_SIZE  = 1024
REF_PRESSURE = 20e-6  # 20 µPa


def listar_micros():
    """Muestra todos los dispositivos con canales de entrada disponibles."""
    print("\n=== Dispositivos de entrada disponibles ===")
    devices = sd.query_devices()
    encontrados = []
    for i, d in enumerate(devices):
        if d["max_input_channels"] > 0:
            print(f"  ID {i:2d} | canales: {d['max_input_channels']} | {d['name']}")
            encontrados.append(i)
    if not encontrados:
        print("  [!] No se encontraron dispositivos de entrada.")
    return encontrados


def abrir_micro(device_id):
    """
    Abre el dispositivo con el número de canales que realmente soporta.
    Devuelve (stream, channels) o lanza excepción si falla.
    """
    info = sd.query_devices(device_id)
    max_ch = int(info["max_input_channels"])

    if max_ch == 0:
        raise ValueError(f"El dispositivo ID {device_id} no tiene canales de entrada.")

    # La mayoría de micrófonos USB son mono; usamos 1 canal siempre que sea posible.
    channels = 1 if max_ch >= 1 else max_ch

    print(f"\n[OK] Usando '{info['name']}' — {channels} canal(es) a {SAMPLE_RATE} Hz")
    stream = sd.InputStream(
        device=device_id,
        channels=channels,
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="float32",
    )
    return stream, channels


def calcular_dba(stream, segundos=1):
    """Captura `segundos` de audio y devuelve el nivel RMS en dBFS."""
    stream.start()
    muestras = int(SAMPLE_RATE * segundos / BLOCK_SIZE)
    cuadrados = []
    for _ in range(muestras):
        bloque, _ = stream.read(BLOCK_SIZE)
        canal = bloque[:, 0]  # siempre usamos el primer canal
        cuadrados.append(np.mean(canal ** 2))
    stream.stop()
    rms = np.sqrt(np.mean(cuadrados))
    db = 20 * np.log10(rms + 1e-9)
    return db


def leer_esp32(puerto, baudrate=115200, timeout=5):
    """Lee una línea de nivel del ESP32 y extrae el valor numérico."""
    try:
        with serial.Serial(puerto, baudrate, timeout=timeout) as s:
            deadline = time.time() + timeout
            while time.time() < deadline:
                linea = s.readline().decode("utf-8", errors="ignore").strip()
                if "Nivel:" in linea:
                    partes = linea.split(":")
                    if len(partes) == 2:
                        return float(partes[1].replace("dBA", "").strip())
    except serial.SerialException as e:
        print(f"  [!] Serial: {e}")
    return None


def main():
    ids_validos = listar_micros()
    if not ids_validos:
        sys.exit(1)

    # --- Selección de dispositivo ---
    try:
        mic_id = int(input("\nIngrese el ID del micrófono USB de referencia: "))
    except ValueError:
        print("[!] ID inválido.")
        sys.exit(1)

    if mic_id not in ids_validos:
        print(f"[!] ID {mic_id} no tiene entradas de audio.")
        sys.exit(1)

    # --- Abrir micrófono ---
    try:
        stream, channels = abrir_micro(mic_id)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # --- Puerto Serial del ESP32 ---
    puerto = input("Puerto serial del ESP32 (ej: /dev/ttyUSB0) [Enter para omitir]: ").strip()

    print("\nIniciando calibración — presione Ctrl+C para detener.\n")
    offset = None

    try:
        while True:
            db_ref = calcular_dba(stream, segundos=1)
            print(f"[Ref USB ] {db_ref:7.2f} dBFS", end="")

            if puerto:
                db_esp = leer_esp32(puerto)
                if db_esp is not None:
                    if offset is None:
                        offset = db_ref - db_esp
                        print(f"\n  -> Offset calculado: {offset:.2f} dB")
                        print(f"     En el ESP32 cambia la línea de calibración a:")
                        print(f"     float db = 20 * log10(rms + 0.0001) + {10 + offset:.1f};")
                    diff = db_ref - db_esp
                    print(f"  |  [ESP32] {db_esp:7.2f} dBA  |  diff {diff:+.2f} dB")
                else:
                    print("  |  [ESP32] sin datos")
            else:
                print()

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[!] Calibración detenida.")
    finally:
        if stream.active:
            stream.stop()
        stream.close()


if __name__ == "__main__":
    main()
