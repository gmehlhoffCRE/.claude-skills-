"""Copy lease figures from the recalculated lease workbook into each leased site's property.json (D["lease"]),
which adds the Lease Summary and Cash Flow Pro Forma pages and drops the Overhead Aerial page.

  python lease_to_json.py Lease_Pro_Forma.xlsx lease_map.json

lease_map.json maps property.json paths to workbook tab names: {"bpo_site1/property.json": "Main St", ...}.
Recalculate the workbook first (xlsx skill scripts/recalc.py); empty inputs render as TBD.
"""
import json, os, sys
from openpyxl import load_workbook
XL, MAP = sys.argv[1], json.load(open(sys.argv[2]))
wb = load_workbook(XL, data_only=True)
def blank(v): return v is None or v == ""
def d(v): return v.strftime("%m/%d/%Y") if hasattr(v, "strftime") else ("TBD" if blank(v) else str(v))
def m(v, dec=0): return "TBD" if blank(v) else (f"${v:,.{dec}f}")
def fmt_mo(v): return f"{v:,.0f}" if abs(v - round(v)) < 0.05 else f"{v:,.1f}"
def pct(v): return "TBD" if blank(v) else f"{v * 100:.1f}%"
def txt(v): return "TBD" if blank(v) else str(v)

def read(ws):
    lab = {}
    for r in range(1, ws.max_row + 1):
        a = ws.cell(r, 1).value
        if isinstance(a, str) and a not in lab: lab[a] = (r, ws.cell(r, 2).value)
    return lab

for p, tab in MAP.items():
    D = json.load(open(p))
    ws = wb[tab]; L = read(ws); g = lambda k: L[k][1]
    D["skip_aerial"] = True
    rsf = g("Rentable SF (RSF)")
    nox = blank(g("Operating Expense Pass-Through / RSF / Yr (Year 1)"))  # pass-through amount not provided
    sched = []  # fixed rent steps from the RENT SCHEDULE block (columns D:E)
    for r in range(1, 20):
        if ws.cell(r, 4).value and str(ws.cell(r, 4).value).startswith("RENT SCHEDULE"):
            for rr in range(r + 2, r + 10):
                dv, rv = ws.cell(rr, 4).value, ws.cell(rr, 5).value
                if hasattr(dv, "year") and rv not in (None, ""): sched.append((dv, rv))
            break
    ad = g("Analysis Date")
    if sched and hasattr(ad, "year"):  # show only the step in effect at the analysis date and later steps
        cur = [i for i, (dv, _) in enumerate(sched) if dv <= ad]
        sched = sched[cur[-1]:] if cur else sched
    if sched:
        esc_txt = "\n".join(f"{m(rv, 2)} from {d(dv)}" for dv, rv in sched)
    else:
        e = g("Annual Rent Escalation")
        flat = not blank(e) and e == 0 and not blank(g("Current Base Rent / RSF / Yr"))
        esc_txt = "TBD" if blank(e) else ("None (flat rent)" if flat else f'{pct(e)} per year')
    rows = [["Analysis Date", d(g("Analysis Date"))], ["Lease Expiration", d(g("Lease Expiration"))],
            ["Remaining Lease Term", "TBD" if blank(g("Remaining Lease Term (Months)")) else f'{round(g("Remaining Lease Term (Months)")):,} Months'],
            ["Rentable Square Feet (RSF)", "TBD" if blank(rsf) else f"{rsf:,}"],
            ["Year 1 Base Rent / RSF", m(g("Current Base Rent / RSF / Yr"), 2)],
            ["Year 1 Operating Expense Pass-Through / RSF", "TBD" if nox else m(g("Operating Expense Pass-Through / RSF / Yr (Year 1)"), 2)],
            ["Year 1 Gross Rent / RSF", "TBD" if nox else m(g("Year 1 Gross Rent / RSF (Base + Expenses)"), 2)],
            ["Rent Schedule / RSF" if sched else "Annual Escalations", esc_txt],
            ["Lease Type", txt(g("Lease Type"))],
            ["Total Base Rent (Less Free Rent)", m(g("Total Base Rent (Less Free Rent)")) if g("Total Base Rent (Less Free Rent)") else "TBD"],
            ["Total Operating Expenses", m(g("Total Additional Expenses")) if g("Total Base Rent (Less Free Rent)") and not nox else "TBD"],
            ["TOTAL CASH LEASE COST" if not nox else "TOTAL BASE RENT OBLIGATION", m(g("TOTAL REMAINING CASH LEASE COST")) if g("TOTAL REMAINING CASH LEASE COST") else "TBD"],
            ["Average Annual Cost", m(g("Average Annual Cost"))], ["Average Monthly Cost", m(g("Average Monthly Cost"))],
            ["Average Annual Cost / RSF", m(g("Average Annual Cost / RSF"), 2)]]
    # Notes carry what the summary table does not: premises/landlord, term history, lease rights and site context.
    # Expiration, escalations, remaining term and costs live in the table, so they are not repeated here.
    notes = []
    prem, ll = g("Premises"), g("Landlord")
    parts = [str(prem)] if not blank(prem) else []
    if not blank(ll): parts.append(f"leased from {ll}")
    if parts:
        line = ", ".join(parts)
        notes.append(line[:1].upper() + line[1:] + ("" if line.endswith(".") else "."))
    comm, exp = g("Original Lease Commencement"), g("Lease Expiration")
    if hasattr(comm, "year"):
        line = f"Original lease commenced {d(comm)}"
        if hasattr(exp, "year"):
            months = (exp.year - comm.year) * 12 + exp.month - comm.month + 1
            y, mo = divmod(months, 12)
            line += f" ({y}-year term)" if not mo else (f" ({y}-year, {mo}-month term)" if y else f" ({mo}-month term)")
        notes.append(D.get("lease_term_note") or (line + "."))  # property.json can describe term history in its own words
    pending = [] if hasattr(comm, "year") else ["commencement date"]
    for key, label in [("Renewal Options", "renewal options"), ("Termination Option", "termination option"), ("ROFR / ROFO", "ROFR / ROFO"),
                       ("Holdover", "holdover"), ("Sublease / Assignment", "sublease / assignment")]:
        v = g(key)
        if blank(v): pending.append(label)
        else: notes.append(f"{label[:1].upper() + label[1:]}: {v}.")
    fr = g("Free Rent Remaining (Months)")
    if not blank(fr) and fr: notes.append(f"Free rent remaining: {fr:g} months.")
    if not blank(g("Notes / Source")): notes.append(str(g("Notes / Source")))
    if blank(g("Current Base Rent / RSF / Yr")): pending.append("rent schedule")
    if pending:
        notes.append("Pending from lease abstract: " + ", ".join(pending) + ".")
    pos, vs = g("Contract Position"), g("Contract Rent vs. Market Opinion")
    if blank(pos):
        op = ("[Lease opinion to come once lease comparables are finalized.]" if not blank(g("Current Base Rent / RSF / Yr"))
              else "[Lease opinion to come once lease comparables are finalized and the current lease terms are confirmed.]")
    else:
        op = (f"The current contract rent of {m(g('Current Base Rent / RSF / Yr'), 2)}/RSF is {abs(vs) * 100:.1f}% "
              f"{'above' if vs > 0 else 'below'} Cresa's market opinion of {m(g('Cresa Market Rent Opinion / RSF / Yr'), 2)}/RSF." if pos != "At market"
              else f"The current contract rent of {m(g('Current Base Rent / RSF / Yr'), 2)}/RSF is in line with current market conditions and nearby comparables.")
    # pro forma
    hr = L["Period"][0]; pf = []; tot = None
    for r in range(hr + 1, hr + 40):
        a = ws.cell(r, 1).value
        if a == "TOTAL":
            v = [ws.cell(r, c).value for c in range(1, 12)]
            if v[8]: tot = ["Total", "", "", f"{round(v[3]):,}", "", m(v[5]), "TBD" if nox else m(v[7]), m(v[8]), "", ""]
            break
        v = [ws.cell(r, c).value for c in range(1, 12)]
        if blank(v[1]): continue
        pf.append([str(v[0]), d(v[1]), d(v[2]), fmt_mo(v[3]), m(v[4], 2), m(v[5]), "TBD" if nox else m(v[7]), m(v[8]), m(v[9]), m(v[10], 2)])
    total = g("TOTAL REMAINING CASH LEASE COST")
    if D.get("lease_opinion"): op = D["lease_opinion"]  # report-specific opinion text set in property.json wins
    labels = D.get("lease_row_labels", {})  # report-specific relabels, e.g. {"Year 1 Operating Expense Pass-Through / RSF": "2026 Estimated Opex / RSF"}
    rows = [[labels.get(k, k), v] for k, v in rows]
    D["lease"] = {"as_of": d(g("Analysis Date")), "table_title": "Current Lease", "summary_rows": rows, "notes": notes, "opinion": op,
                  "pf_rows": pf or None, "pf_total": tot,
                  "pf_note": (f"Remaining {'base rent ' if nox else ''}lease obligation as of {d(g('Analysis Date'))} is {m(total)}. " + ("Current operating expense pass-throughs (CAM, taxes, insurance) were not provided and are excluded until received. " if nox else "") if total else "Lease terms pending; figures populate once the lease abstract is received. ")
                             + ("Base rent follows the lease's fixed rent schedule" if sched else ("Base rent is flat for the remaining term" if (not sched and g("Annual Rent Escalation") == 0) else "Base rent escalates on each anniversary of the original commencement date"))
                             + "; additional expenses include operating expense pass-throughs, taxes and insurance where applicable. A partial first period is prorated."}
    json.dump(D, open(p, "w"), indent=1, ensure_ascii=False)
    print(p, "lease pages:", "data" if pf else "TBD")
