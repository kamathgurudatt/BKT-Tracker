import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/app_state.dart';
import '../services/api_client.dart';
import '../widgets/sentinel_scaffold.dart';

class WishlistScreen extends StatefulWidget {
  const WishlistScreen({super.key});

  @override
  State<WishlistScreen> createState() => _WishlistScreenState();
}

class _WishlistScreenState extends State<WishlistScreen> {
  final _name = TextEditingController();
  bool _loading = false;
  List<Map<String, dynamic>> _wishlists = const [];

  @override
  void initState() { super.initState(); _load(); }
  @override
  void dispose() { _name.dispose(); super.dispose(); }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _wishlists = await context.read<AppState>().api.listWishlists(); }
    on ApiException catch (e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message))); }
    finally { if (mounted) setState(() => _loading = false); }
  }

  Future<void> _create() async {
    if (_name.text.trim().length < 2) return;
    await context.read<AppState>().api.createWishlist(name: _name.text.trim());
    _name.clear();
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    return SentinelScaffold(
      title: 'Wishlists',
      child: Column(children: [
        Row(children: [
          Expanded(child: TextField(controller: _name, decoration: const InputDecoration(labelText: 'Wishlist name'))),
          const SizedBox(width: 8),
          FilledButton(onPressed: _create, child: const Text('Create')),
        ]),
        const SizedBox(height: 12),
        if (_loading) const LinearProgressIndicator(),
        Expanded(child: ListView.builder(itemCount: _wishlists.length, itemBuilder: (_, i) {
          final w = _wishlists[i];
          return ListTile(leading: const Icon(Icons.favorite), title: Text(w['name']?.toString() ?? 'Wishlist'), subtitle: Text('id: ${w['id']}'));
        })),
      ]),
    );
  }
}
