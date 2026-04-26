#!/usr/bin/env node
/**
 * Compatibility wrapper for the Python DOCX renderer.
 *
 * The Python renderer is the primary implementation. Keeping this wrapper lets
 * older commands that invoke `node docx-generator.js ...` continue to work while
 * avoiding two diverging Markdown renderers.
 */

const path = require("path");
const { spawnSync } = require("child_process");

const fallbackScript = path.join(__dirname, "docx-generator.py");
const result = spawnSync("python3", [fallbackScript, ...process.argv.slice(2)], {
  stdio: "inherit",
});

if (result.error) {
  console.error("Error: Python DOCX renderer is unavailable.");
  console.error(`Underlying error: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 0);
