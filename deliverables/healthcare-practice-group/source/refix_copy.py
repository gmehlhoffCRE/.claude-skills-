"""Re-apply the November copy fixes (remove analytics promises) to an unpacked bifold. Run-count checked."""
import os, sys
from lxml import etree
root = sys.argv[1]
EDITS = {
    "u174": [None, None, None, None, "Conflict-free real estate advisory built  specifically with healthcare "
                                     "occupiers in mind."],
    "u230": [None, None, None, None, "Transaction Management", "Location Advisory", "Project & Development Services",
             "Portfolio Solutions", "Lease Administration", "Strategic Consulting", "Workplace Solutions",
             "Capital Strategies"],
    "u568": [None, "Recommendations grounded in market data and Cresa Core™ insight that you can defend to "
                   "leadership and lenders."],
    "u580": [None, "Sites chosen for patient access, clinical talent and total occupancy cost, not just rooftops "
                   "and traffic counts."],
    "u5b0": [None, "Conflict-free guidance that carries the relationship beyond one transaction into ongoing "
                   "portfolio strategy."],
    "u276": ["Assess", "Review your markets and current portfolio"],
    "u2a3": [None, "Prioritize the ", "right markets"],
    "u2fd": [None, "Weigh access to ", "clinical talent"],
    "u32a": ["Negotiate", "Secure the best ", "terms and incentives"],
    "u357": ["Deliver", "Manage build-out through move-in"],
    "u36d": ["From first market study to move-in day. ",
             "One Cresa team manages every step, from location strategy and lease negotiation to project delivery "
             "and lease administration."],
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
print("re-fixed", len(EDITS), "stories")
