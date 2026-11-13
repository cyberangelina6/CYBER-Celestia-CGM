# Printing the CYBER Celestia CGM

How to get the STL files out of Fusion and print every part in one go,
with no test prints.

## 1. Export the STL files

1. Run the script in Fusion (v26 or newer).
2. The pop-up at the end now asks **"Save STL files for printing now?"**. Click **Yes**.
3. Pick a folder. The script makes a new folder called `CelestiaCGM STL v26` inside it.
4. You get **16 files** (see the table below). The pop-up lists any problems.

Before you send the files anywhere, open one in a slicer (Bambu Studio,
PrusaSlicer, Cura, all free) or a free online STL viewer and check its size.
`Frame and grip L` should be about **175 × 142 mm**. If it shows up as
17.5 mm or 1750 mm, the units are wrong: re-import it as millimetres.

## 2. Where to print it cheaply

- **Free or nearly free:** public libraries, schools, colleges and makerspaces
  often have 3D printers and only charge for the plastic (or nothing). This is
  the best option on a tight budget. Bring the STLs on a USB stick and this page.
- **Online:** Craftcloud compares many print shops at once. JLC3DP is
  usually one of the cheapest. Pick **PLA** or **PETG** (FDM), not resin.
  Resin looks great but is brittle for the clips and levers.

**Printer size:** the biggest parts are the two `Frame and grip` halves,
about 175 × 142 × 17 mm each. They need a print bed of at least 180 mm, so
any normal printer (220 mm bed or bigger) works. Tiny printers (under 180 mm)
won't fit them.

## 3. Colours: keep it cheap

Every extra filament colour costs more. The cheapest way to get the look:

| Filament | Print these parts |
| --- | --- |
| **Light pink** | Frame and grip L/R, Recenter button, Rear cap heart L/R |
| **Hot pink / magenta** | Slide L/R, Grip panel L/R, Muzzle and shroud, Trigger, ADS lever, Reload button, Infuse button, Charm |
| **White or clear ("natural")** | LED window (light has to shine through it) |

Then paint the small accents with acrylic paint pens: the cream centres of
both hearts, the muzzle lip, the sight bead and the little grip pin dot.
If a shop offers more colours for free, the full colour list is in the Fusion
model (each part already has its colour).

## 4. Each part: how to lay it on the bed

"Split face down" means the flat inside face (where the left and right halves
meet) goes on the bed. Every L/R half has one, which is what makes them easy to print.

| File | Lay it | Supports | Notes |
| --- | --- | --- | --- |
| Slide L, Slide R | Split face down | Yes: **tree, touching build plate only** | Supports only grow inside the hollow, where nobody sees them |
| Frame and grip L, R | Split face down | Yes: tree, build plate only | The biggest parts. Print these first: if anything fails, it's here |
| Grip panel L, R | Split face down | Yes: tree, build plate only | Includes the trigger guard |
| Muzzle and shroud | Standing up on the **muzzle end** (front face down) | Yes: build plate only, under the heart flange | Short supports; snap them off and sand the flange underside |
| Rear cap heart L, R | Split face down | No | Glue the two halves together (superglue or 2-part epoxy) |
| Trigger, ADS lever | Flat on their side | No | Use **5 walls and 40% infill** so the pivot holes are strong |
| Reload button | Standing up, **flange (wide bottom) down** | No | |
| Infuse button, Recenter button | Round **outer face down** | No | The small flange overhang prints fine |
| LED window | Flat side down | No | 100% infill so it glows evenly |
| Charm | Flat on its side | No | |

The grey switches in the model are stand-ins for the microswitches you buy,
so they aren't exported.

## 5. Slicer settings (FDM)

| Setting | Value |
| --- | --- |
| Material | PLA (easiest) or PETG (tougher, slightly stringier) |
| Nozzle / layer height | 0.4 mm / 0.2 mm (0.12 mm for the buttons and charm if you want them smoother) |
| Walls (perimeters) | 4 (5 for Trigger and ADS lever) |
| Infill | 20% gyroid (15% is fine for the heart; 100% for the LED window) |
| Supports | Tree supports, **build plate only**, only where the table says |
| Brim | 5 mm brim on the Frame and grip halves to stop the corners lifting |

## 6. After printing

1. **Remove supports** and sand any rough spots, especially the split faces,
   which must sit flat against each other.
2. **Clean the holes.** Printed holes come out a little small. Twist a 3 mm
   drill bit through the trigger and ADS pivot holes by hand until the 3 mm
   pins slide in. Check that the M3 standoffs drop into their round pockets
   in the left halves. If they're tight, open the pockets with a 7 mm bit.
3. **Dry-fit everything before gluing.** Put the halves together with the
   standoffs and nuts, check that the trigger and ADS lever click their
   switches and the buttons press, and check that the Nano's USB-C port lines
   up with the hole in the base.
4. **Glue only the parts meant to be glued:** the two heart halves, the
   standoffs into the left-half pockets, and the LED window. The L/R halves
   of the gun stay screwed, so you can open it later.
5. **Paint the accents** last, once everything fits.
