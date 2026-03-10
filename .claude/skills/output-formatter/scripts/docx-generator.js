#!/usr/bin/env node
/**
 * docx-generator.js
 * Generates .docx files from markdown content with legal document formatting.
 *
 * Usage: node docx-generator.js <input.md> <output.docx> [--lang ko|en] [--jurisdiction korea|us|uk|intl]
 *
 * Prerequisites: npm install docx fs-extra
 */

const fs = require("fs");
const path = require("path");

// Check for docx module
let docx;
try {
  docx = require("docx");
} catch {
  console.error(
    "Error: 'docx' package not installed. Run: npm install docx"
  );
  process.exit(1);
}

const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  AlignmentType,
  PageSize,
  convertMillimetersToTwip,
  convertInchesToTwip,
} = docx;

// Page setup configurations
const PAGE_CONFIGS = {
  "ko-korea": {
    size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297) },
    margins: {
      top: convertMillimetersToTwip(20),
      bottom: convertMillimetersToTwip(15),
      left: convertMillimetersToTwip(20),
      right: convertMillimetersToTwip(20),
    },
    bodyFont: "바탕체",
    headingFont: "맑은 고딕",
    fontSize: 24, // half-points (12pt)
  },
  "en-us": {
    size: { width: convertInchesToTwip(8.5), height: convertInchesToTwip(11) },
    margins: {
      top: convertInchesToTwip(1),
      bottom: convertInchesToTwip(1),
      left: convertInchesToTwip(1),
      right: convertInchesToTwip(1),
    },
    bodyFont: "Times New Roman",
    headingFont: "Times New Roman",
    fontSize: 24,
  },
  "en-uk": {
    size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297) },
    margins: {
      top: convertMillimetersToTwip(25.4),
      bottom: convertMillimetersToTwip(25.4),
      left: convertMillimetersToTwip(25.4),
      right: convertMillimetersToTwip(25.4),
    },
    bodyFont: "Times New Roman",
    headingFont: "Arial",
    fontSize: 24,
  },
  "en-intl": {
    size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297) },
    margins: {
      top: convertMillimetersToTwip(25),
      bottom: convertMillimetersToTwip(25),
      left: convertMillimetersToTwip(25),
      right: convertMillimetersToTwip(25),
    },
    bodyFont: "Times New Roman",
    headingFont: "Arial",
    fontSize: 24,
  },
};

function getConfigKey(lang, jurisdiction) {
  if (lang === "ko") return "ko-korea";
  if (jurisdiction === "us") return "en-us";
  if (jurisdiction === "uk") return "en-uk";
  return "en-intl";
}

function parseMarkdownLine(line, config) {
  // Heading detection
  const h1Match = line.match(/^# (.+)/);
  if (h1Match) {
    return new Paragraph({
      text: h1Match[1],
      heading: HeadingLevel.HEADING_1,
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
      run: { font: config.headingFont, size: 32, bold: true },
    });
  }

  const h2Match = line.match(/^## (.+)/);
  if (h2Match) {
    return new Paragraph({
      text: h2Match[1],
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 200, after: 100 },
      run: { font: config.headingFont, size: 28, bold: true },
    });
  }

  const h3Match = line.match(/^### (.+)/);
  if (h3Match) {
    return new Paragraph({
      text: h3Match[1],
      heading: HeadingLevel.HEADING_3,
      spacing: { before: 150, after: 80 },
      run: { font: config.headingFont, size: 24, bold: true },
    });
  }

  // Empty line
  if (line.trim() === "") {
    return new Paragraph({ text: "", spacing: { after: 0 } });
  }

  // Regular paragraph
  return new Paragraph({
    children: [
      new TextRun({
        text: line,
        font: config.bodyFont,
        size: config.fontSize,
      }),
    ],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 120, line: 360 },
  });
}

async function generateDocx(inputPath, outputPath, lang, jurisdiction) {
  const configKey = getConfigKey(lang, jurisdiction);
  const config = PAGE_CONFIGS[configKey];

  const content = fs.readFileSync(inputPath, "utf-8");
  const lines = content.split("\n");

  const paragraphs = lines.map((line) => parseMarkdownLine(line, config));

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            size: config.size,
            margin: config.margins,
          },
        },
        children: paragraphs,
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`Document generated: ${outputPath}`);
}

// CLI
const args = process.argv.slice(2);
if (args.length < 2) {
  console.error("Usage: node docx-generator.js <input.md> <output.docx> [--lang ko|en] [--jurisdiction korea|us|uk|intl]");
  process.exit(1);
}

const inputPath = args[0];
const outputPath = args[1];
const langIdx = args.indexOf("--lang");
const lang = langIdx !== -1 ? args[langIdx + 1] : "ko";
const jurIdx = args.indexOf("--jurisdiction");
const jurisdiction = jurIdx !== -1 ? args[jurIdx + 1] : "korea";

generateDocx(inputPath, outputPath, lang, jurisdiction).catch((err) => {
  console.error("Error generating document:", err.message);
  process.exit(1);
});
