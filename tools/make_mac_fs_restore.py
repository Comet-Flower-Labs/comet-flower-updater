"""Build a file-system-only restore copy of Zoom's Mac "G1 FOUR System v2.00 Updater".

Zoom's updater walks an 8-entry table (_RomProcedure, 16 bytes each: op, addr,
size, resource; op 0 = erase, op 1 = write, anything else = skipped; size 0 on a
write means "whole file"). Resources are indexed by _BinName: 0 Main, 1 MAIN_INFO,
2 FS, 3 Preset, 4 ROM. This copy keeps only:
    erase 0x102000 size 0x2FE000 ; write resource 2 (FS.bin) at 0x102000
and skips the other six stages, so the boot program, firmware and settings
sector are not touched (same layout as tools/make_fs_restore_updater.py).

    python3 -I make_mac_fs_restore.py <official Updater.app> <output Updater.app>
"""
import shutil, struct, subprocess, sys
from pathlib import Path

TABLE_OFF = 0x20870          # _RomProcedure in the __const section
EXPECT = [(0, 0xBF000, 0x1000, 255), (0, 0x28000, 0xB000, 255), (1, 0x28000, 0xB000, 3),
          (0, 0, 0x28000, 255), (1, 0, 0x28000, 4), (0, 0x33000, 0x8C000, 255),
          (1, 0x33000, 0, 0), (1, 0xBF000, 0x1000, 1)]
NEW = [(0, 0x102000, 0x2FE000, 255), (1, 0x102000, 0, 2)] + [(2, 0, 0, 255)] * 6

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
exe_rel = Path("Contents/MacOS/EFX Updater")
fs = src / "Contents/Resources/FS.bin"
assert fs.stat().st_size == 0x2FE000, "FS.bin is not exactly 0x2FE000 bytes"
if dst.exists():
    sys.exit(f"{dst} exists")
shutil.copytree(src, dst, symlinks=True)
exe = dst / exe_rel
data = bytearray(exe.read_bytes())
old = [struct.unpack("<4I", data[TABLE_OFF + 16 * i:TABLE_OFF + 16 * i + 16]) for i in range(8)]
assert old == EXPECT, f"unexpected stage table: {old}"
for i, e in enumerate(NEW):
    data[TABLE_OFF + 16 * i:TABLE_OFF + 16 * i + 16] = struct.pack("<4I", *e)
exe.write_bytes(data)
subprocess.run(["xattr", "-cr", str(dst)], check=True)
subprocess.run(["codesign", "--force", "--deep", "-s", "-", str(dst)], check=True)
print("wrote", dst)
