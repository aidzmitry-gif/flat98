"""Shared millimetre geometry for the B01 radiator, desk and entrance study."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'tmp/b01-o1-two-sashes.json'
OUTPUT = ROOT / 'output/visualizations'
DESK_IMAGE = 'B01_рабочее_место_радиатор_и_кресло_v1.png'
ENTRY_IMAGE = 'B01_вход_и_холодильник_открыты_v1.png'
PLAN_IMAGE = 'B01_проверка_радиатора_кресла_и_дверей_v1.png'

RADIATOR = (5590, 2350, 5710, 2750)
RADIATOR_HEIGHT = 1600
CHAIR_X = 4750
CHAIR_WORK_Y = 2730
CHAIR_TRAVEL = 250
CHAIR_RADIUS = 260
CHAIR_PARKED = (5000, 3010)
CHAIR_BACK_OFFSET = 165
CHAIR_BACK_RADIUS = 196
CHAIR_BACK_STRETCH = (1, .185, .67)
DOMO_OPEN_DEPTH = 2230
DOMO_OPEN_HEIGHT = 640
DOMO_SLEEP_WIDTH = 1800
DOMO_SLEEP_LENGTH = 2160
DINING_PARKED = {
    'table': (1600, 1370, 2400, 2770),
    'chair-1': (1500, 2160, 1900, 2560),
    'chair-2': (1500, 1560, 1900, 1960),
}

# Door parts in their closed planes, as (normal min, run min, normal max, run max).
# Handle dimensions are allowances. Actual door and appliance hardware are unknown.
O1_PARTS = ((-14, 0, 27, 800), (-40, 765, 60, 785))
D2_PARTS = ((-35, 7, -3, 903), (-75, 698, 48, 826))
FRIDGE_PARTS = ((-20, 2, 0, 598), (-65, 20, -20, 568), (0, 475, 40, 590))


def load_model():
    return json.loads(MODEL.read_text(encoding='utf-8'))


def footprints(data):
    return {item['id']: item['rect'] for item in data['furniture']}


def open_sofa(sofa_rect):
    x0, _, x1, back = sofa_rect
    assert x1 - x0 == 1970
    return (x0, back - DOMO_OPEN_DEPTH, x1, back)


def corners(rect):
    x0, y0, x1, y1 = rect
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def door_points(hinge, profile, angle, sign):
    """Rotate a leaf inward. Its closed run points along Y for +1 or -Y for -1."""
    hx, hy = hinge
    c, s = math.cos(angle), math.sin(angle)
    return [(hx + n * c + sign * t * s, hy - n * s + sign * t * c)
            for n, t in corners(profile)]


def rect_distance(point, rect):
    x, y = point
    x0, y0, x1, y1 = rect
    return math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1))


def rect_gap(a, b):
    return math.hypot(max(0, a[0] - b[2], b[0] - a[2]), max(0, a[1] - b[3], b[1] - a[3]))


def overlaps(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def verify_dining_parking(data):
    rects = footprints(data)
    day_table = rects['table']
    table = DINING_PARKED['table']
    chairs = [DINING_PARKED[key] for key in ('chair-1', 'chair-2')]
    bed = open_sofa(rects['sofa'])
    assert (day_table[2] - day_table[0], day_table[3] - day_table[1]) == (1400, 800)
    assert (table[2] - table[0], table[3] - table[1]) == (800, 1400)
    fixed = [r for key, r in rects.items() if key not in DINING_PARKED]
    assert all(not overlaps(r, fixed_item) for r in DINING_PARKED.values() for fixed_item in [*fixed, bed])
    # Chair backs remain outside the top; the seats fit between the table legs
    # at the long side. The dimensions match the current dining render.
    for chair in chairs:
        assert chair[2] - chair[0] == chair[3] - chair[1] == 400
        assert table[1] + 127 < chair[1] < chair[3] < table[3] - 127
        assert chair[0] + 83 < table[0] < chair[2]

    # First put the chairs by the media wall. Move the table in front of the
    # folded sofa, turn it at (1540, 1850), then slide it to the parking spot.
    staged = [(r[0], 600, r[2], 1000) for r in (rects['chair-1'], rects['chair-2'])]
    for key, r in zip(('chair-1', 'chair-2'), staged):
        assert not any(overlaps((r[0], r[1], r[2], rects[key][3]), part) for part in [*fixed, day_table])
    radius = math.hypot(700, 400)
    table_sweeps = [
        (2770, 1450, 4170, 2300),
        (840, 1450, 4170, 2250),
        (1540 - radius, 1850 - radius, 1540 + radius, 1850 + radius),
        (1140, 1150, 2400, 2770),
    ]
    assert not any(overlaps(sweep, part) for sweep in table_sweeps for part in [*fixed, *staged])
    # Rotate each chair in the open area, take it along the kitchen front and
    # slide it under the parked table from the side.
    chair_turn = math.hypot(200, 200)
    for source, dest in zip(staged, chairs):
        sweeps = [
            (950, 600, source[2], 1000),
            (1150 - chair_turn, 800 - chair_turn, 1150 + chair_turn, 800 + chair_turn),
            (950, 600, 1350, dest[3]),
        ]
        assert not any(overlaps(sweep, part) for sweep in sweeps for part in [*fixed, table])
        assert not any(overlaps((950, dest[1], dest[2], dest[3]), part) for part in fixed)
    assert chairs[1][3] < chairs[0][1]

    fridge = rects['fridge']
    dining_left = min(r[0] for r in DINING_PARKED.values())
    d2_reach = max(math.hypot(max(n1, 0), t1) for _, _, n1, t1 in D2_PARTS)
    fridge_reach = fridge[2] + max(math.hypot(max(n1, 0), t1) for _, _, n1, t1 in FRIDGE_PARTS)
    assert dining_left > max(d2_reach, fridge_reach)
    pmm = rects['dishwasher']
    pmm_open = (pmm[2], pmm[1], pmm[2] + 650, pmm[3])
    oven = rects['oven']
    oven_open = (oven[0], oven[1] - 600, oven[2], oven[1])
    assert overlaps(table, oven_open)
    return {
        'aisle': dining_left - pmm[2],
        'pmm_open_gap': min(rect_gap(pmm_open, r) for r in DINING_PARKED.values()),
        'bed_gap': bed[0] - table[2],
        'turn_gap': min(rect_gap(table_sweeps[2], r) for r in fixed),
    }


def closest_sash(hinge, x, y):
    """Closest modelled edge over the provisional 0–90 degree sash travel."""
    dx, dy = x - hinge[0], y - hinge[1]
    best = math.inf
    for step in range(361):
        angle = math.radians(step / 4)
        c, s = math.cos(angle), math.sin(angle)
        local = (dx * c - dy * s, -dx * s - dy * c)
        best = min(best, *(rect_distance(local, part) for part in O1_PARTS))
    return best - CHAIR_RADIUS


def verify_chair_parking(data):
    rects = footprints(data)
    x, y = CHAIR_PARKED
    left, front, right, back = rects['desk']
    # Shift sideways after returning to the working Y, then push under the top.
    # The first part of this move is covered by verify() for the work and pulled poses.
    assert CHAIR_X - CHAIR_RADIUS > rects['sofa'][2]
    sash_end = data['terrace']['end'] + max(-part[0] for part in O1_PARTS)
    assert CHAIR_WORK_Y - CHAIR_RADIUS > sash_end
    assert x + CHAIR_RADIUS < RADIATOR[0]
    assert left + 31 < x - CHAIR_RADIUS and x + CHAIR_RADIUS < right - 31
    assert y + CHAIR_RADIUS < back
    back_to_top = front - (y - CHAIR_BACK_OFFSET + CHAIR_BACK_RADIUS * CHAIR_BACK_STRETCH[1])
    assert back_to_top > 0
    return {'base_in_front': front - (y - CHAIR_RADIUS), 'back_to_top': back_to_top}


def verify(data):
    room = data['room']
    rects = footprints(data)
    assert rects['desk'] == [4500, 2900, 5700, 3500]
    assert rects['sofa'][2] == 4455
    o1 = data['terrace']
    assert room['width'] == 5710 and o1['end'] == 2200 and o1['end'] - o1['split'] == 800
    hinge = (room['width'], o1['end'])
    chair_back_y = CHAIR_WORK_Y - CHAIR_TRAVEL
    # For the modelled profiles the entire sash sweep remains below the chair in Y,
    # so the furthest pulled position is the closest along the straight chair travel.
    sash_max_y = hinge[1] + max(-part[0] for part in O1_PARTS)
    assert sash_max_y < chair_back_y
    desk_leg_inside_x = rects['desk'][0] + 31
    result = {
        'chair_to_sash_work': closest_sash(hinge, CHAIR_X, CHAIR_WORK_Y),
        'chair_to_sash_pulled': closest_sash(hinge, CHAIR_X, chair_back_y),
        'chair_to_sash_at_300': closest_sash(hinge, CHAIR_X, CHAIR_WORK_Y - 300),
        'chair_to_sofa': CHAIR_X - CHAIR_RADIUS - rects['sofa'][2],
        'desk_to_sash_frame': rects['desk'][1] - hinge[1] - 14,
        'radiator_to_sash_sweep': RADIATOR[1] - sash_max_y,
        'radiator_to_desk': rects['desk'][1] - RADIATOR[3],
    }
    assert min(value for key, value in result.items() if key != 'chair_to_sash_at_300') > 0
    assert result['chair_to_sash_at_300'] < 0
    # Where the circular rolling envelope reaches the leg's starting Y at 2942 mm,
    # its half chord is smaller than the centre-to-leg distance.
    leg_front_distance = rects['desk'][1] + 42 - CHAIR_WORK_Y
    assert math.sqrt(CHAIR_RADIUS**2 - leg_front_distance**2) < CHAIR_X - desk_leg_inside_x

    d2 = data['entrance']
    fridge = rects['fridge']
    assert (d2['start'], d2['end'], fridge) == (200, 1110, [0, 1130, 600, 1730])
    d2_far_y = d2['start'] + max(math.hypot(-n0, t1) for n0, _, _, t1 in D2_PARTS)
    d2_far_x = max(math.hypot(max(n1, 0), t1) for _, _, n1, t1 in D2_PARTS)
    # The D2 sweep remains before the fixed case and the full refrigerator leaf.
    assert d2_far_y < fridge[1]
    # The refrigerator handle can only enter that Y range near 90 degrees.
    # At such an angle its smallest possible X is beyond the entire D2 sweep.
    handle = FRIDGE_PARTS[-1]
    cos_limit = (d2_far_y - fridge[1] + handle[2]) / handle[1]
    assert 0 < cos_limit < 1
    assert fridge[2] + handle[1] * math.sqrt(1 - cos_limit**2) > d2_far_x
    # Check refrigerator door sweep against the neighbour's bounding plane.
    assert fridge[1] + max(math.hypot(max(-n0, 0), t1) for n0, _, _, t1 in FRIDGE_PARTS) < fridge[3]
    # At 90 degrees the closest X-overlapping elements are the D2 handle and fridge face.
    assert D2_PARTS[-1][1] < FRIDGE_PARTS[0][3] + fridge[2]
    assert D2_PARTS[-1][3] > FRIDGE_PARTS[0][1] + fridge[2]
    result['fridge_to_jamb'] = fridge[1] - d2['end']
    result['both_doors_at_90'] = fridge[1] - (d2['start'] - D2_PARTS[-1][0])
    return result
