import 'package:flutter/material.dart';
import '../widgets/sentinel_scaffold.dart';
class WishlistScreen extends StatelessWidget { const WishlistScreen({super.key}); @override Widget build(BuildContext context) => const SentinelScaffold(title: 'Wishlists', child: Column(children: [ListTile(leading: Icon(Icons.favorite), title: Text('Dairy essentials'), subtitle: Text('Butter, milk, cheese across Andheri and Powai')), ListTile(leading: Icon(Icons.phone_android), title: Text('Electronics deals'), subtitle: Text('Price-drop watchlist'))])); }
