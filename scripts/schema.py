"""Field definitions for one sale. Shared by validate.py and build.py."""
HOUSES = {"sothebys": "Sotheby's", "christies": "Christie's", "phillips": "Phillips", "other": "Other"}
CATEGORIES = {"fine_art": "Fine art", "design": "Design", "watches": "Watches", "jewelry": "Jewelry",
              "cars": "Cars", "fashion": "Fashion", "other": "Other"}
PRICE_BASIS = {"hammer": "hammer", "with_premium": "incl. premium"}
VS_ESTIMATE = {"below", "within", "above", "no_estimate"}
# "guaranteed" means a source says the lot was guaranteed but not by whom. "unknown" means nothing was reported.
GUARANTEE = {"none": "None", "house": "By the house", "third_party": "By a third party",
             "irrevocable_bid": "Irrevocable bid", "guaranteed": "Guaranteed, backer not stated",
             "unknown": "Not reported"}
BUYER_STATUS = {"named", "reported", "anonymous"}
PRICE_SOURCE = {"house", "press"}
CONFIDENCE = {"high", "medium", "low"}
SOURCE_TYPE = {"primary", "press"}
SYMBOLS = {"USD": "$", "GBP": "£", "EUR": "€", "CHF": "CHF ", "HKD": "HK$", "NLG": "NLG "}
# Earlier changes of hands for the same object, oldest first. The sale itself is not repeated here.
HISTORY_EVENTS = {"auction": "Auction", "private_sale": "Private sale", "acquired": "Acquired", "restitution": "Restitution"}
HISTORY_BASIS = {"hammer": "hammer", "with_premium": "incl. premium", "undisclosed": "basis not stated"}
HISTORY_FIELDS = {"date", "event", "venue", "currency", "price", "price_usd", "basis", "source_url", "publisher", "note"}

REQUIRED = ["id", "issue", "sale_date", "house", "location", "sale_name", "category", "maker", "title",
            "currency", "price_basis", "fx_rate_to_usd", "fx_date", "fx_source", "price_usd", "vs_estimate",
            "guarantee", "buyer_status", "why_it_matters", "featured", "sources", "price_source", "confidence"]
OPTIONAL = ["lot_number", "year_made", "estimate_low", "estimate_high", "estimate_note", "price_hammer",
            "price_with_premium", "seller", "buyer_name", "buyer_attribution", "buyer_profile_url", "bidding_notes",
            "financing_notes", "record", "updated_at", "update_note", "sample", "image", "history"]
