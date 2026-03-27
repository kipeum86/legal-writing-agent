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
const { spawnSync } = require("child_process");

// Check for docx module
let docx;
let usePythonFallback = false;
try {
  docx = require("docx");
} catch {
  usePythonFallback = true;
}

if (usePythonFallback) {
  const fallbackScript = path.join(__dirname, "docx-generator.py");
  const result = spawnSync("python3", [fallbackScript, ...process.argv.slice(2)], {
    stdio: "inherit",
  });

  if (result.error) {
    console.error(
      "Error: neither the Node 'docx' package nor the Python fallback is available.",
    );
    console.error(`Underlying error: ${result.error.message}`);
    process.exit(1);
  }

  process.exit(result.status ?? 0);
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
  "ko-korea-opinion": {
    size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297) },
    margins: {
      top: convertMillimetersToTwip(25.4),
      bottom: convertMillimetersToTwip(25.4),
      left: convertMillimetersToTwip(25.4),
      right: convertMillimetersToTwip(25.4),
    },
    bodyFont: "맑은 고딕",
    headingFont: "맑은 고딕",
    fontSize: 22, // 11pt
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

function getConfigKey(lang, jurisdiction, documentType) {
  if (lang === "ko") {
    if (["advisory", "legal-opinion", "legal-review-opinion", "client-memorandum"].includes(documentType)) {
      return "ko-korea-opinion";
    }
    return "ko-korea";
  }
  if (jurisdiction === "us") return "en-us";
  if (jurisdiction === "uk") return "en-uk";
  return "en-intl";
}

function parseMarkdownLine(line, config) {
  // Heading detection
  const h1Match = line.match(/^# (.+)/);
  if (h1Match) {
    return new Paragraph({
      children: [
        new TextRun({
          text: h1Match[1],
          font: config.headingFont,
          size: 32,
          bold: true,
        }),
      ],
      heading: HeadingLevel.HEADING_1,
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
    });
  }

  const h2Match = line.match(/^## (.+)/);
  if (h2Match) {
    return new Paragraph({
      children: [
        new TextRun({
          text: h2Match[1],
          font: config.headingFont,
          size: 28,
          bold: true,
        }),
      ],
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 200, after: 100 },
    });
  }

  const h3Match = line.match(/^### (.+)/);
  if (h3Match) {
    return new Paragraph({
      children: [
        new TextRun({
          text: h3Match[1],
          font: config.headingFont,
          size: 24,
          bold: true,
        }),
      ],
      heading: HeadingLevel.HEADING_3,
      spacing: { before: 150, after: 80 },
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

async function generateDocx(inputPath, outputPath, lang, jurisdiction, documentType) {
  const configKey = getConfigKey(lang, jurisdiction, documentType);
  const config = PAGE_CONFIGS[configKey];

  if (!fs.existsSync(inputPath)) {
    throw new Error(`Input file not found: ${inputPath}`);
  }

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

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
const docTypeIdx = args.indexOf("--document-type");
const documentType = docTypeIdx !== -1 ? args[docTypeIdx + 1] : undefined;

generateDocx(inputPath, outputPath, lang, jurisdiction, documentType).catch((err) => {
  console.error("Error generating document:", err.message);
  process.exit(1);
});
