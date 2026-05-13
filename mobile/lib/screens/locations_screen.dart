import 'package:flutter/material.dart';

import '../widgets/sentinel_scaffold.dart';

class LocationsScreen extends StatelessWidget {
  const LocationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SentinelScaffold(
      title: 'Multi-location Selector',
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('No locations saved yet. Create locations through the API or app flow to validate real location-specific availability.'),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Location creation UI is not implemented yet. Use POST /api/v1/locations for now.')),
              ),
              icon: const Icon(Icons.info_outline),
              label: const Text('How do I add a location?'),
            ),
          ],
        ),
      ),
    );
  }
}
