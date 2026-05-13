import 'package:flutter/material.dart';

import '../widgets/sentinel_scaffold.dart';

class WishlistScreen extends StatelessWidget {
  const WishlistScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SentinelScaffold(
      title: 'Wishlists',
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('No placeholder inventory is shown. Add products from live search results to populate wishlists.'),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: () => Navigator.pushNamed(context, '/search'),
              icon: const Icon(Icons.search),
              label: const Text('Go to search'),
            ),
          ],
        ),
      ),
    );
  }
}
