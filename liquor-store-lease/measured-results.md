# Measured Distances (replaces earlier estimates)

Measured 2026-09-30. Each address was located with the US Census geocoder (OpenStreetMap where Census had no match). Straight-line distance is calculated from those coordinates. Driving distance comes from the OSRM road router. Churches, schools and playgrounds come from OpenStreetMap within about 0.4 mile of each site.

The liquor store list combines directory listings (Yellow Pages, Yelp and others) with every liquor store tagged in OpenStreetMap across the region: 57 stores in all. A store missing from both sources would not be counted. Raw data: `measured-distances.json`, `liquor-store-coordinates.json`.

## Sites that meet the 1-mile spacing goal

| Site | Nearest liquor store | Straight line | By road | Church / school / playground nearby |
|---|---|---|---|---|
| **364 Longs Pond Rd**, Lexington (I-20 exit 51) | 1316 S Lake Dr (Red Bank Party Shop) | **3.26 mi** | 5.5 mi | Deerfield Elementary / RADIUS Church (638 Longs Pond Rd) about 5,060 ft away. Nothing else found within 0.4 mi |
| **356 Longs Pond Rd**, Lexington (next to Starbucks) | 1316 S Lake Dr | **3.24 mi** | 5.5 mi | Same as 364 |
| **2401 Dutch Fork Rd**, Chapin | Priddy's Party Shop (near 11107 Broad River Rd) | **2.85 mi** | 4.4 mi | None found within 0.4 mi |
| **1623 N Lake Dr**, Lexington | 5222 Sunset Blvd (Knock Knock Spirits); 100 Old Cherokee Rd is closest by road | **1.91 mi** | 2.4 mi | None found within 0.4 mi |
| **Edmund Hwy / S Lake Dr land**, south Red Bank (sampled at 2784 S Lake Dr and 5846-6204 Edmund Hwy) | 5141 Platt Springs Rd | **3.2-4.5 mi** | 4.9+ mi | Not checked (land only) |

## Passes spacing but has a distance-rule risk
| Site | Nearest liquor store | Straight line | By road | Problem |
|---|---|---|---|---|
| 7949 Broad River Rd, Irmo (Friarsgate Plaza) | 800 Lake Murray Blvd (Kroger Liquor) | 1.33 mi | 1.67 mi | Saint Peters Church about **440 ft by road** (317 ft straight). Passes the 300-ft rule inside town limits but **fails 500 ft** outside them. Confirm town limits and have it surveyed |

## Fail the 1-mile goal
| Site | Nearest liquor store | Straight line |
|---|---|---|
| 900 Knox Abbott Dr, Cayce | 212 Knox Abbott Dr; also 1100 Meeting St and 1147 Walter Price Rd | 0.68 mi |
| 1340 Knox Abbott Dr, Cayce | J & F Package Store (Augusta Rd, West Columbia) | 0.71 mi |
| 1424 Two Notch Rd, Red Bank | 1123 S Lake Dr | 0.44 mi |
| 4079 Augusta Hwy, Gilbert area | Murray Town Spirits, 1428 Spring Hill Rd | 0.74 mi (also Centerville Elementary about 660 ft away) |
| 1812 Augusta Hwy (Hope Plaza) | Crouch's, 203 Hwy 378 | 0.72 mi |
| 575 Chapin Rd, Chapin | 1237 and 1419 Chapin Rd, 140 Amicks Ferry Rd | Exact address not found in geocoders; all three Chapin stores are on this road. Treat as fail unless shown otherwise |

## Changes from the earlier estimates
- 1623 N Lake Dr: estimated "borderline", measured **1.9 mi, passes**.
- 7949 Broad River Rd: estimated "borderline", measured **1.3 mi, passes spacing** (church risk).
- 900 Knox Abbott Dr: estimated "possible", measured **0.68 mi, fails**. West Columbia stores on Meeting St and Augusta Rd are also close.
- 4079 Augusta Hwy: estimated "1.5+ mi", measured **0.74 mi, fails**.
- Cayce: no site passes.

## Stores added from OpenStreetMap (not in the directory lists)
Mike's Liquor Store (Dennis Cir, Lexington), Cayce Commons Liquors (N Eden Dr, Cayce), J & F Package Store (Augusta Rd, West Columbia), Priddy's Party Shop (Irmo/Chapin), Blueline Spirits (South Congaree), City Liquor (Zimalcrest Dr), Diamond's Liquor Store and King's Beverage (St Andrews/Broad River), Green's Beverage Warehouse (Fernandina Rd). Also added from directories: Dutch Fork Liquors (1180 Dutch Fork Rd, Irmo), Total Wine (275 Harbison Blvd), and West Columbia stores at 2201/2373/2410/3254 Augusta Rd, 1100 Meeting St, 746 and 2250 Sunset Blvd.
