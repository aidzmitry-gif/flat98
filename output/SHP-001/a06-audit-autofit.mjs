#!/usr/bin/env node
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

for (const fileName of ["procurement-data.json", "workbook-data.json", "qa-result.json"]) JSON.parse(await fs.readFile(fileName, "utf8"));
const file = "SHP-001-procurement.xlsx";
const bytes = await fs.readFile(file);
const beforeSha256 = crypto.createHash("sha256").update(bytes).digest("hex").toUpperCase();
assert.equal(beforeSha256, "36719A8E519E143AE2DF127FAC41509374F9709BDE0A1332FD32E722FF98BD4C");
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
const offers = workbook.worksheets.getItem("Предложения РФ РБ Китай");
assert.equal(offers.getRange("A48:A65").values.length, 18);
offers.getRange("A48:H65").format.wrapText = true;
offers.getRange("A48:H65").format.autofitRows();
await workbook.recalculate();
const out = await SpreadsheetFile.exportXlsx(workbook);
await out.save(file);
const after = await fs.readFile(file);
const finalSha256 = crypto.createHash("sha256").update(after).digest("hex").toUpperCase();
const finalWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
const preview = await finalWorkbook.render({ sheetName: "Предложения РФ РБ Китай", range: "A29:I65", scale: 1, format: "png" });
const previewBytes = new Uint8Array(await preview.arrayBuffer());
await fs.writeFile("preview-03-audit.png", previewBytes);
console.log(JSON.stringify({ result: "PASS", beforeSha256, finalSha256, xlsxBytes: after.length, auditRows: 18, previewBytes: previewBytes.length }, null, 2));
