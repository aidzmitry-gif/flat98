"""Render the same B01 sill detail in daylight and with only SW03 active."""
import argparse
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import median_filter

from b01_workplace_geometry import OUTPUT, ROOT, load_model, verify, verify_chair_parking, verify_dining_parking
from draw_b01_lighting_plan import NIGHT_MARKER_Z, NIGHT_STRIP_Z, SILL_NIGHT
from render_b01_night_light import NightLightRender, sill_visibility
from render_b01_o1_realistic import T, audit, matte, mi, read_pfm, write_pfm

DEST = OUTPUT / 'B01_N3_день_и_ночь_3D_v1.png'
OIDN = ROOT / 'tmp/b01-oidn-runtime/oidn-2.5.1.x64.windows/bin/oidnDenoise.exe'
CAMERA = ([3.40, .51, 1.26], [5.53, 1.38, 1.12], 70)
SIZE = (800, 710)


class SillDetailRender(NightLightRender):
    def __init__(self, data, daytime):
        super().__init__(data, 'walk', NIGHT_MARKER_Z / 1000, NIGHT_STRIP_Z / 1000)
        self.daytime = daytime

    def add(self, name, shape):
        if self.daytime:
            # Same furniture and hardware, with soft daylight for locating the fitting.
            if name in ('daylight_sky', 'detail_fill') or not (
                isinstance(shape, dict) and ('emitter' in shape or shape.get('type') in ('directional', 'spot'))
            ):
                self.parts[f'{name}_{len(self.parts):04d}'] = shape
        else:
            super().add(name, shape)

    def table_and_desk(self):
        super().table_and_desk()
        x, y = (v / 1000 for v in SILL_NIGHT)
        z = self.marker_z
        self.box('N3_shielded_aperture', (x - .007, y - .016, z - .009),
                 (x - .005, y + .016, z + .001), matte('#675f52', .58), .001)
        if self.daytime:
            self.add('detail_fill', {
                'type': 'rectangle',
                'to_world': T().translate([2.72, .91, 1.50]).rotate([0, 1, 0], 90).scale([.81, .73, 1]),
                'emitter': {'type': 'area', 'radiance': {'type': 'rgb', 'value': [4.8, 4.6, 4.25]}},
            })


def project(point, size):
    origin, target, fov = CAMERA
    forward = np.subtract(target, origin)
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, [0, 0, 1])
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    ray = np.subtract(point, origin)
    focal = size[0] / (2 * np.tan(np.deg2rad(fov / 2)))
    return (size[0] / 2 + np.dot(ray, right) * focal / np.dot(ray, forward),
            size[1] / 2 - np.dot(ray, up) * focal / np.dot(ray, forward))


def develop(raw, daytime):
    x = np.maximum(raw, 0) * (1.35 if daytime else 4.2)
    if daytime:
        linear = np.clip(x * (2.51 * x + .03) / (x * (2.43 * x + .59) + .14), 0, 1)
    else:
        linear = (x / (1 + x)) ** .73
    return np.where(linear <= .0031308, linear * 12.92, 1.055 * linear ** (1 / 2.4) - .055)


def tame_speckles(rgb):
    """Suppress sparse path-tracing outliers while retaining frame edges."""
    luminance = rgb @ np.array([.2126, .7152, .0722], dtype='float32')
    reference = median_filter(luminance, 5)
    signal = np.clip(luminance, np.maximum(reference - .04, 0), reference + .052)
    pixels = rgb * (signal / np.maximum(luminance, 1e-5))[..., None]
    h, w = luminance.shape
    padded = np.pad(pixels, ((2, 2), (2, 2), (0, 0)), mode='edge')
    colors = np.zeros_like(pixels)
    weights = np.zeros_like(luminance)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            neighbor = padded[2 + dy:2 + dy + h, 2 + dx:2 + dx + w]
            distance = np.sum(np.square(neighbor - pixels), axis=-1)
            weight = np.exp(-(dx * dx + dy * dy) / 4 - distance / .023)
            colors += neighbor * weight[..., None]
            weights += weight
    return colors / weights[..., None]


def frame(data, daytime, size, samples):
    render = SillDetailRender(data, daytime)
    scene = render.scene(*size, camera=CAMERA)
    if not daytime:
        assert sum(name.startswith('SW03_') for name in render.parts) == 3
        rays, count = sill_visibility(scene, render.width, render.marker_z)
        assert rays == [0, count], rays
        print(f'N3 at +{NIGHT_MARKER_Z}: direct geometric paths {rays[1]}/{count}', flush=True)
    mode = 'day' if daytime else 'night'
    print(f'Rendering {mode}: {size[0]} × {size[1]}, {samples} spp', flush=True)
    raw = np.asarray(mi.render(scene, spp=samples, seed=31))
    assert raw.shape == (*size[::-1], 3) and np.isfinite(raw).all(), raw.shape
    beauty = develop(raw, daytime)
    base = ROOT / 'tmp' / f'b01-n3-v4-{mode}-{size[0]}'
    color, clean = base.with_suffix('.color.pfm'), base.with_suffix('.clean.pfm')
    write_pfm(color, beauty)
    subprocess.run([str(OIDN), '--ldr', str(color), '--srgb',
                    '--device', 'cpu', '-q', 'high', '-o', str(clean), '-v', '0'], check=True)
    clean_pixels = read_pfm(clean)
    assert clean_pixels.shape == beauty.shape and np.isfinite(clean_pixels).all()
    pixels = tame_speckles(np.clip(clean_pixels, 0, 1))
    return Image.fromarray(np.rint(np.clip(pixels, 0, 1) * 255).astype('uint8'))


def board(frames, size):
    gap, margin, header, footer = 26, 42, 144, 112
    w, h = size
    sheet = Image.new('RGB', (2 * w + gap + 2 * margin, h + header + footer), '#f4f1ea')
    draw = ImageDraw.Draw(sheet)
    fonts = Path('C:/Windows/Fonts')

    def label(x, y, value, points, bold=False, color='#263831', anchor='lt'):
        font = ImageFont.truetype(fonts / ('segoeuib.ttf' if bold else 'segoeui.ttf'), points)
        draw.text((x, y), value, font=font, fill=color, anchor=anchor)

    label(margin, 26, 'B01  /  N3 у двери на мансарду', 45, True)
    label(margin, 89, 'Один ракурс из размерной модели. Левая створка открыта внутрь.', 23, color='#54655c')
    px, py = project((SILL_NIGHT[0] / 1000 - .007, SILL_NIGHT[1] / 1000, NIGHT_MARKER_Z / 1000), size)
    assert 0 < px < w and 0 < py < h
    for index, (photo, caption) in enumerate(zip(frames, ('01   Где стоит N3', '02   Ночной свет SW03'))):
        x = margin + index * (w + gap)
        sheet.paste(photo, (x, header))
        u, v = x + px, header + py
        badge_x, badge_y = u + 34, v - 39
        if badge_x + 61 > x + w - 16:
            badge_x = u - 94
        draw.line((u, v, badge_x + 30, badge_y + 16), fill='#172b28', width=6)
        draw.line((u, v, badge_x + 30, badge_y + 16), fill='#faf9eb', width=2)
        draw.ellipse((u - 8, v - 8, u + 8, v + 8), outline='#172b28', width=5)
        draw.ellipse((u - 8, v - 8, u + 8, v + 8), outline='#faf9eb', width=2)
        draw.rounded_rectangle((badge_x, badge_y, badge_x + 61, badge_y + 32), radius=7, fill='#226e73')
        label(badge_x + 30, badge_y + 16, 'N3', 18, True, 'white', 'mm')
        label(x, header + h + 18, caption, 24, True)
    label(margin, header + h + 64,
          'Корпус условный. Ночной кадр показывает направление света при повышенной экспозиции.', 21, color='#54655c')
    return sheet


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--preview', action='store_true')
    cli.add_argument('--samples', type=int, default=32)
    args = cli.parse_args()
    data = load_model()
    audit(data)
    verify(data)
    verify_dining_parking(data)
    verify_chair_parking(data)
    size = tuple(value // 2 for value in SIZE) if args.preview else SIZE
    pictures = [frame(data, daytime, size, args.samples) for daytime in (True, False)]
    path = ROOT / 'tmp/b01-n3-v4-preview.png' if args.preview else DEST
    board(pictures, size).save(path)
    print(path.name, flush=True)


if __name__ == '__main__':
    main()
