# Demographics & Traffic: Sites That Pass the 1-Mile Spacing Goal

Pulled 2026-09-30.
- **Demographics:** US Census American Community Survey (latest 5-year release, via Esri's public ACS layers), by census tract. Each 1/3/5-mile ring includes the share of each tract's area that falls inside the ring, so ring totals are estimates.
- **Growth:** compared with the 2010-2014 ACS.
- **Traffic:** SCDOT 2025 count stations, compared with 2020.
- **Competition:** the 57-store list in `liquor-store-coordinates.json`.
- **Raw data:** `demographics-traffic.json`.

## Summary (3-mile ring unless noted)

| Rank | Site | Population | Adults 18+ | Median HH income | HH earning $100k+ | Growth since 2010-14 | Liquor stores in 3 mi / 5 mi | Adults per store (5 mi) | Traffic on the fronting road (2025) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **2401 Dutch Fork Rd, Chapin** | 16,330 | 12,138 | **$115,203** | **55.7%** | **+59.7%** | 2 / 8 | 3,457 | US-76: 16,600 (Lexington Co. side) to **28,900** (Richland Co. side; the parcel ID is Richland). 2020: 9,800 / n.a. |
| 2 | **364/356 Longs Pond Rd, Lexington** | 20,148 | 14,374 | $98,556 | 49.4% | **+55.6%** | **0** / 10 | 3,983 | Longs Pond Rd: 10,200-**14,200** (up from 9,700-10,600 in 2020). I-20 at exit 51: **51,300** |
| 3 | **1623 N Lake Dr, Lexington** | **25,425** | **19,792** | $105,011 (1 mi: $125,055) | 51.2% | +12.7% | 6 / 18 | 3,562 | SC-6: **20,800-31,300** (2020: 29,100 on the north segment) |
| 4 | Edmund Hwy / S Lake Dr land, Red Bank | 12,578 | 9,037 | $69,219 | 33.4% | +30.1% | **0** / 3 | **8,966** | SC-6: 21,000 (2020: 17,400); SC-302: 12,300 (2020: 10,100) |
| 5 | 7949 Broad River Rd, Irmo | **36,095** | **28,458** | $84,753 | 39.3% | +5.6% | 7 / 11 | 5,333 | US-76: 15,400 in front; 24,500 toward I-26 |

## Rings by site

| Site | 1 mi pop / income | 3 mi pop / income | 5 mi pop / income | Median age (3 mi) |
|---|---|---|---|---|
| 2401 Dutch Fork Rd | 1,895 / $97,681 | 16,330 / $115,203 | 37,059 / $113,220 | 42.2 |
| Longs Pond Rd | 1,931 / $94,413 | 20,148 / $98,556 | 54,721 / $85,125 | 36.2 |
| 1623 N Lake Dr | 2,380 / $125,055 | 25,425 / $105,011 | 82,153 / $91,684 | 45.0 |
| Edmund Hwy land | 1,062 / $59,401 | 12,578 / $69,219 | 36,482 / $64,365 | 35.2 |
| 7949 Broad River Rd | 5,358 / $87,646 | 36,095 / $84,753 | 74,594 / $86,208 | 41.3 |

## Why this order
1. **2401 Dutch Fork Rd (Chapin):** highest incomes of any site, the fastest-growing trade area (+60%), and only 2 competitors within 3 miles. US-76 traffic here grew sharply since 2020. Downside: the space is small (about 1,259 SF) and built out as offices, so the landlord and zoning must allow retail liquor.
2. **Longs Pond Rd (Lexington):** the only site with **no liquor store within 3 miles**, so it would capture all 14,000+ adults nearby. The area is growing fast (+56%), and Longs Pond Rd traffic is up about 34% since 2020 on the busiest segment. I-20 exit 51 adds traveler traffic. Suites from 1,000 SF.
3. **1623 N Lake Dr (Lexington):** the richest 1-mile ring ($125k) and the largest adult population of the top three, on a busy highway (SC-6). It has more competition (6 stores within 3 miles), and growth is slower because the area is already built out. New building.
4. **Edmund Hwy land (Red Bank):** no competition nearby and a busy intersection, but incomes are lower, and it is land only (a new build means more cost and time).
5. **7949 Broad River Rd (Irmo):** big population but flat growth, more competition, and the church about 440 ft away (fails the 500-ft rule outside town limits).

## Limits
- Census income is a household median, not liquor spending. It shows buying power, not sales.
- Ring numbers are area-weighted from census tracts, so rural tracts can blur the 1-mile ring.
- The traffic count is for the nearest SCDOT station on each road, which is not always right in front of the site. The 1623 N Lake Dr listing's "47,000 cars/day" likely combines several roads; SCDOT shows 20,800-31,300 on SC-6.
- A store missing from both the directory listings and OpenStreetMap would not be counted.
