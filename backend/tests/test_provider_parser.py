from app.providers.parser import normalize_product, normalize_search_results


def test_live_payload_parser_normalizes_nested_product_response():
    payload = {
        "data": {
            "product": {
                "product_id": "live-123",
                "product_name": "Real Product Name",
                "selling_price": "₹95",
                "mrp": "₹100",
                "available": True,
                "available_quantity": 4,
                "etaInMinutes": 8,
            }
        }
    }

    product = normalize_product("blinkit", payload)

    assert product.external_product_id == "live-123"
    assert product.name == "Real Product Name"
    assert product.price == 95
    assert product.stock_status == "in_stock"
    assert product.eta_minutes == 8


def test_search_parser_extracts_multiple_live_products():
    payload = {"results": [{"id": "p1", "name": "Milk", "price": 60, "available": True}, {"id": "p2", "name": "Bread", "price": 45, "available": False}]}

    results = normalize_search_results("blinkit", payload)

    assert [item["external_product_id"] for item in results] == ["p1", "p2"]
    assert results[1]["stock_status"] == "out_of_stock"
