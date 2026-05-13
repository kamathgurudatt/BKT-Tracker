from app.models.entities import NotificationType, StockStatus


def detect_changes(previous: dict | None, current: dict) -> list[tuple[NotificationType, str]]:
    events: list[tuple[NotificationType, str]] = []
    if not previous:
        if current.get("stock_status") == StockStatus.IN_STOCK.value:
            events.append((NotificationType.RESTOCK, "Newly listed or available product detected"))
        return events
    if previous.get("stock_status") != "in_stock" and current.get("stock_status") == "in_stock":
        events.append((NotificationType.RESTOCK, "Product is back in stock"))
    if current.get("price") and previous.get("price") and float(current["price"]) < float(previous["price"]):
        events.append((NotificationType.PRICE_DROP, "Product price dropped"))
    if (current.get("stock_quantity") or 0) > (previous.get("stock_quantity") or 0):
        events.append((NotificationType.STOCK_INCREASE, "Stock quantity increased"))
    if current.get("eta_minutes") and previous.get("eta_minutes") and int(current["eta_minutes"]) < int(previous["eta_minutes"]):
        events.append((NotificationType.ETA_IMPROVED, "Delivery ETA improved"))
    return events
