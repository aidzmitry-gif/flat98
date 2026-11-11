# ТВ-стена B01: размерное предложение

2026-09-05. Вариант с дополнительным хранением; существующий кухонный редактор не изменён. Горизонтальные размеры построены по координатам. Рендер служит для оценки материалов; геометрию проверять по размерной модели.

## Источники геометрии

- Комната 5710 × 3500 мм — B01 и текущая пользовательская расстановка. Это проектный контур; контрольные обмеры не полностью совпадают.
- Диван: X=2470, Y=2500, 2000 × 1000; ось X=3470. Стол Ø850: X=1200, Y=1300; рабочее место: X=4500, Y=2900, 1200 × 600.
- ТВ-стена глухая. Вход справа на боковой стене при взгляде с дивана — прямое уточнение пользователя.
- Отступ до D2: 200 мм по `docs/18_Стена_и_размерные_цепочки_APT-001_revision_8.md:8` и `plans/04_Подробный_обмерный_план_A2_М1_50.svg:143`. Проём БТИ 910 и чистый пользовательский контроль 915 × 2150 показаны как разные данные. В модели применена комбинация X=0, Y=200…1115; это не единая проверенная натурная цепочка. Открывание не задано.
- O1: X=5710, Y=600…2200 по БТИ; от ТВ-стены 600 мм, проём 1600, далее 1300. Прежний `kitchen-drag-plan.html` ошибочно содержит другой порядок простенков O1 и положение D2. Новая размерная модель следует подробному плану и уточнению пользователя.
- Высоты из `docs/04_Цифровая_ведомость_обмеров_v1.md`: углы 2727 / 2712 / 2717 / 2714, центр 2719; локально у стены с розетками 2530. Привязка локального понижения к ТВ-стене отсутствует. Высота 2719 в модели — условная горизонтальная линия по точке центра, а не отметка готового потолка.

## Предложение по мебели

Координаты в мм от левого нижнего угла плана. Z — от пола.

| Элемент | X | Y | Ш × Г × В | Z низа |
| --- | ---: | ---: | --- | ---: |
| Подвесная тумба, 4 секции по 500 | 2470 | 0 | 2000 × 300 × 350 | 150 |
| Неглубокий шкаф с полками | 1650 | 0 | 600 × 300 × 2200 | 0 |
| Экран для примерки 65 дюймов | ось 3470 | у ТВ-стены | условный экран 1439 × 809 | центр Z=1100 |

Оси дивана и ТВ совпадают. Между тумбой и шкафом 220 мм. Оба корпуса заканчиваются на Y=300 и не пересекают предусмотренную полосу Y=300…1300 при закрытых фасадах. От переднего края тумбы до переднего края дивана 2200 мм. Открытые фасады и стулья без фактических моделей в этой проверке не учтены.

В развёртке с дивана: 1240 мм слева + тумба 2000 + 2470 мм справа = 5710 мм. Шкаф занимает участок 3460…4060 мм от левого края развёртки, после него до правого угла 1650 мм. Тумба составляет 35,03% ширины всей стены. Исходный вариант 1600 мм также сохранён в переключателе для сравнения; в нём отступы 1410 и 2700 мм и расхождение осей 30 мм.

Наполнение: в тумбе — документы, пульты, небольшие игры и ТВ-оборудование; доступ к оборудованию и его вентиляцию разработать под модель. Шкаф — регулируемые полки для книг, небольших коробок и бытовых запасов. Глубина 300 мм наружная, полезная меньше; это не обычный гардероб для плечиков. Предлагаемые высоты мебели и ТВ не являются пользовательскими обмерами.

Материалы: матовые песочные фасады в гамме кухни, ореховая верхняя плоскость тумбы/боковина шкафа, тонкая матовая латунь. Стена спокойная матовая, без глянцевой плиты за экраном. Приглушённая нижняя подсветка, отдельное управление; световой поток в экран не направлять. Кабельные выводы и крепления уточняются после выбора ТВ, кронштейна и проверки материала стены.

Проверено: расчёт координат, отсутствие пересечений новых закрытых корпусов с диваном/столом/рабочим местом и полосой прохода; работа трёх видов и переключателей; отображение на ширинах 736 и 360 пикселей.

## Задание встроенному Imagegen

Create one carefully scaled photorealistic interior view, using the attached DIMENSIONED FRONT ELEVATION as the geometry authority. The attached image is a diagram with UI and labels: discard its UI and text, but keep the front wall proportions and all furniture placements exactly as depicted in the diagram. Render the same wall in the user's warm sand, walnut and brass kitchen-living-room style, viewed from the sofa. This is a geometry-to-materials rendering, not a freely recomposed room.
THE FRONTAL TV WALL HAS NO DOOR AND NO OPENING. It is 5710mm wide, illustrative2719mm tall. Both perpendicular side walls may be visible at frame edges; the full TV wall must fit in the frame, with both corners visible. Near-frontal, very restrained perspective, seated eye height1100, no zoom into furniture; retain the broad empty parts of wall indicated in the diagram. Use a fairly wide horizontal image showing full wall rather than a close crop. Television is offset left of the full wall center, aligned with sofa, NEVER center all furniture in the wall.

Read these horizontal positions FROM THE LEFT EDGE OF THE FRONT WALL AS THE VIEWER SEES IT:
- left end of floating TV console1240mm; console width2000; right end3240mm. Console is only35.0% of full wall width. Four equal closed lower fronts500mm each. Console bottom150mm above floor, top500mm above floor, height350mm and depth300mm. Matte warm sand fronts, fine walnut top with narrow brushed brass edge, one delicate warm under-console glow.
- thin black wall-mounted screen centered2240mm from left wall corner. Screen approximate65-inch 16:9 silhouette1439mm wide x809mm tall; center1100mm above floor. This is only25.2% of wall width. Slim dark screen, no slideshow.
- narrow separate tall storage cabinet from3460mm to4060mm from the wall's left corner: width600mm, depth300mm, height2200mm, two simple tall matte warm sand doors300mm each, walnut side visible and fine discreet brass detail. Gap between TV console and cabinet220mm. Cabinet front is in same depth plane as console front; it must NOT project further into passage. It is a freestanding-proportioned shallow wall-fixed shelving cabinet, not an entry door. No open niches and no TV cabinet over screen.
- remaining1650mm of uninterrupted matte sand plaster to RIGHT of tall cabinet before right room corner. Keep this empty.

ENTRANCE on the RIGHT PERPENDICULAR SIDE WALL, after turning the right corner; start of opening200mm from TV wall, opening widthalong side wall915mm and height2150mm. Render it as a neutral open doorway without door leaf, hinge or invented swing, clearly foreshortened into the RIGHT SIDE WALL. Absolutely no opening on front TV wall.
TERRACE on LEFT PERPENDICULAR SIDE WALL:600mm solid side-wall return beside front TV-wall corner, then1600mm wide black-framed glazing, no curtains. Glazing height is illustrative; retain simple existing floor-to-high glazing language. Straight side walls, rectangular room, no niches, pillars or jogs.

Finishes: beautiful restrained contemporary warm residential interior, sand matte plaster front wall, cabinet finish matching beige kitchen, muted medium walnut, brushed not bright yellow brass. Pale matte beige greige floor tile with subtle stone texture, no rugs. Gentle daylight from terrace LEFT plus soft dimmable warm under-console light, discreet ceiling downlights. TV wall calm and uncluttered; one small ceramic bowl on console end at most. No kitchen on TV wall; kitchen/sofa/workdesk behind camera. No extra table in this frontal view, no furniture in the passage, no people, no fireplace, no giant marble slabs, no slat wall. Show the TV FRONT.
Priority is the EXACT diagram silhouette ratios and clear right-angle doorway placement. Do not magnify TV/console: the console must be just over one THIRD of full front wall width, and screen one QUARTER. Leave spacious empty wall areas as drawn. No annotations, labels, dimensions, UI, or watermark. One full-bleed photo-realistic rendering.
