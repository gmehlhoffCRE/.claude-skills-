"""Trifold: remove analytics promises (same approach as the bifold). Edits an unpacked IDML in place; run-count checked."""
import os, sys
from lxml import etree
root = sys.argv[1]
EDITS = {
    "u1628": ["POWERED BY CRESA CORE™"],
    "u12d6": ["Every Location, One View", "Never Miss Critical Dates", "Sites Compared Side by Side"],
    "u12ed": ["Audit-Ready Reporting", "Labor & Talent Insight", "AI Market Briefs"],
    "u12bf": ["Whether you lead a health system, physician group, outpatient network or healthcare company, industry "
              "disruption is changing not only how you deliver care, but where. Our specialists help you align real "
              "estate with your mission, building strategies with the economic and functional flexibility to grow. "
              "Cresa Core™, our AI platform, keeps every decision informed."],
    "u131e": [None, "Recommendations grounded in market data and Cresa Core™ insight that you can defend to "
                    "leadership and lenders."],
    "u1337": [None, "Sites chosen for patient access, clinical talent and total occupancy cost, not just rooftops "
                    "and traffic counts."],
    "u1369": [None, "Conflict-free guidance that carries the relationship beyond one transaction into ongoing "
                    "portfolio strategy."],
    "u150a": ["Conflict-free real estate advisory built specifically with healthcare occupiers in mind."],
    "u1398": ["Transaction Management", "Location Advisory", "Project & Development Services", "Portfolio Solutions"],
    "u13b1": ["Lease Administration", "Strategic Consulting", "Workplace Solutions", "Capital Strategies"],
    "u1cb6": ["Transactions in 2022"],
}
for sid, new in EDITS.items():
    p = os.path.join(root, "Stories", f"Story_{sid}.xml")
    t = etree.parse(p)
    cs = list(t.iter("Content"))
    assert len(cs) == len(new), (sid, [c.text for c in cs])
    for c, txt in zip(cs, new):
        if txt is not None:
            c.text = txt
    t.write(p, xml_declaration=True, encoding="UTF-8", standalone=True)
print("fixed", len(EDITS), "stories")
