/**
 * FirebasePublisher.gs — Austin Office Listings (HR Green)
 *
 * Publishes the listings tab of this Google Sheet to Firebase Realtime Database
 * at /datasets/<FB_DATASET>/ so the Cresa map page can read it after login.
 *
 *   /datasets/<FB_DATASET>/data  -> JSON string {headers:[...], rows:[[...], ...]}
 *   /datasets/<FB_DATASET>/meta  -> {hash, updatedAt, checkedAt, rowCount}
 *
 * Setup (one time):
 *   1. Project Settings > Script Properties > add  FB_SECRET = <database secret>
 *      (same secret the Houston sheet's script uses).
 *   2. Run  publishToFirebase  once and approve the permissions.
 *   3. Run  installTrigger  once to publish automatically every 15 minutes
 *      and whenever the sheet is edited.
 */

// ---- CONFIG ---------------------------------------------------------------
const FB_DB_URL  = "https://project-bf670308-68bc-4a62-863-default-rtdb.firebaseio.com";
const FB_DATASET = "aus-office-hrgreen";   // must match FIREBASE_DATASET in the HTML page
const SHEET_TAB  = "";                     // tab name; leave "" to use the first tab
const HEADER_ROW = 1;                      // row number that holds the column headers
// ---------------------------------------------------------------------------

function publishToFirebase() {
  const secret = PropertiesService.getScriptProperties().getProperty("FB_SECRET");
  if (!secret) throw new Error("Add FB_SECRET in Project Settings > Script Properties first.");

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = SHEET_TAB ? ss.getSheetByName(SHEET_TAB) : ss.getSheets()[0];
  if (!sh) throw new Error('Tab "' + SHEET_TAB + '" not found.');

  const values = sh.getDataRange().getValues();
  const headers = values[HEADER_ROW - 1].map(function (h) { return String(h).trim(); });
  const tz = ss.getSpreadsheetTimeZone();

  const rows = values.slice(HEADER_ROW)
    .filter(function (r) { return r.some(function (c) { return c !== "" && c !== null; }); })
    .map(function (r) {
      return r.map(function (c) {
        return c instanceof Date ? Utilities.formatDate(c, tz, "yyyy-MM-dd") : c;
      });
    });

  const payload = JSON.stringify({ headers: headers, rows: rows });
  const hash = Utilities.base64Encode(
    Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, payload));
  const now = Date.now();

  const base = FB_DB_URL + "/datasets/" + encodeURIComponent(FB_DATASET) + "/";
  const auth = "?auth=" + encodeURIComponent(secret);

  const current = JSON.parse(UrlFetchApp.fetch(base + "meta.json" + auth).getContentText() || "null");

  if (current && current.hash === hash) {
    // Nothing changed: just record that we checked.
    put_(base + "meta/checkedAt.json" + auth, now);
    Logger.log("No changes. %s rows.", rows.length);
    return;
  }

  // Data first, then meta, so meta never points at data that isn't there yet.
  put_(base + "data.json" + auth, payload);
  put_(base + "meta.json" + auth, { hash: hash, updatedAt: now, checkedAt: now, rowCount: rows.length });
  Logger.log("Published %s rows to %s.", rows.length, FB_DATASET);
}

function put_(url, value) {
  const res = UrlFetchApp.fetch(url, {
    method: "put",
    contentType: "application/json",
    payload: JSON.stringify(value),
    muteHttpExceptions: true,
  });
  if (res.getResponseCode() >= 300) {
    throw new Error("Firebase write failed (" + res.getResponseCode() + "): " + res.getContentText());
  }
}

/** Run once. Publishes every 15 minutes and shortly after edits. */
function installTrigger() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === "publishToFirebase") ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger("publishToFirebase").timeBased().everyMinutes(15).create();
  ScriptApp.newTrigger("publishToFirebase")
    .forSpreadsheet(SpreadsheetApp.getActive()).onEdit().create();
}
