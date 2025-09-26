import subprocess
import time
import re
import threading
import queue

MOVE_RE = re.compile(r"^([A-Za-z0-9]+):\s+(\d+)$")
TOTAL_RE = re.compile(r"^Nodes searched:\s+(\d+)$")

def start_ink() -> subprocess.Popen:
    """Inicia Stockfish y devuelve el proceso."""
    exe_path = r"E:\Documents\stockfish\stockfish-windows-x86-64-avx2.exe"

    process = subprocess.Popen(
        [exe_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    return process

def send_command(process: subprocess.Popen, command: str) -> None:
    """Envía un comando al CLI sin leer salida."""
    process.stdin.write(command + "\n")
    process.stdin.flush()

def send_command_and_grab_output(process: subprocess.Popen, command: str, timeout: float = 20.0) -> dict[str, int]:
    """
    Envía un comando y devuelve un dict con jugadas y 'Total'.
    Usa un hilo lector + cola para no bloquear en readline().
    """
    q = queue.Queue()

    def reader(proc, q):
        for line in proc.stdout:
            q.put(line)
        q.put(None)  # EOF

    thread = threading.Thread(target=reader, args=(process, q), daemon=True)
    thread.start()

    send_command(process, command)

    result = {}
    deadline = time.time() + timeout

    while True:
        try:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            line = q.get(timeout=remaining)
        except queue.Empty:
            break

        if line is None:  # EOF
            break
        line = line.strip()

        m = MOVE_RE.match(line)
        if m:
            move, value = m.groups()
            result[move] = int(value)
            continue

        t = TOTAL_RE.match(line)
        if t:
            # result["Total"] = int(t.group(1))
            break

    return result

def close_ink(process: subprocess.Popen) -> None:
    """Intenta cerrar el CLI."""
    try:
        send_command(process, "quit")
    except Exception:
        pass
    process.terminate()
