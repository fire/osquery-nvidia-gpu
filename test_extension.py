"""End-to-end check: start osqueryi, attach nvidia_gpu.py, select from the table."""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SOCK = r"\\.\pipe\nvgpu_test" if os.name == "nt" else "/tmp/nvgpu_test.sock"
SQL = ("select gpu_index, name, utilization_gpu_pct, memory_used_mib, memory_total_mib, "
       "power_draw_w, temperature_c from nvidia_gpu;")

shell = subprocess.Popen(
    ["osqueryi", "--nodisable_extensions", f"--extensions_socket={SOCK}", "--json"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
ext = subprocess.Popen(
    [sys.executable, os.path.join(HERE, "nvidia_gpu.py"), "--socket", SOCK,
     "--timeout", "10", "--interval", "1"])
try:
    # Extension tables attach to the shell after it has seen the registration; wait, then probe.
    deadline = time.time() + 20
    out = ""
    while time.time() < deadline:
        time.sleep(3)
        shell.stdin.write(SQL + "\n")
        shell.stdin.flush()
        break
    shell.stdin.write(".exit\n")
    shell.stdin.flush()
    out, err = shell.communicate(timeout=30)
    print(out)
    print(err)
finally:
    ext.kill()
    shell.kill()
