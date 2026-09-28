"""Lease underwriting for 130 Sun Light Dr, Myrtle Beach, SC 29588.

All inputs are assumptions from public-web research (see analysis.md).
Change the numbers below and re-run: python3 lease_model.py
"""

ACRES = 1.57
LAND_SF = ACRES * 43_560

# --- Approach 1: ground lease as a yield on land value -----------------
LAND_VALUE = {"low": 450_000, "mid": 550_000, "high": 650_000}
GROUND_LEASE_YIELD = {"low": 0.06, "mid": 0.07, "high": 0.08}

# --- Approach 2: yard / outdoor-storage lease, $ per acre per month ----
YARD_RATE_PER_ACRE_MO = {"low": 1_500, "mid": 2_100, "high": 2_750}

# --- Approach 3: owner (or operator) runs RV / boat / trailer storage --
USABLE_PCT = 0.70            # after drive aisles, setbacks, stormwater
GROSS_SF_PER_SPACE = 900     # 12x40 stall plus its share of aisle
RATE_PER_SPACE = {"low": 110, "mid": 135, "high": 165}   # blended $/mo
OCCUPANCY = 0.85
OPEX_PCT = 0.35              # mgmt, insurance, taxes, gate/software, upkeep

# --- Listing economics -------------------------------------------------
TERM_YEARS = 5
ANNUAL_BUMP = 0.03
COMMISSION_PCT = 0.06        # of aggregate base rent


def mo(x):
    return f"${x:,.0f}/mo (${x * 12:,.0f}/yr)"


def main():
    print(f"Site: {ACRES} ac = {LAND_SF:,.0f} SF\n")

    print("1) Ground lease (land value x yield), NNN")
    for k in LAND_VALUE:
        print(f"   {k:>4}: {mo(LAND_VALUE[k] * GROUND_LEASE_YIELD[k] / 12)}")

    print("\n2) Yard / outdoor storage lease, NNN")
    for k, r in YARD_RATE_PER_ACRE_MO.items():
        print(f"   {k:>4}: {mo(r * ACRES)}  (${r * ACRES * 12 / LAND_SF:.2f}/SF land/yr)")

    spaces = int(LAND_SF * USABLE_PCT / GROSS_SF_PER_SPACE)
    print(f"\n3) Operate as RV/boat storage: ~{spaces} spaces @ {OCCUPANCY:.0%} occ")
    for k, r in RATE_PER_SPACE.items():
        gross = spaces * r * OCCUPANCY
        print(f"   {k:>4}: gross {mo(gross)}  NOI {mo(gross * (1 - OPEX_PCT))}")

    print(f"\nListing commission, {TERM_YEARS}-yr term, {ANNUAL_BUMP:.0%} bumps, "
          f"{COMMISSION_PCT:.0%} of aggregate rent")
    for start in (3_000, 3_500, 4_000):
        total = sum(start * 12 * (1 + ANNUAL_BUMP) ** y for y in range(TERM_YEARS))
        print(f"   start ${start:,}/mo -> aggregate ${total:,.0f}, "
              f"commission ${total * COMMISSION_PCT:,.0f}")


if __name__ == "__main__":
    main()
