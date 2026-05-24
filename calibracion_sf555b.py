"""
Calibración SF555B en Raspberry Pi.
Compara el micrófono I2S (SF555B, via ALSA) con un micrófono USB de referencia.
Ambos dispositivos se leen directamente como entradas de audio de la RPi.
"""

import sounddevice as sd
import numpy as np
import time
import sys

SAMPLE_RATE = 44100
BLOCK_SIZE  = 1024


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


def abrir_micro(device_id, label=""):
    """
    Abre el dispositivo usando exactamente 1 canal (mono).
    La mayoría de micrófonos USB e I2S exponen 1 canal bajo ALSA.
    Lanza ValueError si el dispositivo no tiene entradas.
    """
    info = sd.query_devices(device_id)
    max_ch = int(info["max_input_channels"])

    if max_ch == 0:
        raise ValueError(f"ID {device_id} ('{info['name']}') no tiene canales de entrada.")

    # Usamos siempre 1 canal para evitar el error channelCount > maxChans
    channels = min(1, max_ch)

    tag = f"[{label}]" if label else ""
    print(f"  {tag} '{info['name']}' — {channels} canal(es) a {SAMPLE_RATE} Hz")

    stream = sd.InputStream(
        device=device_id,
        channels=channels,
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="float32",
    )
    return stream


def medir_db(stream, segundos=1):
    """Devuelve el nivel RMS en dBFS de `segundos` de grabación."""
    n_bloques = max(1, int(SAMPLE_RATE * segundos / BLOCK_SIZE))
    cuadrados = []
    for _ in range(n_bloques):
        bloque, _ = stream.read(BLOCK_SIZE)
        cuadrados.append(np.mean(bloque[:, 0] ** 2))
    rms = np.sqrt(np.mean(cuadrados))
    return 20.0 * np.log10(rms + 1e-9)


def pedir_id(prompt, validos):
    try:
        val = int(input(prompt))
    except ValueError:
        print("[!] Ingrese un número entero.")
        sys.exit(1)
    if val not in validos:
        print(f"[!] ID {val} no es válido o no tiene entradas.")
        sys.exit(1)
    return val


def main():
    ids_validos = listar_micros()
    if not ids_validos:
        sys.exit(1)

    print()
    id_ref = pedir_id("ID del micrófono USB de referencia  : ", ids_validos)
    id_sf  = pedir_id("ID del micrófono I2S SF555B (ALSA)  : ", ids_validos)

    print("\nAbriendo dispositivos...")
    try:
        stream_ref = abrir_micro(id_ref, "USB Ref")
        stream_sf  = abrir_micro(id_sf,  "SF555B ")
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    print("\nIniciando calibración — presione Ctrl+C para detener.\n")
    print(f"{'Tiempo':>8}  {'USB Ref':>10}  {'SF555B':>10}  {'Offset':>10}")
    print("-" * 46)

    offsets = []
    inicio = time.time()

    try:
        stream_ref.start()
        stream_sf.start()
        while True:
            db_ref = medir_db(stream_ref, segundos=1)
            db_sf  = medir_db(stream_sf,  segundos=1)
            offset = db_ref - db_sf
            offsets.append(offset)
            elapsed = time.time() - inicio
            print(f"{elapsed:7.1f}s  {db_ref:9.2f}  {db_sf:9.2f}  {offset:+9.2f}  dBFS")

    except KeyboardInterrupt:
        print("\n--- Calibración detenida ---")

    finally:
        stream_ref.stop(); stream_ref.close()
        stream_sf.stop();  stream_sf.close()

    if offsets:
        offset_medio = np.mean(offsets)
        print(f"\nOffset promedio (USB - SF555B): {offset_medio:+.2f} dB")
        print(f"\nPara ajustar la lectura del SF555B en Python, súmale este valor:")
        print(f"  db_calibrado = db_sf + ({offset_medio:+.2f})")
