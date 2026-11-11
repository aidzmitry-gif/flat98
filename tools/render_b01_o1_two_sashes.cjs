const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const sharp = require('C:/Users/aidzm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');

// Millimetres. X runs from D2 to O1 and Y runs from the media wall to the sofa wall.
// Furniture footprints follow B01_масштабный_план_и_объём_зеркально_v2.
const room = { width: 5710, depth: 3500, assumedHeight: 2700 };
const entrance = { start: 200, end: 1110, height: 2150 };
const terrace = { start: 600, split: 1400, end: 2200, assumedTop: 2300, sketchWidth: 1598, sketchSill: 115 };
const furniture = [
  { id: 'corner', label: ['УГОЛ', '600'], rect: [0, 2900, 600, 3500], h: 860, color: '#e2d3bb' },
  { id: 'prep', label: ['500'], rect: [600, 2900, 1100, 3500], h: 860, color: '#eee4d3' },
  { id: 'hob', label: ['ВАРКА', '500'], rect: [1100, 2900, 1600, 3500], h: 860, color: '#eee4d3' },
  { id: 'pullout', label: ['200'], rect: [1600, 2900, 1800, 3500], h: 860, color: '#ead8b6' },
  { id: 'oven', label: ['ПЕНАЛ', '600'], rect: [1800, 2900, 2400, 3500], h: 2400, color: '#d8be9e' },
  { id: 'sink', label: ['МОЙКА', '570'], rect: [0, 2330, 600, 2900], h: 860, color: '#e8dcc9' },
  { id: 'dishwasher', label: ['ПММ', '600'], rect: [0, 1730, 600, 2330], h: 860, color: '#bed8cf' },
  { id: 'fridge', label: ['ХОЛ.', '600'], rect: [0, 1130, 600, 1730], h: 2400, color: '#d8be9e' },
  { id: 'sofa', label: ['ДИВАН', '1970 × 1200'], rect: [2485, 2300, 4455, 3500], h: 940, color: '#c5cbae' },
  { id: 'desk', label: ['РАБОЧЕЕ МЕСТО'], rect: [4500, 2900, 5700, 3500], h: 750, color: '#d5e3dc' },
  { id: 'table', label: ['СТОЛ', '1400 × 800'], rect: [2770, 1500, 4170, 2300], h: 750, color: '#e7d9c2' },
  { id: 'chair-1', label: ['СТУЛ'], rect: [2880, 1100, 3280, 1500], h: 850, color: '#e8b698' },
  { id: 'chair-2', label: ['СТУЛ'], rect: [3600, 1100, 4000, 1500], h: 850, color: '#e8b698' },
  { id: 'media', label: ['МЕДИАТУМБА 2800 × 450'], rect: [2070, 0, 4870, 450], h: 540, color: '#d6c2a6' },
  { id: 'books', label: ['КНИГИ'], rect: [4870, 0, 5470, 300], h: 2400, color: '#c8ac89' },
];
const data = { room, entrance, terrace, furniture };
const output = path.resolve(__dirname, '../output/visualizations');

function checkGeometry() {
  const byId = Object.fromEntries(furniture.map(item => [item.id, item.rect]));
  assert.equal(terrace.end - terrace.start, 1600);
  assert.equal(terrace.end - terrace.split, 800);
  assert.equal(terrace.split - terrace.start, 800);
  assert.equal(room.depth - terrace.end, 1300);
  assert.equal(byId.fridge[2] - byId.fridge[0], 600);
  assert.equal(byId.dishwasher[3] - byId.dishwasher[1], 600);
  assert.equal(room.depth - byId.fridge[1], 2370);
  assert.equal(byId.oven[2] - byId.corner[0], 2400);
  assert.equal(byId.oven[3], byId.sofa[3]);
  assert.equal(byId.sofa[0] - byId.oven[2], 85);
  assert.equal(byId.table[3], byId.sofa[1]);
  assert.ok(room.width - (terrace.end - terrace.split) > byId.sofa[2]);
  assert.ok(terrace.end < byId.desk[1]);
}

const ink = '#203934';
const muted = '#5d6e65';
const green = '#006c63';
const blue = '#577382';
const panel = '#fcfaf5';

function label(x, y, content, options = {}) {
  const { size = 22, weight = 400, fill = ink, align = 'start' } = options;
  return `<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${align}">${content}</text>`;
}

function line(x1, y1, x2, y2, color, width = 1.5, dash = '') {
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}"${dash ? ` stroke-dasharray="${dash}"` : ''}/>`;
}

function rect(x, y, w, h, fill, stroke = 'none', radius = 0) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${radius}" fill="${fill}" stroke="${stroke}"/>`;
}

function plan() {
  const scale = .139;
  const x = mm => 80 + mm * scale;
  const y = mm => 255 + (room.depth - mm) * scale;
  const wall = x(room.width);
  const hinge = y(terrace.end);
  const meeting = y(terrace.split);
  const sill = y(terrace.start);
  const radius = meeting - hinge;
  const openX = wall - radius;
  const objects = furniture.map(({ label: names, rect: [x0, y0, x1, y1], color, id }) => {
    const font = id === 'pullout' ? 13 : 15;
    const ty = (y(y0) + y(y1)) / 2 + (names.length > 1 ? -3 : 5);
    return rect(x(x0), y(y1), (x1 - x0) * scale, (y1 - y0) * scale, color, '#8a9280', 2) +
      names.map((name, index) => label(x((x0 + x1) / 2), ty + index * 18, name,
        { size: font, weight: 650, align: 'middle' })).join('');
  }).join('');

  return [
    label(80, 198, '01   ПЛАН СВЕРХУ', { size: 23, weight: 720 }),
    label(80, 228, 'Дневная расстановка · размеры в мм', { size: 18, fill: muted }),
    rect(x(0), y(room.depth), room.width * scale, room.depth * scale, '#f6f3eb'),
    objects,
    `<path d="M ${x(0)} ${y(entrance.end)} V ${y(room.depth)} H ${wall} V ${hinge} M ${wall} ${sill} V ${y(0)} H ${x(0)} V ${y(entrance.start)}" fill="none" stroke="${ink}" stroke-width="3.5"/>`,
    line(x(0), y(entrance.start), x(0), y(entrance.end), '#667c7d', 4, '6 4'),
    label(x(0) + 16, (y(entrance.start) + y(entrance.end)) / 2 + 6, 'D2', { size: 17, weight: 700, fill: muted }),
    `<path d="M ${wall} ${hinge} V ${meeting} A ${radius} ${radius} 0 0 1 ${openX} ${hinge} Z" fill="#d9ece4" opacity=".68"/>`,
    `<path d="M ${wall} ${meeting} A ${radius} ${radius} 0 0 1 ${openX} ${hinge}" fill="none" stroke="${green}" stroke-width="2" stroke-dasharray="6 5"/>`,
    line(wall, hinge, wall, meeting, green, 2, '5 5'),
    line(wall, meeting, wall, sill, blue, 6),
    line(wall, hinge, openX, hinge, green, 5.5),
    `<circle cx="${wall}" cy="${hinge}" r="5" fill="${green}"/>`,
    `<circle cx="${wall}" cy="${meeting}" r="4.3" fill="${panel}" stroke="${blue}" stroke-width="2"/>`,
    label(openX - 10, hinge + 5, '1', { size: 19, weight: 750, fill: green, align: 'end' }),
    label(wall - 14, (meeting + sill) / 2 + 6, '2', { size: 19, weight: 750, fill: blue, align: 'end' }),
    line(wall + 23, hinge, wall + 23, sill, blue),
    line(wall + 15, hinge, wall + 31, hinge, blue),
    line(wall + 15, sill, wall + 31, sill, blue),
    label(wall + 39, (hinge + sill) / 2 - 4, 'O1', { size: 18, weight: 750, fill: green }),
    label(wall + 39, (hinge + sill) / 2 + 20, '1600', { size: 18, fill: blue }),
    line(x(0), 770, wall, 770, '#a0a697'),
    line(x(0), 762, x(0), 778, '#a0a697'),
    line(wall, 762, wall, 778, '#a0a697'),
    label((x(0) + wall) / 2, 798, '5710 · по плану БТИ', { size: 18, fill: muted, align: 'middle' }),
  ].join('');
}

function elevation() {
  const scale = .16;
  const x = y => 1028 + (room.depth - y) * scale;
  const ground = 727;
  const left = x(terrace.end);
  const middle = x(terrace.split);
  const right = x(terrace.start);
  const top = ground - terrace.assumedTop * scale;
  const bottom = ground - terrace.sketchSill * scale;
  const edges = [x(room.depth), left, right, x(0)];
  const chain = [room.depth - terrace.end, terrace.end - terrace.start, terrace.start];

  return [
    label(1028, 198, '02   ВИД ИЗ КОМНАТЫ', { size: 23, weight: 720 }),
    label(1028, 228, 'Обе створки закрыты для сравнения', { size: 18, fill: muted }),
    rect(x(room.depth), ground - room.assumedHeight * scale, room.depth * scale, room.assumedHeight * scale,
      '#efe9dc', '#cdc6b7', 2),
    rect(left, bottom, right - left, ground - bottom, '#c7bba5'),
    rect(left, top, right - left, bottom - top, '#344746'),
    rect(left + 8, top + 8, middle - left - 12, bottom - top - 16, '#d2e6dd'),
    rect(middle + 4, top + 8, right - middle - 12, bottom - top - 16, '#dae4e5'),
    line(middle - 15, top + 176, middle - 15, top + 197, green, 4),
    `<circle cx="${left + 3}" cy="${top + 65}" r="5" fill="${green}"/><circle cx="${left + 3}" cy="${ground - 68}" r="5" fill="${green}"/>`,
    label((left + middle) / 2, top + 149, '1', { size: 34, weight: 750, fill: green, align: 'middle' }),
    label((middle + right) / 2, top + 149, '2', { size: 34, weight: 750, fill: blue, align: 'middle' }),
    label((left + middle) / 2, top + 177, 'левая', { size: 18, fill: green, align: 'middle' }),
    label((middle + right) / 2, top + 177, 'правая', { size: 18, fill: blue, align: 'middle' }),
    label(x(room.depth) + 16, ground - 22, 'К рабочему месту', { size: 17, fill: muted }),
    label(x(0) - 9, ground - 22, 'К экрану', { size: 17, fill: muted, align: 'end' }),
    line(edges[0], 763, edges[3], 763, '#a0a697'),
    ...edges.map(edge => line(edge, 756, edge, 770, '#a0a697')),
    ...chain.map((n, i) => label((edges[i] + edges[i + 1]) / 2, 796, String(n),
      { size: 19, weight: 700, fill: i === 1 ? green : muted, align: 'middle' })),
  ].join('');
}

function renderPlan() {
  return `<svg width="1680" height="1000" viewBox="0 0 1680 1000" font-family="Arial, sans-serif" role="img" aria-label="B01. План и фасад двух створок O1">
    ${rect(0, 0, 1680, 1000, '#f2eee4')}
    ${label(60, 58, 'КУХНЯ-ГОСТИНАЯ B01  /  ПРОЁМ O1', { size: 19, weight: 750, fill: green })}
    ${label(60, 113, 'Две створки на мансарду', { size: 49, weight: 750 })}
    ${rect(55, 154, 934, 664, panel, '#ded9ca', 14)}
    ${rect(1003, 154, 622, 664, panel, '#ded9ca', 14)}
    ${plan()}
    ${elevation()}
    ${rect(55, 842, 1570, 111, '#e3ebe2', 'none', 12)}
    ${label(80, 878, '1   Левая открывается внутрь. Петли со стороны рабочего места.', { size: 20, weight: 700 })}
    ${label(80, 914, '2   Правая показана закрытой. Её механизм пока не уточнён.', { size: 19 })}
    ${line(848, 858, 848, 937, '#b2c1b6')}
    ${label(876, 875, `Проём ${terrace.end - terrace.start} мм по БТИ · ${terrace.sketchWidth} мм по обмерному эскизу.`, { size: 19, weight: 700 })}
    ${label(876, 906, 'Деление 800 + 800 мм и угол 90° условны. Под створками 115 мм по эскизу.', { size: 18 })}
    ${label(876, 932, 'Ширину каждой створки, высоту и отметку порога уточнить на месте.', { size: 17, fill: muted })}
  </svg>`;
}

async function main() {
  checkGeometry();
  await sharp(Buffer.from(renderPlan()), { density: 90 }).png()
    .toFile(path.join(output, 'B01_схема_O1_две_створки_v1.png'));
  fs.writeFileSync(path.resolve(__dirname, '../tmp/b01-o1-two-sashes.json'), JSON.stringify(data));
  console.log('B01 plan: verified dimensions and opening side; 2100 × 1250 PNG saved.');
}

main().catch(error => { console.error(error); process.exitCode = 1; });
