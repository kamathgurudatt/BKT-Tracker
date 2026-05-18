import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/app_state.dart';
import '../models/product.dart';
import '../services/api_client.dart';
import '../widgets/sentinel_scaffold.dart';

class ProductDetailScreen extends StatefulWidget {
  const ProductDetailScreen({super.key});

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  bool _loading = false;
  List<Map<String, dynamic>> _locations = const [];
  List<Map<String, dynamic>> _wishlists = const [];
  final Set<int> _selectedLocations = {};
  bool _allLocations = true;
  int? _wishlistId;

  @override
  void initState() { super.initState(); _loadMeta(); }

  Future<void> _loadMeta() async {
    final api = context.read<AppState>().api;
    final locations = await api.listLocations();
    final wishlists = await api.listWishlists();
    if (mounted) setState(() { _locations = locations; _wishlists = wishlists; });
  }

  Future<void> _track(Product product) async {
    setState(() => _loading = true);
    try {
      final locationIds = _allLocations ? _locations.map((e) => e['id'] as int).toList() : _selectedLocations.toList();
      await context.read<AppState>().api.addTrackedItem(
        provider: product.provider,
        externalProductId: product.externalProductId,
        name: product.name,
        imageUrl: product.imageUrl,
        category: product.category,
        wishlistId: _wishlistId,
        locationIds: locationIds,
      );
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Added to tracking successfully.')));
    } on ApiException catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } finally { if (mounted) setState(() => _loading = false); }
  }

  @override
  Widget build(BuildContext context) {
    final product = ModalRoute.of(context)?.settings.arguments as Product?;
    return SentinelScaffold(
      title: product?.name ?? 'Product Detail',
      child: product == null ? const Text('Select a product from search.') : Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(product.name, style: Theme.of(context).textTheme.headlineSmall),
        Text('Price: ₹${product.price?.toStringAsFixed(0) ?? '-'}  •  Status: ${product.stockStatus}'),
        const SizedBox(height: 12),
        SwitchListTile(value: _allLocations, onChanged: (v)=>setState(()=>_allLocations=v), title: const Text('Track for all saved locations')),
        if (!_allLocations)
          Wrap(children: _locations.map((l){ final id=l['id'] as int; return FilterChip(label: Text(l['name'].toString()), selected: _selectedLocations.contains(id), onSelected: (v)=>setState(()=>v?_selectedLocations.add(id):_selectedLocations.remove(id))); }).toList()),
        const SizedBox(height: 8),
        DropdownButtonFormField<int>(
          initialValue: _wishlistId,
          hint: const Text('Optional wishlist'),
          items: _wishlists.map((w)=>DropdownMenuItem<int>(value: w['id'] as int, child: Text(w['name'].toString()))).toList(),
          onChanged: (v)=>setState(()=>_wishlistId=v),
        ),
        const SizedBox(height: 16),
        FilledButton.icon(onPressed: _loading ? null : ()=>_track(product), icon: const Icon(Icons.notifications_active), label: Text(_loading ? 'Saving...' : 'Add to wishlist tracking')),
      ]),
    );
  }
}
