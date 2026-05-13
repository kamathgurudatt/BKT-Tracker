class Product {
  const Product({required this.provider, required this.externalProductId, required this.name, this.imageUrl, this.price, this.mrp, this.discountPercent, this.stockStatus = 'unknown', this.etaMinutes, this.category, this.locationLabel});
  final String provider;
  final String externalProductId;
  final String name;
  final String? imageUrl;
  final double? price;
  final double? mrp;
  final double? discountPercent;
  final String stockStatus;
  final int? etaMinutes;
  final String? category;
  final String? locationLabel;

  factory Product.fromJson(Map<String, dynamic> json) => Product(
    provider: json['provider'] ?? 'blinkit',
    externalProductId: json['external_product_id'] ?? '',
    name: json['name'] ?? '',
    imageUrl: json['image_url'],
    price: (json['price'] as num?)?.toDouble(),
    mrp: (json['mrp'] as num?)?.toDouble(),
    discountPercent: (json['discount_percent'] as num?)?.toDouble(),
    stockStatus: json['stock_status'] ?? 'unknown',
    etaMinutes: json['eta_minutes'],
    category: json['category'],
    locationLabel: json['location_label'],
  );
}
