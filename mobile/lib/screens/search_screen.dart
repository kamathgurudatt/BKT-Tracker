import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/app_state.dart';
import '../services/api_client.dart';
import '../widgets/sentinel_scaffold.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final controller = TextEditingController();
  String? validationError;

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final query = controller.text.trim();
    if (query.length < 2) {
      setState(() => validationError = 'Enter at least 2 characters to search live inventory.');
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter at least 2 characters to search.')));
      return;
    }

    setState(() => validationError = null);
    try {
      await context.read<AppState>().search(query);
      if (mounted) {
        final state = context.read<AppState>();
        final message = state.searchResults.isEmpty ? (state.errorMessage ?? 'No products found.') : 'Loaded ${state.searchResults.length} live product result(s).';
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      }
    } on ApiException catch (exception) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(exception.message)));
      }
    } catch (exception) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Search failed: $exception')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    return SentinelScaffold(
      title: 'Search Products',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SearchBar(
            controller: controller,
            hintText: 'Search public live product listings',
            onSubmitted: (_) => _search(),
            trailing: [IconButton(icon: const Icon(Icons.search), onPressed: state.loading ? null : _search)],
          ),
          if (validationError != null) ...[
            const SizedBox(height: 8),
            Text(validationError!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ],
          if (state.errorMessage != null) ...[
            const SizedBox(height: 8),
            Text(state.errorMessage!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ],
          const SizedBox(height: 12),
          if (state.loading) const LinearProgressIndicator(),
          Expanded(
            child: state.searchResults.isEmpty && !state.loading
                ? const Center(child: Text('Search requires configured live provider endpoints. Errors will appear here if the backend rejects the request.'))
                : ListView.builder(
                    itemCount: state.searchResults.length,
                    itemBuilder: (_, i) {
                      final p = state.searchResults[i];
                      return Card(
                        child: ListTile(
                          leading: const Icon(Icons.shopping_bag),
                          title: Text(p.name),
                          subtitle: Text('${p.stockStatus} • ETA ${p.etaMinutes ?? '-'} min • ${p.locationLabel ?? 'default'}'),
                          trailing: Text('₹${p.price?.toStringAsFixed(0) ?? '-'}'),
                          onTap: () => Navigator.pushNamed(context, '/detail', arguments: p),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
