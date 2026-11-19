# Austin Office Options — HR Green

A single-page map of Austin office buildings for HR Green, behind the same Cresa Firebase login as the Houston comps database.

**Open:** `Cresa_Austin_Office_Options_HR_Green.html`

## Views

| Tab | What it does |
|---|---|
| **Map** | Numbered building pins with a photo list, plus layers for competitors, employee homes (coloured by office) and current HR Green offices. |
| **Table** | Every option in one sortable table. |
| **Drive time** | Ranks buildings by employee commute: average, median, share within 20/30/45 min, team hours per week, and change vs each person's current office. AM peak / PM peak / off-peak; filter by office or department. |
| **Compare** | Up to 6 buildings side by side, including drive-time rows. |

Building filters (submarket, class, city, rent, size, % leased, stories, vintage, 9,000+ SF contiguous, amenities) apply to every tab.

## Data flow

```
Google Sheet (private) → FirebasePublisher.gs → Firebase /datasets/aus-office-hrgreen → this page
```

The script publishes every 15 minutes and after edits. The page checks for updates every 5 minutes.

## Sheet tabs

| Tab | Columns the script reads | Notes |
|---|---|---|
| *first tab* | The listing export (Property Address, Property Name, … Plug & Play) | Any column to the right of **Match Note** is treated as an amenity (Yes / TRUE / 1 / x). |
| **Employees** | `Full Address` (or street / city / state / zip), `HOME DEPARTMENT`, `LOCATION` | Paste the HR roster as-is. Only ZIP, department, office and a location rounded to ~1 km are published — no names or street addresses. |
| **Competitors** | A name column (`Name`, `Company` or `First Name`) and an address (street / city / state / zip) | Paste the competitor list as-is. |
| **Current Offices** | `Name`, `Address`, `Code` | `Code` matches the start of the roster's `LOCATION` (e.g. `AN` ↔ `AN - Austin North`). |

The script adds **Latitude / Longitude** columns to the last three tabs and fills them using Google's geocoder (inside your Google account). Fix a wrong pin by typing the right coordinates in those columns.

## Drive times

- **Estimated** (default): straight-line distance at typical Austin speeds for the time of day. Instant and free.
- **Google drive times**: Uses Google's **Routes API** (enable it on the Maps key), standard drive times without traffic (Compute Route Matrix Essentials — first 10,000 lookups a month free). Only logins in `DRIVE_TIME_ADMINS` see the button; results are saved to Firebase (`datasets/aus-office-hrgreen/drivetimes`) so everyone else reuses them. Billed per lookup — the button shows the count before it runs.

## Rebuilding

Edit `src/template.html`, then run `python3 build.py`. It inlines the Cresa logo, map style and the 71 building photos from `photos/` (matched to rows by address + building name).
