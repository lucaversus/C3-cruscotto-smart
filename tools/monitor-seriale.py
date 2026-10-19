"""Monitor seriale visibile, comandi per riga e copia locale immediata del traffico."""
import argparse
from pathlib import Path
import sys
import threading
import time
import serial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', default='COM3')
    parser.add_argument('--baud', type=int, default=115200)
    parser.add_argument('--log', required=True, type=Path)
    parser.add_argument('--reset', action='store_true', help='Impulso EN tramite RTS, GPIO0 rilasciato')
    args = parser.parse_args()
    args.log.parent.mkdir(parents=True, exist_ok=True)
    port = serial.Serial(port=None, baudrate=args.baud, timeout=0.2, write_timeout=1)
    port.dtr = False
    port.rts = False
    port.port = args.port
    stop = threading.Event()
    try:
        port.open()
        with args.log.open('a', encoding='utf-8', buffering=1) as log:
            print(f'MONITOR {args.port} / {args.baud} baud - Ctrl+C per chiudere', flush=True)
            print(f'Log: {args.log}\nComandi con Invio: status | help | stop', flush=True)
            if args.reset:
                port.rts = True
                time.sleep(0.1)
                port.rts = False

            def commands():
                while not stop.is_set():
                    line = sys.stdin.readline()
                    if not line:
                        return
                    try:
                        port.write(line.rstrip('\r\n').encode('ascii') + b'\n')
                    except (serial.SerialException, UnicodeError) as error:
                        print(f'Comando non inviato: {error}', flush=True)

            threading.Thread(target=commands, daemon=True).start()
            port.write(b'status\n')
            while True:
                data = port.read_until(b'\n')
                if data:
                    text = data.decode('utf-8', errors='replace')
                    print(text, end='', flush=True)
                    log.write(text)
                    log.flush()
    except KeyboardInterrupt:
        print('\nMonitor chiuso.', flush=True)
    finally:
        stop.set()
        if port.is_open:
            port.close()


if __name__ == '__main__':
    main()
