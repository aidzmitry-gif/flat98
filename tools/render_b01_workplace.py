"""Render the B01 workplace, entrance and whole-room views."""
import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image

from b01_workplace_geometry import (
    CHAIR_BACK_OFFSET, CHAIR_BACK_RADIUS, CHAIR_BACK_STRETCH, CHAIR_PARKED, CHAIR_TRAVEL,
    CHAIR_WORK_Y, CHAIR_X, DESK_IMAGE, D2_PARTS, DOMO_OPEN_HEIGHT, DOMO_SLEEP_LENGTH,
    DOMO_SLEEP_WIDTH, ENTRY_IMAGE, FRIDGE_PARTS, OUTPUT, RADIATOR, RADIATOR_HEIGHT, ROOT,
    footprints, load_model, open_sofa, verify, verify_chair_parking,
)
from render_b01_o1_realistic import RoomRender, audit, matte, mi, read_pfm, write_pfm

CAMERAS = {
    'desk': ([3.41, .39, 1.55], [5.07, 2.55, 1.23], 75),
    'entry': ([2.73, 1.88, 1.57], [.45, 1.08, 1.15], 74),
    'wide': ([2.855, -4.75, 1.89], [2.855, 1.95, 1.20], 61),
    'overview': ([4.80, .85, 9.40], [2.855, 1.75, .55], 58),
}
CAMERAS['night'] = CAMERAS['wide']
IMAGES = {
    'desk': DESK_IMAGE,
    'entry': ENTRY_IMAGE,
    'wide': 'B01_общий_вид_вертикальный_радиатор_v1.png',
    'overview': 'B01_вся_комната_радиатор_створка_v1.png',
    'night': 'B01_ночной_режим_Domo_PRO_180_створка_v1.png',
}
SIZES = {
    'desk': (1550, 1020),
    'entry': (1550, 1020),
    'wide': (1600, 750),
    'overview': (1360, 1180),
    'night': (1600, 750),
}


class WorkplaceRender(RoomRender):
    def __init__(self, data, view, park_chair=False):
        super().__init__(data, view == 'overview')
        self.view = view
        self.park_chair = park_chair

    def shell(self):
        super().shell()
        if self.view == 'entry':
            self.box('media_wall_return', (0, -.12, -.11), (self.width, 0, self.height), self.wall)
            # A shallow neutral background, visible through D2 in the sectional view.
            self.box('unmeasured_hall_floor', (-1.5, -.15, -.11), (0, 1.58, -.001), self.kick)
            self.box('unmeasured_hall_backdrop', (-1.5, -.15, 0), (-1.45, 1.58, 2.70), self.wall)
            for ya in (-.15, 1.53):
                self.box('unmeasured_hall_side', (-1.45, ya, 0), (-.16, ya + .05, 2.70), self.wall)
            self.area('entry_fill', (1.30, 1.04, 2.61), .92, .69, 180, [3.5, 3.15, 2.75])

    def entry_leaf(self, a, b, top):
        if self.view != 'entry':
            super().entry_leaf(a, b, top)
            return
        n0, t0, n1, t1 = (value / 1000 for value in D2_PARTS[0])
        self.box('D2_variant_B_inward_90', (t0, a - n1, .009), (t1, a - n0, top - .007),
                 self.ivory, .003)
        for face, outer in ((a - n1, a - .039), (a - n0, a + .065)):
            self.tube('D2_handle_stem', (.817, face, 1.03), (.817, outer, 1.03), .010, self.brass)
            self.tube('D2_handle_lever', (.817, outer, 1.03), (.707, outer, 1.03), .009, self.brass)

    def terrace(self):
        super().terrace()
        if self.overview:
            # Keep the mounting wall immediately behind the radiator in the cutaway.
            x, jamb = self.width, self.data['terrace']['end'] / 1000
            self.box('O1_pier_above_section_cut', (x, jamb, .25),
                     (x + .145, 2.87, self.height), self.wall)

    def fridge(self):
        if self.view != 'entry':
            super().fridge()
            return
        _, y0, x1, y1 = self.rect['fridge']
        outer_end = x1 - .020
        white = matte('#f1f0e9', .31)
        self.box('fridge_plinth', (0, y0 + .004, 0), (x1 - .041, y1 - .004, .069), self.kick)
        self.box('fridge_case_back', (0, y0, .068), (.060, y1, 2.400), self.ivory)
        for za, zb in ((.069, .723), (1.937, 2.400)):
            self.box('fridge_case_closed_compartment', (.060, y0, za), (outer_end, y1, zb), self.ivory)
            self.box('fridge_closed_panel', (outer_end, y0 + .002, za + .002),
                     (x1, y1 - .002, zb - .002), self.ivory, .003)
        for ya, yb in ((y0, y0 + .031), (y1 - .031, y1)):
            self.box('fridge_case_side', (.060, ya, .723), (outer_end, yb, 1.937), self.ivory, .003)
        for z in (.736, .998, 1.250, 1.507, 1.760):
            self.box('fridge_interior_shelf', (.074, y0 + .036, z),
                     (.541, y1 - .034, z + .014), white, .005)
        self.area('fridge_internal_light', (.30, y0 + .30, 1.930), .17, .18, 180, [1.3, 1.43, 1.53])
        for profile, finish in zip(FRIDGE_PARTS[:2], (self.ivory, white)):
            n0, t0, n1, t1 = (value / 1000 for value in profile)
            self.box('fridge_open_90_entry_side_hinge', (x1 + t0, y0 - n1, .727),
                     (x1 + t1, y0 - n0, 1.934), finish, .004)
        self.tube('fridge_open_handle', (x1 + .565, y0 - .031, 1.139),
                  (x1 + .565, y0 - .031, 1.359), .009, self.nickel)
        for z in (1.16, 1.338):
            self.tube('fridge_open_handle_mount', (x1 + .565, y0, z),
                      (x1 + .565, y0 - .031, z), .009, self.nickel)
        for offset, z, color in ((.17, 1.264, '#617e60'), (.36, 1.264, '#ab7843'), (.28, 1.521, '#cbc1a4')):
            self.tube('fridge_content', (.325, y0 + offset, z), (.325, y0 + offset, z + .124),
                      .037, matte(color))

    def desk_accessories(self, laptop_x=5.055, lamp_x=4.657):
        super().desk_accessories(laptop_x=CHAIR_X / 1000, lamp_x=5.367)

    def dining(self):
        if self.view != 'night':
            super().dining()

    def sofa(self):
        if self.view != 'night':
            super().sofa()
            return
        # The external envelope follows the product card. Upholstery and
        # bedding are modelled for this interior.
        x0, y0, x1, y1 = (value / 1000 for value in open_sofa(footprints(self.data)['sofa']))
        folded_front = self.rect['sofa'][1]
        center = (x0 + x1) / 2
        half = DOMO_SLEEP_WIDTH / 2000
        left, right = center - half, center + half
        head = y0 + DOMO_SLEEP_LENGTH / 1000
        self.box('Domo_PRO_rear_upholstered_base', (x0 + .035, folded_front, .093),
                 (x1 - .035, y1, .375), self.olive, .032)
        self.box('Domo_PRO_fixed_back', (x0 + .034, head, .103),
                 (x1 - .034, y1, .482), self.olive, .022)
        for x in (x0, x1 - .070):
            self.box('Domo_PRO_slim_arm_70', (x, folded_front + .015, .104),
                     (x + .070, y1, DOMO_OPEN_HEIGHT / 1000), self.olive, .026)
        self.box('Domo_PRO_unfolded_foot_platform', (left, y0, .207),
                 (right, folded_front + .025, .374), self.olive, .026)
        for x in (left + .075, center, right - .075):
            for y in (y0 + .075, folded_front - .081):
                self.tube('Domo_PRO_pull_out_support', (x, y, .009), (x, y, .235), .013, self.black)
        self.box('Domo_PRO_sleep_surface_1800x2160', (left, y0, .356),
                 (right, head, .485), self.linen, .039)
        self.box('linen_bedcover', (left + .021, y0 + .041, .479),
                 (right - .021, head - .021, .511), matte('#e9dcc5', .56), .014)
        self.box('olive_folded_throw', (left + .017, y0 + .105, .508),
                 (right - .017, y0 + .665, .529), self.olive_dark, .010)
        for x in (center - .448, center + .448):
            self.box('linen_sleep_pillow', (x - .333, head - .455, .503),
                     (x + .333, head - .053, .616), self.linen, .056)
        self.sofa_art()

    def table_and_desk(self):
        super().table_and_desk()
        self.radiator()
        self.task_chair()

    def radiator(self):
        x0, y0, x1, y1 = (value / 1000 for value in RADIATOR)
        z = .14
        top = z + RADIATOR_HEIGHT / 1000
        enamel = matte('#e8e4dc', .26)
        self.box('radiator_rear_collectors', (x0 + .040, y0 + .007, z + .030),
                 (x1 - .022, y1 - .007, top - .031), enamel, .010)
        for i in range(7):
            ya = y0 + .005 + i * .056
            self.box('vertical_radiator_face', (x0 + .009, ya, z),
                     (x1 - .043, ya + .050, top), enamel, .013)
        for y in (y0 + .064, y1 - .064):
            self.tube('radiator_pipe_reserve', (x1 - .032, y, .03), (x1 - .032, y, .174),
                      .009, self.nickel)
        self.tube('radiator_valve', (x0 + .045, y1 - .064, .108), (x1 - .030, y1 - .064, .108),
                  .024, enamel)

    def task_chair(self):
        center = CHAIR_PARKED if self.park_chair else (CHAIR_X, CHAIR_WORK_Y - CHAIR_TRAVEL)
        x, y = (value / 1000 for value in center)
        if self.park_chair:
            # The seat and its mount clear the underside; the upright back stays in front.
            assert max(.459 + .218 * .19, .671 + .018) < .716
        fabric = matte('#888c73', .52)
        self.sphere('armless_chair_seat', (x, y + .014, .459), .218, fabric, (1, .95, .19))
        self.tube('chair_back_mount', (x, y - .125, .446), (x, y - .171, .671), .018, self.black)
        self.sphere('armless_chair_back', (x, y - CHAIR_BACK_OFFSET / 1000, .710),
                    CHAIR_BACK_RADIUS / 1000, fabric, CHAIR_BACK_STRETCH)
        self.tube('chair_gas_lift', (x, y, .068), (x, y, .442), .024, self.black)
        for i in range(5):
            angle = math.tau * i / 5 + .15
            cx, cy = x + .218 * math.cos(angle), y + .218 * math.sin(angle)
            self.tube('chair_star_leg', (x, y, .103), (cx, cy, .063), .013, self.black)
            self.tube('chair_caster', (cx - .012, cy, .026), (cx + .012, cy, .026), .025, self.black)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('view', choices=CAMERAS)
    parser.add_argument('--park-chair', action='store_true', help='Park the chair under the desk in the night view')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--samples', type=int)
    parser.add_argument('--hdr-input', type=Path)
    parser.add_argument('--exposure', type=float, default=1.0)
    options = parser.parse_args()
    data = load_model()
    audit(data)
    verify(data)
    name = options.view
    if options.park_chair:
        if name != 'night':
            parser.error('--park-chair requires the night view')
        verify_chair_parking(data)
    variant = 'night-parked' if options.park_chair else name
    filename = 'B01_ночной_вид_кресло_под_столом_v1.png' if options.park_chair else IMAGES[name]
    if options.hdr_input:
        radiance = read_pfm(options.hdr_input)
    else:
        builder = WorkplaceRender(data, name, options.park_chair)
        dimensions = SIZES[name]
        if options.preview and name in ('wide', 'overview', 'night'):
            dimensions = tuple(n // 2 for n in dimensions)
        elif options.preview:
            dimensions = (850, 560)
        scene = builder.scene(*dimensions, camera=CAMERAS[name])
        samples = options.samples or (12 if options.preview else 100)
        print(f'Rendering {name}: {dimensions}, {samples} spp', flush=True)
        radiance = np.asarray(mi.render(scene, spp=samples, seed=29))
        if not options.preview:
            write_pfm(ROOT / f'tmp/b01-workplace-{variant}.pfm', radiance)
    x = np.maximum(radiance, 0) * options.exposure
    display = np.clip(x * (2.51 * x + .03) / (x * (2.43 * x + .59) + .14), 0, 1)
    display = np.where(display <= .0031308, display * 12.92, 1.055 * display ** (1 / 2.4) - .055)
    dest = ROOT / f'tmp/b01-workplace-preview-{variant}.png' if options.preview else (
        OUTPUT / filename
    )
    Image.fromarray(np.round(display * 255).astype(np.uint8)).save(dest)
    print(f'Wrote {dest.name}', flush=True)


if __name__ == '__main__':
    main()
