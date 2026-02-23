"""
config.py — Central configuration.

Set your secrets as environment variables (or in a .env file).
Never hardcode API keys here.
"""

import os

# ── Slack ─────────────────────────────────────────────────────────────────────
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

# ── JSearch API (RapidAPI) ────────────────────────────────────────────────────
JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY", "")

# ── Job filtering ─────────────────────────────────────────────────────────────
# Only notify for jobs posted within this many days
MAX_AGE_DAYS = 30

# Optional extra keyword filter (set via JOB_KEYWORDS environment variable)
# Leave empty to get all entry-level jobs. Example: "marketing,design,finance"
KEYWORDS = os.environ.get("JOB_KEYWORDS", "").split(",") if os.environ.get("JOB_KEYWORDS") else []

# ── Entry-Level Title Keywords ────────────────────────────────────────────────
# A job MUST contain at least one of these in its title to be included.
# This ensures we only surface early career / internship roles.
ENTRY_LEVEL_TITLE_KEYWORDS = [
    "intern",
    "internship",
    "co-op",
    "coop",
    "apprentice",
    "apprenticeship",
    "entry level",
    "entry-level",
    "associate",
    "junior",
    "jr.",
    "jr ",
    "coordinator",
    "assistant",
    "analyst",
    "specialist i",
    "specialist 1",
    "level 1",
    "level i",
    "graduate",
    "new grad",
    "rotational",
    "early career",
    "campus",
    "emerging talent",
]

# ── Seniority Exclusions ──────────────────────────────────────────────────────
# Jobs with ANY of these in the title are skipped — too senior.
EXCLUDE_TITLE_KEYWORDS = [
    "senior",
    "sr.",
    "sr ",
    "lead",
    "manager",
    "director",
    "head of",
    "vp",
    "vice president",
    "principal",
    "staff",
    "distinguished",
    "executive",
    "chief",
    "partner",
    "svp",
    "evp",
    "cto",
    "cmo",
    "ceo",
    "coo",
    "cfo",
]

# ── Retail / Store Exclusions ─────────────────────────────────────────────────
# Jobs with ANY of these are skipped — store/hourly roles, not corporate.
EXCLUDE_RETAIL_KEYWORDS = [
    "store",
    "retail",
    "cashier",
    "sales associate",
    "stock associate",
    "floor associate",
    "keyholder",
    "key holder",
    "shift supervisor",
    "sales lead",
    "part-time",
    "part time",
    "seasonal",
    "outlet",
    "visual merchandis",
    "loss prevention",
    "fulfillment center",
    "warehouse",
    "distribution center",
    "hourly",
    "stocker",
]

# ── Workday Companies ─────────────────────────────────────────────────────────
# Most major brands use Workday as their ATS.
# We hit their Workday JSON API directly — no fragile HTML parsing needed.
WORKDAY_COMPANIES = [

    # ── Footwear & Athletic ───────────────────────────────────────────────────
    {
        "name": "Nike",
        "tenant": "nike",
        "subdomain": "nike.wd1",
        "career_site": "External",
        "url": "https://jobs.nike.com",
    },
    {
        "name": "Converse",
        "tenant": "nike",               # Converse is owned by Nike, same Workday
        "subdomain": "nike.wd1",
        "career_site": "External",
        "url": "https://jobs.nike.com",
    },
    {
        "name": "Adidas",
        "tenant": "adidas",
        "subdomain": "adidas.wd3",
        "career_site": "External",
        "url": "https://careers.adidas.com",
    },
    {
        "name": "Reebok",
        "tenant": "adidasshoesource",
        "subdomain": "adidasshoesource.wd3",
        "career_site": "External",
        "url": "https://careers.reebok.com",
    },
    {
        "name": "Puma",
        "tenant": "puma",
        "subdomain": "puma.wd3",
        "career_site": "External",
        "url": "https://about.puma.com/en/careers",
    },
    {
        "name": "New Balance",
        "tenant": "newbalance",
        "subdomain": "newbalance.wd1",
        "career_site": "External",
        "url": "https://jobs.newbalance.com",
    },
    {
        "name": "Under Armour",
        "tenant": "underarmour",
        "subdomain": "underarmour.wd5",
        "career_site": "External",
        "url": "https://careers.underarmour.com",
    },
    {
        "name": "ASICS",
        "tenant": "asics",
        "subdomain": "asics.wd3",
        "career_site": "External",
        "url": "https://www.asics.com/us/en-us/careers",
    },
    {
        "name": "Brooks Running",
        "tenant": "brooks",
        "subdomain": "brooks.wd5",
        "career_site": "External",
        "url": "https://www.brooksrunning.com/en_us/careers",
    },
    {
        "name": "On Running",
        "tenant": "onrunning",
        "subdomain": "onrunning.wd3",
        "career_site": "External",
        "url": "https://www.onrunning.com/en-us/careers",
    },
    {
        "name": "Skechers",
        "tenant": "skechers",
        "subdomain": "skechers.wd5",
        "career_site": "External",
        "url": "https://careers.skechers.com",
    },
    {
        "name": "Allbirds",
        "tenant": "allbirds",
        "subdomain": "allbirds.wd5",
        "career_site": "External",
        "url": "https://www.allbirds.com/pages/careers",
    },
    {
        "name": "Crocs",
        "tenant": "crocs",
        "subdomain": "crocs.wd5",
        "career_site": "External",
        "url": "https://careers.crocs.com",
    },
    {
        "name": "Birkenstock",
        "tenant": "birkenstock",
        "subdomain": "birkenstock.wd3",
        "career_site": "External",
        "url": "https://www.birkenstock.com/us/careers",
    },
    {
        "name": "Steve Madden",
        "tenant": "stevemadden",
        "subdomain": "stevemadden.wd1",
        "career_site": "External",
        "url": "https://careers.stevemadden.com",
    },
    {
        "name": "Wolverine World Wide",
        "tenant": "wolverineworldwide",
        "subdomain": "wolverineworldwide.wd5",
        "career_site": "External",
        "url": "https://www.wolverineworldwide.com/careers",
    },

    # ── VF Corporation & Brands ───────────────────────────────────────────────
    {
        "name": "VF Corporation",
        "tenant": "vfc",
        "subdomain": "vfc.wd5",
        "career_site": "External",
        "url": "https://www.vfc.com/careers",
    },
    {
        "name": "Vans",
        "tenant": "vfc",
        "subdomain": "vfc.wd5",
        "career_site": "External",
        "url": "https://www.vfc.com/careers",
    },
    {
        "name": "Timberland",
        "tenant": "vfc",
        "subdomain": "vfc.wd5",
        "career_site": "External",
        "url": "https://www.vfc.com/careers",
    },
    {
        "name": "The North Face",
        "tenant": "vfc",
        "subdomain": "vfc.wd5",
        "career_site": "External",
        "url": "https://www.vfc.com/careers",
    },
    {
        "name": "Dickies",
        "tenant": "vfc",
        "subdomain": "vfc.wd5",
        "career_site": "External",
        "url": "https://www.vfc.com/careers",
    },
    {
        "name": "Altra Running",
        "tenant": "vfc",
        "subdomain": "vfc.wd5",
        "career_site": "External",
        "url": "https://www.vfc.com/careers",
    },

    # ── Deckers Brands ────────────────────────────────────────────────────────
    {
        "name": "Deckers Brands",
        "tenant": "deckers",
        "subdomain": "deckers.wd5",
        "career_site": "External",
        "url": "https://www.deckers.com/careers",
    },
    {
        "name": "HOKA",
        "tenant": "deckers",
        "subdomain": "deckers.wd5",
        "career_site": "External",
        "url": "https://www.deckers.com/careers",
    },
    {
        "name": "UGG",
        "tenant": "deckers",
        "subdomain": "deckers.wd5",
        "career_site": "External",
        "url": "https://www.deckers.com/careers",
    },
    {
        "name": "Teva",
        "tenant": "deckers",
        "subdomain": "deckers.wd5",
        "career_site": "External",
        "url": "https://www.deckers.com/careers",
    },
    {
        "name": "Sanuk",
        "tenant": "deckers",
        "subdomain": "deckers.wd5",
        "career_site": "External",
        "url": "https://www.deckers.com/careers",
    },

    # ── Outdoor & Apparel ─────────────────────────────────────────────────────
    {
        "name": "Patagonia",
        "tenant": "patagonia",
        "subdomain": "patagonia.wd5",
        "career_site": "External",
        "url": "https://www.patagonia.com/jobs",
    },
    {
        "name": "Columbia Sportswear",
        "tenant": "columbia",
        "subdomain": "columbia.wd5",
        "career_site": "External",
        "url": "https://www.columbiasportswear.com/c/careers",
    },
    {
        "name": "Arc'teryx",
        "tenant": "arcteryx",
        "subdomain": "arcteryx.wd3",
        "career_site": "External",
        "url": "https://www.arcteryx.com/us/en/careers",
    },
    {
        "name": "Amer Sports",
        "tenant": "amersports",
        "subdomain": "amersports.wd3",
        "career_site": "External",
        "url": "https://www.amersports.com/careers",
    },
    {
        "name": "Salomon",
        "tenant": "amersports",         # Salomon owned by Amer Sports
        "subdomain": "amersports.wd3",
        "career_site": "External",
        "url": "https://www.amersports.com/careers",
    },
    {
        "name": "Wilson Sporting Goods",
        "tenant": "amersports",         # Wilson owned by Amer Sports
        "subdomain": "amersports.wd3",
        "career_site": "External",
        "url": "https://www.amersports.com/careers",
    },
    {
        "name": "Vuori",
        "tenant": "vuori",
        "subdomain": "vuori.wd5",
        "career_site": "External",
        "url": "https://www.vuoriclothing.com/pages/careers",
    },
    {
        "name": "Alo Yoga",
        "tenant": "aloyoga",
        "subdomain": "aloyoga.wd5",
        "career_site": "External",
        "url": "https://www.aloyoga.com/pages/careers",
    },
    {
        "name": "lululemon",
        "tenant": "lululemon",
        "subdomain": "lululemon.wd3",
        "career_site": "External",
        "url": "https://info.lululemon.com/careers",
    },
    {
        "name": "Fabletics",
        "tenant": "fabletics",
        "subdomain": "fabletics.wd5",
        "career_site": "External",
        "url": "https://www.fabletics.com/careers",
    },
    {
        "name": "Gymshark",
        "tenant": "gymshark",
        "subdomain": "gymshark.wd3",
        "career_site": "External",
        "url": "https://www.gymshark.com/pages/careers",
    },

    # ── Gap Inc. Brands ───────────────────────────────────────────────────────
    {
        "name": "Gap Inc.",
        "tenant": "gap",
        "subdomain": "gap.wd5",
        "career_site": "External",
        "url": "https://www.gapinc.com/careers",
    },
    {
        "name": "Athleta",
        "tenant": "gap",                # Athleta owned by Gap Inc.
        "subdomain": "gap.wd5",
        "career_site": "External",
        "url": "https://www.gapinc.com/careers",
    },
    {
        "name": "Banana Republic",
        "tenant": "gap",
        "subdomain": "gap.wd5",
        "career_site": "External",
        "url": "https://www.gapinc.com/careers",
    },

    # ── Lifestyle & Denim ─────────────────────────────────────────────────────
    {
        "name": "Levi Strauss & Co.",
        "tenant": "levistrauss",
        "subdomain": "levistrauss.wd5",
        "career_site": "External",
        "url": "https://careers.levi.com",
    },
    {
        "name": "Ralph Lauren",
        "tenant": "ralphlauren",
        "subdomain": "ralphlauren.wd5",
        "career_site": "External",
        "url": "https://careers.ralphlauren.com",
    },
    {
        "name": "PVH Corp",             # Parent of Calvin Klein & Tommy Hilfiger
        "tenant": "pvh",
        "subdomain": "pvh.wd5",
        "career_site": "External",
        "url": "https://careers.pvh.com",
    },
    {
        "name": "Tapestry",             # Parent of Coach, Kate Spade, Stuart Weitzman
        "tenant": "tapestry",
        "subdomain": "tapestry.wd5",
        "career_site": "External",
        "url": "https://careers.tapestry.com",
    },

    # ── Specialty Retail (Corporate) ──────────────────────────────────────────
    {
        "name": "Foot Locker",
        "tenant": "footlocker",
        "subdomain": "footlocker.wd5",
        "career_site": "External",
        "url": "https://careers.footlocker.com",
    },
    {
        "name": "DICK'S Sporting Goods",
        "tenant": "dickssportinggoods",
        "subdomain": "dickssportinggoods.wd5",
        "career_site": "External",
        "url": "https://www.dickssportinggoods.com/s/careers",
    },
    {
        "name": "REI",
        "tenant": "rei",
        "subdomain": "rei.wd5",
        "career_site": "External",
        "url": "https://www.rei.com/careers",
    },

    # ── Outdoor / Gear ────────────────────────────────────────────────────────
    {
        "name": "YETI",
        "tenant": "yeti",
        "subdomain": "yeti.wd5",
        "career_site": "External",
        "url": "https://www.yeti.com/en_US/careers",
    },

    # ── Sports Tech / Wearables ───────────────────────────────────────────────
    {
        "name": "WHOOP",
        "tenant": "whoop",
        "subdomain": "whoop.wd5",
        "career_site": "External",
        "url": "https://www.whoop.com/us/en/careers",
    },
    {
        "name": "Oura",
        "tenant": "ouraring",
        "subdomain": "ouraring.wd3",
        "career_site": "External",
        "url": "https://ouraring.com/careers",
    },
    {
        "name": "Strava",
        "tenant": "strava",
        "subdomain": "strava.wd5",
        "career_site": "External",
        "url": "https://www.strava.com/careers",
    },
    {
        "name": "Garmin",
        "tenant": "garmin",
        "subdomain": "garmin.wd5",
        "career_site": "External",
        "url": "https://careers.garmin.com",
    },
    {
        "name": "Peloton",
        "tenant": "peloton",
        "subdomain": "peloton.wd5",
        "career_site": "External",
        "url": "https://careers.onepeloton.com",
    },

    # ── Sports Media ─────────────────────────────────────────────────────────
    {
        "name": "ESPN / Disney",
        "tenant": "disney",             # ESPN is owned by Disney
        "subdomain": "disney.wd5",
        "career_site": "External",
        "url": "https://jobs.disneycareers.com",
    },
    {
        "name": "FOX Sports",
        "tenant": "foxcorporation",
        "subdomain": "foxcorporation.wd5",
        "career_site": "External",
        "url": "https://www.foxcorporation.com/careers",
    },
    {
        "name": "NBC Sports / Comcast",
        "tenant": "comcast",
        "subdomain": "comcast.wd5",
        "career_site": "External",
        "url": "https://jobs.comcast.com",
    },
    {
        "name": "Warner Bros. Discovery Sports",
        "tenant": "warnerbros",
        "subdomain": "warnerbros.wd5",
        "career_site": "External",
        "url": "https://careers.wbd.com",
    },

    # ── Sports Leagues ────────────────────────────────────────────────────────
    {
        "name": "NBA",
        "tenant": "nba",
        "subdomain": "nba.wd5",
        "career_site": "External",
        "url": "https://careers.nba.com",
    },
    {
        "name": "NFL",
        "tenant": "nfl",
        "subdomain": "nfl.wd5",
        "career_site": "External",
        "url": "https://careers.nfl.com",
    },
    {
        "name": "MLB",
        "tenant": "mlb",
        "subdomain": "mlb.wd5",
        "career_site": "External",
        "url": "https://www.mlb.com/careers",
    },
    {
        "name": "MLS",
        "tenant": "mls",
        "subdomain": "mls.wd5",
        "career_site": "External",
        "url": "https://careers.mlssoccer.com",
    },
    {
        "name": "NHL",
        "tenant": "nhl",
        "subdomain": "nhl.wd5",
        "career_site": "External",
        "url": "https://www.nhl.com/info/careers",
    },
    {
        "name": "PGA Tour",
        "tenant": "pgatour",
        "subdomain": "pgatour.wd5",
        "career_site": "External",
        "url": "https://www.pgatour.com/company/careers.html",
    },
    {
        "name": "USTA",
        "tenant": "usta",
        "subdomain": "usta.wd5",
        "career_site": "External",
        "url": "https://www.usta.com/en/home/about-usta/jobs.html",
    },

    # ── Sports Agencies ───────────────────────────────────────────────────────
    {
        "name": "Wasserman",
        "tenant": "wasserman",
        "subdomain": "wasserman.wd5",
        "career_site": "External",
        "url": "https://www.teamwass.com/careers",
    },
    {
        "name": "Octagon",
        "tenant": "octagon",
        "subdomain": "octagon.wd5",
        "career_site": "External",
        "url": "https://www.octagon.com/careers",
    },
    {
        "name": "IMG / WME / Endeavor",
        "tenant": "endeavor",           # IMG and WME are both owned by Endeavor
        "subdomain": "endeavor.wd5",
        "career_site": "External",
        "url": "https://www.endeavorco.com/careers",
    },
    {
        "name": "CAA Sports",
        "tenant": "caa",
        "subdomain": "caa.wd5",
        "career_site": "External",
        "url": "https://www.caa.com/careers",
    },

    # ── Airlines ─────────────────────────────────────────────────────────────
    {
        "name": "United Airlines",
        "tenant": "united",
        "subdomain": "united.wd5",
        "career_site": "External",
        "url": "https://careers.united.com",
    },
    {
        "name": "Delta Air Lines",
        "tenant": "delta",
        "subdomain": "delta.wd5",
        "career_site": "External",
        "url": "https://careers.delta.com",
    },
    {
        "name": "American Airlines",
        "tenant": "aa",
        "subdomain": "aa.wd5",
        "career_site": "External",
        "url": "https://jobs.aa.com",
    },

    # ── Consumer Goods / CPG ──────────────────────────────────────────────────
    {
        "name": "Procter & Gamble",
        "tenant": "pg",
        "subdomain": "pg.wd5",
        "career_site": "External",
        "url": "https://www.pgcareers.com",
    },
    {
        "name": "Unilever",
        "tenant": "unilever",
        "subdomain": "unilever.wd3",
        "career_site": "External",
        "url": "https://careers.unilever.com",
    },
    {
        "name": "PepsiCo",
        "tenant": "pepsico",
        "subdomain": "pepsico.wd5",
        "career_site": "External",
        "url": "https://www.pepsicojobs.com",
    },
    {
        "name": "Coca-Cola",
        "tenant": "cocacola",
        "subdomain": "cocacola.wd5",
        "career_site": "External",
        "url": "https://careers.coca-colacompany.com",
    },
    {
        "name": "Kraft Heinz",
        "tenant": "kraftheinz",
        "subdomain": "kraftheinz.wd5",
        "career_site": "External",
        "url": "https://careers.kraftheinz.com",
    },
    {
        "name": "Mondelez International",
        "tenant": "mondelez",
        "subdomain": "mondelez.wd5",
        "career_site": "External",
        "url": "https://careers.mondelezinternational.com",
    },
    {
        "name": "Mars, Inc.",
        "tenant": "mars",
        "subdomain": "mars.wd5",
        "career_site": "External",
        "url": "https://careers.mars.com",
    },
    {
        "name": "Nestlé",
        "tenant": "nestle",
        "subdomain": "nestle.wd3",
        "career_site": "External",
        "url": "https://www.nestle.com/jobs",
    },
    {
        "name": "General Mills",
        "tenant": "generalmills",
        "subdomain": "generalmills.wd5",
        "career_site": "External",
        "url": "https://careers.generalmills.com",
    },
    {
        "name": "Kellanova",
        "tenant": "kellanova",
        "subdomain": "kellanova.wd5",
        "career_site": "External",
        "url": "https://www.kellanovacareers.com",
    },
    {
        "name": "Conagra Brands",
        "tenant": "conagra",
        "subdomain": "conagra.wd5",
        "career_site": "External",
        "url": "https://careers.conagrabrands.com",
    },
    {
        "name": "The Clorox Company",
        "tenant": "clorox",
        "subdomain": "clorox.wd5",
        "career_site": "External",
        "url": "https://careers.thecloroxcompany.com",
    },
    {
        "name": "Keurig Dr Pepper",
        "tenant": "keurigdrpepper",
        "subdomain": "keurigdrpepper.wd5",
        "career_site": "External",
        "url": "https://careers.keurigdrpepper.com",
    },
    {
        "name": "Church & Dwight",
        "tenant": "churchdwight",
        "subdomain": "churchdwight.wd5",
        "career_site": "External",
        "url": "https://careers.churchdwight.com",
    },
    {
        "name": "Henkel",
        "tenant": "henkel",
        "subdomain": "henkel.wd3",
        "career_site": "External",
        "url": "https://www.henkel-northamerica.com/careers",
    },
    {
        "name": "Edgewell Personal Care",
        "tenant": "edgewell",
        "subdomain": "edgewell.wd5",
        "career_site": "External",
        "url": "https://careers.edgewell.com",
    },
]

# ── JSearch Queries ───────────────────────────────────────────────────────────
# These supplement Workday scraping by catching jobs posted on LinkedIn/Indeed.
# Scoped to entry-level and internship roles only.
JSEARCH_QUERIES = [
    # Footwear
    "Nike entry level corporate",
    "Nike internship",
    "Adidas entry level",
    "Adidas internship",
    "New Balance entry level",
    "New Balance internship",
    "Puma entry level",
    "Under Armour internship",
    "ASICS entry level",
    "Brooks Running internship",
    "HOKA internship",
    "On Running entry level",
    "Skechers corporate entry level",
    "Allbirds entry level",
    "Salomon internship",
    # Outdoor / Apparel
    "The North Face entry level",
    "Vans entry level",
    "VF Corporation internship",
    "Patagonia internship",
    "Columbia Sportswear entry level",
    "Arc'teryx internship",
    "Amer Sports internship",
    "Vuori internship",
    "Alo Yoga entry level",
    "lululemon corporate entry level",
    "Athleta internship",
    "Gap Inc entry level",
    "Levi Strauss entry level",
    # Gear / Tech
    "YETI entry level",
    "Foot Locker corporate internship",
    "Wilson Sporting Goods entry level",
    "Strava entry level",
    "WHOOP internship",
    "Oura Ring entry level",
    "Garmin entry level",
    "Peloton internship",
    # Sports Media & Leagues
    "ESPN internship",
    "NBC Sports internship",
    "FOX Sports entry level",
    "NBA internship",
    "NFL internship",
    "MLB internship",
    "MLS entry level",
    # Sports Agencies
    "Wasserman sports internship",
    "Octagon sports internship",
    "CAA Sports entry level",
    "IMG internship",
    "WME Sports entry level",
    # Airlines
    "United Airlines corporate internship",
    "Delta Air Lines corporate internship",
    # CPG
    "Procter Gamble entry level",
    "Procter Gamble internship",
    "Unilever entry level",
    "Unilever internship",
    "PepsiCo entry level",
    "PepsiCo internship",
    "Coca-Cola entry level",
    "Coca-Cola internship",
    "Kraft Heinz entry level",
    "Mondelez entry level",
    "Mars Inc internship",
    "Nestle entry level",
    "General Mills internship",
    "Kellanova entry level",
    "Conagra entry level",
    "Clorox internship",
    # Broad sweeps
    "sportswear brand entry level corporate",
    "footwear company internship corporate",
    "consumer goods internship",
    "sports marketing entry level",
    "sports business analyst entry level",
]
