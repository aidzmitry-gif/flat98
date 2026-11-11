"""Daytime view from the exact camera used for the B01 night-light view."""
import argparse
import subprocess

import numpy as np
from PIL import Image

from b01_workplace_geometry import (
    OUTPUT, ROOT, footprints, load_model, verify, verify_chair_parking,
)
from draw_b01_lighting_plan import ENTRY_NIGHT, NIGHT_MARKER_Z, SILL_NIGHT
from render_b01_n3_detail import OIDN, tame_speckles
from render_b01_night_light import CAMERAS
from render_b01_o1_realistic import T, audit, mi, read_pfm, write_pfm
from render_b01_workplace import WorkplaceRender

DEST = OUTPUT / 'B01_дневной_вид_от_входа_3D_v1.png'


class DayFromEntrance(WorkplaceRender):
    def __init__(self, data):
        super().__init__(data, 'wide', park_chair=True)

    def shell(self):
        super().shell()
        # The camera is within the room, so the wall behind the media unit is present.
        self.box('media_wall', (0, -.12, -.11), (self.width, 0, self.height), self.wall)
        self.media()
        # Soft photographic fill behind the camera exposes the room's shadows.
        self.add('daylight_photo_fill', {
            'type': 'rectangle',
            'to_world': T().translate((.48, 1.70, 1.45)).rotate([0, 1, 0], 90).scale([1.05, 1.25, 1]),
            'emitter': {'type': 'area', 'radiance': {'type': 'rgb', 'value': [3.8, 3.6, 3.3]}},
        })

    def table_and_desk(self):
        super().table_and_desk()
        x1 = ENTRY_NIGHT[0] / 1000
        z = NIGHT_MARKER_Z / 1000
        self.box('N1_marker_face', (x1 - .027, 0, z - .019),
                 (x1 + .027, .006, z + .021), self.ivory, .005)
        x, y = (value / 1000 for value in SILL_NIGHT)
        self.box('N3_marker_face', (x - .006, y - .025, z - .018),
                 (x, y + .025, z + .021), self.ivory, .005)

    def add(self, name, shape):
        # Keep the display dark, as in the reference, and leave ceiling fittings off.
        if name in ('landscape_on_screen', 'recessed_lamp', 'broad_fill'):
            return
        super().add(name, shape)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--samples', type=int, default=64)
    options = parser.parse_args()
    data = load_model()
    audit(data)
    verify(data)
    verify_chair_parking(data)
    objects = footprints(data)
    sofa, table = objects['sofa'], objects['table']
    assert (sofa[2] - sofa[0], sofa[3] - sofa[1]) == (1970, 1200)
    assert (table[2] - table[0], table[3] - table[1]) == (1400, 800)
    assert table[3] == sofa[1] and 0 < table[0] - sofa[0] == sofa[2] - table[2]
    assert len([objects[name] for name in ('chair-1', 'chair-2')]) == 2

    camera, size = CAMERAS['walk']
    if options.preview:
        size = tuple(v // 2 for v in size)
    builder = DayFromEntrance(data)
    scene = builder.scene(*size, camera=camera)
    assert sum('O1_left_open_glazing' in name for name in builder.parts) == 1
    assert sum('O1_right_glazing' in name for name in builder.parts) == 1
    assert sum('1400x800_stone_tabletop' in name for name in builder.parts) == 1
    assert sum('Domo_seat_base' in name for name in builder.parts) == 1
    print(f'Rendering {size[0]}×{size[1]} with {options.samples} samples', flush=True)
    radiance = np.asarray(mi.render(scene, spp=options.samples, seed=37))
    assert radiance.shape == (*size[::-1], 3) and np.isfinite(radiance).all()
    x = np.maximum(radiance, 0) * 1.65
    display = np.clip(x * (2.51 * x + .03) / (x * (2.43 * x + .59) + .14), 0, 1)
    display = np.where(display <= .0031308, display * 12.92, 1.055 * display ** (1 / 2.4) - .055)
    path = ROOT / 'tmp/b01-day-entry-preview' if options.preview else ROOT / 'tmp/b01-day-entry'
    original, denoised = path.with_suffix('.color.pfm'), path.with_suffix('.denoised.pfm')
    write_pfm(original, display)
    subprocess.run([str(OIDN), '--ldr', str(original), '--srgb', '--device', 'cpu', '-q', 'high',
                    '-o', str(denoised), '-v', '0'], check=True)
    colors = read_pfm(denoised)
    assert colors.shape == display.shape and np.isfinite(colors).all()
    image = Image.fromarray(np.rint(np.clip(tame_speckles(np.clip(colors, 0, 1)), 0, 1) * 255).astype('uint8'))
    destination = ROOT / 'tmp/b01-day-entry-preview.png' if options.preview else DEST
    image.save(destination)
    print(f'Wrote {destination}', flush=True)
    print(f'Sofa {sofa}, table {table}, chairs {objects["chair-1"]}, {objects["chair-2"]}', flush=True)


if __name__ == '__main__':
    main()
