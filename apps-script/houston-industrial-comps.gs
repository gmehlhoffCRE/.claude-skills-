// =============================================================================
// HOUSTON INDUSTRIAL COMPS - SHEET AUTOMATION
// Rows are added directly by the Slack Workflow (form -> Add to Google Sheets).
// This script handles everything AFTER the row lands:
//   Dedupe -> Building DB Enrichment -> Geocoding, plus the dashboard proxy.
// No Slack bot, no AI parsing - the workflow writes structured data already.
//
// COLUMN RESOLUTION
// Both sheets are addressed BY HEADER NAME at runtime, never by hardcoded
// position. Adding, removing, reordering, or re-sorting columns in either sheet
// is safe. If a header cannot be found, the field is SKIPPED and reported -
// the script never falls back to a guessed position, because a wrong guess
// silently writes the wrong data into the comps.
// Run "Comps Pipeline > Validate Schema" after any schema change.
// =============================================================================

const CONFIG = {
  INDUSTRIAL_SHEET_NAME: "Industrial",
};

// Expected header row on the Industrial sheet, in order. Used for the schema
// report and to create script-owned columns; NOT used to address columns.
const SCHEMA = [
  "Tenant Name", "Address", "City", "State", "Zip", "Submarket", "Industrial Park Name",
  "Class", "Property Type", "Property Subtype", "Landlord", "Transaction Type", "SF",
  "Lease Sign Date", "Lease Commencement Date", "Lease Expiration Date", "Lease Term Months",
  "Base Rent/SF", "Rent Type", "OpEx", "Annual Escalations", "Free Rent", "TI ($/SF)",
  "Configuration", "Clear Height", "Outdoor Storage (AC)", "Crane Served",
  "Number of Cranes/Tonnage", "Tenant Broker", "Landlord Broker", "Notes",
  "Company Website", "Complete (Yes/No)", "Confidence",
];

// Trailing columns after SCHEMA on the Industrial tab, in order.
const EXTRA_COLS = ["Latitude", "Longitude", "Building DB Match", "Source", "Date"];

const EXPECTED_HEADERS = SCHEMA.concat(EXTRA_COLS);

// Columns the script writes to and will create at the end of the header row if
// they are missing. Everything else must already exist in the sheet.
const SCRIPT_OWNED_COLS = ["Latitude", "Longitude", "Building DB Match"];

// Industrial headers this script reads by name.
const F = {
  TENANT:    "Tenant Name",
  ADDRESS:   "Address",
  CITY:      "City",
  STATE:     "State",
  ZIP:       "Zip",
  SF:        "SF",
  COMMENCE:  "Lease Commencement Date",
  LAT:       "Latitude",
  LNG:       "Longitude",
  MATCH:     "Building DB Match",
};

// -----------------------------------------------------------------------------
// BUILDING DATABASE
// -----------------------------------------------------------------------------

const BLDG_DB = {
  URL: "https://docs.google.com/spreadsheets/d/1Zrg1JYhqqBmqHawXBPiNcAY1AcuW4B1qQK0oMkmp6kA/edit",
  TAB_NAME: "Buildings",
  ADDRESS_HEADER: "Property Address",
};

// Which Industrial column is filled from which Buildings column, by header name.
// Add a line to wire up a new field - nothing else needs to change.
// A line whose `comp` column does not exist in the Industrial sheet is inert:
// it is skipped and listed in the schema report, so entries can be added here
// before the column is added to the sheet.
const ENRICH_MAP = [
  // --- location ---
  { comp: "City",                 bldg: "City" },
  { comp: "State",                bldg: "State" },
  { comp: "Zip",                  bldg: "Zip" },
  { comp: "Submarket",            bldg: "Submarket Name" },
  { comp: "Industrial Park Name", bldg: "Building Park" },
  { comp: "Latitude",             bldg: "Latitude" },
  { comp: "Longitude",            bldg: "Longitude" },

  // --- ownership ---
  { comp: "Landlord",             bldg: "Owner Name" },

  // --- building characteristics ---
  { comp: "Property Type",        bldg: "Property Type" },
  { comp: "Clear Height",         bldg: "Ceiling Ht" },
  { comp: "Number of Cranes/Tonnage", bldg: "Number of Cranes" },
  {
    comp: "Crane Served",
    bldg: "Number of Cranes",
    // Blank/non-numeric in the building DB is left alone rather than asserted
    // as "No", since absent is not the same as zero. Note Number("") === 0,
    // so the blank check must come first.
    transform: function (v) {
      if (isBlank_(v) || String(v).trim() === "") return null;
      const n = Number(v);
      if (!isFinite(n)) return null;
      return n > 0 ? "Yes" : "No";
    },
  },

  // --- fields available in the Buildings DB with no Industrial column yet.
  // Inert until you add the matching column; uncomment/rename to match your
  // actual header once the column exists. ---
  // { comp: "County",              bldg: "County Name" },
  // { comp: "Submarket Cluster",   bldg: "Submarket Cluster" },
  // { comp: "Building RBA",        bldg: "RBA" },
  // { comp: "Year Built",          bldg: "Year Built" },
  // { comp: "Year Renovated",      bldg: "Year Renovated" },
  // { comp: "Column Spacing",      bldg: "Column Spacing" },
  // { comp: "Dock Doors",          bldg: "Number of Loading Docks" },
  // { comp: "Drive Ins",           bldg: "Drive Ins" },
  // { comp: "Sprinklers",          bldg: "Sprinklers" },
  // { comp: "Rail Served",         bldg: "Rail Lines" },
  // { comp: "Land Area (AC)",      bldg: "Land Area (AC)" },
  // { comp: "Office Space",        bldg: "Office Space" },
  // { comp: "Parking Ratio",       bldg: "Parking Ratio" },
  // { comp: "Power",               bldg: "Power" },
  // { comp: "Construction Material", bldg: "Construction Material" },
  // { comp: "Developer",           bldg: "Developer Name" },
  // { comp: "Leasing Company",     bldg: "Leasing Company Name" },
  // { comp: "Flood Zone",          bldg: "Fema Flood Zone" },
  // { comp: "Building Status",     bldg: "Building Status" },
  // { comp: "Percent Leased",      bldg: "Percent Leased" },
];

// -----------------------------------------------------------------------------
// Header resolution
// -----------------------------------------------------------------------------

// Loose header comparison: case, punctuation, and spacing differences are
// ignored, so "Ceiling Ht", "CEILING HT" and "Ceiling  Ht." all match.
function normHeader_(s) {
  return String(s === null || s === undefined ? "" : s)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function headerIndex_(headerRow) {
  const idx = new Map();
  for (let c = 0; c < headerRow.length; c++) {
    const key = normHeader_(headerRow[c]);
    if (key && !idx.has(key)) idx.set(key, c + 1);
  }
  return idx;
}

// Resolves the Industrial sheet's headers. Missing headers resolve to 0 and are
// reported; script-owned columns are appended to the header row instead.
function resolveCompCols_(sheet) {
  let width = Math.max(sheet.getLastColumn(), 1);
  let header = sheet.getRange(1, 1, 1, width).getValues()[0];
  let idx = headerIndex_(header);

  // Create any script-owned column that does not exist yet.
  const created = [];
  SCRIPT_OWNED_COLS.forEach(function (name) {
    if (idx.has(normHeader_(name))) return;
    if (sheet.getMaxColumns() < width + 1) sheet.insertColumnsAfter(sheet.getMaxColumns(), 1);
    width += 1;
    sheet.getRange(1, width).setValue(name);
    created.push(name + " (col " + width + ")");
  });
  if (created.length) {
    header = sheet.getRange(1, 1, 1, width).getValues()[0];
    idx = headerIndex_(header);
    Logger.log("Created missing script columns: " + created.join(", "));
  }

  const byName = {};
  idx.forEach(function (colNum, key) { byName[key] = colNum; });

  const missing = EXPECTED_HEADERS.filter(function (n) { return !idx.has(normHeader_(n)); });
  const expectedKeys = new Set(EXPECTED_HEADERS.map(normHeader_));
  const extras = [];
  for (let c = 0; c < header.length; c++) {
    const key = normHeader_(header[c]);
    if (key && !expectedKeys.has(key)) extras.push(String(header[c]) + " (col " + (c + 1) + ")");
  }

  return {
    header: header,
    width: width,
    missing: missing,
    extras: extras,
    created: created,
    col: function (name) { return byName[normHeader_(name)] || 0; },
  };
}

// Returns a resolved column or throws - for columns the script cannot run without.
function requireCol_(cols, name) {
  const c = cols.col(name);
  if (!c) throw new Error('Required column "' + name + '" not found in the ' + CONFIG.INDUSTRIAL_SHEET_NAME + " header row.");
  return c;
}

function loadBuildingDb_() {
  const bldgSheet = SpreadsheetApp.openByUrl(BLDG_DB.URL).getSheetByName(BLDG_DB.TAB_NAME);
  if (!bldgSheet) throw new Error("Tab " + BLDG_DB.TAB_NAME + " not found");

  const data = bldgSheet.getDataRange().getValues();
  if (data.length < 2) throw new Error("Tab " + BLDG_DB.TAB_NAME + " has no data rows");

  const idx = headerIndex_(data[0]);
  const addressCol = idx.get(normHeader_(BLDG_DB.ADDRESS_HEADER));
  if (!addressCol) {
    throw new Error('Building DB address column "' + BLDG_DB.ADDRESS_HEADER + '" not found. Update BLDG_DB.ADDRESS_HEADER.');
  }

  return {
    data: data,
    addressCol: addressCol,
    col: function (name) { return idx.get(normHeader_(name)) || 0; },
  };
}

// Resolves ENRICH_MAP into concrete column pairs, dropping (and reporting) any
// entry whose comp or building header does not exist.
function resolvePairs_(cols, bldg) {
  const active = [];
  const inactive = [];
  ENRICH_MAP.forEach(function (m) {
    const compCol = cols.col(m.comp);
    const bldgCol = bldg.col(m.bldg);
    if (compCol && bldgCol) {
      active.push({ name: m.comp, compCol: compCol, bldgCol: bldgCol, transform: m.transform || null });
    } else {
      inactive.push(m.comp + " <- " + m.bldg + " (" +
        (!compCol ? 'no "' + m.comp + '" column in ' + CONFIG.INDUSTRIAL_SHEET_NAME : "") +
        (!compCol && !bldgCol ? "; " : "") +
        (!bldgCol ? 'no "' + m.bldg + '" column in ' + BLDG_DB.TAB_NAME : "") + ")");
    }
  });
  return { active: active, inactive: inactive };
}

// Reports schema drift without changing anything.
function validateSchema() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
  if (!sheet) { SpreadsheetApp.getUi().alert("Sheet " + CONFIG.INDUSTRIAL_SHEET_NAME + " not found."); return; }

  const cols = resolveCompCols_(sheet);
  let msg = CONFIG.INDUSTRIAL_SHEET_NAME + " tab: " + cols.width + " columns.\n\n";

  if (cols.created.length) msg += "Created script columns:\n  " + cols.created.join("\n  ") + "\n\n";
  if (cols.missing.length) msg += "In SCHEMA but NOT in the sheet:\n  " + cols.missing.join("\n  ") + "\n\n";
  if (cols.extras.length)  msg += "In the sheet but NOT in SCHEMA (ignored unless mapped):\n  " + cols.extras.join("\n  ") + "\n\n";
  if (!cols.missing.length && !cols.extras.length) msg += "Header matches SCHEMA + EXTRA_COLS.\n\n";

  try {
    const bldg = loadBuildingDb_();
    const pairs = resolvePairs_(cols, bldg);
    msg += BLDG_DB.TAB_NAME + " DB: " + (bldg.data[0].length) + " columns, " + (bldg.data.length - 1) + " rows.\n";
    msg += 'Address matched on "' + BLDG_DB.ADDRESS_HEADER + '" (col ' + bldg.addressCol + ").\n\n";
    msg += "ACTIVE enrichment mappings (" + pairs.active.length + "):\n  " +
      pairs.active.map(function (p) { return p.name + " <- col " + p.bldgCol; }).join("\n  ") + "\n";
    if (pairs.inactive.length) {
      msg += "\nINACTIVE mappings (" + pairs.inactive.length + "):\n  " + pairs.inactive.join("\n  ") + "\n";
    }

    // Buildings columns not consumed by any mapping - candidates for new fields.
    const used = new Set(ENRICH_MAP.map(function (m) { return normHeader_(m.bldg); }));
    const unused = bldg.data[0].filter(function (h) {
      return normHeader_(h) && !used.has(normHeader_(h));
    });
    msg += "\nBuildings columns not yet mapped (" + unused.length + "):\n  " + unused.join(", ");
  } catch (e) {
    msg += "Building DB check failed: " + e.message;
  }

  Logger.log(msg);
  SpreadsheetApp.getUi().alert(msg);
}

// -----------------------------------------------------------------------------
// Pipeline
// -----------------------------------------------------------------------------

// Dedupe -> Enrich -> Geocode, but only when there are unprocessed rows.
// A row is "new" if it has an Address but a blank Building DB Match cell
// (enrichment stamps that cell on every row it touches, so it doubles as a
// processed marker that survives row deletions and sorting).
function runPipeline() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(1000)) {
    Logger.log("Pipeline: another run holds the lock, skipping.");
    return;
  }
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
    if (!sheet || sheet.getLastRow() <= 1) return;

    let cols = resolveCompCols_(sheet);
    let newRows = findNewRows_(sheet, cols);
    if (newRows.length === 0) {
      Logger.log("Pipeline: no new rows, nothing to do.");
      return;
    }

    removeDuplicatesSilent_();
    cols = resolveCompCols_(sheet);
    newRows = findNewRows_(sheet, cols); // re-detect: dedupe may have shifted rows
    if (newRows.length === 0) return;

    try { enrichFromBuildingDB_({ silent: true, rows: newRows }); }
    catch (e) { Logger.log("Auto-enrich error: " + e.message); }
    // retryNotFound:false - failed geocodes are not re-attempted on every
    // 15-minute run. Use the menu item to retry them deliberately.
    try { runBatchGeocode_({ silent: true, rows: newRows, retryNotFound: false }); }
    catch (e) { Logger.log("Auto-geocode error: " + e.message); }

    ss.toast("Processed " + newRows.length + " new row(s).", "Pipeline", 4);
  } finally {
    lock.releaseLock();
  }
}

function findNewRows_(sheet, cols) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return [];
  const numRows = lastRow - 1;
  const addrs = sheet.getRange(2, requireCol_(cols, F.ADDRESS), numRows, 1).getValues();
  const marks = sheet.getRange(2, requireCol_(cols, F.MATCH), numRows, 1).getValues();
  const rows = [];
  for (let i = 0; i < numRows; i++) {
    const hasAddr = String(addrs[i][0] || "").trim() !== "";
    const marked = String(marks[i][0] || "").trim() !== "";
    if (hasAddr && !marked) rows.push(i + 2);
  }
  return rows;
}

function setupTrigger() {
  try {
    const triggers = ScriptApp.getProjectTriggers();
    for (let i = 0; i < triggers.length; i++) {
      if (triggers[i].getHandlerFunction() === "runPipeline") ScriptApp.deleteTrigger(triggers[i]);
    }
    ScriptApp.newTrigger("runPipeline").timeBased().everyMinutes(15).create();
    SpreadsheetApp.getUi().alert("Trigger set! runPipeline will run every 15 minutes.\n\nIt exits immediately when there are no new rows, and only processes rows that haven't been enriched yet.");
  } catch (e) {
    SpreadsheetApp.getUi().alert("Trigger setup failed: " + e.message);
  }
}

function removeTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "runPipeline") ScriptApp.deleteTrigger(triggers[i]);
  }
  SpreadsheetApp.getUi().alert("Trigger removed.");
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Comps Pipeline")
    .addItem("Run Pipeline Now (Dedupe > Enrich > Geocode)", "runPipeline")
    .addSeparator()
    .addItem("Validate Schema (no changes)", "validateSchema")
    .addItem("Remove Duplicates (with preview)", "removeDuplicates")
    .addSeparator()
    .addItem("Setup Auto-Trigger (every 15 min)", "setupTrigger")
    .addItem("Remove Auto-Trigger", "removeTrigger")
    .addToUi();
  addBuildingDbMenu();
  addGeocoderMenu();
}

// =============================================================================
// DUPLICATE REMOVER
// =============================================================================

// Dates arrive as either real Date objects (Slack workflow) or text, and
// String(new Date(...)) includes a timezone-dependent time component. Normalize
// both to yyyy-MM-dd so the two forms collide in the dedupe key.
function dedupeKeyPart_(v) {
  if (v instanceof Date) return Utilities.formatDate(v, Session.getScriptTimeZone(), "yyyy-MM-dd");
  return String(v === null || v === undefined ? "" : v).trim().toLowerCase();
}

function collectDuplicateRows_(sheet, cols) {
  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) return [];

  const tenantIdx = requireCol_(cols, F.TENANT) - 1;
  const addressIdx = requireCol_(cols, F.ADDRESS) - 1;
  const commenceIdx = cols.col(F.COMMENCE) - 1;
  const sfIdx = cols.col(F.SF) - 1;

  const data = sheet.getRange(2, 1, lastRow - 1, cols.width).getValues();
  const seen = new Set();
  const rowsToDelete = [];

  for (let i = 0; i < data.length; i++) {
    const row = data[i];
    if (!row[tenantIdx] && !row[addressIdx]) continue;
    const key = [
      dedupeKeyPart_(row[tenantIdx]),
      dedupeKeyPart_(row[addressIdx]),
      commenceIdx >= 0 ? dedupeKeyPart_(row[commenceIdx]) : "",
      sfIdx >= 0 ? dedupeKeyPart_(row[sfIdx]) : "",
    ].join("||");

    if (seen.has(key)) rowsToDelete.push(i + 2);
    else seen.add(key);
  }
  return rowsToDelete;
}

// Deletes rows in descending contiguous runs so N adjacent duplicates cost one
// API call instead of N.
function deleteRows_(sheet, rowsAsc) {
  const rows = rowsAsc.slice().sort(function (a, b) { return b - a; });
  let i = 0;
  while (i < rows.length) {
    let j = i;
    while (j + 1 < rows.length && rows[j + 1] === rows[j] - 1) j++;
    sheet.deleteRows(rows[j], j - i + 1);
    i = j + 1;
  }
}

function removeDuplicatesSilent_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
  if (!sheet || sheet.getLastRow() <= 1) return;

  const rowsToDelete = collectDuplicateRows_(sheet, resolveCompCols_(sheet));
  if (rowsToDelete.length === 0) return;

  deleteRows_(sheet, rowsToDelete);
  ss.toast("Auto-removed " + rowsToDelete.length + " duplicate(s).", "Duplicates Cleaned", 4);
}

function removeDuplicates() {
  const ui = SpreadsheetApp.getUi();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
  if (!sheet) { ui.alert("Sheet " + CONFIG.INDUSTRIAL_SHEET_NAME + " not found."); return; }
  if (sheet.getLastRow() <= 1) { ui.alert("No data."); return; }

  const rowsToDelete = collectDuplicateRows_(sheet, resolveCompCols_(sheet));
  if (rowsToDelete.length === 0) { ui.alert("No duplicates found."); return; }

  const preview = rowsToDelete.slice(0, 50).join(", ") + (rowsToDelete.length > 50 ? ", ..." : "");
  const response = ui.alert(
    "Found " + rowsToDelete.length + " duplicate row(s)",
    "Delete rows: " + preview + "?",
    ui.ButtonSet.YES_NO
  );
  if (response !== ui.Button.YES) { ui.alert("Cancelled."); return; }

  deleteRows_(sheet, rowsToDelete);
  ss.toast("Removed " + rowsToDelete.length + " duplicate row(s).", "Duplicates Removed", 5);
}

// =============================================================================
// BUILDING DATABASE ENRICHMENT (fuzzy matching + match reason)
// =============================================================================

function stripSuite_(s) {
  return s
    .replace(/\b(ste|suite|unit|bldg|building|apt|apartment|#)\s*[\w-]+/gi, "")
    .replace(/,\s*$/, "")
    .trim();
}

function normalizeBase_(str) {
  if (!str) return "";
  return String(str)
    .toLowerCase()
    .replace(/[.,;]/g, "")
    .replace(/[()[\]{}]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeAbbreviations_(str) {
  return str
    .replace(/\bparkway\b/g, "pkwy")
    .replace(/\bpky\b/g, "pkwy")
    .replace(/\bfreeway\b/g, "fwy")
    .replace(/\bexpressway\b/g, "fwy")
    .replace(/\bexpy\b/g, "fwy")
    .replace(/\bfrwy\b/g, "fwy")
    .replace(/\bstreet\b/g, "st")
    .replace(/\bavenue\b/g, "ave")
    .replace(/\bav\b/g, "ave")
    .replace(/\bboulevard\b/g, "blvd")
    .replace(/\bbl\b/g, "blvd")
    .replace(/\bdrive\b/g, "dr")
    .replace(/\broad\b/g, "rd")
    .replace(/\bhighway\b/g, "hwy")
    .replace(/\blane\b/g, "ln")
    .replace(/\bcircle\b/g, "cir")
    .replace(/\bcourt\b/g, "ct")
    .replace(/\bplace\b/g, "pl")
    .replace(/\bterrace\b/g, "ter")
    .replace(/\btrail\b/g, "trl")
    .replace(/\bmount\b/g, "mt")
    .replace(/\bfort\b/g, "ft")
    .replace(/\bsaint\b/g, "st ")
    .replace(/\bfirst\b/g, "1st")
    .replace(/\bsecond\b/g, "2nd")
    .replace(/\bthird\b/g, "3rd")
    .replace(/\bfourth\b/g, "4th")
    .replace(/\bfifth\b/g, "5th")
    .replace(/\s+/g, " ")
    .trim();
}

// Compound directionals are listed before their prefixes so the intent is
// explicit; the trailing \b already prevents "north" from matching "northeast".
function normalizeDirectionals_(str) {
  return str
    .replace(/\bnortheast\b/g, "ne")
    .replace(/\bnorthwest\b/g, "nw")
    .replace(/\bsoutheast\b/g, "se")
    .replace(/\bsouthwest\b/g, "sw")
    .replace(/\bnorth\b/g, "n")
    .replace(/\bsouth\b/g, "s")
    .replace(/\beast\b/g, "e")
    .replace(/\bwest\b/g, "w")
    .replace(/\s+/g, " ")
    .trim();
}

function buildLookupKeys_(addr) {
  if (!addr) return { exact: "", abbr: "", suite: "", dir: "" };
  const base = normalizeBase_(addr);
  const abbr = normalizeAbbreviations_(base);
  const suite = stripSuite_(abbr);
  const dir = normalizeDirectionals_(suite);
  return { exact: base, abbr: abbr, suite: suite, dir: dir };
}

function findBuildingMatch_(compAddr, indexes) {
  const keys = buildLookupKeys_(compAddr);
  if (keys.exact && indexes.exact.has(keys.exact)) return { row: indexes.exact.get(keys.exact), reason: "Exact" };
  if (keys.abbr && indexes.abbr.has(keys.abbr))    return { row: indexes.abbr.get(keys.abbr),   reason: "Fuzzy:Abbr" };
  if (keys.suite && indexes.suite.has(keys.suite)) return { row: indexes.suite.get(keys.suite), reason: "Fuzzy:Suite" };
  if (keys.dir && indexes.dir.has(keys.dir))       return { row: indexes.dir.get(keys.dir),     reason: "Fuzzy:Dir" };
  return null;
}

function buildBldgIndexes_(bldgData, addrCol) {
  const indexes = { exact: new Map(), abbr: new Map(), suite: new Map(), dir: new Map() };
  for (let i = 1; i < bldgData.length; i++) {
    const addr = bldgData[i][addrCol - 1];
    if (!addr) continue;
    const keys = buildLookupKeys_(addr);
    if (keys.exact && !indexes.exact.has(keys.exact)) indexes.exact.set(keys.exact, bldgData[i]);
    if (keys.abbr && !indexes.abbr.has(keys.abbr))    indexes.abbr.set(keys.abbr, bldgData[i]);
    if (keys.suite && !indexes.suite.has(keys.suite)) indexes.suite.set(keys.suite, bldgData[i]);
    if (keys.dir && !indexes.dir.has(keys.dir))       indexes.dir.set(keys.dir, bldgData[i]);
  }
  return indexes;
}

function isBlank_(v) {
  return v === "" || v === null || v === undefined;
}

// Writes column-wise: one setValues per touched column over the whole row
// range, instead of one setValue per cell. Cost is ~constant in row count.
function flushColumnUpdates_(sheet, firstRow, numRows, columnValues) {
  Object.keys(columnValues).forEach(function (colStr) {
    sheet.getRange(firstRow, Number(colStr), numRows, 1).setValues(columnValues[colStr]);
  });
  SpreadsheetApp.flush();
}

function enrichFromBuildingDB_(opts) {
  const silent = opts && opts.silent;
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const parsedSheet = ss.getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
  if (!parsedSheet) {
    if (!silent) SpreadsheetApp.getUi().alert("Tab " + CONFIG.INDUSTRIAL_SHEET_NAME + " not found");
    return;
  }

  const cols = resolveCompCols_(parsedSheet);
  const matchCol = requireCol_(cols, F.MATCH);
  const addrCol = requireCol_(cols, F.ADDRESS);

  let bldg;
  try {
    bldg = loadBuildingDb_();
  } catch (e) {
    Logger.log("Building DB load failed: " + e.message);
    if (!silent) SpreadsheetApp.getUi().alert("Could not open building database: " + e.message + "\n\nShare it as Anyone with the link can view.");
    return;
  }

  const pairs = resolvePairs_(cols, bldg);
  if (pairs.active.length === 0) {
    const err = "No enrichment mappings resolved - nothing would be written.\nRun Validate Schema.";
    Logger.log(err);
    if (!silent) SpreadsheetApp.getUi().alert(err);
    return;
  }

  const indexes = buildBldgIndexes_(bldg.data, bldg.addressCol);
  Logger.log("Loaded " + indexes.exact.size + " exact / " + indexes.abbr.size + " abbr / " +
    indexes.suite.size + " suite / " + indexes.dir.size + " dir keys");

  const lastRow = parsedSheet.getLastRow();
  if (lastRow < 2) return;
  const numRows = lastRow - 1;
  const compsData = parsedSheet.getRange(2, 1, numRows, cols.width).getValues();

  // Working copies of every column we might write, so each is flushed once.
  const columnValues = {};
  function columnBuffer(c) {
    if (!columnValues[c]) {
      columnValues[c] = compsData.map(function (row) { return [row[c - 1]]; });
    }
    return columnValues[c];
  }

  const counts = { Exact: 0, "Fuzzy:Abbr": 0, "Fuzzy:Suite": 0, "Fuzzy:Dir": 0, None: 0 };
  const perField = {};
  let enrichedCount = 0;

  // Optional row restriction: opts.rows = array of 1-based row numbers.
  // Used by runPipeline to touch only unprocessed rows. Manual menu runs
  // pass nothing and re-enrich the whole sheet.
  const rowsFilter = opts && opts.rows ? new Set(opts.rows) : null;

  for (let i = 0; i < compsData.length; i++) {
    const sheetRow = i + 2;
    if (rowsFilter && !rowsFilter.has(sheetRow)) continue;
    const compRow = compsData[i];
    const compAddr = compRow[addrCol - 1];
    if (!compAddr) continue;

    const match = findBuildingMatch_(compAddr, indexes);
    const reason = match ? match.reason : "None";
    counts[reason] = (counts[reason] || 0) + 1;
    columnBuffer(matchCol)[i][0] = reason;

    if (!match) continue;

    for (let p = 0; p < pairs.active.length; p++) {
      const pair = pairs.active[p];
      if (!isBlank_(compRow[pair.compCol - 1])) continue;
      let newVal = match.row[pair.bldgCol - 1];
      if (pair.transform) newVal = pair.transform(newVal);
      if (isBlank_(newVal)) continue;
      columnBuffer(pair.compCol)[i][0] = newVal;
      perField[pair.name] = (perField[pair.name] || 0) + 1;
      enrichedCount++;
    }
  }

  flushColumnUpdates_(parsedSheet, 2, numRows, columnValues);

  const totalMatched = counts.Exact + counts["Fuzzy:Abbr"] + counts["Fuzzy:Suite"] + counts["Fuzzy:Dir"];
  let msg =
    "Building DB enrichment complete:\n\n" +
    "Exact matches:        " + counts.Exact + "\n" +
    "Fuzzy (abbreviation): " + counts["Fuzzy:Abbr"] + "\n" +
    "Fuzzy (suite strip):  " + counts["Fuzzy:Suite"] + "\n" +
    "Fuzzy (directional):  " + counts["Fuzzy:Dir"] + "\n" +
    "Unmatched:            " + counts.None + "\n\n" +
    "Total matched: " + totalMatched + "\n" +
    "Cells filled: " + enrichedCount;

  const fieldLines = Object.keys(perField).map(function (k) { return "  " + k + ": " + perField[k]; });
  if (fieldLines.length) msg += "\n\nBy field:\n" + fieldLines.join("\n");
  if (pairs.inactive.length) msg += "\n\nInactive mappings (skipped):\n  " + pairs.inactive.join("\n  ");

  Logger.log(msg);
  if (!silent) SpreadsheetApp.getUi().alert(msg);
  else ss.toast("Enriched " + enrichedCount + " cells across " + totalMatched + " matches.", "Building DB", 4);
}

function enrichFromBuildingDB() {
  enrichFromBuildingDB_({ silent: false });
}

function previewEnrichment() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const parsedSheet = ss.getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
  if (!parsedSheet) { SpreadsheetApp.getUi().alert("Tab " + CONFIG.INDUSTRIAL_SHEET_NAME + " not found"); return; }

  const cols = resolveCompCols_(parsedSheet);
  const addrCol = requireCol_(cols, F.ADDRESS);

  let bldg;
  try {
    bldg = loadBuildingDb_();
  } catch (e) {
    SpreadsheetApp.getUi().alert("Could not open building database: " + e.message);
    return;
  }

  const pairs = resolvePairs_(cols, bldg);
  const indexes = buildBldgIndexes_(bldg.data, bldg.addressCol);
  const lastRow = parsedSheet.getLastRow();
  if (lastRow < 2) { SpreadsheetApp.getUi().alert("No data."); return; }

  const compsData = parsedSheet.getRange(2, 1, lastRow - 1, cols.width).getValues();
  const counts = { Exact: 0, "Fuzzy:Abbr": 0, "Fuzzy:Suite": 0, "Fuzzy:Dir": 0, None: 0 };
  const unmatchedList = [];
  const fuzzyList = [];
  const wouldFill = {};

  for (let i = 0; i < compsData.length; i++) {
    const compRow = compsData[i];
    const compAddr = compRow[addrCol - 1];
    if (!compAddr) continue;
    const match = findBuildingMatch_(compAddr, indexes);
    const reason = match ? match.reason : "None";
    counts[reason] = (counts[reason] || 0) + 1;

    if (reason === "None") {
      if (unmatchedList.length < 10) unmatchedList.push("Row " + (i + 2) + ": " + compAddr);
      continue;
    }
    if (reason.indexOf("Fuzzy") === 0 && fuzzyList.length < 5) {
      fuzzyList.push("Row " + (i + 2) + " [" + reason + "]: " + compAddr + " -> " + match.row[bldg.addressCol - 1]);
    }
    for (let p = 0; p < pairs.active.length; p++) {
      const pair = pairs.active[p];
      if (!isBlank_(compRow[pair.compCol - 1])) continue;
      let newVal = match.row[pair.bldgCol - 1];
      if (pair.transform) newVal = pair.transform(newVal);
      if (isBlank_(newVal)) continue;
      wouldFill[pair.name] = (wouldFill[pair.name] || 0) + 1;
    }
  }

  const total = counts.Exact + counts["Fuzzy:Abbr"] + counts["Fuzzy:Suite"] + counts["Fuzzy:Dir"] + counts.None;
  const matched = total - counts.None;
  const pct = total ? Math.round((matched / total) * 100) : 0;

  let msg =
    "Preview - no changes made\n\n" +
    "Building DB: " + indexes.exact.size + " unique addresses\n" +
    "Rows scanned: " + total + "\n\n" +
    "Exact:       " + counts.Exact + "\n" +
    "Fuzzy:Abbr:  " + counts["Fuzzy:Abbr"] + "\n" +
    "Fuzzy:Suite: " + counts["Fuzzy:Suite"] + "\n" +
    "Fuzzy:Dir:   " + counts["Fuzzy:Dir"] + "\n" +
    "None:        " + counts.None + "\n\n" +
    "Total would match: " + matched + " (" + pct + "%)\n\n" +
    "Cells that would be filled, by field:\n";

  pairs.active.forEach(function (p) { msg += "  " + p.name + ": " + (wouldFill[p.name] || 0) + "\n"; });
  if (pairs.inactive.length) msg += "\nInactive mappings:\n  " + pairs.inactive.join("\n  ") + "\n";
  msg += "\n";

  if (fuzzyList.length) msg += "Sample fuzzy matches (verify):\n" + fuzzyList.join("\n") + "\n\n";
  if (unmatchedList.length) msg += "First unmatched:\n" + unmatchedList.join("\n");

  Logger.log(msg);
  SpreadsheetApp.getUi().alert(msg);
}

// Repair tool. Enrichment only fills BLANK cells, so values written by a
// previously mis-mapped run are never corrected by re-running it. This clears
// the enrichment target columns and the match stamp so the next run refills
// them from scratch.
// DESTRUCTIVE: it also clears anything typed into those columns by hand.
function clearEnrichedValues() {
  const ui = SpreadsheetApp.getUi();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
  if (!sheet) { ui.alert("Sheet " + CONFIG.INDUSTRIAL_SHEET_NAME + " not found."); return; }
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) { ui.alert("No data."); return; }

  const cols = resolveCompCols_(sheet);
  let bldg;
  try { bldg = loadBuildingDb_(); }
  catch (e) { ui.alert("Could not open building database: " + e.message); return; }

  const pairs = resolvePairs_(cols, bldg);
  const targets = pairs.active.map(function (p) { return p.name; });
  if (!targets.length) { ui.alert("No active mappings; nothing to clear."); return; }

  const resp = ui.alert(
    "Clear enriched values on " + (lastRow - 1) + " row(s)?",
    "This clears these columns AND the '" + F.MATCH + "' stamp:\n\n  " + targets.join("\n  ") +
      "\n\nAnything typed into those columns by hand is also cleared. " +
      "The next pipeline run refills them from the Building DB.\n\nContinue?",
    ui.ButtonSet.YES_NO
  );
  if (resp !== ui.Button.YES) { ui.alert("Cancelled."); return; }

  const n = lastRow - 1;
  pairs.active.forEach(function (p) { sheet.getRange(2, p.compCol, n, 1).clearContent(); });
  sheet.getRange(2, requireCol_(cols, F.MATCH), n, 1).clearContent();
  SpreadsheetApp.flush();
  ui.alert("Cleared " + targets.length + " column(s) plus the match stamp on " + n + " row(s).\n\nRun the pipeline to re-enrich.");
}

// -----------------------------------------------------------------------------
// CORRUPTION AUDIT / TARGETED REPAIR
//
// When the Buildings tab was re-sorted, enrichment wrote the wrong field into
// several columns (text into Latitude, a construction date into Landlord, and
// so on). Re-running enrichment does NOT fix that: it only fills blank cells,
// so a bad value is never overwritten.
//
// Every mis-mapped field has a distinct type signature, so bad cells can be
// identified and cleared individually - leaving rows that were enriched
// correctly before the schema change, and anything typed by hand, untouched.
//
// These are heuristics, not proof. Always run the audit (read-only) first and
// eyeball the samples before running the repair.
// -----------------------------------------------------------------------------

function looksLikeDate_(v) {
  if (v instanceof Date) return true;
  const s = String(v).trim();
  if (!s || !/\d/.test(s)) return false;
  return /^\d{1,4}[-\/]\d{1,2}[-\/]\d{1,4}$/.test(s);
}

function isNumericish_(v) {
  if (typeof v === "number") return isFinite(v);
  const s = String(v).trim().replace(/[$,%\s,]/g, "");
  return s !== "" && isFinite(Number(s));
}

function hasDigit_(v) {
  return /\d/.test(String(v));
}

// A check returns true when the value is PLAUSIBLE for that column.
// Blank always passes - a blank cell is not corruption.
const FIELD_CHECKS = [
  {
    comp: "Latitude",
    expect: "a number near 29-30 (was overwritten with Construction Material)",
    ok: function (v) {
      if (String(v).trim() === "NOT FOUND") return true;
      const n = Number(v);
      return isFinite(n) && n >= 20 && n <= 50;
    },
  },
  {
    comp: "Longitude",
    expect: "a negative number near -95 (was overwritten with Cooling Redundancy)",
    ok: function (v) {
      if (String(v).trim() === "NOT FOUND") return true;
      const n = Number(v);
      return isFinite(n) && n >= -107 && n <= -88;
    },
  },
  {
    comp: "City",
    expect: "text (was overwritten with Average Weighted Rent)",
    ok: function (v) { return !isNumericish_(v) && !looksLikeDate_(v); },
  },
  {
    comp: "State",
    expect: "letters only (was overwritten with Building Operating Expenses)",
    ok: function (v) { return /^[A-Za-z][A-Za-z .]{0,19}$/.test(String(v).trim()); },
  },
  {
    comp: "Zip",
    expect: "5 digits (was overwritten with Building Status)",
    ok: function (v) { return /^\d{5}(-\d{4})?$/.test(String(v).trim()); },
  },
  {
    comp: "Submarket",
    expect: "text (was overwritten with Capacity - Critical IT kW)",
    ok: function (v) { return !isNumericish_(v) && !looksLikeDate_(v); },
  },
  {
    comp: "Landlord",
    expect: "a company name (was overwritten with Construction Begin, a date)",
    ok: function (v) { return !looksLikeDate_(v) && !isNumericish_(v); },
  },
  {
    comp: "Clear Height",
    expect: "a number (was overwritten with Collateral Type)",
    ok: function (v) { return hasDigit_(v); },
  },
];

// Scans the sheet and returns { findings, byField, checked } without writing.
function scanForBadValues_(sheet, cols) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return { findings: [], byField: {}, checked: [] };

  const checked = FIELD_CHECKS.filter(function (c) { return cols.col(c.comp); });
  const numRows = lastRow - 1;
  const data = sheet.getRange(2, 1, numRows, cols.width).getValues();

  const findings = [];
  const byField = {};
  for (let i = 0; i < numRows; i++) {
    for (let k = 0; k < checked.length; k++) {
      const chk = checked[k];
      const c = cols.col(chk.comp);
      const v = data[i][c - 1];
      if (isBlank_(v) || String(v).trim() === "") continue;
      if (chk.ok(v)) continue;
      findings.push({ row: i + 2, col: c, field: chk.comp, value: v });
      byField[chk.comp] = (byField[chk.comp] || 0) + 1;
    }
  }
  return { findings: findings, byField: byField, checked: checked };
}

// Read-only. Reports what the repair would clear.
function auditEnrichedValues() {
  const ui = SpreadsheetApp.getUi();
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
  if (!sheet) { ui.alert("Sheet " + CONFIG.INDUSTRIAL_SHEET_NAME + " not found."); return; }

  const cols = resolveCompCols_(sheet);
  const scan = scanForBadValues_(sheet, cols);
  const lastRow = sheet.getLastRow();

  const badRows = new Set(scan.findings.map(function (f) { return f.row; }));
  let msg = "Audit - no changes made\n\n" +
    "Rows scanned: " + Math.max(lastRow - 1, 0) + "\n" +
    "Columns checked: " + scan.checked.map(function (c) { return c.comp; }).join(", ") + "\n\n" +
    "Suspect cells: " + scan.findings.length + " across " + badRows.size + " row(s)\n\n";

  if (!scan.findings.length) {
    msg += "Nothing looks mis-mapped. You still need to clear the '" + F.MATCH +
      "' column so previously stamped rows get re-enriched.";
    ui.alert(msg);
    return;
  }

  msg += "By field:\n";
  scan.checked.forEach(function (c) {
    msg += "  " + c.comp + ": " + (scan.byField[c.comp] || 0) + "   (expects " + c.expect + ")\n";
  });

  msg += "\nSamples (first 3 per field):\n";
  scan.checked.forEach(function (c) {
    const ex = scan.findings.filter(function (f) { return f.field === c.comp; }).slice(0, 3);
    if (!ex.length) return;
    ex.forEach(function (f) {
      msg += "  " + f.field + " row " + f.row + ": " + JSON.stringify(String(f.value)).slice(0, 60) + "\n";
    });
  });

  msg += "\nThese are heuristics. Spot-check a few before running Repair.";
  Logger.log(msg);
  ui.alert(msg);
}

// Clears ONLY the cells that failed their type check, plus the whole
// "Building DB Match" column so every row is re-enriched on the next run.
// Rows enriched correctly before the schema change, and hand-typed values that
// pass their check, are left alone.
function repairEnrichedValues() {
  const ui = SpreadsheetApp.getUi();
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
  if (!sheet) { ui.alert("Sheet " + CONFIG.INDUSTRIAL_SHEET_NAME + " not found."); return; }

  const cols = resolveCompCols_(sheet);
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) { ui.alert("No data."); return; }

  const scan = scanForBadValues_(sheet, cols);
  const badRows = new Set(scan.findings.map(function (f) { return f.row; }));

  const fieldLines = Object.keys(scan.byField).map(function (k) { return "  " + k + ": " + scan.byField[k]; });
  const resp = ui.alert(
    "Repair mis-mapped values?",
    "Clears " + scan.findings.length + " suspect cell(s) across " + badRows.size + " row(s):\n" +
      (fieldLines.length ? fieldLines.join("\n") : "  (none)") +
      "\n\nAlso clears the entire '" + F.MATCH + "' column (" + (lastRow - 1) + " rows) so every " +
      "row is re-enriched on the next run. That column is a script marker, not data.\n\n" +
      "Everything else is left untouched. Continue?",
    ui.ButtonSet.YES_NO
  );
  if (resp !== ui.Button.YES) { ui.alert("Cancelled."); return; }

  // Clear failing cells column-wise: read the column, blank the bad rows, write once.
  const byCol = {};
  scan.findings.forEach(function (f) {
    if (!byCol[f.col]) byCol[f.col] = [];
    byCol[f.col].push(f.row);
  });
  const numRows = lastRow - 1;
  Object.keys(byCol).forEach(function (colStr) {
    const c = Number(colStr);
    const range = sheet.getRange(2, c, numRows, 1);
    const vals = range.getValues();
    byCol[colStr].forEach(function (r) { vals[r - 2][0] = ""; });
    range.setValues(vals);
  });

  sheet.getRange(2, requireCol_(cols, F.MATCH), numRows, 1).clearContent();
  SpreadsheetApp.flush();

  ui.alert(
    "Repaired.\n\n" +
    "Cleared " + scan.findings.length + " cell(s) and the " + F.MATCH + " stamp on " + numRows + " row(s).\n\n" +
    "Next: Building DB > Preview Matches to sanity-check the match rate, then " +
    "Comps Pipeline > Run Pipeline Now, then Geocoder > Retry NOT FOUND Rows."
  );
}

function addBuildingDbMenu() {
  SpreadsheetApp.getUi()
    .createMenu("Building DB")
    .addItem("Preview Matches (no changes)", "previewEnrichment")
    .addItem("Run Enrichment (writes to Industrial)", "enrichFromBuildingDB")
    .addSeparator()
    .addItem("Audit Mis-Mapped Values (no changes)", "auditEnrichedValues")
    .addItem("Repair Mis-Mapped Values", "repairEnrichedValues")
    .addSeparator()
    .addItem("Clear ALL Enriched Values (last resort)", "clearEnrichedValues")
    .addToUi();
}

// =============================================================================
// GEOCODER (Google Maps)
// =============================================================================

// Read from Script Properties (Project Settings > Script Properties).
// Property name must be exactly: MAPS_API_KEY
const GEO_API_KEY = PropertiesService.getScriptProperties().getProperty("MAPS_API_KEY");
const GEO_START_ROW = 2;
const GEO_DEFAULT_CITY = "Houston";
const GEO_DEFAULT_STATE = "TX";
const GEO_DELAY_MS = 100;
const GEO_BOUNDS = "29.30,-96.00%7C30.30,-94.70";
// Stop well short of the 6-minute execution limit and resume on the next run.
const GEO_MAX_RUNTIME_MS = 4 * 60 * 1000;

function addGeocoderMenu() {
  SpreadsheetApp.getUi()
    .createMenu("Geocoder")
    .addItem("Batch Geocode Addresses", "runBatchGeocode")
    .addItem("Retry NOT FOUND Rows", "retryFailedGeocodes")
    .addItem("Clear Lat/Lng Columns", "clearLatLng")
    .addToUi();
}

function runBatchGeocode_(opts) {
  const silent = opts && opts.silent;
  const retryNotFound = !!(opts && opts.retryNotFound);
  if (!GEO_API_KEY) {
    if (!silent) SpreadsheetApp.getUi().alert("Google Maps API key not set. Add MAPS_API_KEY in Script Properties.");
    return;
  }

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
  if (!sheet) { Logger.log(CONFIG.INDUSTRIAL_SHEET_NAME + " tab not found."); return; }

  const lastRow = sheet.getLastRow();
  if (GEO_START_ROW > lastRow) {
    if (!silent) SpreadsheetApp.getUi().alert("No data found starting at row " + GEO_START_ROW);
    return;
  }

  const cols = resolveCompCols_(sheet);
  const numRows = lastRow - GEO_START_ROW + 1;

  function colValues(name) {
    const c = cols.col(name);
    if (!c) return null;
    return sheet.getRange(GEO_START_ROW, c, numRows, 1).getValues();
  }

  const addresses = sheet.getRange(GEO_START_ROW, requireCol_(cols, F.ADDRESS), numRows, 1).getValues();
  const cities = colValues(F.CITY);
  const states = colValues(F.STATE);
  const zips   = colValues(F.ZIP);
  const latRange = sheet.getRange(GEO_START_ROW, requireCol_(cols, F.LAT), numRows, 1);
  const lngRange = sheet.getRange(GEO_START_ROW, requireCol_(cols, F.LNG), numRows, 1);
  const existingLat = latRange.getValues();
  const existingLng = lngRange.getValues();

  function cell(arr, i) { return arr ? String(arr[i][0] || "").trim() : ""; }

  const rowsFilter = opts && opts.rows ? new Set(opts.rows) : null;
  const started = Date.now();
  let geocoded = 0, skipped = 0, failed = 0, timedOut = false;
  const failedAddresses = [];

  for (let i = 0; i < addresses.length; i++) {
    if (Date.now() - started > GEO_MAX_RUNTIME_MS) { timedOut = true; break; }

    const sheetRow = i + GEO_START_ROW;
    if (rowsFilter && !rowsFilter.has(sheetRow)) { skipped++; continue; }

    const address = String(addresses[i][0] || "").trim();
    if (address === "") { skipped++; continue; }

    const existing = existingLat[i][0];
    const isNotFound = existing === "NOT FOUND";
    if (!isBlank_(existing) && !(isNotFound && retryNotFound)) { skipped++; continue; }

    const fullAddress = buildFullAddress_(address, cell(cities, i), cell(states, i), cell(zips, i));
    const result = geocodeAddress_(fullAddress);

    if (result) {
      existingLat[i][0] = result.lat;
      existingLng[i][0] = result.lng;
      geocoded++;
    } else {
      existingLat[i][0] = "NOT FOUND";
      existingLng[i][0] = "NOT FOUND";
      failedAddresses.push("Row " + sheetRow + ": " + fullAddress);
      failed++;
    }

    if ((geocoded + failed) % 25 === 0) {
      latRange.setValues(existingLat);
      lngRange.setValues(existingLng);
      SpreadsheetApp.flush();
    }
    Utilities.sleep(GEO_DELAY_MS);
  }

  latRange.setValues(existingLat);
  lngRange.setValues(existingLng);
  SpreadsheetApp.flush();

  let msg = "Batch Geocode Complete!\n\nGeocoded: " + geocoded + "\nSkipped: " + skipped + "\nNot Found: " + failed;
  if (timedOut) msg += "\n\nStopped early at the runtime guard - run again to continue.";
  if (failedAddresses.length > 0 && failedAddresses.length <= 20) {
    msg += "\n\nFailed:\n" + failedAddresses.join("\n");
  }

  Logger.log(msg);
  if (!silent) SpreadsheetApp.getUi().alert(msg);
  else SpreadsheetApp.getActiveSpreadsheet().toast("Geocoded " + geocoded + ", skipped " + skipped + ", failed " + failed, "Geocoder", 4);
}

function runBatchGeocode() { runBatchGeocode_({ silent: false, retryNotFound: false }); }
function retryFailedGeocodes() { runBatchGeocode_({ silent: false, retryNotFound: true }); }

function clearLatLng() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.alert("Clear Lat/Lng", "Clear Lat/Lng columns on " + CONFIG.INDUSTRIAL_SHEET_NAME + " from row " + GEO_START_ROW + " down?", ui.ButtonSet.YES_NO);
  if (response !== ui.Button.YES) return;

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
  if (!sheet) { ui.alert(CONFIG.INDUSTRIAL_SHEET_NAME + " tab not found."); return; }

  const lastRow = sheet.getLastRow();
  if (lastRow < GEO_START_ROW) { ui.alert("No data."); return; }

  const cols = resolveCompCols_(sheet);
  const n = lastRow - GEO_START_ROW + 1;
  sheet.getRange(GEO_START_ROW, requireCol_(cols, F.LAT), n, 1).clearContent();
  sheet.getRange(GEO_START_ROW, requireCol_(cols, F.LNG), n, 1).clearContent();
  ui.alert("Cleared Lat/Lng from row " + GEO_START_ROW + " to " + lastRow);
}

function buildFullAddress_(address, city, state, zip) {
  const parts = [address];
  if (city !== "") parts.push(city);
  else parts.push(GEO_DEFAULT_CITY);

  // Use explicit state if provided, otherwise check if state is already in
  // the address/city string, otherwise fall back to default.
  if (state !== "") {
    parts.push(state);
  } else {
    const upper = (address + " " + city).toUpperCase();
    if (!/\b(TX|TEXAS)\b/.test(upper)) parts.push(GEO_DEFAULT_STATE);
  }

  if (zip !== "") parts.push(zip);

  return parts.join(", ");
}

function geocodeAddress_(address) {
  const url = "https://maps.googleapis.com/maps/api/geocode/json"
    + "?address=" + encodeURIComponent(address)
    + "&bounds=" + GEO_BOUNDS
    + "&region=us"
    + "&key=" + GEO_API_KEY;

  const options = { method: "get", muteHttpExceptions: true };

  function accept(data) {
    if (data.status !== "OK" || !data.results || data.results.length === 0) return null;
    const r = data.results[0];
    if (r.partial_match === true) {
      Logger.log("REJECTED partial match for " + address + " -> " + r.formatted_address);
      return null;
    }
    if (r.geometry.location_type === "APPROXIMATE") {
      Logger.log("REJECTED approximate for " + address + " -> " + r.formatted_address);
      return null;
    }
    return { lat: r.geometry.location.lat, lng: r.geometry.location.lng };
  }

  try {
    let data = JSON.parse(UrlFetchApp.fetch(url, options).getContentText());
    if (data.status === "OVER_QUERY_LIMIT") {
      Utilities.sleep(2000);
      data = JSON.parse(UrlFetchApp.fetch(url, options).getContentText());
    }
    const ok = accept(data);
    if (ok) return ok;
    Logger.log("Geocode failed for " + address + ": status=" + data.status);
  } catch (e) {
    Logger.log("Geocode error for " + address + ": " + e.message);
  }

  return null;
}

// =============================================================================
// DASHBOARD DATA PROXY (serves Industrial sheet to the dashboard)
// =============================================================================

// Read from Script Properties (Project Settings > Script Properties).
// Property name must be exactly: DASHBOARD_TOKEN
// Its value must match SHEET_TOKEN in the dashboard HTML.
const DASHBOARD_TOKEN = PropertiesService.getScriptProperties().getProperty("DASHBOARD_TOKEN");

function doGet(e) {
  const token    = e && e.parameter && e.parameter.token;
  const callback = e && e.parameter && e.parameter.callback;

  function respond(obj) {
    const json = JSON.stringify(obj);
    if (callback) {
      return ContentService.createTextOutput(callback + "(" + json + ")")
        .setMimeType(ContentService.MimeType.JAVASCRIPT);
    }
    return ContentService.createTextOutput(json)
      .setMimeType(ContentService.MimeType.JSON);
  }

  if (!DASHBOARD_TOKEN) return respond({ error: "Server token not configured. Add DASHBOARD_TOKEN in Script Properties." });
  if (token !== DASHBOARD_TOKEN) return respond({ error: "Unauthorized" });

  try {
    const ss    = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(CONFIG.INDUSTRIAL_SHEET_NAME);
    if (!sheet) throw new Error("Tab '" + CONFIG.INDUSTRIAL_SHEET_NAME + "' not found");

    const data = sheet.getDataRange().getValues();
    if (data.length < 2) return respond({ headers: [], rows: [] });

    const headers = data[0].map(String);
    const rows = [];
    for (let i = 1; i < data.length; i++) {
      const obj = {};
      headers.forEach(function (h, j) {
        const v = data[i][j];
        obj[h] = isBlank_(v) ? "" : v;
      });
      rows.push(obj);
    }
    // headers is echoed so the dashboard can render new schema fields without
    // a code change on its side.
    return respond({ headers: headers, rows: rows });

  } catch (err) {
    return respond({ error: err.message });
  }
}
