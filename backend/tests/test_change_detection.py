from app.models.entities import NotificationType
from app.services.change_detection import detect_changes


def test_detects_restock_price_and_eta_changes():
    previous = {"stock_status": "out_of_stock", "price": 120, "stock_quantity": 0, "eta_minutes": 20}
    current = {"stock_status": "in_stock", "price": 99, "stock_quantity": 5, "eta_minutes": 10}

    events = dict(detect_changes(previous, current))

    assert NotificationType.RESTOCK in events
    assert NotificationType.PRICE_DROP in events
    assert NotificationType.STOCK_INCREASE in events
    assert NotificationType.ETA_IMPROVED in events
