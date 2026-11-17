/**
 * FirebasePublisher.gs — Austin Office Options (HR Green)
 *
 * Publishes this Google Sheet to Firebase Realtime Database at /datasets/<FB_DATASET>/
 * so the Cresa map page can read it after login. The sheet itself stays private.
 *
 * Tabs it reads:
 *   1. Listings        — the first tab (or LISTINGS_TAB). One row per building.
 *   2. Employees       — HR Green roster (home address, department, office). OPTIONAL.
 *   3. Competitors     — competitor offices (name + address). OPTIONAL.
 *   4. Current Offices — HR Green's existing Austin offices (Name, Address, Code). OPTIONAL.
 *
 * Tabs 2–4 are geocoded here, inside your Google account: the script adds Latitude /
 * Longitude columns and fills any blanks. Rows that already have coordinates are skipped.
 *
 * Employee privacy: only ZIP, department, office and a location rounded to ~1 km are
 * published. Names and street addresses never leave the sheet.
 *
 * Setup (one time):
 *   1. Project Settings > Script Properties > add  FB_SECRET = <database secret>
 *   2. Run  publishToFirebase  once and approve the permissions.
 *   3. Run  installTrigger  once (publishes every 15 minutes and after edits).
 */

// ---- CONFIG ---------------------------------------------------------------
const FB_DB_URL  = "https://project-bf670308-68bc-4a62-863-default-rtdb.firebaseio.com";
const FB_DATASET = "aus-office-hrgreen";   // must match FIREBASE_DATASET in the HTML page
const LISTINGS_TAB = "";                   // listings tab name; "" = first tab
const HEADER_ROW = 1;                      // header row on every tab
const EMPLOYEES_TAB = "Employees";
const COMPETITORS_TAB = "Competitors";
const OFFICES_TAB = "Current Offices";
const EMPLOYEE_ROUNDING = 2;               // decimals kept on employee lat/lng (2 ≈ 1 km)
// ---------------------------------------------------------------------------

function publishToFirebase() {
  const secret = PropertiesService.getScriptProperties().getProperty("FB_SECRET");
  if (!secret) throw new Error("Add FB_SECRET in Project Settings > Script Properties first.");

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tz = ss.getSpreadsheetTimeZone();
  const sh = LISTINGS_TAB ? ss.getSheetByName(LISTINGS_TAB) : ss.getSheets()[0];
  if (!sh) throw new Error('Tab "' + LISTINGS_TAB + '" not found.');

  const values = sh.getDataRange().getValues();
  const headers = values[HEADER_ROW - 1].map(function (h) { return String(h).trim(); });
  const rows = values.slice(HEADER_ROW)
    .filter(function (r) { return r.some(function (c) { return c !== "" && c !== null; }); })
    .map(function (r) {
      return r.map(function (c) { return c instanceof Date ? Utilities.formatDate(c, tz, "yyyy-MM-dd") : c; });
    });

  const layers = {
    employees: readEmployees_(ss),
    competitors: readPlaces_(ss, COMPETITORS_TAB),
    offices: readPlaces_(ss, OFFICES_TAB),
  };

  const payload = JSON.stringify({ headers: headers, rows: rows, layers: layers });
  const hash = Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, payload));
  const now = Date.now();
  const base = FB_DB_URL + "/datasets/" + encodeURIComponent(FB_DATASET) + "/";
  const auth = "?auth=" + encodeURIComponent(secret);

  const current = JSON.parse(UrlFetchApp.fetch(base + "meta.json" + auth).getContentText() || "null");
  if (current && current.hash === hash) {
    put_(base + "meta/checkedAt.json" + auth, now);
    Logger.log("No changes. %s buildings, %s employees, %s competitors, %s offices.",
      rows.length, layers.employees.length, layers.competitors.length, layers.offices.length);
    return;
  }
  // Data first, then meta, so meta never points at data that isn't there yet.
  put_(base + "data.json" + auth, payload);
  put_(base + "meta.json" + auth, { hash: hash, updatedAt: now, checkedAt: now, rowCount: rows.length });
  Logger.log("Published %s buildings, %s employees, %s competitors, %s offices to %s.",
    rows.length, layers.employees.length, layers.competitors.length, layers.offices.length, FB_DATASET);
}

// ---------- tab readers ----------

function readEmployees_(ss) {
  const t = readGeoTab_(ss, EMPLOYEES_TAB);
  if (!t) return [];
  const zipCol = findCol_(t.headers, [/zip/i, /postal/i]);
  const deptCol = findCol_(t.headers, [/home department/i, /^department$/i, /^dept/i, /^team$/i, /group/i]);
  const officeCol = findCol_(t.headers, [/^location$/i, /^office$/i, /current office/i]);
  const unitCol = findCol_(t.headers, [/business unit/i]);
  const p = Math.pow(10, EMPLOYEE_ROUNDING);
  return t.rows.filter(function (r) { return r.lat != null; }).map(function (r) {
    return {
      zip: zipCol >= 0 ? String(r.cells[zipCol]).trim().slice(0, 5) : "",
      dept: deptCol >= 0 ? cleanDept_(r.cells[deptCol]) : "",
      office: officeCol >= 0 ? String(r.cells[officeCol]).trim() : "",
      unit: unitCol >= 0 ? String(r.cells[unitCol]).trim() : "",
      lat: Math.round(r.lat * p) / p,
      lng: Math.round(r.lng * p) / p,
    };
  });
}

function readPlaces_(ss, tabName) {
  const t = readGeoTab_(ss, tabName);
  if (!t) return [];
  const nameCol = findCol_(t.headers, [/^name$/i, /company/i, /firm/i, /^first name$/i, /office name/i]);
  const typeCol = findCol_(t.headers, [/^type$/i, /category/i]);
  const codeCol = findCol_(t.headers, [/^code$/i, /^location$/i]);
  const noteCol = findCol_(t.headers, [/note/i]);
  return t.rows.filter(function (r) { return r.lat != null; }).map(function (r) {
    return {
      name: nameCol >= 0 ? String(r.cells[nameCol]).trim() : r.address,
      address: r.address,
      type: typeCol >= 0 ? String(r.cells[typeCol]).trim() : "",
      code: codeCol >= 0 ? String(r.cells[codeCol]).trim() : "",
      note: noteCol >= 0 ? String(r.cells[noteCol]).trim() : "",
      lat: r.lat, lng: r.lng,
    };
  });
}

/** Reads a tab, builds a one-line address per row, geocodes blanks and writes coordinates back. */
function readGeoTab_(ss, tabName) {
  const sh = ss.getSheetByName(tabName);
  if (!sh || sh.getLastRow() <= HEADER_ROW) return null;
  let headers = sh.getRange(HEADER_ROW, 1, 1, sh.getLastColumn()).getValues()[0].map(function (h) { return String(h).trim(); });

  // Make sure Latitude / Longitude columns exist.
  let latCol = headers.indexOf("Latitude"), lngCol = headers.indexOf("Longitude");
  if (latCol < 0) { sh.getRange(HEADER_ROW, headers.length + 1).setValue("Latitude"); headers.push("Latitude"); latCol = headers.length - 1; }
  if (lngCol < 0) { sh.getRange(HEADER_ROW, headers.length + 1).setValue("Longitude"); headers.push("Longitude"); lngCol = headers.length - 1; }

  const n = sh.getLastRow() - HEADER_ROW;
  const cells = sh.getRange(HEADER_ROW + 1, 1, n, headers.length).getValues();
  const full = findCol_(headers, [/^full address$/i, /^address$/i]);
  const street = findCol_(headers, [/address line 1/i, /street address/i, /^street$/i, /^address 1$/i]);
  const city = findCol_(headers, [/city/i]);
  const state = findCol_(headers, [/state/i]);
  const zip = findCol_(headers, [/zip/i, /postal/i]);

  const geocoder = Maps.newGeocoder().setRegion("us");
  const out = [];
  let geocoded = 0;
  cells.forEach(function (c, i) {
    if (!c.some(function (v) { return v !== "" && v !== null; })) return;
    let address = full >= 0 && String(c[full]).trim() ? String(c[full]).trim()
      : [street, city, state, zip].filter(function (k) { return k >= 0 && String(c[k]).trim(); })
          .map(function (k) { return String(c[k]).trim(); }).join(", ");
    if (!address) return;
    let lat = num_(c[latCol]), lng = num_(c[lngCol]);
    if ((lat == null || lng == null) && geocoded < 300) {
      try {
        const res = geocoder.geocode(address);
        if (res.status === "OK" && res.results.length) {
          lat = res.results[0].geometry.location.lat;
          lng = res.results[0].geometry.location.lng;
          sh.getRange(HEADER_ROW + 1 + i, latCol + 1, 1, 2).setValues([[lat, lng]]);
        } else {
          Logger.log('%s row %s: could not geocode "%s" (%s)', tabName, HEADER_ROW + 1 + i, address, res.status);
        }
      } catch (e) {
        Logger.log("%s row %s: geocode error %s", tabName, HEADER_ROW + 1 + i, e);
      }
      geocoded++;
      Utilities.sleep(120);
    }
    out.push({ cells: c, address: address, lat: lat, lng: lng });
  });
  return { headers: headers, rows: out };
}

// ---------- helpers ----------

function findCol_(headers, patterns) {
  for (let p = 0; p < patterns.length; p++) {
    for (let i = 0; i < headers.length; i++) if (patterns[p].test(headers[i])) return i;
  }
  return -1;
}
function num_(v) { const n = typeof v === "number" ? v : parseFloat(v); return isFinite(n) ? n : null; }
/** "16-912 - Land Development  Austin" -> "Land Development Austin" */
function cleanDept_(v) { return String(v).replace(/^[\d-]+\s*-\s*/, "").replace(/\s+/g, " ").trim(); }

function put_(url, value) {
  const res = UrlFetchApp.fetch(url, {
    method: "put", contentType: "application/json", payload: JSON.stringify(value), muteHttpExceptions: true,
  });
  if (res.getResponseCode() >= 300) throw new Error("Firebase write failed (" + res.getResponseCode() + "): " + res.getContentText());
}

/** Run once. Publishes every 15 minutes and shortly after edits. */
function installTrigger() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === "publishToFirebase") ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger("publishToFirebase").timeBased().everyMinutes(15).create();
  ScriptApp.newTrigger("publishToFirebase").forSpreadsheet(SpreadsheetApp.getActive()).onEdit().create();
}
