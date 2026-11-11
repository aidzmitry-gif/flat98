#!/usr/bin/env node
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const dir = path.dirname(fileURLToPath(import.meta.url));
process.chdir(dir);
const procurement = JSON.parse(await fs.readFile("procurement-data.json", "utf8"));
const workbookData = JSON.parse(await fs.readFile("workbook-data.json", "utf8"));
const qaData = JSON.parse(await fs.readFile("qa-result.json", "utf8"));
assert.equal(procurement.originalGapAudit.length, 18);
assert.equal(workbookData.bom.length, 48);
assert.equal(qaData.tokens, null);

const file = "SHP-001-procurement.xlsx";
const expectedSha256 = "1388A28FAAEA902275A476880B18A69CC57D9221BBA002139BCFA80830E9A689";
const before = await fs.readFile(file);
const beforeSha256 = crypto.createHash("sha256").update(before).digest("hex").toUpperCase();
assert.equal(beforeSha256, expectedSha256, "Unexpected workbook state before visual repair");
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
const offers = workbook.worksheets.getItem("Предложения РФ РБ Китай");
assert(offers.tables.items.some((table) => table.name === "OriginalGapAudit"));
assert.equal(offers.getRange("A47").values[0][0], "BOM ID");
assert.equal(offers.getRange("A48:A65").values.length, 18);

const auditTitle = "Исходный аудит 18 строк: 24 ценовые ссылки / 15 текущих обязательных строк без цены; O22–O24 только справочные. Candidate, stale, OOS, 403 и 0 остаются неценовыми наблюдениями.";
const titleRange = offers.getRange("A46:H46");
titleRange.merge();
titleRange.values = [[auditTitle]];
titleRange.format.wrapText = true;
titleRange.format.verticalAlignment = "center";
titleRange.format.rowHeight = 32;
offers.getRange("A47:H47").format.wrapText = true;
offers.getRange("A47:H47").format.rowHeight = 32;
offers.getRange("A48:H65").format.wrapText = true;
offers.getRange("A48:H65").format.verticalAlignment = "center";
offers.getRange("A48:H65").format.rowHeight = 56;

await workbook.recalculate();
const summary = workbook.worksheets.getItem("Сводка");
assert(Math.abs(summary.getRange("B7").values[0][0] - procurement.totalsControl.pricedNoSparesBYN) < 1e-8);
assert.equal(summary.getRange("B15").values[0][0], 15);
const out = await SpreadsheetFile.exportXlsx(workbook);
await out.save(file);
const finalBytes = await fs.readFile(file);
const finalSha256 = crypto.createHash("sha256").update(finalBytes).digest("hex").toUpperCase();
const finalWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
const finalOffers = finalWorkbook.worksheets.getItem("Предложения РФ РБ Китай");
assert.equal(finalOffers.getRange("A46").values[0][0], auditTitle);
assert.equal(finalOffers.getRange("A48:A65").values.length, 18);
const preview = await finalWorkbook.render({ sheetName: "Предложения РФ РБ Китай", range: "A29:I65", scale: 1, format: "png" });
const previewBytes = new Uint8Array(await preview.arrayBuffer());
await fs.writeFile("preview-03-audit.png", previewBytes);
console.log(JSON.stringify({ result: "PASS", beforeSha256, finalSha256, xlsxBytes: finalBytes.length, auditTitleMerged: true, auditRows: 18, previewBytes: previewBytes.length }, null, 2));
