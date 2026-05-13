import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';
import '../widgets/sentinel_scaffold.dart';

class SearchScreen extends StatefulWidget { const SearchScreen({super.key}); @override State<SearchScreen> createState() => _SearchScreenState(); }
class _SearchScreenState extends State<SearchScreen> { final controller = TextEditingController(text: 'amul butter');
  @override Widget build(BuildContext context) { final state = context.watch<AppState>(); return SentinelScaffold(title: 'Search Products', child: Column(children: [SearchBar(controller: controller, hintText: 'Search public product listings', onSubmitted: state.search, trailing: [IconButton(icon: const Icon(Icons.search), onPressed: () => state.search(controller.text))]), const SizedBox(height: 12), if (state.loading) const LinearProgressIndicator(), Expanded(child: ListView.builder(itemCount: state.searchResults.length, itemBuilder: (_, i) { final p = state.searchResults[i]; return Card(child: ListTile(leading: const Icon(Icons.shopping_bag), title: Text(p.name), subtitle: Text('${p.stockStatus} • ETA ${p.etaMinutes ?? '-'} min • ${p.locationLabel ?? 'default'}'), trailing: Text('₹${p.price?.toStringAsFixed(0) ?? '-'}'), onTap: () => Navigator.pushNamed(context, '/detail', arguments: p))); }))])); }}
