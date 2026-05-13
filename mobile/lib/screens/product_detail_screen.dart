import 'package:flutter/material.dart';

import '../models/product.dart';
import '../widgets/sentinel_scaffold.dart';

class ProductDetailScreen extends StatelessWidget {
  const ProductDetailScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final product = ModalRoute.of(context)?.settings.arguments as Product?;
    return SentinelScaffold(
      title: product?.name ?? 'Product Detail',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(product?.name ?? 'Select a product', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 12),
          Text('Provider: ${product?.provider ?? '-'}'),
          Text('Status: ${product?.stockStatus ?? '-'}'),
          Text('MRP: ₹${product?.mrp ?? '-'} | Price: ₹${product?.price ?? '-'}'),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: product == null
                ? null
                : () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Tracking requires saved locations. Add a location before creating a monitor.')),
                    );
                  },
            icon: const Icon(Icons.notifications_active),
            label: const Text('Track across locations'),
          ),
        ],
      ),
    );
  }
}
