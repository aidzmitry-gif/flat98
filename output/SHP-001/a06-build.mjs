#!/usr/bin/env node
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { inflateRawSync } from "node:zlib";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const dir = path.dirname(fileURLToPath(import.meta.url));
process.chdir(dir);
const readJson = async (name) => JSON.parse(await fs.readFile(name, "utf8"));
const procurement = await readJson("procurement-data.json");
const data = await readJson("workbook-data.json");
const qa = await readJson("qa-result.json");
const file = "SHP-001-procurement.xlsx";
const marker = "C:/Users/aidzm/.codex/plugins/cache/openai-primary-runtime/spreadsheets/26.1017.11052/skills/spreadsheets/container_tools/mark_artifact_operation_started.mjs";
const expectedBaselineSha256 = "710FAB0CDA44094A455BB08C48E2DACEDDCD9B28523CFFFBFBA9A56F35F97C43";
const summaryPolicyNote = "Условия Seeed по экспортному соответствию блокируют поставки в Беларусь и Россию, включая конечное использование и реэкспорт; O04/O05 остаются справочными ценами только по условиям этого поставщика; обход не предлагается. GBP — 4,0131 BYN за единицу по справочному курсу НБРБ на 19.10.2026; это не курс платежа. Доставка и расходы по другим регионам неизвестны.";
const seeedPolicyText = "Квартира и конечная доставка — Беларусь, подтверждено владельцем. Условия Seeed по экспортному соответствию блокируют поставки в Беларусь и Россию, включая конечное использование и реэкспорт; O04/O05 остаются только справочными ценами, доступный маршрут не подтверждён. Для всех поставок из Китая доставка, посредник, таможня и прочие дополнительные расходы исключены из сметы по указанию владельца; это не нулевые расходы. Условия конкретного поставщика, не общее правовое заключение; обход не предлагается. Расходы на доставку по другим регионам неизвестны.";
const originalGapAuditHeaders = ["ID BOM", "Количество", "Исходное обоснование", "Текущий статус", "Учёт цены", "Источник", "Нижняя граница резерва, BYN", "Верхняя граница резерва, BYN"];
const captionTargets = [
  { sheet: "Выбранное оборудование", cell: "C29", before: "Обязательная позиция — цена неизвестна", value: "Основное оборудование" },
  { sheet: "Выбранное оборудование", cell: "C33", before: "Обязательная позиция — цена неизвестна", value: "Основное оборудование" },
  { sheet: "Выбранное оборудование", cell: "C37", before: "Обязательная позиция — цена неизвестна", value: "Основное оборудование" },
  { sheet: "Выбранное оборудование", cell: "C38", before: "Обязательная позиция — цена неизвестна", value: "Основное оборудование" },
  { sheet: "Сводка", cell: "A2", before: "Рабочая справочная оценка в BYN, не заказ. 28 активных ценовых ссылок и 11 строк без цены; Беларусь подтверждена владельцем. Сумма неполная: O27 указана без НДС, дополнительный НДС неизвестен; O28 включает НДС. Неизвестные расходы не равны нулю. Для поставок из Китая доставка, посредник, таможня и прочие расходы исключены владельцем из сметы (не 0).", value: "Рабочая оценка в BYN, не заказ. 28 активных ценовых ссылок и 11 строк без цены; Беларусь подтверждена владельцем. Сумма неполная и смешанная NET/GROSS: O27 указана без НДС, дополнительный НДС неизвестен; O28 включает НДС. По указанию владельца доставка, посредник, таможня и прочие логистические расходы для всех регионов исключены из сметы; это не нулевые расходы." },
  { sheet: "Сводка", cell: "D7", before: "Текущие карточки и официальные справочные цены; без доставки и налогов.", value: "Цены NET/GROSS указаны по источникам; O27 — цена без НДС, дополнительный НДС неизвестен; O28 включает НДС. По указанию владельца доставка, посредник, таможня и прочие логистические расходы по всем регионам исключены из сметы (не 0)." },
  { sheet: "Сводка", cell: "D11", before: "28 ссылок — справочные, не твёрдые заказы; 11 обязательных строк остаются без цены. Сумма частичная и смешанная NET/GROSS: для O27 дополнительный НДС неизвестен; доставка и прочие расходы по другим регионам неизвестны. Китайские дополнительные расходы исключены владельцем (не 0).", value: "28 ссылок — справочные, не твёрдые заказы; 11 обязательных строк остаются без цены. Сумма частичная и смешанная NET/GROSS: O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС. Доставка, посредник, таможня и прочие логистические расходы по всем регионам исключены владельцем из сметы (не 0)." },
  { sheet: "Сводка", cell: "D14", before: "Без проектирования, доставки и налогов.", value: "Без проектирования. По указанию владельца доставка, посредник, таможня и прочие логистические расходы по всем регионам исключены из сметы (не 0). Налоговый режим цен сохранён по источникам: O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС." },
  { sheet: "Сводка", cell: "D16", before: "Квартира и доставка — Беларусь, подтверждено владельцем. Условия Seeed по экспортному соответствию блокируют поставки в Беларусь и Россию, включая конечное использование и реэкспорт; O04/O05 — справочные цены только по условиям этого поставщика, доступный маршрут не подтверждён, обход не предлагается. Для всех поставок из Китая доставка, посредник, таможня и прочие дополнительные расходы исключены из сметы по указанию владельца; это не нулевые расходы. GBP — 4,0131 BYN за единицу по справочному курсу НБРБ на 19.10.2026, не курс платежа. Доставка и прочие расходы по другим регионам неизвестны.", value: "Квартира и конечная доставка — Беларусь, подтверждено владельцем. Условия Seeed по экспортному соответствию блокируют поставки в Беларусь и Россию, включая конечное использование и реэкспорт; O04/O05 — справочные цены только по условиям этого поставщика, доступный маршрут не подтверждён, обход не предлагается. По указанию владельца доставка, посредник, таможня и прочие логистические расходы по всем регионам исключены из сметы (не 0). O27 — цена без НДС, дополнительный НДС неизвестен; O28 включает НДС. GBP — 4,0131 BYN за единицу по справочному курсу НБРБ на 19.10.2026, не курс платежа." },
  { sheet: "Выбранное оборудование", cell: "A2", before: "28 ценовых ориентиров — справочные, не твёрдые заказы. Квартира и доставка — Беларусь, подтверждено владельцем. Итог смешивает NET-цену O27 без НДС и цены с включённым НДС; дополнительный НДС по O27 неизвестен и не равен нулю, поэтому это не полная сумма с налогами и доставкой. По другим регионам расходы неизвестны. Для всех поставок из Китая доставка, посредник, таможня и прочие дополнительные расходы исключены из сметы по указанию владельца; это не нулевые расходы. По 11 обязательным позициям цена не подтверждена. См. Сводку.", value: data.sheet.equipmentCaption },
  { sheet: "Предложения РФ РБ Китай", cell: "A2", before: "28 активных справочных ценовых ссылок; 11 обязательных строк без цены. O25–O28 — справочные, не твёрдые заказы. O27 — цена без НДС, дополнительный НДС неизвестен; O28 — цена с НДС. Беларусь подтверждена владельцем. Для поставок из Китая дополнительные расходы исключены из сметы владельцем (не 0); условия Seeed относятся только к этому поставщику. Остальные неизвестные значения не считаются нулём.", value: "28 активных справочных ценовых ссылок; 11 обязательных строк без цены. O25–O28 — справочные, не твёрдые заказы. O27 — цена без НДС, дополнительный НДС неизвестен; O28 — цена с НДС. Беларусь подтверждена владельцем. Доставка, посредник, таможня и прочие логистические расходы для всех регионов исключены владельцем из сметы (не 0); условия Seeed относятся только к этому поставщику. Остальные неизвестные значения не считаются нулём." },
];
const sourceRows = [
  ["O22", "Наблюдение CUA — справочная цена", "2026-10-19", "РФ — международный справочный ориентир", "Tinko", "TL-POE160S — 2 827,11 RUB/шт., количество 2, под заказ. Ревизия оборудования, региональный комплект, НДС и конечная доставка неизвестны. Только справочная цена, не твёрдый заказ.", "https://www.tinko.ru/catalog/product/298553/"],
  ["O23", "Наблюдение CUA — справочная цена", "2026-10-19", "Германия — международный справочный ориентир", "OBI E-Commerce GmbH", "Ei650 — 19,99 EUR/шт. с НДС Германии 19%; комплект включает батарею, винты и дюбели. Доставка 4,95 EUR только по Германии и не включена; наличие и доставка до Беларуси неизвестны. Проект пожарной безопасности и размещение — СТОП.", "https://www.obi.de/p/5693585/ei-electronics-rauchmelder-ei650-mit-10-jahres-batterie"],
  ["O24", "Наблюдение CUA — справочная цена", "2026-10-19", "Великобритания — международный справочный ориентир", "Westbase Direct UK", "FBT4N — 33,24 GBP с НДС; отправка за 2–3 дня не является конечной доставкой. Не подменять цену без НДС, рекомендованную цену или соседнюю модель TGBT4N. Все условия установки остаются СТОП.", "https://westbasedirect.com/products/fbt4n"],
  ["SRC-SEEED-POLICY", "Метаданные политики поставщика", "2026-10-19", "Беларусь — подтверждённая страна установки и доставки", "Seeed Studio", seeedPolicyText, "https://www.seeedstudio.com/export_compliance"],
];
const sameCell = (left, right) => Object.is(left === "" || left === undefined ? null : left, right === "" || right === undefined ? null : right);
const bomValues = (item) => [
  item.id, item.item, item.class, item.requiredQty, item.firstBenchQty ?? null,
  item.knownFullBYN ?? null, item.knownBenchBYN ?? null, item.allowanceLowBYN ?? null,
  item.allowanceHighBYN ?? null, item.benchAllowanceLowBYN ?? null, item.benchAllowanceHighBYN ?? null,
  item.source ?? null, item.url ?? null, item.gate ?? null,
];

if (process.argv.includes("--audit-source-only")) {
  const root = path.resolve(dir, "../..");
  const candidate = path.join(root, ".harness", "tmp", "SHP-001-audit-source-candidate.xlsx");
  const beforeZip = path.join(root, ".harness", "tmp", "SHP-001-audit-source-before.zip");
  const inspectSidecar = `${candidate}.inspect.ndjson`;
  const expectedBefore = "49A545EB446AD4B0084B2F9F7F90C5F0CA82690DE4CA8994DC73A6F21E4B275B";
  const expectedBeforeZip = "103A3D1EC2CCDC41BEE703D23E4304F98FD2A499C52AD3DA0FFADA7D3E2689DC";
  const fileHash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex").toUpperCase();
  const originalBytes = await fs.readFile(file);
  const originalSha256 = fileHash(originalBytes);
  assert.equal(originalSha256, expectedBefore, "Local XLSX changed since the approved audit-source preimage");
  assert.equal(fileHash(await fs.readFile(beforeZip)), expectedBeforeZip, "Immutable audit-source before ZIP changed");
  assert.equal(await fs.stat(candidate).then(() => true, () => false), false, "Approved audit-source candidate path already exists; refusing overwrite");
  assert.equal(await fs.stat(inspectSidecar).then(() => true, () => false), false, "Candidate inspect sidecar already exists; refusing overwrite");
  assert.equal(procurement.offers.length, 28, "Active offer count changed");
  assert.equal(procurement.unpriced.length, 11, "Unpriced line count changed");
  assert.equal(data.bom.length, 48, "BOM model count changed");
  assert.equal(data.scenarios.length, 42, "Scenario count changed");
  assert.equal(data.acceptance.length, 19, "Acceptance row count changed");
  assert.equal(data.sheet.tabs.length, 8, "Workbook tab count changed");

  const sourceTargets = [
    { id: "B27", evidenceCell: "C59", sourceCell: "F59", beforeEvidence: "Gidrolock-prof art.20110111 с АКБ12V/1,2Ah —10 390 RUB за 1 блок; комплект указан продавцом.", beforeSource: "https://gidrolock-prof.ru/bloki-upravleniya-gidrolock/bu-premium-s-akb.html", evidence: "Старый SanToros URL дал 404; найденный art.20120111 за 6 500 RUB — другой SKU; 7 200 RUB остаются историей.", source: "https://santoros.ru/blok-upravleniya-premium/" },
    { id: "B34", evidenceCell: "C63", sourceCell: "F63", beforeEvidence: "Farnell Belgium: официальный БП Pi4 SC0444/ordercode3106941, цена за штуку 6,90 EUR без НДС, минимум/кратность 1.", beforeSource: "https://be.farnell.com/en-BE/raspberry-pi/sc0213/rpi-power-supply-usb-c-5-1v-3a/dp/3106941", evidence: "Официальный USB-C БП Raspberry Pi EU: белый SC0444 или чёрный SC0217, несъёмный кабель 1,5 м; точный цвет/SKU не выбран.", source: "https://datasheets.raspberrypi.com/power-supply/usb-c-power-supply-product-brief.pdf" },
    { id: "B35", evidenceCell: "C64", sourceCell: "F64", beforeEvidence: "MONRASPBERRY: корпус Flirc FLIRC4 для Pi4 за 22,68 EUR с НДС; в комплекте термопрокладка, винты и ножки; заявленные 2 шт. не резерв.", beforeSource: "https://monraspberry.com/en/product/flirc-box-for-raspberry-pi-4/", evidence: "X-Com карточка 1 458 RUB; дата самовывоза 22.08.2026 прошла.", source: "https://omsk.xcom-shop.ru/flirc_raspberry_pi_4_case_black_edition_1039999.html" },
  ];
  for (const target of sourceTargets) {
    const row = procurement.originalGapAudit.find((item) => item.id === target.id);
    assert(row, `Missing original gap row ${target.id}`);
    assert.equal(row.evidence, target.evidence, `${target.id} evidence must be restored from the immutable preimage`);
    assert.equal(row.source, target.source, `${target.id} source must be restored from the immutable preimage`);
  }

  const sourceFiles = ["procurement-data.json", "workbook-data.json", "qa-result.json"];
  const inputHashes = Object.fromEntries(await Promise.all(sourceFiles.map(async (name) => [name, fileHash(await fs.readFile(name))])));
  assert.equal(inputHashes["workbook-data.json"], "D260B10D854803CB1A31602D65E48D170F7DFCA205579E4FA83C76F2AAD22728", "Workbook JSON must remain frozen");
  assert.equal(inputHashes["qa-result.json"], "F51914EFE6825D5F54F8ABBB686A3EA0C442EC51AAFD5B152947E9619894248F", "QA history must remain frozen until candidate/native checks pass");

  const readZipEntry = async (archivePath, entryName) => {
    const bytes = await fs.readFile(archivePath);
    let eocd = -1;
    for (let offset = bytes.length - 22; offset >= Math.max(0, bytes.length - 65_557); offset--) {
      if (bytes.readUInt32LE(offset) === 0x06054b50) { eocd = offset; break; }
    }
    assert(eocd >= 0, "Before ZIP has no end-of-central-directory record");
    const entries = bytes.readUInt16LE(eocd + 10);
    let cursor = bytes.readUInt32LE(eocd + 16);
    for (let i = 0; i < entries; i++) {
      assert.equal(bytes.readUInt32LE(cursor), 0x02014b50, "Invalid ZIP central-directory entry");
      const method = bytes.readUInt16LE(cursor + 10);
      const compressedSize = bytes.readUInt32LE(cursor + 20);
      const uncompressedSize = bytes.readUInt32LE(cursor + 24);
      const nameLength = bytes.readUInt16LE(cursor + 28);
      const extraLength = bytes.readUInt16LE(cursor + 30);
      const commentLength = bytes.readUInt16LE(cursor + 32);
      const name = bytes.subarray(cursor + 46, cursor + 46 + nameLength).toString("utf8");
      const localOffset = bytes.readUInt32LE(cursor + 42);
      if (name === entryName) {
        assert.equal(bytes.readUInt32LE(localOffset), 0x04034b50, "Invalid ZIP local header");
        const localNameLength = bytes.readUInt16LE(localOffset + 26);
        const localExtraLength = bytes.readUInt16LE(localOffset + 28);
        const dataStart = localOffset + 30 + localNameLength + localExtraLength;
        const compressed = bytes.subarray(dataStart, dataStart + compressedSize);
        const output = method === 0 ? compressed : method === 8 ? inflateRawSync(compressed) : null;
        assert(output, `Unsupported compression method ${method} in ${entryName}`);
        assert.equal(output.length, uncompressedSize, `Unexpected uncompressed size for ${entryName}`);
        return output;
      }
      cursor += 46 + nameLength + extraLength + commentLength;
    }
    assert.fail(`Missing ZIP entry ${entryName}`);
  };
  const archivedProcurement = JSON.parse((await readZipEntry(beforeZip, "current/output/SHP-001/procurement-data.json")).toString("utf8"));
  const normalizeAuditFields = (document) => {
    const copy = JSON.parse(JSON.stringify(document));
    for (const row of copy.originalGapAudit.filter((item) => ["B27", "B34", "B35"].includes(item.id))) {
      row.evidence = "__APPROVED_FIELD__";
      row.source = "__APPROVED_FIELD__";
    }
    return copy;
  };
  assert.deepEqual(normalizeAuditFields(procurement), normalizeAuditFields(archivedProcurement), "Procurement JSON has changes outside the six approved source/evidence fields");

  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  const sheetNames = [];
  for (let i = 0; i < 8; i++) sheetNames.push(workbook.worksheets.getItemAt(i).name);
  assert.deepEqual(sheetNames, data.sheet.tabs, "Existing workbook tabs/order changed");
  const tableMetadata = (book) => sheetNames.flatMap((sheetName) => book.worksheets.getItem(sheetName).tables.items.map((table) => ({
    sheetName, name: table.name, address: table.address, style: table.style, columns: table.columnNames,
    showHeaders: table.showHeaders, showTotals: table.showTotals, showBandedRows: table.showBandedRows,
    showBandedColumns: table.showBandedColumns, highlightFirstColumn: table.highlightFirstColumn,
    highlightLastColumn: table.highlightLastColumn, showFilterButton: table.showFilterButton,
  })));
  const beforeTables = tableMetadata(workbook);
  assert.equal(beforeTables.length, 13, "Local XLSX must retain all 13 existing native table objects");
  const snapshot = (book) => Object.fromEntries(sheetNames.map((sheetName) => {
    const used = book.worksheets.getItem(sheetName).getUsedRange();
    return [sheetName, used ? {
      address: used.address, rowIndex: used.rowIndex, columnIndex: used.columnIndex,
      values: used.values.map((row) => row.slice()), formulas: used.formulas.map((row) => row.slice()),
    } : null];
  }));
  const beforeCells = snapshot(workbook);
  const formulaCount = sheetNames.reduce((sum, name) => {
    const used = workbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(formulaCount, 218, "The frozen local workbook must retain all 218 formulas");
  const changes = [];
  for (const target of sourceTargets) {
    const sheet = workbook.worksheets.getItem("Предложения РФ РБ Китай");
    for (const [cell, beforeValue, nextValue, field] of [
      [target.evidenceCell, target.beforeEvidence, target.evidence, "evidence"],
      [target.sourceCell, target.beforeSource, target.source, "source"],
    ]) {
      const range = sheet.getRange(cell);
      assert.equal(range.values[0][0], beforeValue, `Unexpected local preimage at ${target.id}/${field}`);
      assert(!range.formulas[0][0], `Target must be a literal text cell at ${target.id}/${field}`);
      assert.equal(nextValue, procurement.originalGapAudit.find((item) => item.id === target.id)[field]);
      range.values = [[nextValue]];
      changes.push({ sheet: "Предложения РФ РБ Китай", cell, value: nextValue });
    }
  }

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(candidate);
  for (const [name, beforeHash] of Object.entries(inputHashes)) assert.equal(fileHash(await fs.readFile(name)), beforeHash, `${name} changed while exporting the audit-source candidate`);
  assert.equal(fileHash(await fs.readFile(file)), expectedBefore, "The final XLSX must not change before candidate acceptance");
  assert.equal(await fs.stat(inspectSidecar).then(() => true, () => false), false, "Exporter created an inspect sidecar; stop before final replacement/native write");

  const candidateWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(candidate));
  const candidateNames = [];
  for (let i = 0; i < 8; i++) candidateNames.push(candidateWorkbook.worksheets.getItemAt(i).name);
  assert.deepEqual(candidateNames, sheetNames, "Candidate export changed the existing 8 tabs");
  assert.deepEqual(tableMetadata(candidateWorkbook), beforeTables, "Candidate export changed local table names/ranges/styles/flags/columns");
  const afterCells = snapshot(candidateWorkbook);
  const targetMap = new Map(changes.map((item) => [`${item.sheet}!${item.cell}`, item.value]));
  const colName = (index) => {
    let value = index + 1, result = "";
    while (value > 0) { const rem = (value - 1) % 26; result = String.fromCharCode(65 + rem) + result; value = Math.floor((value - 1) / 26); }
    return result;
  };
  let valueChanges = 0;
  for (const name of sheetNames) {
    const before = beforeCells[name], after = afterCells[name];
    assert.equal(after?.address ?? null, before?.address ?? null, `Used-range layout changed on ${name}`);
    if (!before) continue;
    assert.equal(after.values.length, before.values.length, `Used-range row count changed on ${name}`);
    for (let r = 0; r < before.values.length; r++) {
      assert.equal(after.values[r].length, before.values[r].length, `Used-range column count changed on ${name}, row ${r + 1}`);
      assert.deepEqual(after.formulas[r], before.formulas[r], `Formula row changed on ${name}, row ${r + 1}`);
      for (let c = 0; c < before.values[r].length; c++) {
        const cell = `${colName((before.columnIndex ?? 0) + c)}${(before.rowIndex ?? 0) + r + 1}`;
        const key = `${name}!${cell}`;
        const expectedValue = targetMap.has(key) ? targetMap.get(key) : before.values[r][c];
        if (targetMap.has(key)) valueChanges++;
        assert.deepEqual(after.values[r][c], expectedValue, `Unexpected value change at ${key}`);
      }
    }
  }
  assert.equal(valueChanges, 6, "Exactly the approved six text cells must change");
  const candidateFormulaCount = candidateNames.reduce((sum, name) => {
    const used = candidateWorkbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(candidateFormulaCount, 218, "Candidate export must preserve all 218 formulas");
  const equipment = candidateWorkbook.worksheets.getItem("Выбранное оборудование");
  assert(!equipment.getRange("G25").formulas[0][0], "G25 must remain a true blank, not a formula");
  assert(equipment.getRange("G25").values[0][0] == null || equipment.getRange("G25").values[0][0] === "", "G25 must remain blank, not zero");

  const candidateFormulaErrors = candidateNames.reduce((sum, name) => {
    const used = candidateWorkbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.values.flat().filter((value) => typeof value === "string" && /^#(REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!)/.test(value)).length ?? 0);
  }, 0);
  assert.equal(candidateFormulaErrors, 0, "Candidate must have no formula error values");
  console.log(JSON.stringify({
    result: "AUDIT_SOURCE_CANDIDATE_READY_FOR_NATIVE_PREIMAGE_CHECK",
    beforeSha256: originalSha256, candidateSha256: fileHash(await fs.readFile(candidate)),
    candidateBytes: (await fs.stat(candidate)).size, changedCells: valueChanges,
    formulasBefore: formulaCount, formulasAfter: candidateFormulaCount,
    localTablesBefore: beforeTables.length, localTablesAfter: tableMetadata(candidateWorkbook).length,
    tabNames: candidateNames, fullReadOnlyStyleAndCacheGuard: "pending external check", noInspectSidecar: true,
  }, null, 2));
  process.exit(0);
}

if (process.argv.includes("--caption-only")) {
  const root = path.resolve(dir, "../..");
  const candidate = path.join(root, ".harness", "tmp", "SHP-001-admission28-labels-candidate.xlsx");
  const beforeZip = path.join(root, ".harness", "tmp", "SHP-001-admission28-labels-before.zip");
  const expectedBefore = "9C162209EDE81F5F29D214BCBE598922BA2020AE0B448F2B12E610224F117B1F";
  const fileHash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex").toUpperCase();
  const originalBytes = await fs.readFile(file);
  const originalSha256 = fileHash(originalBytes);
  assert.equal(originalSha256, expectedBefore, "Local XLSX changed since the accepted 11-cell prewrite baseline");
  assert.equal(await fs.stat(beforeZip).then(() => true, () => false), true, "Approved immutable prewrite ZIP is required");
  assert.equal(await fs.stat(candidate).then(() => true, () => false), false, "Approved caption candidate path already exists; refusing overwrite");
  assert.equal(data.sheet.equipmentCaption, "28 ценовых ориентиров — справочные, не твёрдые заказы. Квартира и конечное использование — Беларусь. Сумма смешанная NET/GROSS: O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС. Доставка, посредник, таможня и прочие логистические расходы для всех регионов исключены владельцем из сметы (не 0). По 11 обязательным позициям цена не подтверждена. См. Сводку.", "Equipment caption JSON must contain the exact accepted target");
  assert.equal(captionTargets.length, 11, "The caption-only path must remain bounded to exactly 11 text cells");
  assert.equal(procurement.offers.length, 28);
  assert.equal(procurement.unpriced.length, 11);
  assert.equal(data.bom.length, 48);
  assert.equal(data.scenarios.length, 42);
  assert.equal(data.acceptance.length, 19);
  assert.equal(data.sheet.tabs.length, 8);

  const inputHashes = {};
  for (const name of ["procurement-data.json", "workbook-data.json", "qa-result.json"]) inputHashes[name] = fileHash(await fs.readFile(name));
  assert.equal(inputHashes["procurement-data.json"], "36D57E255A4DB1E171C297A9759C4C37521C326216880012628D98862E72B20D", "Procurement JSON must remain frozen");
  assert.equal(inputHashes["qa-result.json"], "D070EAF7BA1C4A130FF656FA98B1D03BEA67C91865AAB47799BE688EC136CD4E", "QA history must remain unchanged until candidate and native checks pass");

  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  const sheetNames = [];
  for (let i = 0; i < 8; i++) sheetNames.push(workbook.worksheets.getItemAt(i).name);
  assert.deepEqual(sheetNames, data.sheet.tabs, "Existing workbook tabs/order changed");
  const tableMetadata = (book) => sheetNames.flatMap((sheetName) => book.worksheets.getItem(sheetName).tables.items.map((table) => ({
    sheetName, name: table.name, address: table.address, style: table.style, columns: table.columnNames,
    showHeaders: table.showHeaders, showTotals: table.showTotals, showBandedRows: table.showBandedRows,
    showBandedColumns: table.showBandedColumns, highlightFirstColumn: table.highlightFirstColumn,
    highlightLastColumn: table.highlightLastColumn, showFilterButton: table.showFilterButton,
  })));
  const beforeTables = tableMetadata(workbook);
  assert.equal(beforeTables.length, 13, "Local XLSX must retain all 13 existing native table objects");
  const snapshot = (book) => Object.fromEntries(sheetNames.map((sheetName) => {
    const used = book.worksheets.getItem(sheetName).getUsedRange();
    return [sheetName, used ? {
      address: used.address, rowIndex: used.rowIndex, columnIndex: used.columnIndex,
      values: used.values.map((row) => row.slice()), formulas: used.formulas.map((row) => row.slice()),
    } : null];
  }));
  const beforeCells = snapshot(workbook);
  const formulaCount = sheetNames.reduce((sum, name) => {
    const used = workbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(formulaCount, 218, "The frozen local workbook must retain all 218 formulas");
  for (const target of captionTargets) {
    const sheet = workbook.worksheets.getItem(target.sheet);
    assert.equal(sheet.getRange(target.cell).values[0][0], target.before, `Unexpected preimage at ${target.sheet}!${target.cell}`);
    assert(!sheet.getRange(target.cell).formulas[0][0], `Target must be a literal text cell: ${target.sheet}!${target.cell}`);
    sheet.getRange(target.cell).values = [[target.value]];
  }

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(candidate);
  for (const [name, beforeHash] of Object.entries(inputHashes)) assert.equal(fileHash(await fs.readFile(name)), beforeHash, `${name} changed while exporting the caption-only candidate`);
  assert.equal(fileHash(await fs.readFile(file)), expectedBefore, "The final XLSX must not change before candidate acceptance");

  const candidateWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(candidate));
  const candidateNames = [];
  for (let i = 0; i < 8; i++) candidateNames.push(candidateWorkbook.worksheets.getItemAt(i).name);
  assert.deepEqual(candidateNames, sheetNames, "Candidate export changed the existing 8 tabs");
  assert.deepEqual(tableMetadata(candidateWorkbook), beforeTables, "Candidate export changed local table names/ranges/styles/flags/columns");
  const afterCells = snapshot(candidateWorkbook);
  const targetMap = new Map(captionTargets.map((target) => [`${target.sheet}!${target.cell}`, target.value]));
  const colName = (index) => {
    let value = index + 1, result = "";
    while (value > 0) { const rem = (value - 1) % 26; result = String.fromCharCode(65 + rem) + result; value = Math.floor((value - 1) / 26); }
    return result;
  };
  let valueChanges = 0;
  for (const name of sheetNames) {
    const before = beforeCells[name], after = afterCells[name];
    assert.equal(after?.address ?? null, before?.address ?? null, `Used-range layout changed on ${name}`);
    if (!before) continue;
    assert.equal(after.values.length, before.values.length, `Used-range row count changed on ${name}`);
    for (let r = 0; r < before.values.length; r++) {
      assert.equal(after.values[r].length, before.values[r].length, `Used-range column count changed on ${name}, row ${r + 1}`);
      assert.deepEqual(after.formulas[r], before.formulas[r], `Formula row changed on ${name}, row ${r + 1}`);
      for (let c = 0; c < before.values[r].length; c++) {
        const cell = `${colName((before.columnIndex ?? 0) + c)}${(before.rowIndex ?? 0) + r + 1}`;
        const key = `${name}!${cell}`;
        const expectedValue = targetMap.has(key) ? targetMap.get(key) : before.values[r][c];
        if (targetMap.has(key)) {
          const mapped = captionTargets.find((item) => `${item.sheet}!${item.cell}` === key);
          assert.equal(before.values[r][c], mapped.before, `Unexpected mapped preimage at ${key}`);
          valueChanges++;
        }
        assert.deepEqual(after.values[r][c], expectedValue, `Unexpected value change at ${key}`);
      }
    }
  }
  assert.equal(valueChanges, 11, "Exactly the approved 11 text cells must change");
  const candidateFormulaCount = candidateNames.reduce((sum, name) => {
    const used = candidateWorkbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(candidateFormulaCount, 218, "Candidate export must preserve all 218 formulas");
  const equipmentCandidate = candidateWorkbook.worksheets.getItem("Выбранное оборудование");
  assert(!equipmentCandidate.getRange("G25").formulas[0][0], "G25 must remain a true blank, not a formula");
  assert(equipmentCandidate.getRange("G25").values[0][0] == null || equipmentCandidate.getRange("G25").values[0][0] === "", "G25 must remain blank, not zero");
  const candidateSummary = candidateWorkbook.worksheets.getItem("Сводка");
  const originalSummary = workbook.worksheets.getItem("Сводка");
  for (const cell of ["B7","B8","B9","B10","C10","B11","C11","B12","B13","C13","B14","C14","B15"]) {
    assert.deepEqual(candidateSummary.getRange(cell).values, originalSummary.getRange(cell).values, `Financial control changed at Summary!${cell}`);
  }
  console.log(JSON.stringify({
    result: "CAPTION_ONLY_CANDIDATE_READY_FOR_INDEPENDENT_FULL_GUARD",
    baselineSha256: originalSha256, candidateSha256: fileHash(await fs.readFile(candidate)),
    candidateBytes: (await fs.stat(candidate)).size, changedTextCells: valueChanges,
    formulasBefore: formulaCount, formulasAfter: candidateFormulaCount,
    localTablesBefore: beforeTables.length, localTablesAfter: tableMetadata(candidateWorkbook).length,
    tabNames: candidateNames, inputsUnchanged: inputHashes,
  }, null, 2));
  process.exit(0);
}

if (process.argv.includes("--b36-o30")) {
  const root = path.resolve(dir, "../..");
  const candidate = path.join(root, ".harness", "tmp", "SHP-001-B36-O30-candidate.xlsx");
  const inspectSidecar = candidate + ".inspect.ndjson";
  const beforeZip = path.join(root, ".harness", "tmp", "SHP-001-B36-O30-before.zip");
  const expectedBefore = "05D0DB3ACF421C37C66A16CF769A1F83073B045E3BB41A9580FFA08A0441E891";
  const expectedBeforeZip = "854B2E3EA85756C971E6A375F20E8DBABFE0702A230ACF5F8FC7433415F1695A";
  const fileHash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex").toUpperCase();
  const close = (actual, expected, label) => assert(Number.isFinite(actual) && Math.abs(actual - expected) < 1e-8, `${label}: ${actual} != ${expected}`);
  const inputNames = ["procurement-data.json", "workbook-data.json", "qa-result.json"];
  const inputHashes = Object.fromEntries(await Promise.all(inputNames.map(async (name) => [name, fileHash(await fs.readFile(name))])));
  const offer = procurement.offers.find((item) => item.id === "O30");
  assert(offer, "The approved O30 record is required");
  assert.deepEqual([offer.bom, offer.qty, offer.packQty, offer.currency, offer.unit], ["B36", 1, 1, "RUB", 1479.56]);
  assert.equal(offer.date, "2026-10-20");
  assert(offer.url.endsWith("ELEMENT_ID=351419&SECTION_ID=64639"));
  assert(offer.notes.includes("1 546,13 RUB") && offer.notes.includes("не зарезервирован"));
  assert(offer.notes.includes("12 месяцев — заявление продавца") && offer.notes.includes("НДС"));
  assert.equal(offer.taxBasis, "UNKNOWN");
  assert.equal(offer.additionalVAT, null);
  assert.equal(procurement.offers.length, 30);
  assert.equal(new Set(procurement.offers.map((item) => item.bom)).size, 30);
  assert.equal(procurement.unpriced.length, 9);
  assert.equal(procurement.unpriced.some((item) => item.id === "B36"), false);
  assert.equal(procurement.originalGapAudit.length, 18);
  assert.equal(procurement.sources.length, 38);
  assert.equal(procurement.sources.at(-1), offer.url);
  assert.equal(procurement.historical.length, 9);
  assert.equal(procurement.fx.RUB, 0.03604);
  const gapB36 = procurement.originalGapAudit.find((row) => row.id === "B36");
  assert(gapB36 && gapB36.evidence.startsWith("AudioHead:"));
  assert.equal(gapB36.source, "https://audiohead.ru/catalog/karty_pamyati/samsung_pro_endurance_64gb_microsd_sd_adapter_mb_mj64ka/");
  assert.equal(gapB36.allowanceLowBYN, null);
  assert.equal(gapB36.allowanceHighBYN, null);
  const h09 = procurement.historical.find((row) => row.id === "H09");
  assert(h09?.originalOfferSnapshot && Object.keys(h09.originalOfferSnapshot).length === 16, "Full H09 history must remain unchanged");
  assert.equal(data.bom.length, 48);
  assert.equal(data.scenarios.length, 42);
  assert.equal(data.acceptance.length, 19);
  assert.equal(data.rooms.length, 9);
  assert.equal(data.sheet.tabs.length, 8);
  const bomB36 = data.bom.find((item) => item.id === "B36");
  assert(bomB36 && bomB36.class === "Основное оборудование");
  assert.deepEqual([bomB36.requiredQty, bomB36.firstBenchQty, bomB36.knownFullBYN, bomB36.knownBenchBYN], [1, 1, 53.3233424, 53.3233424]);
  for (const key of ["allowanceLowBYN", "allowanceHighBYN", "benchAllowanceLowBYN", "benchAllowanceHighBYN"]) assert.equal(bomB36[key], null);

  const expectedTotals = {
    pricedNoSparesBYN: 17331.9009872, sparesBYN: 450.25187, pricedWithSparesBYN: 17782.1528572,
    allowancesLowBYN: 18475, allowancesHighBYN: 45125,
    planningLowBYN: 36257.1528572, planningHighBYN: 62907.1528572,
    pilotKnownBYN: 5077.1999244, pilotAllowLowBYN: 65, pilotAllowHighBYN: 155,
    pilotPlanLowBYN: 5142.1999244, pilotPlanHighBYN: 5232.1999244, mandatoryUnpricedLines: 9,
  };
  const procurementTotalKeys = ["pricedNoSparesBYN", "pricedWithSparesBYN", "allowancesLowBYN", "allowancesHighBYN", "planningLowBYN", "planningHighBYN", "pilotKnownBYN", "pilotAllowLowBYN", "pilotAllowHighBYN", "mandatoryUnpricedLines"];
  for (const key of procurementTotalKeys) close(procurement.totalsControl[key], expectedTotals[key], "procurement.totalsControl." + key);
  for (const key of Object.keys(data.controls)) close(data.controls[key], expectedTotals[key], "workbook-data.controls." + key);
  close(expectedTotals.pilotPlanLowBYN, expectedTotals.pilotKnownBYN + expectedTotals.pilotAllowLowBYN, "pilot plan low control");
  close(expectedTotals.pilotPlanHighBYN, expectedTotals.pilotKnownBYN + expectedTotals.pilotAllowHighBYN, "pilot plan high control");

  const originalBytes = await fs.readFile(file);
  const originalSha256 = fileHash(originalBytes);
  assert.equal(originalSha256, expectedBefore, "The accepted main workbook changed before the candidate-only stage");
  assert.equal(fileHash(await fs.readFile(beforeZip)), expectedBeforeZip, "The immutable 19-member prewrite ZIP changed");
  assert.equal(await fs.stat(candidate).then(() => true, () => false), false, "The sole approved candidate path already exists");
  assert.equal(await fs.stat(inspectSidecar).then(() => true, () => false), false, "The candidate inspect sidecar existed before the sole export");

  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  const sheetNames = [];
  for (let index = 0; index < 8; index++) sheetNames.push(workbook.worksheets.getItemAt(index).name);
  assert.deepEqual(sheetNames, data.sheet.tabs, "The existing eight tabs/order changed");
  const summary = workbook.worksheets.getItem("Сводка");
  const equipment = workbook.worksheets.getItem("Выбранное оборудование");
  const offersSheet = workbook.worksheets.getItem("Предложения РФ РБ Китай");
  const sources = workbook.worksheets.getItem("Источники и курсы");
  const affectedNames = ["CurrentOffers", "HistoricalOnly", "PlatformAudit", "OriginalGapAudit"];
  const tableMetadata = (book) => sheetNames.flatMap((sheetName) => book.worksheets.getItem(sheetName).tables.items.map((table) => ({
    sheetName, name: table.name, address: table.address, style: table.style, columns: table.columnNames,
    showHeaders: table.showHeaders, showTotals: table.showTotals, showBandedRows: table.showBandedRows,
    showBandedColumns: table.showBandedColumns, highlightFirstColumn: table.highlightFirstColumn,
    highlightLastColumn: table.highlightLastColumn, showFilterButton: table.showFilterButton,
  })));
  const beforeTables = tableMetadata(workbook);
  assert.equal(beforeTables.length, 13, "All 13 existing local Excel tables must be present");
  const offersTableMap = new Map(offersSheet.tables.items.map((table) => [table.name, table]));
  assert.equal(offersTableMap.get("CurrentOffers")?.address, "A4:W33");
  assert.equal(offersTableMap.get("HistoricalOnly")?.address, "A34:I43");
  assert.equal(offersTableMap.get("PlatformAudit")?.address, "A45:E49");
  assert.equal(offersTableMap.get("OriginalGapAudit")?.address, "A52:H70");
  const sourceTable = sources.tables.items.find((table) => table.name === "SourceRegister");
  assert(sourceTable && sourceTable.address === "A12:G81");
  assert.equal(sources.getRange("A82:G82").values.flat().filter((value) => value !== null && value !== "").length, 0, "SourceRegister append row 82 must be blank");
  assert(offersSheet.getRange("A51").values[0][0].includes("29 активных ценовых ссылок") && offersSheet.getRange("A51").values[0][0].includes("10 текущих строк без цены"));
  assert.deepEqual(offersSheet.getRange("A52:H52").values[0], originalGapAuditHeaders, "Visible Russian original-gap headers changed");
  const beforeFormulaCount = sheetNames.reduce((sum, name) => {
    const used = workbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(beforeFormulaCount, 224, "Current candidate baseline must contain 224 formulas");

  const oldEffectiveHeights = new Map();
  for (let row = 33; row <= 70; row++) {
    const height = offersSheet.getRange("A" + row).format.rowHeight;
    oldEffectiveHeights.set(row, Number.isFinite(height) ? height : 15);
  }
  const originalAuditTitle = offersSheet.getRange("A51").values[0][0];
  const copyRow = (sourceRow, targetRow) => {
    offersSheet.getRange("A" + sourceRow + ":W" + sourceRow).copyTo(offersSheet.getRange("A" + targetRow + ":W" + targetRow), "all");
    offersSheet.getRange("A" + targetRow).format.rowHeight = oldEffectiveHeights.get(sourceRow);
  };
  for (const name of affectedNames) offersTableMap.get(name).delete();
  offersSheet.getRange("A51:H51").unmerge();
  for (let sourceRow = 70; sourceRow >= 34; sourceRow--) copyRow(sourceRow, sourceRow + 1);
  offersSheet.getRange("A34:W34").clear({ applyTo: "contents" });
  copyRow(33, 34);
  const buildOfferRow = (item) => [
    item.id, item.bom, item.sku, item.qty, item.packQty, null, item.unit, item.currency, procurement.fx[item.currency], null, null,
    procurement.pilotQty[item.bom] ?? null, null, null, item.evidence, item.date, item.region, item.seller,
    item.shipping ?? "unknown", item.duty ?? "unknown", item.warranty ?? "unknown", item.notes, item.url,
  ];
  offersSheet.getRange("A34:W34").values = [buildOfferRow(offer)];
  offersSheet.getRange("F34").formulas = [["=IF(OR(D34=\"\",E34=\"\"),\"\",ROUNDUP(D34/E34,0))"]];
  offersSheet.getRange("J34").formulas = [["=IF(OR(G34=\"\",I34=\"\"),\"\",G34*I34)"]];
  offersSheet.getRange("K34").formulas = [["=IF(OR(D34=\"\",E34=\"\",G34=\"\",I34=\"\"),\"\",F34*G34*I34)"]];
  offersSheet.getRange("M34").formulas = [["=IF(OR(L34=\"\",E34=\"\"),\"\",ROUNDUP(L34/E34,0))"]];
  offersSheet.getRange("N34").formulas = [["=IF(OR(L34=\"\",G34=\"\",I34=\"\"),\"\",M34*G34*I34)"]];
  offersSheet.mergeCells("A52:H52");
  const newAuditTitle = originalAuditTitle
    .replace("29 активных ценовых ссылок", "30 активных ценовых ссылок")
    .replace("10 текущих строк без цены", "9 текущих строк без цены")
    + " O30 — наличная цена продавца за точный артикул; налоговый режим неизвестен, это справочный ориентир, не заказ.";
  offersSheet.getRange("A52").values = [[newAuditTitle]];
  offersSheet.getRange("A53:H53").values = [["BOM ID", "Qty", "Original evidence", "Current status", "Price treatment", "Source", "Allowance low BYN", "Allowance high BYN"]];
  const auditB36Row = 54 + procurement.originalGapAudit.findIndex((row) => row.id === "B36");
  assert(auditB36Row >= 54 && auditB36Row <= 71);
  offersSheet.getRange("D" + auditB36Row + ":E" + auditB36Row).values = [[gapB36.currentStatus, gapB36.priceTreatment]];
  offersSheet.getRange("G" + auditB36Row + ":H" + auditB36Row).values = [[null, null]];
  offersSheet.getRange("A53:H53").values = [originalGapAuditHeaders];

  const equipmentRows = equipment.getRange("A5:N52").values;
  assert.equal(equipmentRows.length, 48);
  const equipmentRowById = new Map(equipmentRows.map((row, index) => [row[0], index + 5]));
  assert.equal(equipmentRowById.size, 48);
  const b36Row = equipmentRowById.get("B36");
  assert.equal(b36Row, 39, "B36 coordinate must resolve by BOM ID");
  assert.equal(equipment.getRange("C39").values[0][0], "Обязательная позиция — цена неизвестна", "B36 class preimage changed unexpectedly");
  equipment.getRange("C39").values = [[bomB36.class]];
  const lookupF = "=IFERROR(IF(INDEX('Предложения РФ РБ Китай'!$K$5:$K$34,MATCH($A39,'Предложения РФ РБ Китай'!$B$5:$B$34,0))=\"\",\"\",INDEX('Предложения РФ РБ Китай'!$K$5:$K$34,MATCH($A39,'Предложения РФ РБ Китай'!$B$5:$B$34,0))),\"\")";
  const lookupG = "=IFERROR(IF(INDEX('Предложения РФ РБ Китай'!$N$5:$N$34,MATCH($A39,'Предложения РФ РБ Китай'!$B$5:$B$34,0))=\"\",\"\",INDEX('Предложения РФ РБ Китай'!$N$5:$N$34,MATCH($A39,'Предложения РФ РБ Китай'!$B$5:$B$34,0))),\"\")";
  equipment.getRange("F39").formulas = [[lookupF]];
  equipment.getRange("G39").formulas = [[lookupG]];
  equipment.getRange("H39:I39").clear({ applyTo: "contents" });
  equipment.getRange("L39:N39").values = [[bomB36.source ?? null, bomB36.url ?? null, bomB36.gate ?? null]];
  equipment.getRange("A2").values = [[data.sheet.equipmentCaption]];

  const summaryCaption = "Рабочая оценка в BYN, не заказ. 30 активных ценовых ссылок и 9 строк без цены; Беларусь подтверждена владельцем. Сумма частичная и смешанная NET/GROSS: O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС; налоговый режим O29 и O30 неизвестен. По указанию владельца доставка, посредник, таможня и прочие логистические расходы для всех регионов исключены из сметы; это не нулевые расходы.";
  const moneyCaption = "Цены NET/GROSS отражены по источникам: O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС; налоговый режим O29 и O30 неизвестен. По указанию владельца доставка, посредник, таможня и прочие логистические расходы для всех регионов исключены из сметы (не 0).";
  const countCaption = "30 ссылок — справочные, не твёрдые заказы; 9 обязательных строк остаются без цены. Сумма частичная и смешанная NET/GROSS: O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС; налоговый режим O29/O30 неизвестен. Доставка, посредник, таможня и прочие логистические расходы по всем регионам исключены владельцем из сметы (не 0).";
  const pilotCaption = "Без проектирования. O29 не включён в первый стенд; O30 включён по выбранной наличной цене. Безналичная альтернатива O30 не учитывается. НДС O30 неизвестен. По указанию владельца доставка, посредник, таможня и прочие логистические расходы по всем регионам исключены из сметы (не 0). Налоговый режим O27/O28 сохранён по источникам: O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС.";
  const policyCaption = "Квартира и конечная доставка — Беларусь, подтверждено владельцем. Условия Seeed по экспортному соответствию блокируют поставки в Беларусь и Россию, включая конечное использование и реэкспорт; O04/O05 остаются справочными ценами только по условиям этого поставщика, доступный маршрут не подтверждён; обход не предлагается. Для всех регионов доставка, посредник, таможня и прочие логистические расходы исключены из сметы по указанию владельца; это не нулевые расходы. GBP — 4,0131 BYN за единицу по справочному курсу НБРБ на 19.10.2026, не курс платежа. O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС; налоги O29/O30 неизвестны.";
  summary.getRange("A2").values = [[summaryCaption]];
  summary.getRange("D7").values = [[moneyCaption]];
  summary.getRange("D11").values = [[countCaption]];
  summary.getRange("D14").values = [[pilotCaption]];
  summary.getRange("D16").values = [[policyCaption]];
  summary.getRange("B15").values = [[9]];
  const offersCaption = "30 текущих ценовых ссылок — справочные, не твёрдые заказы; 9 обязательных строк остаются без цены. O25–O30 — справочные ориентиры. O30: 1 479,56 RUB наличными учтены; безналичная альтернатива 1 546,13 RUB исключена; наличие — заявление продавца, требуется подтверждение менеджера, резерва нет; гарантия 12 месяцев — заявление продавца; НДС и подлинность неизвестны. Доставка, посредник, таможня и прочие логистические расходы для всех регионов исключены владельцем из сметы (не 0). Условия Seeed относятся только к этому поставщику.";
  offersSheet.getRange("A2").values = [[offersCaption]];

  const sourceRow = [offer.id, offer.evidence, offer.date, offer.region, offer.seller, offer.notes, offer.url];
  sourceTable.rows.add(null, [sourceRow]);
  assert.deepEqual(sources.getRange("A82:G82").values[0], sourceRow, "SourceRegister O30 append must match source evidence and notes");

  const tableFlags = { showHeaders: true, showTotals: false, showBandedRows: true, showBandedColumns: false, highlightFirstColumn: false, highlightLastColumn: false, showFilterButton: false };
  const setTableFlags = (table) => { for (const [key, value] of Object.entries(tableFlags)) table[key] = value; };
  const expectedTableRanges = [
    ["CurrentOffers", "A4:W34"], ["HistoricalOnly", "A35:I44"],
    ["PlatformAudit", "A46:E50"], ["OriginalGapAudit", "A53:H71"],
  ];
  for (const [name, address] of expectedTableRanges) {
    if (name === "OriginalGapAudit") offersSheet.getRange("A53:H53").values = [["BOM ID", "Qty", "Original evidence", "Current status", "Price treatment", "Source", "Allowance low BYN", "Allowance high BYN"]];
    const table = offersSheet.tables.add(address, true, name);
    table.style = "TableStyleLight1";
    setTableFlags(table);
    if (name === "OriginalGapAudit") offersSheet.getRange("A53:H53").values = [originalGapAuditHeaders];
  }

  await workbook.recalculate();
  const totals = {
    pricedNoSparesBYN: summary.getRange("B7").values[0][0], sparesBYN: summary.getRange("B8").values[0][0],
    pricedWithSparesBYN: summary.getRange("B9").values[0][0], allowancesLowBYN: summary.getRange("B10").values[0][0],
    allowancesHighBYN: summary.getRange("C10").values[0][0], planningLowBYN: summary.getRange("B11").values[0][0],
    planningHighBYN: summary.getRange("C11").values[0][0], pilotKnownBYN: summary.getRange("B12").values[0][0],
    pilotAllowLowBYN: summary.getRange("B13").values[0][0], pilotAllowHighBYN: summary.getRange("C13").values[0][0],
    pilotPlanLowBYN: summary.getRange("B14").values[0][0], pilotPlanHighBYN: summary.getRange("C14").values[0][0],
    mandatoryUnpricedLines: summary.getRange("B15").values[0][0],
  };
  for (const [key, value] of Object.entries(expectedTotals)) close(totals[key], value, "Summary control " + key);
  close(equipment.getRange("F39").values[0][0], 53.3233424, "B36 full cost from O30 lookup");
  close(equipment.getRange("G39").values[0][0], 53.3233424, "B36 pilot cost from O30 lookup");
  assert.deepEqual(equipment.getRange("H39:I39").values[0], [null, null]);
  assert.equal(offersSheet.getRange("A33").values[0][0], "O29");
  assert.equal(offersSheet.getRange("A34").values[0][0], "O30");
  close(offersSheet.getRange("K34").values[0][0], 53.3233424, "O30 BYN line total");
  close(offersSheet.getRange("N34").values[0][0], 53.3233424, "O30 pilot line total");
  assert.equal(offersSheet.getRange("A44").values[0][0], "H09");
  assert.equal(offersSheet.getRange("A52").values[0][0], newAuditTitle);
  assert.deepEqual(offersSheet.getRange("A53:H53").values[0], originalGapAuditHeaders);
  assert.equal(offersSheet.getRange("A" + auditB36Row).values[0][0], "B36");
  assert.deepEqual(offersSheet.getRange("G" + auditB36Row + ":H" + auditB36Row).values[0], [null, null]);
  const afterTables = tableMetadata(workbook);
  assert.equal(afterTables.length, 13, "All 13 local tables must remain");
  const rangeUpdates = new Map([...expectedTableRanges, ["SourceRegister", "A12:G82"]]);
  const expectedTableMetadata = beforeTables.map((table) => ({ ...table, address: rangeUpdates.get(table.name) ?? table.address }));
  assert.deepEqual(afterTables, expectedTableMetadata, "Local table names, columns, style and flags must be preserved except approved ranges");
  assert.deepEqual(offersSheet.tables.items.filter((table) => affectedNames.includes(table.name)).map((table) => [table.name, table.address]).sort(), expectedTableRanges.map((item) => item.slice()).sort());
  const afterFormulaCount = sheetNames.reduce((sum, name) => {
    const used = workbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(afterFormulaCount, 231, "Expected 224 preserved formulas plus five O30 and two BOM-ID lookup formulas");
  const formulaErrors = [];
  for (const sheetName of sheetNames) {
    const sheet = workbook.worksheets.getItem(sheetName);
    const used = sheet.getUsedRange();
    if (!used) continue;
    for (const [rowIndex, row] of used.values.entries()) for (const [columnIndex, value] of row.entries()) {
      if (typeof value === "string" && /^#(REF!|VALUE!|DIV\/0!|NAME\?|N\/A|NUM!|NULL!)/.test(value)) formulaErrors.push(sheetName + "!r" + (rowIndex + 1) + "c" + (columnIndex + 1) + "=" + value);
    }
  }
  assert.deepEqual(formulaErrors, [], "Candidate has formula error values");
  assert.deepEqual(offersSheet.getRange("A5:A34").values.map((row) => row[0]), procurement.offers.map((item) => item.id));
  assert.deepEqual(offersSheet.getRange("A54:A71").values.map((row) => row[0]), procurement.originalGapAudit.map((row) => row.id));
  assert.equal(sources.getRange("A82:G82").values[0][0], "O30");

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(candidate);
  for (const [name, beforeHash] of Object.entries(inputHashes)) assert.equal(fileHash(await fs.readFile(name)), beforeHash, name + " changed during candidate export");
  assert.equal(fileHash(await fs.readFile(file)), expectedBefore, "The main workbook must remain unchanged before external acceptance");
  const candidateBytes = await fs.readFile(candidate);
  const candidateHash = fileHash(candidateBytes);
  const sidecarInfo = await fs.stat(inspectSidecar).then(async (stat) => ({ path: path.resolve(inspectSidecar), bytes: stat.size, sha256: fileHash(await fs.readFile(inspectSidecar)) }), () => null);
  const candidateWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(candidate));
  const candidateNames = [];
  for (let index = 0; index < 8; index++) candidateNames.push(candidateWorkbook.worksheets.getItemAt(index).name);
  assert.deepEqual(candidateNames, sheetNames);
  const candidateTables = tableMetadata(candidateWorkbook);
  assert.deepEqual(candidateTables, afterTables, "Candidate export changed the 13-table metadata after the in-memory checks");
  const candidateFormulaCount = candidateNames.reduce((sum, name) => {
    const used = candidateWorkbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(candidateFormulaCount, 231);
  assert.equal(candidateWorkbook.worksheets.getItem("Предложения РФ РБ Китай").getRange("A34").values[0][0], "O30");
  close(candidateWorkbook.worksheets.getItem("Предложения РФ РБ Китай").getRange("K34").values[0][0], 53.3233424, "Exported O30 BYN total");
  close(candidateWorkbook.worksheets.getItem("Выбранное оборудование").getRange("F39").values[0][0], 53.3233424, "Exported B36 full lookup");
  close(candidateWorkbook.worksheets.getItem("Выбранное оборудование").getRange("G39").values[0][0], 53.3233424, "Exported B36 pilot lookup");
  console.log(JSON.stringify({
    result: "B36_O30_LOCAL_CANDIDATE_READY_FOR_H01_FULL_GUARD", mode: "single O30/B36 local candidate only",
    beforeZipSha256: expectedBeforeZip, beforeSha256: originalSha256, candidateSha256: candidateHash, candidateBytes: candidateBytes.length,
    totals, formulaErrors: 0, formulasBefore: beforeFormulaCount, formulasCandidate: candidateFormulaCount,
    localTablesBefore: beforeTables.length, localTablesCandidate: candidateTables.length,
    tableRanges: expectedTableRanges, sourceRegister: "A12:G81 -> A12:G82", offers: 30, unpriced: 9,
    originalGapAuditRows: 18, sourceAppend: sourceRow, sidecar: sidecarInfo,
    mainStillUnchanged: fileHash(await fs.readFile(file)) === expectedBefore,
    fullStyleLayoutHeightGuard: "pending H01; preserve all effective row heights and previously accepted B39 states",
  }, null, 2));
  process.exit(0);
}

if (process.argv.includes("--b36-o30-contact-corrective")) {
  const root = path.resolve(dir, "../..");
  const candidate = path.join(root, ".harness", "tmp", "SHP-001-B36-O30-corrected-candidate.xlsx");
  const inspectSidecar = candidate + ".inspect.ndjson";
  const beforeZip = path.join(root, ".harness", "tmp", "SHP-001-B36-O30-before.zip");
  const firstCandidate = path.join(root, ".harness", "tmp", "SHP-001-B36-O30-candidate.xlsx");
  const firstInspect = firstCandidate + ".inspect.ndjson";
  const nativePreimage = path.join(root, ".harness", "tmp", "SHP-001-B36-O30-native-preimage.json");
  const expectedMain = "1893BACA02FC85472C9F91F1DEBE1CD92EFA7154E0C0B6FA19E2B3E48218E130";
  const expectedBeforeZip = "854B2E3EA85756C971E6A375F20E8DBABFE0702A230ACF5F8FC7433415F1695A";
  const expectedFirstInspect = "525B5FFB1C75A5E68366C7EF1306B6824F907C7C644418C956FD4F51ECA80ABE";
  const expectedNativePreimage = "8D63C6DDA021DB5A1B2C037DFE3A5879818DB0DCC42F55F8B542395C35DBA227";
  const fileHash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex").toUpperCase();
  const close = (actual, expected, label) => assert(Number.isFinite(actual) && Math.abs(actual - expected) < 1e-8, `${label}: ${actual} != ${expected}`);
  const phones = ["+7 (495) 565-34-90", "+7 (495) 615-01-01"];
  const inputNames = ["procurement-data.json", "workbook-data.json", "qa-result.json"];
  const inputHashesBefore = Object.fromEntries(await Promise.all(inputNames.map(async (name) => [name, fileHash(await fs.readFile(name))])));
  const offer = procurement.offers.find((item) => item.id === "O30");
  assert(offer && offer.bom === "B36" && offer.seller.startsWith("ONECOM"), "O30 must remain the selected B36/ONECOM line");
  assert(phones.every((phone) => offer.notes.includes(phone)), "O30 procurement notes must include both authorized ONECOM seller phones");
  const oldNotes = offer.notes.replace(` Контакты продавца ONECOM: ${phones[0]}; ${phones[1]}.`, "");
  assert.notEqual(oldNotes, offer.notes, "The only approved procurement change is the appended ONECOM contact sentence");

  const mainBytes = await fs.readFile(file);
  assert.equal(fileHash(mainBytes), expectedMain, "Current main must remain the already-promoted first candidate");
  assert.deepEqual(mainBytes, await fs.readFile(firstCandidate), "First candidate must remain byte-identical to current main");
  assert.equal(fileHash(await fs.readFile(beforeZip)), expectedBeforeZip, "Immutable original before ZIP changed");
  assert.equal(fileHash(await fs.readFile(firstInspect)), expectedFirstInspect, "First candidate inspect sidecar changed");
  assert.equal(fileHash(await fs.readFile(nativePreimage)), expectedNativePreimage, "Native preimage sidecar changed");
  assert.equal(await fs.stat(candidate).then(() => true, () => false), false, "Corrected candidate path already exists; refusing overwrite");
  assert.equal(await fs.stat(inspectSidecar).then(() => true, () => false), false, "Corrected candidate inspect path already exists; refusing overwrite");

  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  const sheetNames = [];
  for (let index = 0; index < 8; index++) sheetNames.push(workbook.worksheets.getItemAt(index).name);
  assert.deepEqual(sheetNames, data.sheet.tabs, "The existing eight tabs/order changed");
  const offers = workbook.worksheets.getItem("Предложения РФ РБ Китай");
  const sources = workbook.worksheets.getItem("Источники и курсы");
  assert.equal(offers.getRange("A34").values[0][0], "O30");
  assert.equal(offers.getRange("V34").values[0][0], oldNotes, "Offers V34 must be the unchanged first-candidate note preimage");
  assert.equal(offers.getRange("W34").values[0][0], offer.url, "Do not overwrite the O30 URL in Offers W34");
  assert.equal(sources.getRange("A82").values[0][0], "O30");
  assert.equal(sources.getRange("F82").values[0][0], oldNotes, "Sources F82 must be the unchanged first-candidate note preimage");
  assert.equal(sources.getRange("G82").values[0][0], offer.url, "Do not overwrite the O30 URL in Sources G82");

  const tableMetadata = (book) => sheetNames.flatMap((sheetName) => book.worksheets.getItem(sheetName).tables.items.map((table) => ({
    sheetName, name: table.name, address: table.address, style: table.style, columns: table.columnNames,
    showHeaders: table.showHeaders, showTotals: table.showTotals, showBandedRows: table.showBandedRows,
    showBandedColumns: table.showBandedColumns, highlightFirstColumn: table.highlightFirstColumn,
    highlightLastColumn: table.highlightLastColumn, showFilterButton: table.showFilterButton,
  })));
  const beforeTables = tableMetadata(workbook);
  assert.equal(beforeTables.length, 13, "All 13 previously verified local tables must remain present");
  const expectedRanges = new Map([
    ["CurrentOffers", "A4:W34"], ["HistoricalOnly", "A35:I44"], ["PlatformAudit", "A46:E50"],
    ["OriginalGapAudit", "A53:H71"], ["SourceRegister", "A12:G82"],
  ]);
  for (const table of beforeTables) if (expectedRanges.has(table.name)) assert.equal(table.address, expectedRanges.get(table.name));

  const snapshot = (book) => Object.fromEntries(sheetNames.map((sheetName) => {
    const used = book.worksheets.getItem(sheetName).getUsedRange();
    return [sheetName, used ? { address: used.address, rowIndex: used.rowIndex, columnIndex: used.columnIndex,
      values: used.values.map((row) => row.slice()), formulas: used.formulas.map((row) => row.slice()) } : null];
  }));
  const beforeCells = snapshot(workbook);
  const formulaCount = sheetNames.reduce((sum, name) => {
    const used = workbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(formulaCount, 231, "Corrective candidate must preserve all 231 formulas");
  const targetChanges = [
    { sheet: "Предложения РФ РБ Китай", cell: "V34", value: offer.notes },
    { sheet: "Источники и курсы", cell: "F82", value: offer.notes },
  ];
  offers.getRange("V34").values = [[offer.notes]];
  sources.getRange("F82").values = [[offer.notes]];
  const afterEdit = snapshot(workbook);
  const targetMap = new Map(targetChanges.map((item) => [`${item.sheet}!${item.cell}`, item.value]));
  const columnName = (index) => {
    let value = index + 1, result = "";
    while (value > 0) { const rem = (value - 1) % 26; result = String.fromCharCode(65 + rem) + result; value = Math.floor((value - 1) / 26); }
    return result;
  };
  const sourceD1FormulaCacheWhitelist = new Set([
    ...[6, 11, 12, 13, 14, 16, 17, 18, 19, 20, 22, 23, 29, 33].map((row) => `Выбранное оборудование!G${row}`),
    ...[37, 38, 39].flatMap((row) => ["J", "K"].map((column) => `Выбранное оборудование!${column}${row}`)),
    ...[6, 11, 12, 13, 14, 16, 17, 18, 19, 20, 22, 23, 25, 26, 27, 28, 29, 30, 33]
      .flatMap((row) => ["M", "N"].map((column) => `Предложения РФ РБ Китай!${column}${row}`)),
  ]);
  assert.equal(sourceD1FormulaCacheWhitelist.size, 58, "Source D1 empty-formula-cache whitelist must contain exactly 58 cells");
  const inMemoryNormalizedFormulaCaches = [];
  const inMemoryChangedTargets = [];
  const inMemoryUnexpectedChanges = [];
  for (const sheetName of sheetNames) {
    const before = beforeCells[sheetName], after = afterEdit[sheetName];
    assert.equal(after?.address ?? null, before?.address ?? null, `Used range changed on ${sheetName}`);
    if (!before) continue;
    assert.deepEqual(after.formulas, before.formulas, `Formula changed on ${sheetName}`);
    for (let row = 0; row < before.values.length; row++) {
      assert.equal(after.values[row].length, before.values[row].length);
      for (let column = 0; column < before.values[row].length; column++) {
        const cell = `${columnName((before.columnIndex ?? 0) + column)}${(before.rowIndex ?? 0) + row + 1}`;
        const key = `${sheetName}!${cell}`;
        const original = before.values[row][column];
        const actual = after.values[row][column];
        const expected = targetMap.has(key) ? targetMap.get(key) : before.values[row][column];
        if (targetMap.has(key)) {
          assert.deepEqual(actual, expected, `Approved target value did not land at ${key}`);
          if (!Object.is(actual, original)) inMemoryChangedTargets.push(key);
        } else if (!Object.is(actual, original)) {
          const beforeFormula = before.formulas[row][column];
          const afterFormula = after.formulas[row][column];
          if (sourceD1FormulaCacheWhitelist.has(key) && typeof beforeFormula === "string" && beforeFormula.startsWith("=") &&
              afterFormula === beforeFormula && (original === null || original === "") && (actual === null || actual === "")) {
            inMemoryNormalizedFormulaCaches.push(key);
          } else {
            inMemoryUnexpectedChanges.push(key);
          }
        }
      }
    }
  }
  assert.deepEqual(inMemoryChangedTargets.sort(), [...targetMap.keys()].sort(), "Only the two approved note cells may change in memory");
  assert.deepEqual(inMemoryNormalizedFormulaCaches.sort(), [...sourceD1FormulaCacheWhitelist].sort(), "In-memory empty-formula-cache differences must match Source D1's exact 58-cell witness");
  assert.deepEqual(inMemoryUnexpectedChanges, [], "Unexpected in-memory changes exist outside the two notes and Source D1 cache whitelist");

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(candidate);
  const currentInputHashes = Object.fromEntries(await Promise.all(inputNames.map(async (name) => [name, fileHash(await fs.readFile(name))])));
  assert.deepEqual(currentInputHashes, inputHashesBefore, "JSON/QA inputs changed while exporting the corrective candidate");
  assert.equal(fileHash(await fs.readFile(file)), expectedMain, "Main workbook changed during corrective candidate export");
  assert.equal(fileHash(await fs.readFile(firstCandidate)), expectedMain, "First candidate changed during corrective export");
  assert.equal(fileHash(await fs.readFile(beforeZip)), expectedBeforeZip);
  assert.equal(fileHash(await fs.readFile(firstInspect)), expectedFirstInspect);
  assert.equal(fileHash(await fs.readFile(nativePreimage)), expectedNativePreimage);
  const candidateBytes = await fs.readFile(candidate);
  const candidateHash = fileHash(candidateBytes);
  const inspectStat = await fs.stat(inspectSidecar);
  const inspectInfo = { path: path.resolve(inspectSidecar), bytes: inspectStat.size, sha256: fileHash(await fs.readFile(inspectSidecar)) };
  const candidateWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(candidate));
  const candidateNames = [];
  for (let index = 0; index < 8; index++) candidateNames.push(candidateWorkbook.worksheets.getItemAt(index).name);
  assert.deepEqual(candidateNames, sheetNames);
  assert.deepEqual(tableMetadata(candidateWorkbook), beforeTables, "Candidate export changed local table names/ranges/styles/flags/columns");
  const afterCells = snapshot(candidateWorkbook);
  const reimportNormalizedFormulaCaches = [];
  const reimportChangedTargets = [];
  const reimportUnexpectedChanges = [];
  for (const sheetName of sheetNames) {
    const before = beforeCells[sheetName], after = afterCells[sheetName];
    assert.equal(after?.address ?? null, before?.address ?? null, `Candidate used range changed on ${sheetName}`);
    if (!before) continue;
    assert.deepEqual(after.formulas, before.formulas, `Candidate formulas changed on ${sheetName}`);
    for (let row = 0; row < before.values.length; row++) for (let column = 0; column < before.values[row].length; column++) {
      const cell = `${columnName((before.columnIndex ?? 0) + column)}${(before.rowIndex ?? 0) + row + 1}`;
      const key = `${sheetName}!${cell}`;
      const original = before.values[row][column];
      const actual = after.values[row][column];
      const expected = targetMap.has(key) ? targetMap.get(key) : before.values[row][column];
      if (targetMap.has(key)) {
        assert.deepEqual(actual, expected, `Approved exported target value did not land at ${key}`);
        if (!Object.is(actual, original)) reimportChangedTargets.push(key);
      } else if (!Object.is(actual, original)) {
        const beforeFormula = before.formulas[row][column];
        const afterFormula = after.formulas[row][column];
        if (sourceD1FormulaCacheWhitelist.has(key) && typeof beforeFormula === "string" && beforeFormula.startsWith("=") &&
            afterFormula === beforeFormula && (original === null || original === "") && (actual === null || actual === "")) {
          reimportNormalizedFormulaCaches.push(key);
        } else {
          reimportUnexpectedChanges.push(key);
        }
      }
    }
  }
  assert.deepEqual(reimportChangedTargets.sort(), [...targetMap.keys()].sort(), "Only the two approved note cells may differ after reimport");
  assert(reimportNormalizedFormulaCaches.length <= sourceD1FormulaCacheWhitelist.size, "Reimport normalized more empty formula caches than Source D1 witnessed");
  assert.deepEqual(reimportUnexpectedChanges, [], "Unexpected exported changes exist outside the two notes and Source D1 cache whitelist");
  assert.equal(candidateWorkbook.worksheets.getItem("Предложения РФ РБ Китай").getRange("V34").values[0][0], offer.notes);
  assert.equal(candidateWorkbook.worksheets.getItem("Предложения РФ РБ Китай").getRange("W34").values[0][0], offer.url);
  assert.equal(candidateWorkbook.worksheets.getItem("Источники и курсы").getRange("F82").values[0][0], offer.notes);
  assert.equal(candidateWorkbook.worksheets.getItem("Источники и курсы").getRange("G82").values[0][0], offer.url);
  const candidateFormulaCount = candidateNames.reduce((sum, name) => {
    const used = candidateWorkbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(candidateFormulaCount, 231);
  const formulaErrors = candidateNames.flatMap((name) => {
    const used = candidateWorkbook.worksheets.getItem(name).getUsedRange();
    return used?.values.flat().filter((value) => typeof value === "string" && /^#(REF!|VALUE!|DIV\/0!|NAME\?|N\/A|NUM!|NULL!)/.test(value)).map((value) => `${name}:${value}`) ?? [];
  });
  assert.deepEqual(formulaErrors, []);
  const controls = candidateWorkbook.worksheets.getItem("Сводка");
  const expectedControls = { B7: 17331.9009872, B8: 450.25187, B9: 17782.1528572, B10: 18475, C10: 45125,
    B11: 36257.1528572, C11: 62907.1528572, B12: 5077.1999244, B13: 65, C13: 155,
    B14: 5142.1999244, C14: 5232.1999244, B15: 9 };
  for (const [cell, value] of Object.entries(expectedControls)) close(controls.getRange(cell).values[0][0], value, `Financial control ${cell}`);
  console.log(JSON.stringify({
    result: "CONTACT_CORRECTIVE_CANDIDATE_READY_FOR_ROOT_AND_SOURCE_REVIEW",
    beforeSha256: expectedMain, firstCandidateSha256: expectedMain, candidateSha256: candidateHash,
    correctedCells: ["Предложения РФ РБ Китай!V34", "Источники и курсы!F82"],
    phones, seller: "ONECOM; not Samsung", unchangedURLCells: ["Предложения РФ РБ Китай!W34", "Источники и курсы!G82"],
    formulasBefore: formulaCount, formulasAfter: candidateFormulaCount, formulaErrors: 0, localTables: beforeTables.length,
    sourceD1FormulaCacheWhitelistCount: sourceD1FormulaCacheWhitelist.size,
    inMemoryFormulaCacheNormalizations: inMemoryNormalizedFormulaCaches.sort(),
    reimportFormulaCacheNormalizations: reimportNormalizedFormulaCaches.sort(),
    unexpectedInMemoryChanges: inMemoryUnexpectedChanges, unexpectedReimportChanges: reimportUnexpectedChanges,
    preExportNumericTableIDWitness: "Read-only check on the exact current-main SHA confirmed all 13 existing table IDs; post-export full ID guard remains with root",
    controls, inputHashes: currentInputHashes,
    sidecar: inspectInfo, mainStillUnchanged: fileHash(await fs.readFile(file)) === expectedMain,
    firstCandidateUnchanged: fileHash(await fs.readFile(firstCandidate)) === expectedMain,
    fullSemanticStyleHeightIDGuard: "Root comparison pending; no promotion authorized",
  }, null, 2));
  process.exit(0);
}

if (process.argv.includes("--b39-o29")) {
  const root = path.resolve(dir, "../..");
  const candidateName = process.argv.includes("--style-repair")
    ? "SHP-001-B39-O29-style-repair.xlsx"
    : "SHP-001-B39-O29-candidate.xlsx";
  const candidate = path.join(root, ".harness", "tmp", candidateName);
  const expectedBefore = "280D9851594E6519F7060A5B4CD87DA23C21D799DED5C1CB790168BF7FAC58C3";
  const fileHash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex").toUpperCase();
  const inputNames = ["procurement-data.json", "workbook-data.json", "qa-result.json"];
  const inputHashes = Object.fromEntries(await Promise.all(inputNames.map(async (name) => [name, fileHash(await fs.readFile(name))])));
  const offer = procurement.offers.find((item) => item.id === "O29");
  assert(offer, "Accepted O29 must exist in the procurement packet");
  assert.equal(procurement.offers.length, 29);
  assert.equal(new Set(procurement.offers.map((item) => item.bom)).size, 29);
  assert.equal(procurement.unpriced.length, 10);
  assert.equal(procurement.originalGapAudit.length, 18);
  assert.deepEqual([offer.bom, offer.qty, offer.packQty, offer.currency, offer.unit], ["B39", 30, 1, "RUB", 322.69]);
  assert.equal(offer.evidence, "Первичный источник проверен Source 2026-10-19; официальная опубликованная цена производителя за единицу, не твёрдая или оптовая котировка");
  assert(offer.notes.includes("support@systeme.ru") && offer.notes.includes("+7 495 777 99 88"), "O29 notes must include the public manufacturer contacts");
  assert.equal(offer.taxBasis, "UNKNOWN");
  assert.equal(offer.additionalVAT, null);
  assert.equal(procurement.fx.RUB, 0.03604, "Existing RUB reference FX must remain unchanged");
  assert.equal(procurement.totalsControl.pricedNoSparesBYN, 17278.5776448);
  assert(Math.abs(procurement.totalsControl.pricedWithSparesBYN - procurement.totalsControl.pricedNoSparesBYN - 450.25187) < 1e-8);
  assert.equal(procurement.totalsControl.pricedWithSparesBYN, 17728.8295148);
  assert.equal(procurement.totalsControl.allowancesLowBYN, 18525);
  assert.equal(procurement.totalsControl.allowancesHighBYN, 45245);
  assert.equal(procurement.totalsControl.planningLowBYN, 36253.8295148);
  assert.equal(procurement.totalsControl.planningHighBYN, 62973.8295148);
  assert.equal(procurement.totalsControl.pilotKnownBYN, 5023.876582);
  assert.equal(procurement.totalsControl.pilotAllowLowBYN, 115);
  assert.equal(procurement.totalsControl.pilotAllowHighBYN, 275);
  assert.equal(procurement.totalsControl.mandatoryUnpricedLines, 10);
  assert.equal(procurement.unpriced.some((item) => item.id === "B39"), false);
  assert.equal(data.bom.length, 48);
  assert.equal(data.scenarios.length, 42);
  assert.equal(data.acceptance.length, 19);
  assert.equal(data.rooms.length, 9);
  assert.equal(data.sheet.tabs.length, 8);
  assert.equal(procurement.offers.filter((item) => ["O25", "O26", "O27", "O28"].includes(item.id)).length, 4, "The accepted prior four offers must remain present");
  const gapB39 = procurement.originalGapAudit.find((row) => row.id === "B39");
  assert(gapB39, "B39 audit row is required");
  assert.equal(gapB39.allowanceLowBYN, null);
  assert.equal(gapB39.allowanceHighBYN, null);
  const h09 = procurement.historical.find((row) => row.id === "H09");
  assert(h09?.originalOfferSnapshot && Object.keys(h09.originalOfferSnapshot).length === 16, "H09 full 16-field history snapshot must remain intact");

  const originalBytes = await fs.readFile(file);
  const originalSha256 = fileHash(originalBytes);
  assert.equal(originalSha256, expectedBefore, "Local XLSX changed since the accepted G07 prewrite snapshot");
  assert.equal(await fs.stat(candidate).then(() => true, () => false), false, "Approved candidate path already exists; stop instead of overwriting it");
  const inspectSidecar = `${candidate}.inspect.ndjson`;
  assert.equal(await fs.stat(inspectSidecar).then(() => true, () => false), false, "Candidate inspect sidecar existed before the sole export");

  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  const sheetNames = [];
  for (let index = 0; index < 8; index++) sheetNames.push(workbook.worksheets.getItemAt(index).name);
  assert.deepEqual(sheetNames, data.sheet.tabs, "Existing workbook tabs/order changed");
  const summary = workbook.worksheets.getItem("Сводка");
  const equipment = workbook.worksheets.getItem("Выбранное оборудование");
  const offers = workbook.worksheets.getItem("Предложения РФ РБ Китай");
  const sources = workbook.worksheets.getItem("Источники и курсы");
  const offersTableNames = ["CurrentOffers", "HistoricalOnly", "PlatformAudit", "OriginalGapAudit"];
  const tablesByName = new Map(offers.tables.items.map((table) => [table.name, table]));
  for (const name of offersTableNames) assert(tablesByName.has(name), `Missing existing local table ${name}`);
  const allTables = sheetNames.flatMap((name) => workbook.worksheets.getItem(name).tables.items);
  assert.equal(allTables.length, 13, "The local workbook must keep all 13 native Excel tables");
  const tableFlags = {
    showHeaders: true, showTotals: false, showBandedRows: true, showBandedColumns: false,
    highlightFirstColumn: false, highlightLastColumn: false, showFilterButton: false,
  };
  const tableMetadata = (book) => sheetNames.flatMap((sheetName) => book.worksheets.getItem(sheetName).tables.items.map((table) => ({
    sheetName, name: table.name, address: table.address, style: table.style, columns: table.columnNames,
    showHeaders: table.showHeaders, showTotals: table.showTotals, showBandedRows: table.showBandedRows,
    showBandedColumns: table.showBandedColumns, highlightFirstColumn: table.highlightFirstColumn,
    highlightLastColumn: table.highlightLastColumn, showFilterButton: table.showFilterButton,
  })));
  const oldTableMetadata = tableMetadata(workbook);
  const oldFormulaCount = sheetNames.reduce((sum, name) => {
    const used = workbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(oldFormulaCount, 218, "Current accepted local workbook must begin with 218 formulas");
  assert.equal(tablesByName.get("CurrentOffers").address, "A4:W32");
  assert.equal(tablesByName.get("HistoricalOnly").address, "A33:I42");
  assert.equal(tablesByName.get("PlatformAudit").address, "A44:E48");
  assert.equal(tablesByName.get("OriginalGapAudit").address, "A51:H69");
  assert.equal(offers.getRange("A50").values[0][0] !== null, true, "Original audit title is required");
  assert.equal(offers.getRange("A49:H49").values.flat().filter((value) => value !== null && value !== "").length, 0, "Original gap row 49 must remain blank");
  assert.deepEqual(offers.getRange("A51:H51").values[0], originalGapAuditHeaders, "Visible Russian original-audit headers changed");
  const sourceTable = sources.tables.items.find((table) => table.name === "SourceRegister");
  assert(sourceTable, "Existing SourceRegister table is required");
  assert.equal(sourceTable.address, "A12:G80");
  assert.equal(sources.getRange("A81:G81").values.flat().filter((value) => value !== null && value !== "").length, 0, "SourceRegister append row 81 must be blank");

  const copyRow = (sourceRow, targetRow, lastColumn) => {
    offers.getRange(`A${sourceRow}:${lastColumn}${sourceRow}`).copyTo(offers.getRange(`A${targetRow}:${lastColumn}${targetRow}`), "all");
    const height = offers.getRange(`A${sourceRow}`).format.rowHeight;
    if (Number.isFinite(height)) offers.getRange(`A${targetRow}`).format.rowHeight = height;
  };
  const moveRowsBottomUp = (sourceFirst, sourceLast, targetFirst, lastColumn) => {
    for (let sourceRow = sourceLast; sourceRow >= sourceFirst; sourceRow--) copyRow(sourceRow, targetFirst + sourceRow - sourceFirst, lastColumn);
  };
  for (const name of offersTableNames) tablesByName.get(name).delete();
  moveRowsBottomUp(51, 69, 52, "H");
  offers.getRange("A51:H51").clear({ applyTo: "all" });
  const oldAuditTitle = offers.getRange("A50").values[0][0];
  assert(typeof oldAuditTitle === "string" && oldAuditTitle.includes("28 активных ценовых ссылок") && oldAuditTitle.includes("11 текущих строк без цены"), "Original gap title counts do not match the frozen 28/11 baseline");
  offers.getRange("A50:H50").unmerge();
  copyRow(50, 51, "H");
  offers.mergeCells("A51:H51");
  offers.getRange("A50:H50").clear({ applyTo: "all" });
  moveRowsBottomUp(44, 48, 45, "E");
  offers.getRange("A44:E44").clear({ applyTo: "all" });
  moveRowsBottomUp(33, 42, 34, process.argv.includes("--style-repair") ? "W" : "I");
  offers.getRange("A33:I33").clear({ applyTo: "contents" });

  const fxRate = (item) => {
    const value = procurement.fx[item.currency];
    assert(Number.isFinite(value), `Missing reference FX for ${item.currency}`);
    return value;
  };
  const buildOfferRow = (item) => [
    item.id, item.bom, item.sku, item.qty, item.packQty, null, item.unit, item.currency, fxRate(item), null, null,
    procurement.pilotQty[item.bom] ?? null, null, null, item.evidence, item.date, item.region, item.seller,
    item.shipping ?? "unknown", item.duty ?? "unknown", item.warranty ?? "unknown", item.notes, item.url,
  ];
  copyRow(32, 33, "W");
  offers.getRange("A33:W33").values = [buildOfferRow(offer)];
  offers.getRange("F33").formulas = [["=IF(OR(D33=\"\",E33=\"\"),\"\",ROUNDUP(D33/E33,0))"]];
  offers.getRange("J33").formulas = [["=IF(OR(G33=\"\",I33=\"\"),\"\",G33*I33)"]];
  offers.getRange("K33").formulas = [["=IF(OR(D33=\"\",E33=\"\",G33=\"\",I33=\"\"),\"\",F33*G33*I33)"]];
  offers.getRange("M33").formulas = [["=IF(OR(L33=\"\",E33=\"\"),\"\",ROUNDUP(L33/E33,0))"]];
  offers.getRange("N33").formulas = [["=IF(OR(L33=\"\",G33=\"\",I33=\"\"),\"\",M33*G33*I33)"]];

  const historyRows = procurement.historical;
  assert.equal(historyRows.length, 9, "All nine historical records, including H09, must remain");
  const auditB39Row = 53 + procurement.originalGapAudit.findIndex((row) => row.id === "B39");
  assert(auditB39Row >= 53 && auditB39Row <= 70, "Could not map B39 in the moved original-gap table");
  offers.getRange(`D${auditB39Row}:E${auditB39Row}`).values = [[gapB39.currentStatus, gapB39.priceTreatment]];
  offers.getRange(`G${auditB39Row}:H${auditB39Row}`).values = [[null, null]];
  const newAuditTitle = oldAuditTitle
    .replace("28 активных ценовых ссылок", "29 активных ценовых ссылок")
    .replace("11 текущих строк без цены", "10 текущих строк без цены")
    + " O29 — опубликованная цена производителя за механизм; наличие партии, НДС и оптовая цена неизвестны; стоимость не является твёрдым предложением.";
  offers.getRange("A51").values = [[newAuditTitle]];
  offers.getRange("A52:H52").values = [originalGapAuditHeaders];

  const bomById = new Map(data.bom.map((item) => [item.id, item]));
  const equipmentValues = equipment.getRange("A5:N52").values;
  assert.equal(equipmentValues.length, 48);
  const equipmentRowById = new Map(equipmentValues.map((row, index) => [row[0], index + 5]));
  assert.equal(equipmentRowById.size, 48);
  const b39Row = equipmentRowById.get("B39");
  assert.equal(b39Row, 42, "B39 equipment coordinate is part of the accepted packet");
  const bomB39 = bomById.get("B39");
  assert(bomB39, "B39 canonical BOM record is required");
  assert.equal(equipment.getRange(`C${b39Row}`).values[0][0], "Обязательная позиция — цена неизвестна", "B39 class preimage changed unexpectedly");
  equipment.getRange(`C${b39Row}`).values = [[bomB39.class]];
  equipment.getRange(`F${b39Row}`).formulas = [["=IFERROR(IF(INDEX('Предложения РФ РБ Китай'!$K$5:$K$33,MATCH($A42,'Предложения РФ РБ Китай'!$B$5:$B$33,0))=\"\",\"\",INDEX('Предложения РФ РБ Китай'!$K$5:$K$33,MATCH($A42,'Предложения РФ РБ Китай'!$B$5:$B$33,0))),\"\")"]];
  equipment.getRange(`G${b39Row}:I${b39Row}`).clear({ applyTo: "contents" });
  equipment.getRange(`L${b39Row}:N${b39Row}`).values = [[bomB39.source ?? null, bomB39.url ?? null, bomB39.gate ?? null]];
  equipment.getRange("A2").values = [[data.sheet.equipmentCaption]];

  const summaryCaption = "Рабочая оценка в BYN, не заказ. 29 активных ценовых ссылок и 10 строк без цены; Беларусь подтверждена владельцем. Сумма частичная и смешанная NET/GROSS: O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС; налоговый режим O29 неизвестен. По указанию владельца доставка, посредник, таможня и прочие логистические расходы для всех регионов исключены из сметы; это не нулевые расходы.";
  const moneyCaption = "Цены NET/GROSS отражены по источникам: O27 указана без НДС, дополнительный НДС неизвестен; O28 включает НДС; налоговый режим O29 неизвестен. По указанию владельца доставка, посредник, таможня и прочие логистические расходы для всех регионов исключены из сметы (не 0).";
  const countCaption = "29 ссылок — справочные, не твёрдые заказы; 10 обязательных строк остаются без цены. Сумма частичная и смешанная NET/GROSS: O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС; налоговый режим O29 неизвестен. Доставка, посредник, таможня и прочие логистические расходы по всем регионам исключены владельцем из сметы (не 0).";
  const pilotCaption = "Без проектирования. O29 не включён в первый стенд. По указанию владельца доставка, посредник, таможня и прочие логистические расходы по всем регионам исключены из сметы (не 0). Налоговый режим O27/O28/O29 сохранён по источникам: O27 без НДС, дополнительный НДС неизвестен; O28 включает НДС; НДС O29 неизвестен.";
  const policyCaption = "Квартира и конечная доставка — Беларусь, подтверждено владельцем. Условия Seeed по экспортному соответствию блокируют поставки в Беларусь и Россию, включая конечное использование и реэкспорт; O04/O05 остаются справочными ценами только по условиям этого поставщика, доступный маршрут не подтверждён; обход не предлагается. Для всех регионов доставка, посредник, таможня и прочие логистические расходы исключены из сметы по указанию владельца; это не нулевые расходы. GBP — 4,0131 BYN за единицу по справочному курсу НБРБ на 19.10.2026, не курс платежа. O29 — справочная цена без подтверждения НДС и наличия партии.";
  summary.getRange("A2").values = [[summaryCaption]];
  summary.getRange("D7").values = [[moneyCaption]];
  summary.getRange("D11").values = [[countCaption]];
  summary.getRange("D14").values = [[pilotCaption]];
  summary.getRange("D16").values = [[policyCaption]];
  summary.getRange("D7:D16").format.wrapText = true;
  summary.getRange("B15").values = [[10]];

  const offersCaption = "29 текущих ценовых ссылок, не твёрдые заказы; 10 обязательных строк остаются без цены. O25–O29 — справочные ориентиры; для O29 неизвестны наличие 30 шт., НДС и цена партии. Страна доставки — Беларусь, подтверждено владельцем. По указанию владельца доставка, посредник, таможня и прочие логистические расходы для всех регионов исключены из сметы (не 0). Условия Seeed блокируют Беларусь/Россию; O04/O05 — справочные цены по условиям этого поставщика.";
  offers.getRange("A2").values = [[offersCaption]];

  const sourceRow = [offer.id, offer.evidence, offer.date, offer.region, offer.seller, offer.notes, offer.url];
  sourceTable.rows.add(null, [sourceRow]);
  const sourceAdded = sources.getRange("A81:G81").values[0];
  assert.deepEqual(sourceAdded, sourceRow, "SourceRegister O29 row must retain Source attribution, contacts and exact offer notes");

  const setTableFlags = (table) => { for (const [key, value] of Object.entries(tableFlags)) table[key] = value; };
  const expectedTableRanges = [
    ["CurrentOffers", "A4:W33"],
    ["HistoricalOnly", "A34:I43"],
    ["PlatformAudit", "A45:E49"],
    ["OriginalGapAudit", "A52:H70"],
  ];
  for (const [name, address] of expectedTableRanges) {
    if (name === "OriginalGapAudit") offers.getRange("A52:H52").values = [["BOM ID", "Qty", "Original evidence", "Current status", "Price treatment", "Source", "Allowance low BYN", "Allowance high BYN"]];
    const table = offers.tables.add(address, true, name);
    table.style = "TableStyleLight1";
    setTableFlags(table);
    if (name === "OriginalGapAudit") offers.getRange("A52:H52").values = [originalGapAuditHeaders];
  }

  await workbook.recalculate();
  const totals = {
    pricedNoSparesBYN: summary.getRange("B7").values[0][0],
    sparesBYN: summary.getRange("B8").values[0][0],
    pricedWithSparesBYN: summary.getRange("B9").values[0][0],
    allowancesLowBYN: summary.getRange("B10").values[0][0],
    allowancesHighBYN: summary.getRange("C10").values[0][0],
    planningLowBYN: summary.getRange("B11").values[0][0],
    planningHighBYN: summary.getRange("C11").values[0][0],
    pilotKnownBYN: summary.getRange("B12").values[0][0],
    pilotAllowLowBYN: summary.getRange("B13").values[0][0],
    pilotAllowHighBYN: summary.getRange("C13").values[0][0],
    pilotPlanLowBYN: summary.getRange("B14").values[0][0],
    pilotPlanHighBYN: summary.getRange("C14").values[0][0],
    mandatoryUnpricedLines: summary.getRange("B15").values[0][0],
  };
  const expectedTotals = {
    pricedNoSparesBYN: 17278.5776448, sparesBYN: 450.25187, pricedWithSparesBYN: 17728.8295148,
    allowancesLowBYN: 18525, allowancesHighBYN: 45245, planningLowBYN: 36253.8295148, planningHighBYN: 62973.8295148,
    pilotKnownBYN: 5023.876582, pilotAllowLowBYN: 115, pilotAllowHighBYN: 275,
    pilotPlanLowBYN: 5138.876582, pilotPlanHighBYN: 5298.876582, mandatoryUnpricedLines: 10,
  };
  for (const [key, expected] of Object.entries(expectedTotals)) assert(Number.isFinite(totals[key]) && Math.abs(totals[key] - expected) < 1e-8, `${key} mismatch: ${totals[key]} vs ${expected}`);
  assert(Math.abs(equipment.getRange(`F${b39Row}`).values[0][0] - 348.892428) < 1e-8, "B39 price must resolve from the linked O29 offer row");
  assert.deepEqual(equipment.getRange(`G${b39Row}:I${b39Row}`).values[0], [null, null, null], "O29 must remain outside the pilot and B39 allowances must be blank");
  assert.equal(offers.getRange("A33").values[0][0], "O29");
  assert(Math.abs(offers.getRange("K33").values[0][0] - 348.892428) < 1e-8);
  assert.equal(offers.getRange("A43").values[0][0], "H09", "H09 must remain at its shifted history position");
  assert.deepEqual(offers.getRange("A51:H51").values[0].slice(0, 1), [newAuditTitle]);
  assert.equal(offers.getRange(`A${auditB39Row}`).values[0][0], "B39");
  assert.deepEqual(offers.getRange(`G${auditB39Row}:H${auditB39Row}`).values[0], [null, null]);
  const candidateTableMetadata = tableMetadata(workbook);
  assert.equal(candidateTableMetadata.length, 13);
  for (const [name, address] of expectedTableRanges) assert.equal(offers.tables.items.find((table) => table.name === name)?.address, address, `${name} range mismatch`);
  const candidateFormulaCount = sheetNames.reduce((sum, name) => {
    const used = workbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(candidateFormulaCount, 224, "The local workbook must contain 218 original formulas plus 6 linked offer/BOM formulas");
  const formulaErrors = [];
  for (const sheetName of sheetNames) {
    const sheet = workbook.worksheets.getItem(sheetName);
    const used = sheet.getUsedRange();
    if (!used) continue;
    for (const [rowIndex, row] of used.values.entries()) for (const [columnIndex, value] of row.entries()) {
      if (typeof value === "string" && /^#(REF!|VALUE!|DIV\/0!|NAME\?|N\/A|NUM!|NULL!)/.test(value)) formulaErrors.push(`${sheetName}!r${rowIndex + 1}c${columnIndex + 1}=${value}`);
    }
  }
  assert.deepEqual(formulaErrors, [], `Formula error scan found: ${formulaErrors.join(", ")}`);
  assert.deepEqual(offers.getRange("A4:A33").values.slice(1).map((row) => row[0]), procurement.offers.map((item) => item.id));
  assert.deepEqual(offers.getRange("A53:A70").values.map((row) => row[0]), procurement.originalGapAudit.map((row) => row.id));
  assert.equal(sources.getRange("A81:G81").values[0][0], "O29");

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(candidate);
  for (const [name, beforeHash] of Object.entries(inputHashes)) assert.equal(fileHash(await fs.readFile(name)), beforeHash, `${name} changed during candidate export`);
  assert.equal(fileHash(await fs.readFile(file)), expectedBefore, "Final XLSX must remain untouched before candidate acceptance");
  assert.equal(await fs.stat(inspectSidecar).then(() => true, () => false), false, "Artifact export created an inspect sidecar; stop before final replacement/native write");
  const candidateBytes = await fs.readFile(candidate);
  const candidateHash = fileHash(candidateBytes);
  const candidateWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(candidate));
  const candidateNames = [];
  for (let index = 0; index < 8; index++) candidateNames.push(candidateWorkbook.worksheets.getItemAt(index).name);
  assert.deepEqual(candidateNames, data.sheet.tabs);
  assert.equal(candidateNames.length, 8);
  assert.equal(candidateWorkbook.worksheets.getItem("Предложения РФ РБ Китай").getRange("A33").values[0][0], "O29");
  assert(Math.abs(candidateWorkbook.worksheets.getItem("Предложения РФ РБ Китай").getRange("K33").values[0][0] - 348.892428) < 1e-8);
  assert(Math.abs(candidateWorkbook.worksheets.getItem("Выбранное оборудование").getRange("F42").values[0][0] - 348.892428) < 1e-8);
  assert.deepEqual(tableMetadata(candidateWorkbook), candidateTableMetadata, "Candidate export changed local table metadata after the workbook-level checks");
  const candidateFormulaCountAfterExport = candidateNames.reduce((sum, name) => {
    const used = candidateWorkbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(candidateFormulaCountAfterExport, 224);
  console.log(JSON.stringify({ result: "CANDIDATE_READY_FOR_EXTERNAL_FULL_GUARD", mode: "B39/O29 only", beforeSha256: originalSha256, candidateSha256: candidateHash, candidateBytes: candidateBytes.length, totals, formulaErrors: 0, formulaCountBefore: oldFormulaCount, formulaCountCandidate: candidateFormulaCountAfterExport, localTablesBefore: oldTableMetadata.length, localTablesAfter: candidateTableMetadata.length, offers: 29, unpriced: 10, auditRows: 18, sourceAppend: sourceAdded, tabs: candidateNames.length, sidecarCreated: false }, null, 2));
  process.exit(0);
}

if (process.argv.includes("--admission28")) {
  const root = path.resolve(dir, "../..");
  const candidate = path.join(root, ".harness", "tmp", "SHP-001-A06-admission28-candidate.xlsx");
  const expectedBefore = "9CDD79250A7BD6DA1FF78861D3560F048D716196C575A87A4BCB8640EAB342B8";
  const fileHash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex").toUpperCase();
  const inputHashes = {};
  for (const name of ["procurement-data.json", "workbook-data.json", "qa-result.json"]) {
    inputHashes[name] = fileHash(await fs.readFile(name));
  }
  assert.equal(procurement.offers.length, 28, "Admission28 requires exactly 28 active offers");
  assert.equal(new Set(procurement.offers.map((offer) => offer.bom)).size, 28, "Each active offer must map to a unique BOM ID");
  assert.equal(procurement.unpriced.length, 11, "Admission28 requires 11 unpriced BOM lines");
  assert.equal(procurement.originalGapAudit.length, 18, "The original gap audit must keep all 18 rows");
  assert.equal(data.bom.length, 48, "The BOM must retain all 48 rows");
  assert.equal(data.scenarios.length, 42, "The scenario model must retain all 42 rows");
  assert.equal(data.acceptance.length, 19, "The physical test list must retain all 19 rows");
  assert.equal(data.sheet.tabs.length, 8, "The workbook must retain the existing 8 tabs");
  assert.equal(procurement.totalsControl.pricedNoSparesBYN, 16929.6852168);
  assert.equal(procurement.totalsControl.pricedWithSparesBYN, 17379.9370868);
  assert.equal(procurement.totalsControl.allowancesLowBYN, 18975);
  assert.equal(procurement.totalsControl.allowancesHighBYN, 46445);
  assert.equal(procurement.totalsControl.planningLowBYN, 36354.9370868);
  assert.equal(procurement.totalsControl.planningHighBYN, 63824.9370868);
  assert.equal(procurement.totalsControl.pilotKnownBYN, 5023.876582);
  assert.equal(procurement.totalsControl.pilotAllowLowBYN, 115);
  assert.equal(procurement.totalsControl.pilotAllowHighBYN, 275);
  assert.equal(procurement.totalsControl.mandatoryUnpricedLines, 11);
  assert.equal(procurement.fx.GBP, 4.0131, "Existing GBP reference FX must remain unchanged");
  assert.equal(procurement.unpriced.some((line) => line.id === "B09"), false, "B09 is priced by O25, not an active unpriced line");
  for (const [id, currency, unit] of [["O25", "RUB", 42733], ["O26", "RUB", 10390], ["O27", "EUR", 6.9], ["O28", "EUR", 22.68]]) {
    const offer = procurement.offers.find((item) => item.id === id);
    assert(offer, `Missing accepted offer ${id}`);
    assert.equal(offer.currency, currency);
    assert.equal(offer.unit, unit);
    assert.equal(offer.qty, 1);
    assert.equal(offer.packQty, 1);
  }
  const netOffer = procurement.offers.find((offer) => offer.id === "O27");
  const grossOffer = procurement.offers.find((offer) => offer.id === "O28");
  assert.equal(netOffer.taxBasis, "NET/exVAT");
  assert.equal(netOffer.additionalVAT, null, "Additional O27 VAT must remain unknown/null, not zero");
  assert.equal(grossOffer.taxBasis, "GROSS/VAT included");
  const activeO02 = procurement.offers.find((offer) => offer.id === "O02");
  assert.equal(activeO02.unit, 485.72);
  assert(activeO02.notes.includes("485,72 BYN/шт. действует только при 100% оплате сразу одним чеком"), "Active O02 must disclose the seller's full-payment price condition");
  assert(data.bom.find((item) => item.id === "B07").gate.includes("485,72 BYN/шт. действует только при 100% оплате сразу одним чеком"), "B07 gate must surface the O02 full-payment price condition");
  const historyO02 = procurement.historical.find((item) => item.id === "H09");
  assert(historyO02 && historyO02.originalOfferSnapshot, "H09 must retain the complete O02 snapshot");
  assert.equal(Object.keys(historyO02.originalOfferSnapshot).length, 16, "The original O02 snapshot must retain all 16 fields");
  assert.equal(historyO02.qty, 2);
  assert.equal(historyO02.historicalPrice, 13390);
  assert.equal(historyO02.seller, "TP-Link Russia store");
  assert.equal(historyO02.date, "2026-10-19");
  assert(historyO02.note.includes("13 390 RUB за штуку") && historyO02.note.includes("количество 2"), "Visible H09 note must state the dated old price and quantity");

  const originalBytes = await fs.readFile(file);
  const originalSha256 = fileHash(originalBytes);
  assert.equal(originalSha256, expectedBefore, "Local workbook changed since the immutable admission28 prewrite snapshot");
  assert.equal(await fs.stat(candidate).then(() => true, () => false), false, "Approved candidate path already exists; stop instead of overwriting it");

  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  const sheetNames = [];
  for (let i = 0; i < 8; i++) sheetNames.push(workbook.worksheets.getItemAt(i).name);
  assert.deepEqual(sheetNames, data.sheet.tabs, "Existing workbook tab names/order changed");
  const allTables = sheetNames.flatMap((name) => workbook.worksheets.getItem(name).tables.items);
  assert.equal(allTables.length, 13, "The local XLSX must retain all 13 native table objects");

  const summary = workbook.worksheets.getItem("Сводка");
  const equipment = workbook.worksheets.getItem("Выбранное оборудование");
  const offers = workbook.worksheets.getItem("Предложения РФ РБ Китай");
  const sources = workbook.worksheets.getItem("Источники и курсы");
  const tablesByName = new Map(offers.tables.items.map((table) => [table.name, table]));
  const targetTableNames = ["CurrentOffers", "HistoricalOnly", "PlatformAudit", "OriginalGapAudit"];
  for (const name of targetTableNames) assert(tablesByName.has(name), `Missing existing local table ${name}`);
  const tableStyles = Object.fromEntries(targetTableNames.map((name) => [name, tablesByName.get(name).style]));
  assert.deepEqual(tableStyles, Object.fromEntries(targetTableNames.map((name) => [name, "TableStyleLight1"])));
  const baselineFormulaCount = sheetNames.reduce((sum, name) => {
    const used = workbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(baselineFormulaCount, 190, "The local XLSX must start with the 190 accepted baseline formulas");

  const originalHistory = offers.getRange("A29:I37").values;
  const originalPlatform = offers.getRange("A40:E44").values;
  const originalAudit = offers.getRange("A47:H65").values;
  const originalTitle = offers.getRange("A46:H46").values[0][0];
  assert.deepEqual(originalHistory[0], offers.getRange("A29:I29").values[0]);
  assert.equal(originalHistory[0][0], "ID");
  assert.equal(originalPlatform[0][0], "Площадка");
  assert.equal(originalAudit.length, 19);
  assert(originalTitle, "The original audit title must exist before it is moved");
  assert.deepEqual(offers.getRange("A47:H47").values[0], originalGapAuditHeaders, "The visible Russian audit headers changed before the move");
  assert.deepEqual(offers.getRange("A29:I37").formulas.flat().filter(Boolean), [], "Historical rows must not contain formulas");
  assert.deepEqual(offers.getRange("A40:E44").formulas.flat().filter(Boolean), [], "Platform audit must not contain formulas");
  assert.deepEqual(offers.getRange("A47:H65").formulas.flat().filter(Boolean), [], "Original gap audit must not contain formulas");

  const tableFlags = {
    showHeaders: true,
    showTotals: false,
    showBandedRows: true,
    showBandedColumns: false,
    showFilterButton: false,
  };
  for (const name of targetTableNames) tablesByName.get(name).delete();
  const copyRow = (sourceRow, targetRow, lastColumn) => {
    offers.getRange(`A${sourceRow}:${lastColumn}${sourceRow}`).copyTo(offers.getRange(`A${targetRow}:${lastColumn}${targetRow}`), "all");
    const height = offers.getRange(`A${sourceRow}`).format.rowHeight;
    if (Number.isFinite(height)) offers.getRange(`A${targetRow}`).format.rowHeight = height;
  };
  const moveRowsBottomUp = (sourceFirst, sourceLast, targetFirst, lastColumn) => {
    for (let sourceRow = sourceLast; sourceRow >= sourceFirst; sourceRow--) copyRow(sourceRow, targetFirst + sourceRow - sourceFirst, lastColumn);
  };

  // Move bottom-up to protect overlapping source rows; source registers and native Sheets remain untouched here.
  moveRowsBottomUp(47, 65, 51, "H");
  offers.getRange("A47:H50").clear({ applyTo: "all" });
  assert.equal(offers.getRange("A49:H49").values.flat().filter((value) => value !== null && value !== "").length, 0, "Row 49 must be blank after the audit range moves");
  offers.getRange("A46:H46").unmerge();
  copyRow(46, 50, "H");
  offers.mergeCells("A50:H50");
  offers.getRange("A46:H46").clear({ applyTo: "all" });
  moveRowsBottomUp(40, 44, 44, "E");
  offers.getRange("A40:E43").clear({ applyTo: "all" });
  moveRowsBottomUp(29, 37, 33, "I");
  offers.getRange("A29:I32").clear({ applyTo: "contents" });

  const fxRate = (offer) => {
    const value = procurement.fx[offer.currency];
    assert(Number.isFinite(value), `Missing reference FX for ${offer.currency}`);
    return value;
  };
  const buildOfferRow = (offer) => [
    offer.id, offer.bom, offer.sku, offer.qty, offer.packQty, null, offer.unit, offer.currency, fxRate(offer), null, null,
    procurement.pilotQty[offer.bom] ?? null, null, null, offer.evidence, offer.date, offer.region, offer.seller,
    offer.shipping ?? "unknown", offer.duty ?? "unknown", offer.warranty ?? "unknown", offer.notes, offer.url,
  ];
  const newOffers = procurement.offers.filter((offer) => ["O25", "O26", "O27", "O28"].includes(offer.id));
  assert.deepEqual(newOffers.map((offer) => offer.id), ["O25", "O26", "O27", "O28"]);
  for (let rowNo = 29; rowNo <= 32; rowNo++) copyRow(28, rowNo, "W");
  offers.getRange("A29:W32").values = newOffers.map(buildOfferRow);
  for (let rowNo = 29; rowNo <= 32; rowNo++) {
    offers.getRange(`F${rowNo}`).formulas = [[`=IF(OR(D${rowNo}="",E${rowNo}=""),"",ROUNDUP(D${rowNo}/E${rowNo},0))`]];
    offers.getRange(`J${rowNo}`).formulas = [[`=IF(OR(G${rowNo}="",I${rowNo}=""),"",G${rowNo}*I${rowNo})`]];
    offers.getRange(`K${rowNo}`).formulas = [[`=IF(OR(D${rowNo}="",E${rowNo}="",G${rowNo}="",I${rowNo}=""),"",F${rowNo}*G${rowNo}*I${rowNo})`]];
    offers.getRange(`M${rowNo}`).formulas = [[`=IF(OR(L${rowNo}="",E${rowNo}=""),"",ROUNDUP(L${rowNo}/E${rowNo},0))`]];
    offers.getRange(`N${rowNo}`).formulas = [[`=IF(OR(L${rowNo}="",G${rowNo}="",I${rowNo}=""),"",M${rowNo}*G${rowNo}*I${rowNo})`]];
  }

  const currentOffers = offers.getRange("A5:W28").values;
  const offerRowById = new Map(currentOffers.map((row, index) => [row[0], index + 5]));
  assert(offerRowById.has("O02"), "The existing O02 row must be mapped by offer ID");
  const currentO02 = procurement.offers.find((offer) => offer.id === "O02");
  const o02Row = offerRowById.get("O02");
  offers.getRange(`G${o02Row}:I${o02Row}`).values = [[currentO02.unit, currentO02.currency, fxRate(currentO02)]];
  offers.getRange(`O${o02Row}:R${o02Row}`).values = [[currentO02.evidence, currentO02.date, currentO02.region, currentO02.seller]];
  offers.getRange(`V${o02Row}:W${o02Row}`).values = [[currentO02.notes, currentO02.url]];

  const historyRows = procurement.historical.map((item) => [item.id, item.bom, item.region, item.sku, item.historicalPrice, item.currency, item.status, item.note, item.url]);
  assert.equal(historyRows.length, 9, "Historical table must retain eight existing entries and H09");
  copyRow(41, 42, "I");
  offers.getRange("A42:I42").values = [historyRows.find((row) => row[0] === "H09")];

  const auditRows = procurement.originalGapAudit.map((row) => [
    row.id, row.qty, row.evidence, row.currentStatus, row.priceTreatment, row.source || null,
    row.allowanceLowBYN ?? null, row.allowanceHighBYN ?? null,
  ]);
  assert.equal(auditRows.length, 18);
  const auditTitle = "Исходный аудит 18 строк: 28 активных ценовых ссылок и 11 текущих строк без цены. B09: предложение O25 включено; HPE 25 696 RUB сохранено как прежний CANDIDATE, предупреждение относится к актуальности самой цены. NET без дополнительного НДС, включённый НДС и неизвестные расходы отмечены отдельно; не цена заказа.";
  offers.getRange("A50").values = [[auditTitle]];
  offers.getRange("A51:H51").values = [originalGapAuditHeaders];
  offers.getRange("A52:H69").values = auditRows;

  const bomById = new Map(data.bom.map((item) => [item.id, item]));
  const equipmentValues = equipment.getRange("A5:N52").values;
  assert.equal(equipmentValues.length, 48, "Equipment identity map must cover the 48 existing rows");
  const equipmentRowById = new Map(equipmentValues.map((row, index) => [row[0], index + 5]));
  assert.equal(equipmentRowById.size, 48);
  const offerIndexFormula = (equipmentRow, offerColumn) => {
    const source = `'Предложения РФ РБ Китай'!$${offerColumn}$5:$${offerColumn}$32`;
    const ids = `'Предложения РФ РБ Китай'!$B$5:$B$32`;
    const match = `MATCH($A${equipmentRow},${ids},0)`;
    const lookup = `INDEX(${source},${match})`;
    return `=IFERROR(IF(${lookup}="","",${lookup}),"")`;
  };
  for (const id of ["B07", "B09", "B27", "B34", "B35"]) {
    const item = bomById.get(id);
    const rowNo = equipmentRowById.get(id);
    assert(item && rowNo, `Could not map equipment ${id} by BOM ID`);
    equipment.getRange(`L${rowNo}:N${rowNo}`).values = [[item.source ?? null, item.url ?? null, item.gate ?? null]];
    if (id !== "B07") {
      equipment.getRange(`F${rowNo}`).formulas = [[offerIndexFormula(rowNo, "K")]];
      equipment.getRange(`G${rowNo}`).formulas = [[offerIndexFormula(rowNo, "N")]];
      equipment.getRange(`H${rowNo}:I${rowNo}`).clear({ applyTo: "contents" });
    }
  }

  const sourceRows = newOffers.map((offer) => [
    offer.id, "Наблюдение H01 — справочная цена", offer.date, offer.region, offer.seller, offer.notes, offer.url,
  ]);
  const sourceRange = sources.getRange("A12:G76").values;
  const sourceRowById = new Map(sourceRange.map((row, index) => [row[0], index + 12]));
  const sourceO02Row = sourceRowById.get("O02");
  assert(sourceO02Row, "Current SourceRegister O02 row must be mapped by ID");
  sources.getRange(`A${sourceO02Row}:G${sourceO02Row}`).values = [[
    currentO02.id, "Наблюдение H01 — справочная цена", currentO02.date, currentO02.region, currentO02.seller, currentO02.notes, currentO02.url,
  ]];
  const sourceTable = sources.tables.items.find((table) => table.name === "SourceRegister");
  assert(sourceTable, "Existing SourceRegister table is required");
  sourceTable.rows.add(null, sourceRows);

  for (const target of captionTargets) workbook.worksheets.getItem(target.sheet).getRange(target.cell).values = [[target.value]];
  summary.getRange("D16").format.wrapText = true;
  summary.getRange("B15").values = [[11]];
  for (const id of ["B09", "B27", "B34", "B35"]) {
    const rowNo = equipmentRowById.get(id);
    assert.equal(equipment.getRange(`C${rowNo}`).values[0][0], bomById.get(id).class, `${id} equipment class must match the canonical BOM record`);
    assert.equal(bomById.get(id).class, "Основное оборудование", `${id} canonical class must remain the approved Russian category`);
  }

  const setTableFlags = (table) => { for (const [key, value] of Object.entries(tableFlags)) table[key] = value; };
  for (const [name, address] of [
    ["CurrentOffers", "A4:W32"],
    ["HistoricalOnly", "A33:I42"],
    ["PlatformAudit", "A44:E48"],
    ["OriginalGapAudit", "A51:H69"],
  ]) {
    if (name === "OriginalGapAudit") {
      offers.getRange("A51:H51").values = [["BOM ID", "Qty", "Original evidence", "Current status", "Price treatment", "Source", "Allowance low BYN", "Allowance high BYN"]];
    }
    const table = offers.tables.add(address, true, name);
    table.style = "TableStyleLight1";
    setTableFlags(table);
    if (name === "OriginalGapAudit") offers.getRange("A51:H51").values = [originalGapAuditHeaders];
  }

  await workbook.recalculate();
  const expectedTotals = procurement.totalsControl;
  const totals = {
    pricedNoSparesBYN: summary.getRange("B7").values[0][0],
    sparesBYN: summary.getRange("B8").values[0][0],
    pricedWithSparesBYN: summary.getRange("B9").values[0][0],
    allowancesLowBYN: summary.getRange("B10").values[0][0],
    allowancesHighBYN: summary.getRange("C10").values[0][0],
    planningLowBYN: summary.getRange("B11").values[0][0],
    planningHighBYN: summary.getRange("C11").values[0][0],
    pilotKnownBYN: summary.getRange("B12").values[0][0],
    pilotAllowLowBYN: summary.getRange("B13").values[0][0],
    pilotAllowHighBYN: summary.getRange("C13").values[0][0],
    pilotPlanLowBYN: summary.getRange("B14").values[0][0],
    pilotPlanHighBYN: summary.getRange("C14").values[0][0],
    mandatoryUnpricedLines: summary.getRange("B15").values[0][0],
  };
  const expectedDisplayed = {
    pricedNoSparesBYN: expectedTotals.pricedNoSparesBYN,
    sparesBYN: expectedTotals.pricedWithSparesBYN - expectedTotals.pricedNoSparesBYN,
    pricedWithSparesBYN: expectedTotals.pricedWithSparesBYN,
    allowancesLowBYN: expectedTotals.allowancesLowBYN,
    allowancesHighBYN: expectedTotals.allowancesHighBYN,
    planningLowBYN: expectedTotals.planningLowBYN,
    planningHighBYN: expectedTotals.planningHighBYN,
    pilotKnownBYN: expectedTotals.pilotKnownBYN,
    pilotAllowLowBYN: expectedTotals.pilotAllowLowBYN,
    pilotAllowHighBYN: expectedTotals.pilotAllowHighBYN,
    pilotPlanLowBYN: expectedTotals.pilotKnownBYN + expectedTotals.pilotAllowLowBYN,
    pilotPlanHighBYN: expectedTotals.pilotKnownBYN + expectedTotals.pilotAllowHighBYN,
    mandatoryUnpricedLines: expectedTotals.mandatoryUnpricedLines,
  };
  for (const [key, expected] of Object.entries(expectedDisplayed)) {
    assert(Number.isFinite(totals[key]) && Math.abs(totals[key] - expected) < 1e-8, `${key} mismatch: ${totals[key]} vs ${expected}`);
  }
  assert.equal(equipment.getRange("F5:F43").values.length, 39, "The base summary must continue to include all 39 mandatory equipment rows");
  assert.equal(equipment.getRange("G5:G43").values.length, 39, "The pilot summary must continue to include all 39 mandatory equipment rows");
  for (const id of ["B09", "B27", "B34", "B35"]) {
    const rowNo = equipmentRowById.get(id);
    assert.equal(equipment.getRange(`H${rowNo}:I${rowNo}`).values[0].filter((value) => value !== null && value !== "").length, 0, `${id} allowance must be blank, not zero`);
    assert.equal(equipment.getRange(`F${rowNo}`).values[0][0], bomById.get(id).knownFullBYN, `${id} full price must resolve by BOM ID`);
  }
  for (const id of ["B34", "B35"]) assert.equal(equipment.getRange(`G${equipmentRowById.get(id)}`).values[0][0], bomById.get(id).knownBenchBYN, `${id} pilot price must resolve by BOM ID`);
  const b32Row = equipmentRowById.get("B32");
  assert.equal(equipment.getRange(`F${b32Row}`).values[0][0], null, "B32 cable purchase amount must remain blank");
  assert.equal(equipment.getRange(`D${b32Row}`).values[0][0], 0, "B32 cable purchase quantity must remain zero");
  assert.deepEqual(offers.getRange("A4:A32").values.slice(1).map((row) => row[0]), procurement.offers.map((offer) => offer.id));
  assert.deepEqual(offers.getRange("A33:A42").values.slice(1).map((row) => row[0]), procurement.historical.map((item) => item.id));
  assert.deepEqual(offers.getRange("A52:A69").values.map((row) => row[0]), procurement.originalGapAudit.map((row) => row.id));
  assert.deepEqual(offers.getRange("A51:H51").values[0], originalGapAuditHeaders);
  assert.deepEqual(offers.getRange("A34:I34").values[0], historyRows.find((row) => row[0] === "H01"));
  assert.deepEqual(offers.getRange("A42:I42").values[0], historyRows.find((row) => row[0] === "H09"));
  assert.equal(offers.getRange("A50").values[0][0], auditTitle);
  assert.equal(sources.getRange("A12:G80").values.length, 69);
  assert.deepEqual(sources.getRange("A77:A80").values.map((row) => row[0]), ["O25", "O26", "O27", "O28"]);

  const formulaErrors = [];
  let formulaCount = 0;
  for (const name of sheetNames) {
    const used = workbook.worksheets.getItem(name).getUsedRange();
    if (!used) continue;
    for (const [rowIndex, row] of used.values.entries()) {
      for (const [columnIndex, value] of row.entries()) {
        if (typeof value === "string" && /^#(REF!|VALUE!|DIV\/0!|NAME\?|N\/A|NUM!|NULL!)/.test(value)) formulaErrors.push(`${name} r${rowIndex + 1}c${columnIndex + 1}=${value}`);
      }
    }
    formulaCount += used.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length;
  }
  assert.deepEqual(formulaErrors, [], `Formula errors after recalculation: ${formulaErrors.join(", ")}`);
  assert.equal(formulaCount, baselineFormulaCount + 28, "Expected 20 offer formulas and 8 BOM-ID lookup formulas over the 190 baseline formulas");

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(candidate);
  for (const [name, beforeHash] of Object.entries(inputHashes)) assert.equal(fileHash(await fs.readFile(name)), beforeHash, `${name} changed during local XLSX candidate authoring`);
  const candidateBytes = await fs.readFile(candidate);
  const candidateWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(candidate));
  const candidateNames = [];
  for (let i = 0; i < 8; i++) candidateNames.push(candidateWorkbook.worksheets.getItemAt(i).name);
  assert.deepEqual(candidateNames, data.sheet.tabs, "Candidate export changed workbook tabs");
  const candidateSummary = candidateWorkbook.worksheets.getItem("Сводка");
  for (const [key, cell] of Object.entries({
    pricedNoSparesBYN: "B7", sparesBYN: "B8", pricedWithSparesBYN: "B9", allowancesLowBYN: "B10", allowancesHighBYN: "C10",
    planningLowBYN: "B11", planningHighBYN: "C11", pilotKnownBYN: "B12", pilotAllowLowBYN: "B13", pilotAllowHighBYN: "C13",
    pilotPlanLowBYN: "B14", pilotPlanHighBYN: "C14", mandatoryUnpricedLines: "B15",
  })) assert(Math.abs(candidateSummary.getRange(cell).values[0][0] - expectedDisplayed[key]) < 1e-8, `Candidate reimport ${key} mismatch`);
  const candidateOffers = candidateWorkbook.worksheets.getItem("Предложения РФ РБ Китай");
  assert.deepEqual(candidateOffers.getRange("A4:A32").values.slice(1).map((row) => row[0]), procurement.offers.map((offer) => offer.id));
  assert.equal(candidateOffers.getRange("A50").values[0][0], auditTitle);
  const candidateFormulas = candidateNames.reduce((sum, name) => {
    const used = candidateWorkbook.worksheets.getItem(name).getUsedRange();
    return sum + (used?.formulas.flat().filter((value) => typeof value === "string" && value.startsWith("=")).length ?? 0);
  }, 0);
  assert.equal(candidateFormulas, formulaCount, "Candidate export changed the formula count");
  console.log(JSON.stringify({
    result: "CANDIDATE_READY_FOR_INDEPENDENT_FULL_GUARD",
    baselineSha256: originalSha256,
    candidateSha256: fileHash(candidateBytes),
    candidateBytes: candidateBytes.length,
    activeOffers: procurement.offers.length,
    uniqueBOMReferences: new Set(procurement.offers.map((offer) => offer.bom)).size,
    mandatoryUnpriced: procurement.unpriced.length,
    baselineFormulas: baselineFormulaCount,
    newOfferAndBOMLookupFormulas: formulaCount - baselineFormulaCount,
    totalFormulas: formulaCount,
    localTablesBeforeRebuild: allTables.length,
    totals,
    auditRows: auditRows.length,
    sourceRowsAdded: sourceRows.map((row) => row[0]),
  }, null, 2));
  process.exit(0);
}

if (process.argv.includes("--policy-refresh")) {
  const currentBytes = await fs.readFile(file);
  const currentSha256 = crypto.createHash("sha256").update(currentBytes).digest("hex").toUpperCase();
  assert.equal(currentSha256, "33C795ED1FA7D6CAC9B33525E15B04561A14835512162F836A0D51176A3EF2E4", "Unexpected XLSX state before scoped metadata correction retry");
  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  const tabs = [];
  for (let i = 0; i < 8; i++) tabs.push(workbook.worksheets.getItemAt(i).name);
  assert.deepEqual(tabs, data.sheet.tabs, "The existing 8-tab workbook changed before metadata refresh");
  const summary = workbook.worksheets.getItem("Сводка");
  const equipment = workbook.worksheets.getItem("Выбранное оборудование");
  const offers = workbook.worksheets.getItem("Предложения РФ РБ Китай");
  const sources = workbook.worksheets.getItem("Источники и курсы");
  const equipmentRows = equipment.getRange("A5:N52").values;
  assert.equal(equipmentRows.length, 48, "Equipment matrix must retain all 48 rows");
  const equipmentRowById = new Map(equipmentRows.map((row, index) => [row[0], { rowNo: index + 5, row }]));
  assert.deepEqual([...equipmentRowById.keys()].sort(), data.bom.map((item) => item.id).sort(), "Equipment BOM ID set changed");
  const allowedMetadataIds = new Set(["B02", "B03", "B08", "B09", "B44"]);
  const preRefreshMismatches = [];
  for (const item of data.bom) {
    const current = equipmentRowById.get(item.id).row;
    const expected = bomValues(item);
    for (let col = 0; col < 14; col++) {
      if (sameCell(current[col], expected[col])) continue;
      assert(allowedMetadataIds.has(item.id) && [11, 13].includes(col), `Unexpected workbook-data drift at ${item.id} column ${col + 1}`);
      preRefreshMismatches.push(`${item.id}:${col + 1}`);
    }
  }
  for (const id of allowedMetadataIds) {
    const item = data.bom.find((row) => row.id === id);
    const { rowNo } = equipmentRowById.get(id);
    assert(item, `Current workbook-data metadata missing for ${id}`);
    equipment.getRange(`C${rowNo}`).values = [[item.class]];
    equipment.getRange(`L${rowNo}:N${rowNo}`).values = [[item.source ?? null, item.url ?? null, item.gate ?? null]];
  }
  const offerRows = offers.getRange("A4:W28").values;
  const offerRowById = new Map(offerRows.map((row, index) => [row[0], index + 4]));
  assert.deepEqual(offerRows.slice(1).map((row) => row[0]).slice(-3), ["O22", "O23", "O24"]);
  const currentSourceValues = sources.getRange("A12:G76").values;
  const sourceRowById = new Map(currentSourceValues.map((row, index) => [row[0], index + 12]));
  const noteById = new Map(procurement.offers.filter((offer) => ["O04", "O05"].includes(offer.id)).map((offer) => [offer.id, offer]));
  const excludedExtras = "Исключено владельцем из расчёта; не 0";
  for (const id of ["O04", "O05"]) {
    const offer = noteById.get(id);
    const rowNo = offerRowById.get(id);
    const sourceRowNo = sourceRowById.get(id);
    assert(offer && rowNo && sourceRowNo, `Could not map ${id} by ID in existing Offers/SourceRegister tables`);
    assert.equal(offer.shipping, excludedExtras);
    assert.equal(offer.duty, excludedExtras);
    offers.getRange(`S${rowNo}:T${rowNo}`).values = [[offer.shipping, offer.duty]];
    offers.getRange(`V${rowNo}`).values = [[offer.notes]];
    sources.getRange(`F${sourceRowNo}`).values = [[offer.notes]];
  }
  const policyRowNo = sourceRowById.get("SRC-SEEED-POLICY");
  assert(policyRowNo, "Existing Seeed policy source row is missing");
  sources.getRange(`D${policyRowNo}`).values = [["Беларусь — подтверждённая страна установки и доставки"]];
  sources.getRange(`F${policyRowNo}`).values = [[seeedPolicyText]];
  for (const [id, type, date, region, vendor, note, url] of sourceRows) {
    const rowNo = sourceRowById.get(id);
    assert(rowNo, `Current source row missing for ${id}`);
    const existing = sources.getRange(`A${rowNo}:G${rowNo}`).values[0];
    assert.deepEqual([existing[0], existing[2], existing[4], existing[6]], [id, date, vendor, url], `Source identity changed for ${id}`);
    sources.getRange(`B${rowNo}`).values = [[type]];
    sources.getRange(`D${rowNo}`).values = [[region]];
    sources.getRange(`F${rowNo}`).values = [[note]];
  }
  const auditRows = procurement.originalGapAudit.map((row) => [
    row.id, row.qty, row.evidence, row.currentStatus, row.priceTreatment, row.source || null,
    row.allowanceLowBYN ?? null, row.allowanceHighBYN ?? null,
  ]);
  assert.equal(auditRows.length, 18, "Original gap audit must retain exactly 18 entries");
  offers.getRange("A47:H47").values = [originalGapAuditHeaders];
  offers.getRange("A48:H65").values = auditRows;
  summary.getRange("A2").values = [["Рабочая оценка в BYN, не заказ и не разрешение на монтаж. 24 справочные ценовые ссылки, включая O22–O24; неизвестные значения не считаются нулём. Страна установки и доставки — Беларусь (подтверждено). Китайские доставка, посредник, таможня и прочие расходы исключены по указанию владельца (не 0)."]];
  summary.getRange("D11").values = [["24 ссылки не являются твёрдыми заказами; 15 обязательных строк без цены. Неизвестное не ноль. Китайские дополнительные расходы исключены владельцем (не 0); расходы по другим регионам остаются unknown."]];
  summary.getRange("D16").values = [[summaryPolicyNote]];
  summary.getRange("D16").format.wrapText = true;
  equipment.getRange("A2").values = [[data.sheet.equipmentCaption]];
  offers.getRange("A2").values = [["24 текущие ценовые ссылки, не твёрдые заказы; неизвестные цены не равны нулю. O22–O24 — справочные; stale/OOS/403/0 не считаются ценой. Страна доставки — Беларусь. Для China-origin позиций дополнительные расходы исключены владельцем (не 0); другие регионы остаются unknown. Условия Seeed блокируют Беларусь/Россию; O04/O05 — только price references."]];
  await workbook.recalculate();
  const expectedTotals = procurement.totalsControl;
  const totals = {
    pricedNoSparesBYN: summary.getRange("B7").values[0][0], sparesBYN: summary.getRange("B8").values[0][0],
    pricedWithSparesBYN: summary.getRange("B9").values[0][0], allowancesLowBYN: summary.getRange("B10").values[0][0],
    allowancesHighBYN: summary.getRange("C10").values[0][0], planningLowBYN: summary.getRange("B11").values[0][0],
    planningHighBYN: summary.getRange("C11").values[0][0], pilotKnownBYN: summary.getRange("B12").values[0][0],
    pilotAllowLowBYN: summary.getRange("B13").values[0][0], pilotAllowHighBYN: summary.getRange("C13").values[0][0],
    mandatoryUnpricedLines: summary.getRange("B15").values[0][0],
  };
  for (const [key, actual] of Object.entries(totals)) {
    const expected = key === "sparesBYN" ? expectedTotals.pricedWithSparesBYN - expectedTotals.pricedNoSparesBYN : expectedTotals[key];
    assert(Math.abs(actual - expected) < 1e-8, `${key} changed during metadata-only refresh: ${actual} vs ${expected}`);
  }
  const formulaErrors = [];
  for (const name of tabs) {
    const sheet = workbook.worksheets.getItem(name);
    const used = sheet.getUsedRange();
    if (!used) continue;
    for (const [r, row] of used.values.entries()) for (const [c, value] of row.entries()) {
      if (typeof value === "string" && /^#(REF!|VALUE!|DIV\/0!|NAME\?|N\/A|NUM!|NULL!)/.test(value)) formulaErrors.push(`${name} r${r + 1}c${c + 1}=${value}`);
    }
  }
  assert.deepEqual(formulaErrors, [], `Formula error scan found: ${formulaErrors.join(", ")}`);
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(file);
  const finalBytes = await fs.readFile(file);
  const finalSha256 = crypto.createHash("sha256").update(finalBytes).digest("hex").toUpperCase();
  const finalWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  const finalSummary = finalWorkbook.worksheets.getItem("Сводка");
  const finalOffers = finalWorkbook.worksheets.getItem("Предложения РФ РБ Китай");
  const finalSources = finalWorkbook.worksheets.getItem("Источники и курсы");
  const finalEquipment = finalWorkbook.worksheets.getItem("Выбранное оборудование");
  const finalEquipmentRows = finalEquipment.getRange("A5:N52").values;
  assert.equal(finalEquipmentRows.length * 14, 672);
  const finalEquipmentById = new Map(finalEquipmentRows.map((row) => [row[0], row]));
  const postRefreshMismatches = [];
  for (const item of data.bom) {
    const actual = finalEquipmentById.get(item.id);
    assert(actual, `Exported Equipment row missing for ${item.id}`);
    const expected = bomValues(item);
    for (let col = 0; col < 14; col++) if (!sameCell(actual[col], expected[col])) postRefreshMismatches.push(`${item.id}:${col + 1}`);
  }
  assert.deepEqual(postRefreshMismatches, [], `Equipment matrix differs from current BOM metadata: ${postRefreshMismatches.join(", ")}`);
  for (const id of ["O04", "O05"]) {
    const rowNo = offerRowById.get(id);
    const offer = noteById.get(id);
    assert.deepEqual(finalOffers.getRange(`S${rowNo}:T${rowNo}`).values[0], [offer.shipping, offer.duty]);
    assert.equal(finalOffers.getRange(`V${rowNo}`).values[0][0], offer.notes);
  }
  assert.equal(finalSources.getRange(`D${policyRowNo}`).values[0][0], "Беларусь — подтверждённая страна установки и доставки");
  assert.equal(finalSummary.getRange("D16").values[0][0], summaryPolicyNote);
  assert.deepEqual(finalOffers.getRange("A47:H47").values[0], originalGapAuditHeaders);
  assert.deepEqual(finalOffers.getRange("A48:H65").values, auditRows);
  for (const [id, type, date, region, vendor, note, url] of sourceRows) {
    const rowNo = sourceRowById.get(id);
    assert.deepEqual(finalSources.getRange(`A${rowNo}:G${rowNo}`).values[0], [id, type, date, region, vendor, note, url]);
  }
  assert.equal(finalOffers.getRange("A26").values[0][0], "O22");
  assert.equal(finalOffers.getRange("A27").values[0][0], "O23");
  assert.equal(finalOffers.getRange("A28").values[0][0], "O24");
  const previews = [
    ["Сводка", "A1:D16", "preview-01.png"],
    ["Выбранное оборудование", "A1:G23", "preview-02.png"],
    ["Выбранное оборудование", "A1:N10", "preview-02-country-policy.png"],
    ["Выбранное оборудование", "L26:N28", "preview-02-candidate-gates.png"],
    ["Выбранное оборудование", "L42:N43", "preview-02-FBT4N-gate.png"],
    ["Предложения РФ РБ Китай", "A1:N28", "preview-03.png"],
    ["Предложения РФ РБ Китай", "A47:H65", "preview-03-audit.png"],
    ["Предложения РФ РБ Китай", "O4:W28", "preview-03-source-notes.png"],
    ["Источники и курсы", "A1:G76", "preview-08.png"],
  ];
  const previewStats = [];
  for (const [sheetName, range, name] of previews) {
    const image = await finalWorkbook.render({ sheetName, range, scale: 1, format: "png" });
    const bytes = new Uint8Array(await image.arrayBuffer());
    await fs.writeFile(name, bytes);
    previewStats.push({ name, bytes: bytes.length });
  }
  const fullInspect = await finalWorkbook.inspect({ kind: "workbook,sheet,table", maxChars: 8000000, tableMaxRows: 120, tableMaxCols: 30, tableMaxCellChars: 2000 });
  assert.equal(fullInspect.truncated, false, "XLSX inspect sidecar must include the full saved workbook");
  await fs.writeFile(`${file}.inspect.ndjson`, fullInspect.ndjson, "utf8");
  console.log(JSON.stringify({ result: "PASS", mode: "scoped G07 metadata correction", beforeSha256: currentSha256, finalSha256, xlsxBytes: finalBytes.length, totals, formulaErrors: 0, equipmentMatrixCellsCompared: 672, equipmentMatrixMismatches: postRefreshMismatches.length, allowedPreRefreshMetadataMismatches: preRefreshMismatches, originalGapAuditRows: auditRows.length, sourceRowsVerified: sourceRows.map((row) => row[0]), tabs: tabs.length, inspectSidecarBytes: Buffer.byteLength(fullInspect.ndjson), previews: previewStats }, null, 2));
  process.exit(0);
}

assert.equal(procurement.offers.length, 24, "Expected 24 active reference offers");
assert.equal(procurement.unpriced.length, 15, "Expected 15 mandatory unpriced lines");
assert.equal(procurement.originalGapAudit.length, 18, "Expected the 18-line original gap audit");
assert.deepEqual(procurement.offers.filter((o) => ["O22", "O23", "O24"].includes(o.id)).map((o) => o.id), ["O22", "O23", "O24"]);
assert.equal(procurement.unpriced.find((x) => x.id === "B09")?.allowanceLowBYN, 1000);
assert.equal(procurement.unpriced.find((x) => x.id === "B09")?.allowanceHighBYN, 2200);
assert.equal(data.bom.length, 48, "Frozen BOM must remain 48 lines");
assert.equal(data.scenarios.length, 42, "Frozen scenario model must remain 42 lines");
assert.equal(data.acceptance.length, 19, "Frozen physical acceptance list must remain 19 lines");
assert.equal(procurement.fx.GBP, 4.0131);
assert.equal(data.sheet.tabs.length, 8, "Native workbook scope remains 8 tabs");

const originalBytes = await fs.readFile(file);
const originalSha256 = crypto.createHash("sha256").update(originalBytes).digest("hex").toUpperCase();
assert.equal(originalSha256, expectedBaselineSha256, "Local workbook changed since the verified prewrite baseline");
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
const summary = workbook.worksheets.getItem("Сводка");
const equipment = workbook.worksheets.getItem("Выбранное оборудование");
const offers = workbook.worksheets.getItem("Предложения РФ РБ Китай");
const sources = workbook.worksheets.getItem("Источники и курсы");
const existingSheets = [];
for (let i = 0; i < 8; i++) existingSheets.push(workbook.worksheets.getItemAt(i).name);
assert.deepEqual(existingSheets, data.sheet.tabs, "Workbook tab names/order differ from the frozen 8-tab baseline");

const offerTables = new Map(offers.tables.items.map((table) => [table.name, table]));
for (const name of ["CurrentOffers", "HistoricalOnly", "PlatformAudit"]) assert(offerTables.has(name), `Missing existing table ${name}`);
const originalStyles = Object.fromEntries(["CurrentOffers", "HistoricalOnly", "PlatformAudit"].map((name) => [name, offerTables.get(name).style]));
assert.deepEqual(originalStyles, { CurrentOffers: "TableStyleLight1", HistoricalOnly: "TableStyleLight1", PlatformAudit: "TableStyleLight1" });
const fxTable = sources.tables.items.find((table) => table.name === "FxRates");
const sourceTable = sources.tables.items.find((table) => table.name === "SourceRegister");
assert(fxTable && sourceTable, "Existing FX and source-register tables must be present");

const historyValues = offers.getRange("A26:I34").values;
const historyFormulas = offers.getRange("A26:I34").formulas;
const platformValues = offers.getRange("A37:E41").values;
const platformFormulas = offers.getRange("A37:E41").formulas;
assert(historyFormulas.flat().every((v) => !v), "Historical-only range unexpectedly contains formulas");
assert(platformFormulas.flat().every((v) => !v), "Platform audit unexpectedly contains formulas");
assert.deepEqual(historyValues[0][0], "ID");
assert.deepEqual(platformValues[0][0], "Площадка");

const equipmentValuesBefore = equipment.getRange("A4:N52").values;
const equipmentRows = new Map(equipmentValuesBefore.map((row, i) => [row[0], { rowNo: 4 + i, values: row }]));
assert(equipmentRows.has("B32"), "Included cable B32 must remain present");
const b32Before = equipmentRows.get("B32").values;
assert.equal(b32Before[3], 0, "B32 purchase quantity must remain zero");
assert(b32Before.slice(5, 11).every((value) => value === null || value === ""), "B32 money fields must remain blank");
for (const id of ["B08", "B30", "B44", "B09", "B02", "B03", "B04"]) assert(equipmentRows.has(id), `Missing frozen BOM row ${id}`);

const blank = (values) => values.flat().every((value) => value === null || value === "");
assert(blank(offers.getRange("A46:H65").values), "Original-gap audit destination is not empty; stop to protect existing content");
assert(blank(sources.getRange("A73:G76").values), "Source-register append area is not empty; stop to protect existing content");
assert(blank(sources.getRange("A10:E10").values), "GBP FX append row is not empty; stop to protect existing content");
const physicalStatuses = workbook.worksheets.getItem("Внедрение и приёмка").getRange("D12:D30").values.flat();
assert.equal(physicalStatuses.length, 19);
assert(physicalStatuses.every((value) => value === "Не проводилось"), "Physical acceptance status changed from the frozen baseline");

// First mutation was marked once on the original run; recovery attempts skip the marker.
if (!process.argv.includes("--resume-after-marker")) {
  execFileSync(process.execPath, [marker, "--operation-kind", "edit", "--expected-output-count", "1", "--output-format", "xlsx"], { stdio: "inherit" });
}

// Keep the existing offer, history, and marketplace evidence tables and style while moving only their ranges.
for (const name of ["CurrentOffers", "HistoricalOnly", "PlatformAudit"]) offerTables.get(name).delete();
offers.getRange("A26:W37").clear({ applyTo: "contents" });
offers.getRange("A37:W44").clear({ applyTo: "contents" });
offers.getRange("A29:I37").values = historyValues;
offers.getRange("A40:E44").values = platformValues;
for (const row of [26, 27, 28]) offers.getRange("A25:W25").copyTo(offers.getRange(`A${row}:W${row}`), "all");

const fxRate = (offer) => {
  const value = procurement.fx[offer.currency];
  assert(Number.isFinite(value), `No FX rate for ${offer.currency}`);
  return value;
};
const buildOfferRow = (offer) => [
  offer.id, offer.bom, offer.sku, offer.qty, offer.packQty, null, offer.unit, offer.currency, fxRate(offer), null, null,
  procurement.pilotQty[offer.bom] ?? null, null, null, offer.evidence, offer.date, offer.region, offer.seller,
  offer.shipping ?? "unknown", offer.duty ?? "unknown", offer.warranty ?? "unknown", offer.notes, offer.url,
];
const newOffers = procurement.offers.filter((offer) => ["O22", "O23", "O24"].includes(offer.id));
const newRows = newOffers.map(buildOfferRow);
assert(newRows.every((row) => row.length === 23), "Offer table rows must match A:W");
offers.getRange("A26:W28").values = newRows;
for (const [offset, rowNo] of [26, 27, 28].entries()) {
  offers.getRange(`F${rowNo}`).formulas = [[`=IF(OR(D${rowNo}="",E${rowNo}=""),"",ROUNDUP(D${rowNo}/E${rowNo},0))`]];
  offers.getRange(`J${rowNo}`).formulas = [[`=IF(OR(G${rowNo}="",I${rowNo}=""),"",G${rowNo}*I${rowNo})`]];
  offers.getRange(`K${rowNo}`).formulas = [[`=IF(OR(D${rowNo}="",E${rowNo}="",G${rowNo}="",I${rowNo}=""),"",F${rowNo}*G${rowNo}*I${rowNo})`]];
  offers.getRange(`M${rowNo}`).formulas = [[`=IF(OR(L${rowNo}="",E${rowNo}=""),"",ROUNDUP(L${rowNo}/E${rowNo},0))`]];
  offers.getRange(`N${rowNo}`).formulas = [[`=IF(OR(L${rowNo}="",G${rowNo}="",I${rowNo}=""),"",M${rowNo}*G${rowNo}*I${rowNo})`]];
}

// Replace only the three accepted reference rows' former allowance treatment; B09 remains an unpriced candidate.
const bomById = new Map(data.bom.map((item) => [item.id, item]));
const offerBodyBefore = offers.getRange("A4:W25").values;
for (const offerId of ["O04", "O05"]) {
  const sourceOffer = procurement.offers.find((offer) => offer.id === offerId);
  const rowNo = 4 + offerBodyBefore.findIndex((row, i) => i > 0 && row[0] === offerId);
  assert(rowNo >= 5 && sourceOffer, `Could not map ${offerId} to the existing offers range`);
  offers.getRange(`V${rowNo}`).values = [[sourceOffer.notes]];
}
const equipmentValueMap = new Map(equipmentValuesBefore.map((row, i) => [row[0], { rowNo: 4 + i, row }]));
const refreshBomRow = (id) => {
  const item = bomById.get(id);
  const found = equipmentValueMap.get(id);
  assert(item && found, `Could not map BOM ${id} by its ID`);
  const rowNo = found.rowNo;
  equipment.getRange(`C${rowNo}`).values = [[item.class]];
  if (["B08", "B09", "B30", "B44"].includes(id)) {
    equipment.getRange(`F${rowNo}:K${rowNo}`).values = [[
      item.knownFullBYN ?? null, item.knownBenchBYN ?? null, item.allowanceLowBYN ?? null,
      item.allowanceHighBYN ?? null, item.benchAllowanceLowBYN ?? null, item.benchAllowanceHighBYN ?? null,
    ]];
  }
  equipment.getRange(`L${rowNo}:N${rowNo}`).values = [[item.source ?? null, item.url ?? null, item.gate ?? null]];
};
for (const id of ["B02", "B03", "B04", "B08", "B09", "B30", "B44"]) refreshBomRow(id);
assert.deepEqual(equipment.getRange(`A${equipmentValueMap.get("B32").rowNo}:N${equipmentValueMap.get("B32").rowNo}`).values[0], b32Before, "B32 changed unexpectedly");

summary.getRange("B7").formulas = [["=SUM('Выбранное оборудование'!F5:F43)"]];
summary.getRange("B12").formulas = [["=SUM('Выбранное оборудование'!G5:G43)"]];
summary.getRange("B15").values = [[15]];
summary.getRange("D11").values = [["Справочные цены; O22–O24 не являются твёрдыми заказами. 15 обязательных строк остаются без цены; доставка и налоги не включены."]];
  summary.getRange("D16").values = [[summaryPolicyNote]];
summary.getRange("D16").format.wrapText = true;
summary.getRange("A2").values = [["Рабочая оценка в BYN, не заказ и не разрешение на монтаж. 24 справочные ценовые ссылки, включая O22–O24; неизвестные значения не считаются нулём. Страна установки и доставки — Беларусь (подтверждено). Китайские доставка, посредник, таможня и прочие расходы исключены по указанию владельца (не 0)."]];
equipment.getRange("A2").values = [[data.sheet.equipmentCaption]];
offers.getRange("A2").values = [["24 текущие ценовые ссылки, не твёрдые заказы; неизвестные цены не равны нулю. O22–O24 — справочные; stale/OOS/403/0 не считаются ценой. Страна доставки — Беларусь. Для China-origin позиций дополнительные расходы исключены владельцем (не 0); другие регионы остаются unknown. Условия Seeed блокируют Беларусь/Россию; O04/O05 — только price references."]];

const offerStyle = originalStyles.CurrentOffers;
const historyStyle = originalStyles.HistoricalOnly;
const platformStyle = originalStyles.PlatformAudit;
for (const [name, address, style] of [
  ["CurrentOffers", "A4:W28", offerStyle],
  ["HistoricalOnly", "A29:I37", historyStyle],
  ["PlatformAudit", "A40:E44", platformStyle],
]) {
  const table = offers.tables.add(address, true, name);
  table.style = style;
}

const auditTitle = "Исходный аудит 18 строк: 24 ссылок / 15 текущих обязательных строк без цены; O22–O24 только справочные. Candidate, stale, OOS, 403 и 0 остаются неценовыми наблюдениями.";
offers.getRange("A46:H46").values = [[auditTitle, null, null, null, null, null, null, null]];
offers.getRange("A46:H46").format.fill = "#D9EAF7";
offers.getRange("A46:H46").format.font = { bold: true, color: "#1F4E78" };
offers.getRange("A46:H46").format.wrapText = true;
offers.getRange("A46:H46").format.rowHeight = 36;
const auditRows = procurement.originalGapAudit.map((row) => [
  row.id, row.qty, row.evidence, row.currentStatus, row.priceTreatment, row.source || null,
  row.allowanceLowBYN ?? null, row.allowanceHighBYN ?? null,
]);
offers.getRange("A47:H47").values = [originalGapAuditHeaders];
offers.getRange("A48:H65").values = auditRows;
const gapAuditTable = offers.tables.add("A47:H65", true, "OriginalGapAudit");
gapAuditTable.style = "TableStyleLight1";

const existingSourceValues = sources.getRange("A12:G72").values;
const sourceRowById = new Map(existingSourceValues.map((row, index) => [row[0], 12 + index]));
for (const id of ["O04", "O05"]) {
  const rowNo = sourceRowById.get(id);
  const offer = procurement.offers.find((item) => item.id === id);
  assert(rowNo && offer, `Source-register metadata row missing for ${id}`);
  sources.getRange(`F${rowNo}`).values = [[offer.notes]];
}
sourceTable.rows.add(null, sourceRows);
fxTable.rows.add(null, [["GBP", 4.0131, "BYN за 1 единицу", "2026-10-19", procurement.fxSource]]);

await workbook.recalculate();
const expectedTotals = procurement.totalsControl;
const actualTotals = {
  pricedNoSparesBYN: summary.getRange("B7").values[0][0],
  sparesBYN: summary.getRange("B8").values[0][0],
  pricedWithSparesBYN: summary.getRange("B9").values[0][0],
  allowancesLowBYN: summary.getRange("B10").values[0][0],
  allowancesHighBYN: summary.getRange("C10").values[0][0],
  planningLowBYN: summary.getRange("B11").values[0][0],
  planningHighBYN: summary.getRange("C11").values[0][0],
  pilotKnownBYN: summary.getRange("B12").values[0][0],
  pilotAllowLowBYN: summary.getRange("B13").values[0][0],
  pilotAllowHighBYN: summary.getRange("C13").values[0][0],
  mandatoryUnpricedLines: summary.getRange("B15").values[0][0],
};
const assertClose = (actual, expected, label) => assert(Math.abs(actual - expected) < 1e-8, `${label}: expected ${expected}, got ${actual}`);
for (const [key, expected] of Object.entries({
  pricedNoSparesBYN: expectedTotals.pricedNoSparesBYN,
  sparesBYN: expectedTotals.pricedWithSparesBYN - expectedTotals.pricedNoSparesBYN,
  pricedWithSparesBYN: expectedTotals.pricedWithSparesBYN,
  allowancesLowBYN: expectedTotals.allowancesLowBYN,
  allowancesHighBYN: expectedTotals.allowancesHighBYN,
  planningLowBYN: expectedTotals.planningLowBYN,
  planningHighBYN: expectedTotals.planningHighBYN,
  pilotKnownBYN: expectedTotals.pilotKnownBYN,
  pilotAllowLowBYN: expectedTotals.pilotAllowLowBYN,
  pilotAllowHighBYN: expectedTotals.pilotAllowHighBYN,
  mandatoryUnpricedLines: expectedTotals.mandatoryUnpricedLines,
})) assertClose(actualTotals[key], expected, key);

const offerValues = offers.getRange("A4:W28").values;
const offerIds = offerValues.slice(1).map((row) => row[0]);
assert.equal(offerIds.length, 24);
assert.equal(new Set(offerIds).size, 24);
assert.deepEqual(offerIds.slice(-3), ["O22", "O23", "O24"]);
for (const [i, offer] of newOffers.entries()) {
  const row = offerValues[22 + i];
  assert.equal(row[0], offer.id);
  assert.equal(row[1], offer.bom);
  assert.equal(row[6], offer.unit);
  assert.equal(row[7], offer.currency);
  assert.equal(row[8], fxRate(offer));
  assert.equal(row[14], offer.evidence);
  assert.equal(row[18], "unknown");
}
const fxValues = sources.getRange("A4:E10").values;
assert.deepEqual(fxValues[6], ["GBP", 4.0131, "BYN за 1 единицу", "2026-10-19", procurement.fxSource]);
const sourceValues = sources.getRange("A12:G76").values;
assert.equal(sourceValues.length, 65);
assert.deepEqual(sourceValues.slice(-4).map((row) => row[0]), ["O22", "O23", "O24", "SRC-SEEED-POLICY"]);
assert.deepEqual(offers.getRange("A29:I37").values, historyValues, "Historical rows were not preserved exactly");
assert.deepEqual(offers.getRange("A40:E44").values, platformValues, "Marketplace audit rows were not preserved exactly");
assert.equal(offers.getRange("A30").values[0][0], "H01");
assert.equal(offers.getRange("A47:H65").values.length, 19);
assert.equal(offers.getRange("A48:A65").values.length, 18);
assert.deepEqual(offers.getRange("A48:A65").values.map((r) => r[0]), procurement.originalGapAudit.map((r) => r.id));

const formulaErrors = [];
for (const name of existingSheets) {
  const sheet = workbook.worksheets.getItem(name);
  const used = sheet.getUsedRange();
  if (!used) continue;
  for (const [r, row] of used.values.entries()) {
    for (const [c, value] of row.entries()) if (typeof value === "string" && /^#(REF!|VALUE!|DIV\/0!|NAME\?|N\/A|NUM!|NULL!)/.test(value)) formulaErrors.push(`${name} r${r + 1}c${c + 1}=${value}`);
  }
}
assert.deepEqual(formulaErrors, [], `Formula error scan found: ${formulaErrors.join(", ")}`);

const exportBlob = await SpreadsheetFile.exportXlsx(workbook);
await exportBlob.save(file);
const outputBytes = await fs.readFile(file);
const outputSha256 = crypto.createHash("sha256").update(outputBytes).digest("hex").toUpperCase();
const finalWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
const finalSummary = finalWorkbook.worksheets.getItem("Сводка");
for (const [key, cell] of Object.entries({
  pricedNoSparesBYN: "B7", sparesBYN: "B8", pricedWithSparesBYN: "B9", allowancesLowBYN: "B10", allowancesHighBYN: "C10",
  planningLowBYN: "B11", planningHighBYN: "C11", pilotKnownBYN: "B12", pilotAllowLowBYN: "B13", pilotAllowHighBYN: "C13",
})) assertClose(finalSummary.getRange(cell).values[0][0], actualTotals[key], `reimport ${key}`);
const finalSheetNames = [];
for (let i = 0; i < 8; i++) finalSheetNames.push(finalWorkbook.worksheets.getItemAt(i).name);
assert.deepEqual(finalSheetNames, data.sheet.tabs, "XLSX export changed sheet count/order");
const finalOffers = finalWorkbook.worksheets.getItem("Предложения РФ РБ Китай");
assert.deepEqual(finalOffers.getRange("A29:I37").values, historyValues);
assert.deepEqual(finalOffers.getRange("A40:E44").values, platformValues);
assert.equal(finalOffers.getRange("A26").values[0][0], "O22");
assert.equal(finalOffers.getRange("A27").values[0][0], "O23");
assert.equal(finalOffers.getRange("A28").values[0][0], "O24");

const previewSpecs = [
  ["Сводка", "A1:D21", "preview-01.png"],
  ["Выбранное оборудование", "A1:G23", "preview-02.png"],
  ["Выбранное оборудование", "A1:N10", "preview-02-country-policy.png"],
  ["Выбранное оборудование", "L26:N28", "preview-02-candidate-gates.png"],
  ["Выбранное оборудование", "L42:N43", "preview-02-FBT4N-gate.png"],
  ["Выбранное оборудование", "A23:K52", "preview-02-allowances.png"],
  ["Предложения РФ РБ Китай", "A1:N28", "preview-03.png"],
  ["Предложения РФ РБ Китай", "A29:I65", "preview-03-audit.png"],
  ["Предложения РФ РБ Китай", "O4:W28", "preview-03-source-notes.png"],
  ["Источники и курсы", "A1:G76", "preview-08.png"],
];
const previewStats = [];
for (const [sheetName, range, name] of previewSpecs) {
  const rendered = await finalWorkbook.render({ sheetName, range, scale: 1, format: "png" });
  const bytes = new Uint8Array(await rendered.arrayBuffer());
  await fs.writeFile(name, bytes);
  previewStats.push({ sheet: sheetName, range, file: path.join(dir, name), bytes: bytes.length });
}

console.log(JSON.stringify({
  result: "PASS",
  marker: "called once immediately before XLSX authoring",
  baselineSha256: originalSha256,
  outputSha256,
  outputBytes: outputBytes.length,
  sheets: finalSheetNames.length,
  offers: offerIds.length,
  unpriced: procurement.unpriced.length,
  b09: { price: null, allowanceLowBYN: 1000, allowanceHighBYN: 2200, candidateRetained: true },
  originalGapAuditRows: 18,
  historyPreserved: true,
  marketplaceAuditPreserved: true,
  formulaErrors: formulaErrors.length,
  totals: actualTotals,
  previews: previewStats,
}, null, 2));
