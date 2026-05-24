"""
Calibración SF555B con micrófono USB en Raspberry Pi.
"""

import sounddevice as sd
import numpy as np
import time
import sys

SAMPLE_RATE = 44100
BLOCK_SIZE  = 1024


def listar_micros():
    print("\n=== Dispositivos de entrada disponibles ===")
    encontrados = []
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0:
            print(f"  ID {i:2d} | canales: {d['max_input_channels']} | {d['name']}")
            encontrados.append(i)
    if not encontrados:
        print("  [!] No se encontraron dispositivos de entrada.")
    return encontrados


def abrir_micro(device_id):
    info = sd.query_devices(device_id)
    max_ch = int(info["max_input_channels"])
    if max_ch == 0:
        raise ValueError(f"ID {device_id} ('{info['name']}') no tiene canales de entrada.")
    print(f"\n[OK] '{info['name']}' — 1 canal a {SAMPLE_RATE} Hz")
    return sd.InputStream(
        device=device_id,
        channels=1,
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="float32",
    )


def medir_db(stream, segundos=1):
    n_bloques = max(1, int(SAMPLE_RATE * segundos / BLOCK_SIZE))
    cuadrados = []
    for _ in range(n_bloques):
        bloque, _ = stream.read(BLOCK_SIZE)
        cuadrados.append(np.mean(bloque[:, 0] ** 2))
    rms = np.sqrt(np.mean(cuadrados))
    return 20.0 * np.log10(rms + 1e-9)


def main():
    ids_validos = listar_micros()
    if not ids_validos:
        sys.exit(1)

    try:
        mic_id = int(input("\nIngrese el ID del micrófono USB: "))
    except ValueError:
        sys.exit("[!] ID inválido.")
    if mic_id not in ids_validos:
        sys.exit(f"[!] ID {mic_id} no válido.")

    try:
        stream = abrir_micro(mic_id)
    except ValueError as e:
        sys.exit(f"[ERROR] {e}")

    print("\nMidiendo — presione Ctrl+C para detener.\n")
    inicio = time.time()

    try:
        stream.start()
        while True:
            db = medir_db(stream)
            print(f"{time.time()-inicio:7.1f}s  {db:8.2f} dBFS")
    except KeyboardInterrupt:
        print("\n--- Detenido ---")
    finally:
        stream.stop()
        stream.close()
