from app.models.entities import NotificationType
from app.services.change_detection import detect_changes
from app.services.state_hash import inventory_hash


def test_detects_real_state_transitions_without_initial_fake_event():
    assert detect_changes(None, {"stock_status": "in_stock", "price": 99}) == []

    previous = {"stock_status": "out_of_stock", "price": 120, "stock_quantity": 0, "eta_minutes": 20}
    current = {"stock_status": "in_stock", "price": 99, "stock_quantity": 5, "eta_minutes": 10}

    events = dict(detect_changes(previous, current))

    assert NotificationType.RESTOCK in events
    assert NotificationType.PRICE_DROP in events
    assert NotificationType.STOCK_INCREASE in events
    assert NotificationType.ETA_IMPROVED in events


def test_inventory_hash_changes_only_when_inventory_state_changes():
    first = {"external_product_id": "123", "stock_status": "in_stock", "price": 99, "raw_payload": {"ignored": 1}}
    same_state = {"external_product_id": "123", "stock_status": "in_stock", "price": 99, "raw_payload": {"ignored": 2}}
    changed = {"external_product_id": "123", "stock_status": "out_of_stock", "price": 99}

    assert inventory_hash(first) == inventory_hash(same_state)
    assert inventory_hash(first) != inventory_hash(changed)
