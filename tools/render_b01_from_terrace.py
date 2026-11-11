"""B01 from the terrace side with the current day furniture geometry."""
import argparse
import subprocess

import numpy as np
from PIL import Image

from b01_workplace_geometry import OUTPUT, ROOT, footprints, load_model, verify, verify_chair_parking
from render_b01_n3_detail import OIDN, tame_speckles
from render_b01_o1_realistic import T, audit, mi, read_pfm, write_pfm
from render_b01_workplace import WorkplaceRender

CAMERAS = {
    'aperture': (([5.48, 2.40, 1.65], [1.82, 1.65, 1.20], 110), False),
    'section': (([6.90, 2.80, 1.72], [2.20, 1.65, 1.12], 110), True),
    'section_far': (([7.40, 2.60, 1.72], [2.20, 1.75, 1.12], 104), True),
    'section_media': (([6.80, .75, 1.70], [1.90, 2.40, 1.15], 110), True),
    'section_media_far': (([7.40, .75, 1.70], [1.90, 2.40, 1.15], 105), True),
    'section_balanced': (([6.90, 1.40, 1.70], [1.90, 2.25, 1.15], 108), True),
    'section_full': (([7.30, 1.70, 1.90], [1.50, 2.30, 1.08], 100), True),
}
DEST = OUTPUT / 'B01_вид_со_стороны_террасы_3D_v1.png'


class TerraceSide(WorkplaceRender):
    def __init__(self, data, section):
        super().__init__(data, 'wide', park_chair=True)
        self.section = section

    def shell(self):
        super().shell()
        self.box('media_wall', (0, -.12, -.11), (self.width, 0, self.height), self.wall)
        self.media()
        self.add('daylight_photo_fill', {
            'type': 'rectangle',
            'to_world': T().translate((9.50, 1.75, 1.45)).rotate([0, 1, 0], -90).scale([1.25, 1.55, 1]),
            'emitter': {'type': 'area', 'radiance': {'type': 'rgb', 'value': [8.0, 7.6, 7.0]}},
        })

    def terrace(self):
        if not self.section:
            super().terrace()

    def radiator(self):
        # The radiator belongs to the terrace-side wall, which is cut away in section.
        if not self.section:
            super().radiator()

    def add(self, name, shape):
        if name in ('landscape_on_screen', 'recessed_lamp', 'broad_fill'):
            return
        super().add(name, shape)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('view', choices=CAMERAS)
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--samples', type=int, default=64)
    options = parser.parse_args()
    data = load_model()
    audit(data)
    verify(data)
    verify_chair_parking(data)
    objects = footprints(data)
    sofa, table, desk, media = (objects[name] for name in ('sofa', 'table', 'desk', 'media'))
    assert (sofa[2] - sofa[0], sofa[3] - sofa[1]) == (1970, 1200)
    assert (table[2] - table[0], table[3] - table[1]) == (1400, 800)
    assert table[3] == sofa[1] and table[0] - sofa[0] == sofa[2] - table[2] == 285
    assert desk == [4500, 2900, 5700, 3500] and media == [2070, 0, 4870, 450]

    camera, section = CAMERAS[options.view]
    size = (800, 500) if options.preview else (1600, 1000)
    builder = TerraceSide(data, section)
    scene = builder.scene(*size, camera=camera)
    assert sum('1200x600_desk_surface' in name for name in builder.parts) == 1
    assert sum('1400x800_stone_tabletop' in name for name in builder.parts) == 1
    assert sum('ALR_screen' in name for name in builder.parts) == 1
    assert sum('Domo_seat_base' in name for name in builder.parts) == 1
    print(f'Rendering {options.view} {size[0]}×{size[1]} at {options.samples} spp', flush=True)
    radiance = np.asarray(mi.render(scene, spp=options.samples, seed=39))
    assert radiance.shape == (*size[::-1], 3) and np.isfinite(radiance).all()
    x = np.maximum(radiance, 0) * 1.35
    display = np.clip(x * (2.51 * x + .03) / (x * (2.43 * x + .59) + .14), 0, 1)
    display = np.where(display <= .0031308, display * 12.92, 1.055 * display ** (1 / 2.4) - .055)
    path = ROOT / 'tmp' / f'b01-terrace-{options.view}'
    original, denoised = path.with_suffix('.color.pfm'), path.with_suffix('.denoised.pfm')
    write_pfm(original, display)
    subprocess.run([str(OIDN), '--ldr', str(original), '--srgb', '--device', 'cpu', '-q', 'high',
                    '-o', str(denoised), '-v', '0'], check=True)
    colors = read_pfm(denoised)
    assert colors.shape == display.shape and np.isfinite(colors).all()
    result = np.rint(np.clip(tame_speckles(np.clip(colors, 0, 1)), 0, 1) * 255).astype('uint8')
    destination = ROOT / f'tmp/b01-terrace-{options.view}-preview.png' if options.preview else DEST
    Image.fromarray(result).save(destination)
    print(f'Wrote {destination}', flush=True)


if __name__ == '__main__':
    main()
