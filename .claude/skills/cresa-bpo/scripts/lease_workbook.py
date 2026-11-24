"""Lease snapshot + cash flow pro forma workbook for leased BPO sites (one tab per site, plus Summary and Example).

  python lease_workbook.py lease_sites.json Lease_Pro_Forma.xlsx
  python <xlsx skill>/scripts/recalc.py Lease_Pro_Forma.xlsx 60      # always recalc before reading values

lease_sites.json (see templates/lease_sites_template.json):
  {"title": "...", "subtitle": "...", "analysis_date": "2027-01-01",
   "sites": [{"tab": "Short Tab", "address": "123 Main St, City, TX 77000", "premises": "Suite 100", "landlord": "...",
              "rsf": 2500, "commencement": "2020-06-01" | null, "expiration": "2030-08-31" | null, "notes": "..."}]}

Yellow cells (blue text) are inputs; escalations apply on each anniversary of the original commencement date.
The Example tab reproduces the Leased Property BOV template math (base rent $609,882 over 9/12/12/12/3 months).
"""
import datetime as dt, json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment

CFG = json.load(open(sys.argv[1])); OUT = sys.argv[2]
def _d(v): return dt.date.fromisoformat(v) if v else None
F = "Arial"
NAVY = "1F2A44"
def font(**k): return Font(name=F, size=k.pop("size", 10), **k)
BLUE = font(color="0000FF"); BLACK = font(); GREEN = font(color="008000"); BOLD = font(bold=True)
HDR = font(bold=True, color="FFFFFF"); TITLE = font(bold=True, size=14, color=NAVY)
YEL = PatternFill("solid", fgColor="FFFF00"); NAVYF = PatternFill("solid", fgColor=NAVY); GRAY = PatternFill("solid", fgColor="EEF0F4")
thin = Side(style="thin", color="BFC5D0"); BOT = Border(bottom=thin)
CUR = '$#,##0;($#,##0);"-"'; MO = '#,##0.0;(#,##0.0);"-"'; CUR2 = '$#,##0.00;($#,##0.00);"-"'; PCT = '0.0%;(0.0%);"-"'; DATE = "mm/dd/yyyy"; NUM = '#,##0;(#,##0);"-"'
MAXP = 18  # pro forma periods

SITES = [(s["tab"], s["address"], s.get("premises", ""), s.get("landlord", ""), s.get("rsf"), _d(s.get("commencement")), _d(s.get("expiration")), s.get("notes", ""))
         for s in CFG["sites"]]
TERMS = {s["tab"]: s for s in CFG["sites"]}  # optional lease terms per site (keys match the input labels' keys, plus "schedule")
EXAMPLE = ("Example", "100 Example Ave, Anytown, TX 77000", "Suite 200", "Example Landlord LLC", 3107, dt.date(2020, 6, 1), dt.date(2030, 8, 31),
           "Example only: inputs from the Leased Property BOV template (Lease Summary dated 9/1/2026).")

wb = Workbook()
S = wb.active; S.title = "Summary"

INPUTS = [  # row label, key, fmt, comment
 ("Property Address", "addr", None), ("Premises", "suite", None), ("Landlord", "ll", None),
 ("Analysis Date", "adate", DATE), ("Original Lease Commencement", "comm", DATE), ("Lease Expiration", "exp", DATE),
 ("Rentable SF (RSF)", "rsf", NUM), ("Current Base Rent / RSF / Yr", "rent", CUR2), ("Annual Rent Escalation", "esc", PCT),
 ("Operating Expense Pass-Through / RSF / Yr (Year 1)", "opex", CUR2), ("Operating Expense Annual Growth", "og", PCT),
 ("Lease Type", "type", None), ("Free Rent Remaining (Months)", "free", NUM),
 ("Renewal Options", "ren", None), ("Termination Option", "term", None), ("ROFR / ROFO", "rofr", None),
 ("Holdover", "hold", None), ("Sublease / Assignment", "sub", None), ("Cresa Market Rent Opinion / RSF / Yr", "mkt", CUR2), ("Notes / Source", "notes", None),
]
R0 = 5  # first input row

def site_tab(name, addr, suite, ll, rsf, comm, exp, notes, example=False):
    ws = wb.create_sheet(name)
    ws.column_dimensions["A"].width = 44; ws.column_dimensions["B"].width = 30
    for c in "CDEFGHIJK": ws.column_dimensions[c].width = 15
    ws["A1"] = f"Lease Snapshot and Cash Flow Pro Forma: {addr.split(',')[0]}"; ws["A1"].font = TITLE
    ws["A2"] = "Yellow cells are inputs (blue text). Everything else is calculated." if not example else "EXAMPLE ONLY: template inputs to show the expected format and check the math (base rent ties to the template's $609,882)."
    ws["A2"].font = font(italic=True, color="555555")
    ws.cell(R0 - 1, 1, "LEASE INPUTS").font = BOLD
    ref = {}
    ex = {"adate": dt.date(2026, 9, 1), "rent": 46.57, "esc": 0.03, "opex": 6.58, "og": 0.03, "type": "Modified Gross", "free": 0,
          "ren": "Two 5-year options (9/1/30-8/31/35; 9/1/35-8/31/40)", "term": "N/A", "rofr": "N/A", "hold": "150%",
          "sub": "Allowed with Landlord consent", "mkt": 46.57}
    for i, (lab, key, fmt) in enumerate(INPUTS):
        r = R0 + i; ref[key] = f"$B${r}"
        ws.cell(r, 1, lab).font = BLACK
        c = ws.cell(r, 2)
        val = {"addr": addr, "suite": suite, "ll": ll, "rsf": rsf, "comm": comm, "exp": exp, "notes": notes}.get(key)
        if example and key in ex: val = ex[key]
        terms = {} if example else TERMS.get(name, {}).get("terms", {})
        if key in terms: val = terms[key]
        if key == "adate" and not example:
            c.value = "=Summary!$C$4"; c.font = GREEN
        else:
            c.value = val; c.font = BLUE; c.fill = YEL
        if fmt: c.number_format = fmt
        c.alignment = Alignment(horizontal="right" if fmt else "left", wrap_text=(key in ("notes", "ren")))
        c.border = BOT; ws.cell(r, 1).border = BOT
    # optional fixed rent schedule (overrides the annual escalation when any start date is entered)
    ws.cell(R0 - 1, 4, "RENT SCHEDULE (optional; overrides escalation)").font = BOLD
    for j, h in enumerate(("Start Date", "Base Rent / RSF / Yr")):
        c = ws.cell(R0, 4 + j, h); c.font = HDR; c.fill = NAVYF; c.alignment = Alignment(horizontal="center", wrap_text=True)
    NS = 8
    for i in range(NS):
        for j, fmt in enumerate((DATE, CUR2)):
            c = ws.cell(R0 + 1 + i, 4 + j); c.font = BLUE; c.fill = YEL; c.number_format = fmt; c.border = BOT
    for i, (d0, rr) in enumerate(([] if example else TERMS.get(name, {}).get("schedule", []))[:NS]):
        ws.cell(R0 + 1 + i, 4).value = _d(d0); ws.cell(R0 + 1 + i, 5).value = rr
    SD, SR = f"$D${R0 + 1}:$D${R0 + NS}", f"$E${R0 + 1}:$E${R0 + NS}"
    ws.cell(R0 + 1 + NS, 4, "Rent in effect from each start date until the next. Leave blank to use the escalation.").font = font(italic=True, color="555555", size=9)
    ws.cell(ref and int(ref["notes"][3:]), 2).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[int(ref["notes"][3:])].height = 42
    ws[ref["adate"].replace("$", "")].comment = Comment("Linked to the portfolio Analysis Date on the Summary tab. Overwrite here only for a site-specific date.", "Cresa")
    ws[ref["rent"].replace("$", "")].comment = Comment("Contract base rent in effect on the Analysis Date. Escalations apply on each anniversary of the original commencement date.", "Cresa")
    ws[ref["opex"].replace("$", "")].comment = Comment("Tenant-paid operating expenses, taxes, insurance, CAM, parking. For a full service lease enter 0 (included in base rent).", "Cresa")
    ws[ref["mkt"].replace("$", "")].comment = Comment("Cresa's market rent opinion from the BOV Market Value page, on the same lease-type basis as the contract rent.", "Cresa")
    B = ref
    # ---- pro forma (built first so the summary can reference it)
    P0 = R0 + len(INPUTS) + 16  # header row of pro forma
    hdrs = ["Period", "From", "To", "Months", "Base Rent / RSF", "Base Rent", "Free Rent Months", "Additional Expenses", "Total Cash Cost", "Avg Monthly Cost", "Annualized Cost / RSF"]
    ws.cell(P0 - 1, 1, "CASH FLOW PRO FORMA (by lease year from the Analysis Date)").font = BOLD
    # helper: completed lease years at analysis date
    H = P0 - 3
    ws.cell(H, 1, "Lease years completed at Analysis Date (helper)").font = font(color="777777", italic=True)
    ws.cell(H, 2, f'=IF(OR({B["comm"]}="",{B["adate"]}=""),"",DATEDIF({B["comm"]},{B["adate"]},"y"))').font = BLACK
    HB = f"$B${H}"
    cols = "ABCDEFGHIJK"
    # header row: use columns A..K but A is wide label col; put Period in A
    for j, h in enumerate(hdrs):
        c = ws.cell(P0, j + 1, h); c.font = HDR; c.fill = NAVYF; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[P0].height = 30
    ok = f'AND({B["adate"]}<>"",{B["comm"]}<>"",{B["exp"]}<>"",{B["rsf"]}<>"",{B["rent"]}<>"",{B["exp"]}>={B["adate"]})'
    for k in range(1, MAXP + 1):
        r = P0 + k; prev = r - 1
        ws.cell(r, 1, k).font = BLACK; ws.cell(r, 1).alignment = Alignment(horizontal="center")
        if k == 1:
            frm = f'=IF({ok},{B["adate"]},"")'
        else:
            frm = f'=IF(B{prev}="","",IF(EDATE({B["comm"]},12*({HB}+{k - 1}))>{B["exp"]},"",EDATE({B["comm"]},12*({HB}+{k - 1}))))'
        ws.cell(r, 2, frm)
        ws.cell(r, 3, f'=IF(B{r}="","",MIN(EDATE({B["comm"]},12*({HB}+{k}))-1,{B["exp"]}))')
        m = f'DATEDIF(B{r},C{r}+1,"m")'
        ws.cell(r, 4, f'=IF(B{r}="","",{m}+(C{r}+1-EDATE(B{r},{m}))/(EDATE(B{r},{m}+1)-EDATE(B{r},{m})))')  # whole months + partial month
        esc_rent = f'{B["rent"]}*(1+N({B["esc"]}))^({k}-1)'
        sched = f'INDEX({SR},MATCH(SUMPRODUCT(MAX(({SD}<>"")*({SD}<=B{r})*{SD})),{SD},0))'
        ws.cell(r, 5, f'=IF(B{r}="","",IF(COUNT({SD})=0,{esc_rent},IFERROR({sched},{B["rent"]})))')
        cum = "0" if k == 1 else f"SUM($D${P0 + 1}:D{prev})"
        ws.cell(r, 7, f'=IF(B{r}="","",MAX(0,MIN(D{r},N({B["free"]})-{cum})))')
        ws.cell(r, 6, f'=IF(B{r}="","",E{r}*{B["rsf"]}/12*(D{r}-G{r}))')
        ws.cell(r, 8, f'=IF(B{r}="","",N({B["opex"]})*(1+N({B["og"]}))^({k}-1)*{B["rsf"]}/12*D{r})')
        ws.cell(r, 9, f'=IF(B{r}="","",F{r}+H{r})')
        ws.cell(r, 10, f'=IF(OR(B{r}="",N(D{r})=0),"",I{r}/D{r})')
        ws.cell(r, 11, f'=IF(OR(B{r}="",N(D{r})=0),"",I{r}/D{r}*12/{B["rsf"]})')
        for j, fmt in zip(range(2, 12), [DATE, DATE, MO, CUR2, CUR, MO, CUR, CUR, CUR, CUR2]):
            c = ws.cell(r, j); c.number_format = fmt; c.font = BLACK; c.border = BOT
            if k % 2 == 0: c.fill = GRAY
        if k % 2 == 0: ws.cell(r, 1).fill = GRAY
    T = P0 + MAXP + 1
    ws.cell(T, 1, "TOTAL").font = BOLD
    for j, col in ((4, "D"), (6, "F"), (7, "G"), (8, "H"), (9, "I")):
        c = ws.cell(T, j, f"=SUM({col}{P0 + 1}:{col}{P0 + MAXP})"); c.font = BOLD; c.number_format = MO if col in "DG" else CUR
    ws.cell(T + 1, 1, f"Pro forma covers up to {MAXP} lease-year periods. Months include partial months (e.g. 9.9) so a mid-month analysis date prorates the first period.").font = font(italic=True, color="555555", size=9)
    # ---- lease summary
    L0 = R0 + len(INPUTS) + 1
    ws.cell(L0, 1, "LEASE SUMMARY (calculated)").font = BOLD
    rng = lambda col: f"{col}{P0 + 1}:{col}{P0 + MAXP}"
    rows = [
     ("Remaining Lease Term (Months)", f'=IF(AND({B["adate"]}<>"",{B["exp"]}<>"",{B["exp"]}>={B["adate"]}),DATEDIF({B["adate"]},{B["exp"]}+1,"m")+({B["exp"]}+1-EDATE({B["adate"]},DATEDIF({B["adate"]},{B["exp"]}+1,"m")))/(EDATE({B["adate"]},DATEDIF({B["adate"]},{B["exp"]}+1,"m")+1)-EDATE({B["adate"]},DATEDIF({B["adate"]},{B["exp"]}+1,"m"))),"")', NUM),
     ("Year 1 Gross Rent / RSF (Base + Expenses)", f'=IF({B["rent"]}="","",{B["rent"]}+N({B["opex"]}))', CUR2),
     ("Total Base Rent (Less Free Rent)", f"=SUM({rng('F')})", CUR),
     ("Total Additional Expenses", f"=SUM({rng('H')})", CUR),
     ("TOTAL REMAINING CASH LEASE COST", f"=SUM({rng('I')})", CUR),
     ("Average Annual Cost", f'=IF(OR(N(B{L0 + 1})=0,N(B{L0 + 5})=0),"",B{L0 + 5}/B{L0 + 1}*12)', CUR),
     ("Average Monthly Cost", f'=IF(OR(N(B{L0 + 1})=0,N(B{L0 + 5})=0),"",B{L0 + 5}/B{L0 + 1})', CUR),
     ("Average Annual Cost / RSF", f'=IF(OR(B{L0 + 6}="",N({B["rsf"]})=0),"",B{L0 + 6}/{B["rsf"]})', CUR2),
     ("Contract Rent vs. Market Opinion", f'=IF(OR(N({B["mkt"]})=0,{B["rent"]}=""),"",{B["rent"]}/{B["mkt"]}-1)', PCT),
     ("Contract Position", f'=IF(B{L0 + 9}="","",IF(B{L0 + 9}>0.025,"Above market",IF(B{L0 + 9}<-0.025,"Below market","At market")))', None),
     ("Annual Rent Difference vs. Market (Year 1)", f'=IF(B{L0 + 9}="","",({B["rent"]}-{B["mkt"]})*{B["rsf"]})', CUR),
    ]
    for i, (lab, f, fmt) in enumerate(rows):
        r = L0 + 1 + i
        ws.cell(r, 1, lab).font = BOLD if lab.startswith("TOTAL") else BLACK
        c = ws.cell(r, 2, f); c.font = BOLD if lab.startswith("TOTAL") else BLACK; c.border = BOT; ws.cell(r, 1).border = BOT
        c.alignment = Alignment(horizontal="right")
        if fmt: c.number_format = fmt
        if lab.startswith("TOTAL"): ws.cell(r, 1).fill = GRAY; c.fill = GRAY
    ws.cell(L0 + 13, 1, "Contract Position uses a +/-2.5% band around Cresa's market opinion.").font = font(italic=True, color="555555", size=9)
    ws.freeze_panes = "A4"
    return {"rsf": B["rsf"], "exp": B["exp"], "rent": B["rent"], "mkt": B["mkt"], "months": f"$B${L0 + 1}", "total": f"$B${L0 + 5}",
            "avg": f"$B${L0 + 6}", "vs": f"$B${L0 + 9}", "pos": f"$B${L0 + 10}", "addr": B["addr"], "comm": B["comm"]}

# ---- Summary tab
S.column_dimensions["A"].width = 22; S.column_dimensions["B"].width = 40
for c in "CDEFGHIJKL": S.column_dimensions[c].width = 15
S["A1"] = CFG.get("title", "Leased Locations: Lease Snapshot Summary"); S["A1"].font = TITLE
S["A2"] = CFG.get("subtitle", "Prepared by Cresa. Draft: lease terms pending."); S["A2"].font = font(italic=True, color="555555")
S["B4"] = "Portfolio Analysis Date"; S["B4"].font = BOLD
S["C4"] = _d(CFG.get("analysis_date")) or dt.date.today().replace(day=1); S["C4"].font = BLUE; S["C4"].fill = YEL; S["C4"].number_format = DATE
S["C4"].comment = Comment("Date the remaining obligation is measured from. Change as needed.", "Cresa")
heads = ["Tab", "Address", "RSF", "Commencement", "Expiration", "Remaining Months", "Contract Rent / RSF", "Market Opinion / RSF", "Contract vs. Market", "Position", "Remaining Cash Lease Cost", "Avg Annual Cost"]
for j, h in enumerate(heads):
    c = S.cell(6, j + 1, h); c.font = HDR; c.fill = NAVYF; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
S.row_dimensions[6].height = 32
r = 7
for site in SITES:
    ref = site_tab(*site)
    q = f"'{site[0]}'!"
    vals = [site[0], f"={q}{ref['addr']}", f"={q}{ref['rsf']}", f'=IF({q}{ref["comm"]}="","",{q}{ref["comm"]})', f'=IF({q}{ref["exp"]}="","",{q}{ref["exp"]})',
            f"={q}{ref['months']}", f'=IF({q}{ref["rent"]}="","",{q}{ref["rent"]})', f'=IF({q}{ref["mkt"]}="","",{q}{ref["mkt"]})', f"={q}{ref['vs']}", f"={q}{ref['pos']}",
            f"={q}{ref['total']}", f"={q}{ref['avg']}"]
    fmts = [None, None, NUM, DATE, DATE, NUM, CUR2, CUR2, PCT, None, CUR, CUR]
    for j, (v, fm) in enumerate(zip(vals, fmts)):
        c = S.cell(r, j + 1, v); c.font = BLACK if j == 0 else GREEN; c.border = BOT
        if fm: c.number_format = fm
    r += 1
S.cell(r, 1, "TOTAL").font = BOLD
for col in ("C", "K", "L"):
    c = S[f"{col}{r}"]; c.value = f"=SUM({col}7:{col}{r - 1})"; c.font = BOLD; c.number_format = NUM if col == "C" else CUR
leg = r + 2
for i, t in enumerate([
    "How to use",
    "1. On each site tab, fill the yellow cells (blue text) from the lease or abstract: commencement, expiration, current base rent, escalation, expense pass-through, free rent and options.",
    "2. Enter Cresa's market rent opinion per site once lease comps are finalized; the tab compares contract rent to market.",
    "3. Escalations apply on each anniversary of the original commencement date; a fixed rent schedule (columns D:E) overrides them. Partial months are prorated.",
    "4. 'Example' holds the template's sample inputs to show the expected format; it is not part of the portfolio totals.",
    "Color key: blue text in yellow = input; black = formula; green = link from another tab."]):
    S.cell(leg + i, 1, t).font = BOLD if i == 0 else font(size=9)
S.freeze_panes = "A7"
site_tab(*EXAMPLE, example=True)
wb.save(OUT); print("saved", OUT)
