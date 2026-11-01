"""osquery extension: an nvidia_gpu table, one row per NVIDIA card, read from nvidia-smi."""
import subprocess

import osquery

FIELDS = [
    ("gpu_index", "index", "INTEGER"),
    ("uuid", "uuid", "TEXT"),
    ("name", "name", "TEXT"),
    ("utilization_gpu_pct", "utilization.gpu", "INTEGER"),
    ("utilization_mem_pct", "utilization.memory", "INTEGER"),
    ("memory_used_mib", "memory.used", "INTEGER"),
    ("memory_total_mib", "memory.total", "INTEGER"),
    ("power_draw_w", "power.draw", "DOUBLE"),
    ("power_limit_w", "power.limit", "DOUBLE"),
    ("temperature_c", "temperature.gpu", "INTEGER"),
    ("clock_sm_mhz", "clocks.sm", "INTEGER"),
    ("driver_version", "driver_version", "TEXT"),
]


def query_rows():
    """Run nvidia-smi once; return a list of dicts keyed by column name (all values str)."""
    query = ",".join(f for _, f, _ in FIELDS)
    out = subprocess.run(
        ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=10, check=True,
    ).stdout
    rows = []
    for line in out.strip().splitlines():
        vals = [v.strip() for v in line.split(",")]
        # "[N/A]" or "[Not Supported]" becomes an empty string, which osquery reads as NULL-ish.
        rows.append({c: ("" if v.startswith("[") else v) for (c, _, _), v in zip(FIELDS, vals)})
    return rows


@osquery.register_plugin
class NvidiaGpuTable(osquery.TablePlugin):
    def name(self):
        return "nvidia_gpu"

    def columns(self):
        kinds = {"INTEGER": osquery.INTEGER, "TEXT": osquery.STRING, "DOUBLE": "DOUBLE"}
        return [osquery.TableColumn(name=c, type=kinds[t]) for c, _, t in FIELDS]

    def generate(self, context):
        try:
            return query_rows()
        except (OSError, subprocess.SubprocessError):
            return []  # no driver or no nvidia-smi: an empty table, not an error


if __name__ == "__main__":
    osquery.start_extension(name="nvidia_gpu", version="0.1.0")
