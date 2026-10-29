# G1 FOUR recovery on macOS: pedal hangs at the ZOOM logo

Same fix as `RECOVERY_G1.md` (rewrite the effect file system from update
mode), for a **Zoom G1 FOUR** driven from a **Mac**. Confirmed working on a
G1 FOUR with a Mac, 2026-10-29. One unit, one run: not a guarantee.

## What this adds
`RECOVERY_G1.md` uses the Windows updater and `make_fs_restore_updater.py`
(which patches a PE `.exe`). Zoom also ships Mac updaters
(`G1_FOUR_v2.00_Mac_E.zip`, `G1X_FOUR_v2.00_Mac_E.zip` from zoomcorp.com).
`tools/make_mac_fs_restore.py` patches the Mac one the same way.

## What the Mac updater looks like
- `Contents/MacOS/EFX Updater` is an x86_64 Mach-O (runs under Rosetta on
  Apple silicon).
- The resources are separate files in `Contents/Resources/`, indexed by
  `_BinName`: 0 `Main`, 1 `MAIN_INFO`, 2 `FS`, 3 `Preset`, 4 `ROM`.
- `_RomProcedure` (file offset 0x20870, 8 entries of 16 bytes: op, flash
  address, size, resource) is walked by `-[MainWindow DoUpdate]`. Op 0 =
  erase, op 1 = write (size 0 = whole file), anything else is skipped. The
  original table writes boot (0x0), Preset (0x28000), Main (0x33000) and
  MAIN_INFO (0xBF000), and never sends `FS.bin`.
- G1 FOUR and G1X FOUR v2.00 carry identical `ROM.bin`, `Main.bin` and
  `MAIN_INFO.bin`. They differ only in `FS.bin` and `Preset.bin`. Both
  `FS.bin` are 0x2FE000 bytes, the size of the file-system region at
  0x102000 in `RECOVERY_G1.md`.

## Steps
1. Download and unzip the Mac updater for your model.
2. Build the copy (use the updater matching your pedal):
   `python3 -I tools/make_mac_fs_restore.py "<...>/ZOOM G1 FOUR System v2.00 Updater.app" "G1FOUR FS restore (patched updater).app"`
   It refuses to patch unless the original table matches exactly, and
   re-signs the copy ad hoc.
3. Enter update mode: hold both footswitches while connecting USB until
   FIRMWARE UPDATE appears.
4. Open the copy (right-click > Open if Gatekeeper complains), select
   ZOOM G Series for MIDI IN and OUT, Execute. Wait for "Version update
   completed".
5. Unplug USB and power on.

The pedal comes back with the factory effects; DIY effects must be
reinstalled. The boot program, firmware, presets and settings sector are not
written.

## Notes
- Do not commit or redistribute the patched `.app`. It contains Zoom's
  firmware, and Zoom's licence forbids altering the updater; this is for
  repairing your own unit.
- The G1X FOUR variant is the same script on the G1X FOUR updater. It has
  not been run on hardware.
