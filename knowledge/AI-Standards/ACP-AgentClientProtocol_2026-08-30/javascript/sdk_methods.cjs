/**
 * ACP TypeScript SDK introspection - enumerate public API surface.
 *
 * No API calls. Inspects the installed `@agentclientprotocol/sdk` package
 * and outputs structured data about available exports.
 */
const fs = require("fs");
const path = require("path");

const PKG_NAME = "@agentclientprotocol/sdk";
const OUT = path.join(__dirname, "sdk_methods.json");

function inspectExport(name) {
  try {
    const mod = require(name);
    const keys = Object.keys(mod).filter((k) => !k.startsWith("_"));
    const classes = [];
    const functions = [];
    const constants = [];

    for (const key of keys) {
      const val = mod[key];
      if (typeof val === "function") {
        if (/^[A-Z]/.test(key) && val.prototype && val.prototype.constructor === val) {
          const methods = Object.getOwnPropertyNames(val.prototype)
            .filter((m) => m !== "constructor" && !m.startsWith("_"));
          classes.push({ name: key, methods });
        } else {
          functions.push({ name: key, length: val.length });
        }
      } else if (typeof val === "object" && val !== null) {
        constants.push({ name: key, type: "object", keys: Object.keys(val).slice(0, 10) });
      } else {
        constants.push({ name: key, type: typeof val, value: String(val).slice(0, 100) });
      }
    }
    return { module: name, classes, functions, constants, exportCount: keys.length };
  } catch (e) {
    return { module: name, error: e.message };
  }
}

function main() {
  const pkgJson = JSON.parse(
    fs.readFileSync(
      path.join(__dirname, "node_modules", PKG_NAME, "package.json"),
      "utf8"
    )
  );

  const exportNames = Object.keys(pkgJson.exports || {});
  console.log(`ACP TS SDK v${pkgJson.version}`);
  console.log(`Export paths: ${exportNames.length}`);

  const results = {
    package: PKG_NAME,
    version: pkgJson.version,
    node: process.version,
    exportPaths: exportNames,
    modules: [],
  };

  // Inspect main export
  const mainResult = inspectExport(PKG_NAME);
  results.modules.push(mainResult);

  // Inspect experimental exports
  for (const exp of exportNames) {
    if (exp === ".") continue;
    const fullName = PKG_NAME + exp.slice(1); // "./foo" -> "@agentclientprotocol/sdk/foo"
    const modResult = inspectExport(fullName);
    results.modules.push(modResult);
  }

  fs.writeFileSync(OUT, JSON.stringify(results, null, 2), "utf8");
  console.log(`\nWrote ${OUT}`);

  // Summary
  let totalExports = 0;
  let totalClasses = 0;
  let totalFunctions = 0;
  let errors = 0;
  for (const m of results.modules) {
    if (m.error) { errors++; continue; }
    totalExports += m.exportCount || 0;
    totalClasses += (m.classes || []).length;
    totalFunctions += (m.functions || []).length;
  }
  console.log(`\nSummary:`);
  console.log(`  Version: ${pkgJson.version}`);
  console.log(`  Export paths: ${exportNames.length}`);
  console.log(`  Total exports: ${totalExports}`);
  console.log(`  Classes: ${totalClasses}`);
  console.log(`  Functions: ${totalFunctions}`);
  console.log(`  Import errors: ${errors}`);
}

main();
