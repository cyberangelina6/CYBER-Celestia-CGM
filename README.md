# CYBER-Celestia-CGM
My CGM specs, modelling and code

## Layout

| Path | What |
| --- | --- |
| `reference/concept-sketch-v1.webp` | Concept sketch with labelled parts |
| `Fusion/Scripts/CelestiaGunMouse/` | Fusion script that builds the starter model |
| `Fusion/preview/` | Side-view preview of the script's outlines (no Fusion needed) |
| `Fusion/PRINTING.md` | Exporting STL files and how to print each part |

## Building the model in Fusion

1. Download this repo (Code → Download ZIP) and unzip it.
2. In Fusion: **Utilities → Add-Ins → Scripts and Add-Ins**.
3. Click **+** → *Script or add-in from device* and pick the
   `Fusion/Scripts/CelestiaGunMouse` folder.
4. Select **CelestiaGunMouse** and click **Run**. It opens a new design.

Each part of the sketch becomes its own component: Slide, Muzzle & Shroud,
Frame & Grip, Grip Panel, Trigger, Top Button, Rear Cap (Heart) and Charm.
The model is mirrored so Fusion's Front view shows the left side (with the
readout), matching the sketch.

**Changing sizes**
- Widths and cut depths: **Modify → Change Parameters** (live).
- Lengths, heights, angles and positions: edit the `DIMENSIONS` block at the
  top of `CelestiaGunMouse.py`, then run the script again.

To check proportions without Fusion: `pip install matplotlib pillow`, then
`python Fusion/preview/preview_side.py` (writes `Fusion/preview/side-view.png`).
