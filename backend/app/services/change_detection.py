from app.models.entities import NotificationType, StockStatus


def detect_changes(previous: dict | None, current: dict) -> list[tuple[NotificationType, str]]:
    """Return user-notifiable changes from two real provider snapshots."""
    events: list[tuple[NotificationType, str]] = []
    if not previous:
        return events
    previous_status = previous.get("stock_status")
    current_status = current.get("stock_status")
    if previous_status != StockStatus.IN_STOCK.value and current_status == StockStatus.IN_STOCK.value:
        events.append((NotificationType.RESTOCK, "Product is back in stock"))
    if previous_status == StockStatus.IN_STOCK.value and current_status == StockStatus.OUT_OF_STOCK.value:
        events.append((NotificationType.SYSTEM, "Product went out of stock"))
    if previous_status in {StockStatus.HIDDEN.value, "removed"} and current_status != StockStatus.HIDDEN.value:
        events.append((NotificationType.SYSTEM, "Product was relisted"))
    if current_status in {StockStatus.HIDDEN.value, "removed"} and previous_status != current_status:
        events.append((NotificationType.SYSTEM, "Product appears removed or hidden"))
    if current.get("price") is not None and previous.get("price") is not None and float(current["price"]) != float(previous["price"]):
        event = NotificationType.PRICE_DROP if float(current["price"]) < float(previous["price"]) else NotificationType.SYSTEM
        events.append((event, "Product price changed"))
    if current.get("stock_quantity") is not None and previous.get("stock_quantity") is not None and int(current["stock_quantity"]) != int(previous["stock_quantity"]):
        events.append((NotificationType.STOCK_INCREASE, "Stock quantity changed"))
    if current.get("eta_minutes") is not None and previous.get("eta_minutes") is not None and int(current["eta_minutes"]) != int(previous["eta_minutes"]):
        events.append((NotificationType.ETA_IMPROVED, "Delivery ETA changed"))
    return events
