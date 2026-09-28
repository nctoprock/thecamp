# 130 Sun Light Dr, Myrtle Beach, SC 29588 — Lease Analysis

*First pass, 2026-09-28. Built from public web data only; items marked **VERIFY** need the owner, the county, or a site visit.*

## The property

| | |
|---|---|
| Parcel | APN 44001020052, Horry County (unincorporated) |
| Land | 1.57 ac (~68,400 SF) |
| Zoning | HC (Highway Commercial) + CFA (Commercial Forest/Agriculture), a split zoning |
| Improvements | Front section fenced, several metal carports, sign. No building |
| Utilities | Water and sewer on site. **VERIFY** power service |
| Location | Off SC-544 beside the SC-31 (Carolina Bays Pkwy) interchange. Neighbor at 120 Sun Light is Grassie Granite (fabricator) |
| Traffic | About 36,700–37,300 vehicles/day on SC-544 and 28,500–33,600 on SC-31 (2025 SCDOT) |
| Last activity | Listed and sold under MLS# 2219477 around 2022–23. Online estimate is about $448K. **VERIFY** the sale price and the owner's basis |

## Best operational use

The site is already set up as a **fenced yard**: fence, carports and utilities, with no building. Next to the SC-31 interchange it gives fast access to the whole Grand Strand. In order of likelihood, the tenants are:

1. **Contractor, equipment or fleet yard (industrial outdoor storage).** This is the deepest tenant pool: landscapers, pool, roofing, HVAC, marine, utility and telecom subs, and a granite fabricator next door. It's the easiest lease to sign.
2. **Used-car or powersports sales lot.** HC zoning plus a fenced front section with carports is close to a turnkey car lot, and a dealer will pay for the traffic count. A small office trailer would be needed.
3. **RV, boat and trailer storage operator.** Demand is proven on this corridor (Quest RV at 8550 Hwy 544, 544 RV/Boat on Dick Pond, Harbor Haven on 707). The owner could lease to an operator or run it himself (see Approach 3).
4. **Upside: pad or build-to-suit ground lease** (QSR, express car wash, auto service, flex). This only works if the site has **direct SC-544 frontage or a curb cut**. **VERIFY**: the address is on Sun Light Dr, so it may be a side-street lot.

## The numbers

Run `python3 lease_model.py` to reproduce these or change the assumptions. All figures are NNN (tenant pays taxes, insurance and upkeep).

| Approach | Low | Mid | High |
|---|---|---|---|
| **1. Ground lease**: land value $450K / $550K / $650K × 6% / 7% / 8% yield | $2,250/mo | $3,200/mo | $4,330/mo |
| **2. Yard/IOS lease**: $1,500 / $2,100 / $2,750 per acre per month | $2,355/mo | $3,300/mo | $4,320/mo |
| **3. Self-operate RV/boat storage (NOI)**: about 53 spaces, $110–$165/mo, 85% occupied, 35% opex | $3,220/mo | $3,950/mo | $4,830/mo |

Where the land values come from:
- Online estimate for the subject: about $448K (about $286K per acre)
- 7794 Hwy 544: 1.61 ac with paved, fenced lots and a small office, asking $795K (about $494K per acre)
- 8545 Hwy 544: 0.80 ac retail, asking $625K
- Myrtle Beach commercial land overall: average asking price about $485K per acre

## Recommendation

- **List at $3,950/mo NNN** (about $47.4K/yr) for a yard, car-lot or storage user. Expect to sign at **$3,250–$3,500/mo** with 3% annual increases on a 3–5 year term.
- **Floor:** about $2,500/mo. Below that, the owner earns more running storage himself or selling.
- **Show as divisible:** the front fenced section and the rear section can be offered separately. Small contractors often want only 0.5–0.75 ac, and two tenants usually pay more per acre in total than one.
- If the site does have real 544 frontage, market a pad ground lease in parallel. A QSR or car wash tenant on a 36K-VPD road could pay well above the yard numbers.
- Self-operating storage adds only about $500–$700/mo over a straight lease, plus vacancy and management work. A clean NNN lease is the better pitch for most owners.

**Our fee, for reference:** a 5-year lease at $3,500/mo with 3% increases is about $223K of total rent. At 6% commission that's about $13.4K.

## Public-records follow-up (2026-09-28)

Direct fetches to the county land records and GIS, LoopNet, Zillow and Otter's site are blocked from this research environment. What's below comes from search-result snippets.

| # | Question | What we found | Status |
|---|---|---|---|
| 1 | Frontage on SC-544? | Access to Sun Light Dr is **from SC-544 onto Dick Pond Rd, then onto Sun Light Dr**. 100 (Otter Self Storage) and 120 (Grassie Granite) sit between the subject and the corner. The listing's "along Hwy 544" is probably visibility, not road frontage | **Likely no direct 544 frontage.** Check the plat |
| 2 | HC/CFA split | The county card lists it as "a portion of Tract B", which suggests the lot came from a larger subdivided tract. Boundary line not found. Horry County retired CFA for new rezonings but it still applies to existing parcels | Open. Need GIS zoning layer |
| 3 | Surface | Not found | Open. Site visit |
| 4 | Permits / power | Not found. **Note:** HC zoning requires outdoor storage to be screened by a **fully opaque fence or wall at least 6 ft tall**. If the current fence is chain-link, a yard or storage tenant would need slats or new fencing | Open |
| 5 | Price paid / taxes | Owner of record: **CDM LAND LLC, 36 Ferebee Ct, Bluffton, SC 29910** (PIN 44001020052, TMS 1790002083). Sold around 2022–23 under MLS 2219477; price not found | Open. County card / Register of Deeds |
| 6 | Current occupant | No business listing at 130 Sun Light Dr | Likely vacant |

**New market facts**
- **Otter Self Storage, 100 Sun Light Dr (next door)** offers RV, boat and vehicle parking. It advertises 9'x18' parking at about **$99/mo** (promo). This is a direct comp and also competition, so self-operated RV storage here would be undercut on price. That favors leasing to a yard or car-lot user over Approach 3.
- A 2025 rezoning (case 2025-11-005) covers residential lots at **Rosebud Ln & Sun Light Dr**, so the street turns residential behind the commercial frontage. Expect buffer and screening conditions on noisy yard uses.

**Effect on the numbers:** the land-lease upside for a restaurant or car wash is unlikely without 544 frontage, so value the site mostly as a yard. Keep the asking rent at $3,950/mo, but expect to sign closer to **$3,000–$3,500/mo**. Budget for opaque screening if the fence isn't already compliant.

## Questions for the owner / to verify

1. Does the lot touch SC-544 directly, or is access only from Sun Light Dr? Is there a curb cut?
2. Where is the HC/CFA zoning boundary on the lot? Can the CFA part be used for storage, or does it need rezoning to HC?
3. Surface: gravel, paved or dirt? Is there any stormwater or wetland restriction on the rear?
4. Were the carports and fence permitted? What is the power service (needed for a gate, lights, cameras)?
5. What price did the owner pay in 2022–23, and what is the current tax bill? These set the owner's return expectations.
6. Is there any current tenant or month-to-month occupant?
7. What lease term does the owner want, and would he consider selling or a build-to-suit?

## Sources
- [Homes.com — 130 Sun Light Dr](https://www.homes.com/property/130-sun-light-dr-myrtle-beach-sc/g8x7yzx8k2w1t/)
- [LoopNet — 130 Sun Light Dr](https://www.loopnet.com/Listing/130-Sun-Light-Dr-Myrtle-Beach-SC/36180020/)
- [Realty.com — 7794 Hwy 544](https://www.realty.com/commercial-listings/336399074/7794-Highway-544-Myrtle-Beach-SC-29588)
- [Realty.com — 8545 Hwy 544](https://www.realty.com/commercial-listings/322609024/8545-Highway-544-Myrtle-Beach-SC-29588)
- [LandSearch — Myrtle Beach commercial land](https://www.landsearch.com/commercial/myrtle-beach-sc)
- [SCDOT traffic counts](https://www.scdot.org/travel/travel-trafficdata.html)
- [Horry County Zoning Ordinance (Jan 2026)](https://www.horrycountysc.gov/media/u1xbawev/appendix-b-zoning-ordinance-172026.pdf)
- [Quest RV & Boat Storage, 8550 Hwy 544](https://www.questrvstorage.com/)
- [Grassie Granite, 120 Sun Light Dr](https://grassiegranite.com/)
