import hashlib
import json
from typing import Any

HASH_FIELDS = ("external_product_id", "stock_status", "price", "mrp", "stock_quantity", "eta_minutes")


def inventory_hash(snapshot: dict[str, Any]) -> str:
    stable = {key: snapshot.get(key) for key in HASH_FIELDS}
    return hashlib.sha256(json.dumps(stable, sort_keys=True, default=str).encode()).hexdigest()
