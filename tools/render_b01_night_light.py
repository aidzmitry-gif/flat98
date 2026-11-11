"""Illustrate the SW03 night route on the parked-table B01 room model."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from b01_workplace_geometry import DINING_PARKED, OUTPUT, ROOT, load_model, verify, verify_chair_parking, verify_dining_parking
from draw_b01_lighting_plan import ENTRY_NIGHT, NIGHT_STRIP, SILL_NIGHT
from render_b01_o1_realistic import T, audit, mi, read_pfm, write_pfm
from render_b01_workplace import WorkplaceRender

DRAFT_SILL_Y = 2280
SILL_Y = SILL_NIGHT[1]
FIXTURE_Z = .238
CAMERAS = {
    'walk': (([.52, .82, 1.45], [4.76, 1.39, .73], 84), (1560, 940)),
    'overview': (([4.80, .85, 9.40], [2.855, 1.75, .55], 59), (1360, 1180)),
}
IMAGES = {
    'walk': 'B01_ночная_подсветка_путь_к_мансарде_v1.png',
    'overview': 'B01_ночная_подсветка_вся_комната_v1.png',
}


class NightLightRender(WorkplaceRender):
    def __init__(self, data, view, marker_z=FIXTURE_Z, strip_z=.078):
        super().__init__(data, 'night', park_chair=True)
        self.overview = view == 'overview'
        self.marker_z = marker_z
        self.strip_z = strip_z

    def add(self, name, shape):
        # This render uses only the three night fittings from SW03.
        emitter = isinstance(shape, dict) and ('emitter' in shape or shape.get('type') in ('directional', 'constant', 'spot'))
        if (emitter and not name.startswith('SW03_')) or name == 'landscape_on_screen':
            return
        super().add(name, shape)

    def shell(self):
        super().shell()
        if not self.overview:
            self.box('media_wall', (0, -.12, -.11), (self.width, 0, self.height), self.wall)
            self.media()

    def dining(self):
        parked = {key: tuple(v / 1000 for v in rect) for key, rect in DINING_PARKED.items()}
        self.dining_table(parked['table'], turned=True)
        for name in ('chair-1', 'chair-2'):
            self.dining_chair(parked[name], facing_x=True)

    def table_and_desk(self):
        super().table_and_desk()
        x1 = ENTRY_NIGHT[0] / 1000
        self.box('N1_recessed_marker_face', (x1 - .027, 0, self.marker_z - .019),
                 (x1 + .027, .006, self.marker_z + .021), self.ivory, .005)
        self.spot('SW03_N1', (x1, .012, self.marker_z), (.68, .64, 0), .77, 43)

        left, right = [point[0] / 1000 for point in NIGHT_STRIP]
        y2 = NIGHT_STRIP[0][1] / 1000
        # Use a continuous grazing source and a small shield to soften the
        # patch immediately at the plinth while lighting the walking lane.
        self.box('N2_profile_lower_shield', (left, y2 - .009, .044),
                 (right, y2 + .031, .052), self.kick)
        self.area('SW03_N2', ((left + right) / 2, y2, self.strip_z),
                  (right - left) / 2, .011, 263, [11.5, 8.05, 5.05])

        x, y = self.width, SILL_Y / 1000
        if self.overview:
            # Retain the wall behind the marker above the low section cut.
            self.box('sill_marker_backing', (x, 0, .25), (x + .145, .60, .36), self.wall)
        self.box('N3_recessed_marker_face', (x - .006, y - .025, self.marker_z - .018),
                 (x, y + .025, self.marker_z + .021), self.ivory, .005)
        self.spot('SW03_N3', (x - .014, y, self.marker_z), (x - .23, 1.65, .075), 1.24, 30)

    def spot(self, name, origin, aim, intensity, cutoff):
        self.add(name, {'type': 'spot', 'to_world': T().look_at(origin=origin, target=aim, up=[0, 0, 1]),
                        'intensity': {'type': 'rgb', 'value': [intensity, .70 * intensity, .43 * intensity]},
                        'cutoff_angle': cutoff, 'beam_width': cutoff * .65})


def sill_visibility(scene, width, marker_z=FIXTURE_Z):
    """Geometric rays to the inner threshold lip at six Y positions."""
    targets = [(width - .005, y, .119) for y in (1.46, 1.58, 1.71, 1.84, 1.97, 2.12)]
    counts = []
    for y in (DRAFT_SILL_Y, SILL_Y):
        source = np.array((width - .014, y / 1000, marker_z))
        open_count = 0
        for target in targets:
            vector = np.array(target) - source
            distance = np.linalg.norm(vector)
            ray = mi.Ray3f(mi.Point3f(source), mi.Vector3f(vector / distance))
            ray.maxt = distance - .002
            open_count += not scene.ray_test(ray)
        counts.append(open_count)
    return counts, len(targets)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('view', choices=CAMERAS)
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--samples', type=int, default=96)
    parser.add_argument('--hdr-input', type=Path)
    parser.add_argument('--exposure', type=float, default=4.0)
    options = parser.parse_args()
    name = options.view
    if options.hdr_input:
        raw = read_pfm(options.hdr_input)
    else:
        data = load_model()
        audit(data)
        verify(data)
        verify_dining_parking(data)
        verify_chair_parking(data)
        builder = NightLightRender(data, name)
        camera, size = CAMERAS[name]
        if options.preview:
            size = tuple(n // 2 for n in size)
        scene = builder.scene(*size, camera=camera)
        sources = [part for part in builder.parts if part.startswith('SW03_')]
        assert len(sources) == 3, sources
        clear, total = sill_visibility(scene, builder.width)
        print(f'Direct geometric paths to sill: original {clear[0]}/{total}; proposed {clear[1]}/{total}', flush=True)
        assert clear[0] < clear[1] == total, clear
        raw = np.asarray(mi.render(scene, spp=options.samples, seed=29))
        if not options.preview:
            write_pfm(ROOT / f'tmp/b01-sw03-{name}.pfm', raw)
    x = np.maximum(raw, 0) * options.exposure
    # Lift the dark tones for review while keeping the scene illuminated by SW03 only.
    display = (x / (1 + x)) ** .68
    display = np.where(display <= .0031308, display * 12.92, 1.055 * display ** (1 / 2.4) - .055)
    dest = ROOT / f'tmp/b01-sw03-{name}-preview.png' if options.preview else OUTPUT / IMAGES[name]
    Image.fromarray(np.round(display * 255).astype(np.uint8)).save(dest)
    print(f'Wrote {dest.name}', flush=True)


if __name__ == '__main__':
    main()
