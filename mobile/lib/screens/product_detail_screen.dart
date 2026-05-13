import 'package:flutter/material.dart';
import '../models/product.dart';
import '../widgets/sentinel_scaffold.dart';

class ProductDetailScreen extends StatelessWidget { const ProductDetailScreen({super.key}); @override Widget build(BuildContext context) { final product = ModalRoute.of(context)?.settings.arguments as Product?; return SentinelScaffold(title: product?.name ?? 'Product Detail', child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(product?.name ?? 'Select a product', style: Theme.of(context).textTheme.headlineSmall), Text('Provider: ${product?.provider ?? '-'}'), Text('Status: ${product?.stockStatus ?? '-'}'), Text('MRP: ₹${product?.mrp ?? '-'} | Price: ₹${product?.price ?? '-'}'), const SizedBox(height: 16), FilledButton.icon(onPressed: () {}, icon: const Icon(Icons.notifications_active), label: const Text('Track across locations'))])); }}
