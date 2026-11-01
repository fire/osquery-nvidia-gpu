# osquery-nvidia-gpu

An osquery extension that adds an `nvidia_gpu` table: one row per NVIDIA card, read from `nvidia-smi`.
Stock osquery has no GPU table, so GPU load, VRAM and power were invisible to it.

Columns: gpu_index, uuid, name, utilization_gpu_pct, utilization_mem_pct, memory_used_mib,
memory_total_mib, power_draw_w, power_limit_w, temperature_c, clock_sm_mhz, driver_version.
A value `nvidia-smi` reports as `[N/A]` comes back empty. With no driver the table is empty.

## Install

    pip install osquery

## Use with osqueryi

Start the shell with extensions on and note the socket it prints, then run the extension against it:

    osqueryi --nodisable_extensions
    osquery> select value from osquery_flags where name = 'extensions_socket';

    python nvidia_gpu.py --socket <that socket>

In the shell: `select * from nvidia_gpu;`

`gpu_index` is the nvidia-smi index. CUDA orders cards differently (fastest first), so do not
reuse it as `CUDA_VISIBLE_DEVICES`; match on `uuid`.

## osqueryd

Autoload needs an `.exe` that only Administrators can write. Checked on Windows 11 with the
osquery 5.24.0 MSI service:

1. `pip install pyinstaller`, then `python -m PyInstaller --onefile --name nvidia_gpu nvidia_gpu.py`.
2. Copy `dist\nvidia_gpu.exe` to `C:\Program Files\osquery\extensions\`. Remove inherited ACLs and
   own it as Administrators (see the osquery extensions page).
3. Put its full path in `extensions\extensions.load`, and add `--disable_extensions=false`,
   `--extensions_autoload=<path to extensions.load>` and `--extensions_timeout=10` to `osquery.flags`.
4. Add a snapshot query to `osquery.conf`, for example
   `{"query": "SELECT * FROM nvidia_gpu;", "interval": 60, "snapshot": true}`, then restart `osqueryd`.

Rows land in `log\osqueryd.snapshots.log` under the query's name.
https://osquery.readthedocs.io/en/latest/deployment/extensions/

## Test

    python test_extension.py

Starts `osqueryi`, attaches the extension and selects from `nvidia_gpu`. Checked on Windows 11 with
osquery 5.24.0, osquery-python 3.1.1 and an RTX 4090. On a scoop Python, `pip install` can fail with
WinError 448 on a scoop `current` junction; `pip install --no-warn-script-location osquery` works.

## Licence

MIT. See [LICENSE](LICENSE).
