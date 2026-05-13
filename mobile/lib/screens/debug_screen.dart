import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/app_state.dart';
import '../widgets/sentinel_scaffold.dart';

class DebugScreen extends StatefulWidget {
  const DebugScreen({super.key});

  @override
  State<DebugScreen> createState() => _DebugScreenState();
}

class _DebugScreenState extends State<DebugScreen> {
  Map<String, dynamic>? data;
  Map<String, dynamic>? testModeData;
  String? error;
  bool loading = false;
  final trackedProductController = TextEditingController();
  final locationController = TextEditingController();

  Future<void> load() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      data = await context.read<AppState>().api.debugMonitoring();
    } catch (e) {
      error = '$e';
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  Future<void> runTestMode() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      testModeData = await context.read<AppState>().api.debugTestMode(
        trackedProductId: int.parse(trackedProductController.text),
        locationId: int.parse(locationController.text),
      );
    } catch (e) {
      error = '$e';
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  void initState() {
    super.initState();
    Future.microtask(load);
  }

  @override
  Widget build(BuildContext context) {
    const encoder = JsonEncoder.withIndent('  ');
    final debugData = data;
    return SentinelScaffold(
      title: 'Raw Inventory Inspector',
      child: ListView(
        children: [
          FilledButton.icon(
            onPressed: loading ? null : load,
            icon: const Icon(Icons.refresh),
            label: const Text('Refresh live debug state'),
          ),
          const SizedBox(height: 12),
          const Text('Live Verification Test', style: TextStyle(fontWeight: FontWeight.bold)),
          if (loading) const LinearProgressIndicator(),
          if (error != null)
            SelectableText(
              error!,
              style: const TextStyle(color: Colors.red),
            ),
          if (debugData != null) ...[
            for (final key in const [
              'last_api_response_timestamp',
              'source_endpoint_called',
              'response_latency_ms',
              'response_timestamp',
              'location_id',
              'request_status',
              'last_detected_change_type',
              'live_data_available',
              'live_unavailable_message',
            ])
              ListTile(
                title: Text(key),
                subtitle: SelectableText('${debugData[key]}'),
              ),
            const Text('Raw stock response'),
            SelectableText(encoder.convert(debugData['raw_stock_response'] ?? {})),
            const Text('Request headers used'),
            SelectableText(encoder.convert(debugData['request_headers_used'] ?? {})),
            const Text('Parsed stock fields'),
            SelectableText(encoder.convert(debugData['parsed_stock_fields'] ?? {})),
            const Text('Location / pincode used'),
            SelectableText(encoder.convert(debugData['location_context'] ?? {})),
            const Text('Polling proof'),
            SelectableText(encoder.convert(debugData['polling_proof'] ?? {})),
            const Text('Inventory change proof'),
            SelectableText(encoder.convert(debugData['inventory_change_proof'] ?? [])),
            const Text('Endpoint audit'),
            SelectableText(encoder.convert(debugData['endpoint_audit'] ?? [])),
            const Text('Failed requests'),
            SelectableText(encoder.convert(debugData['failed_requests'] ?? [])),
          ],
          const Divider(),
          const Text('Test mode (15-second live polling)'),
          TextField(controller: trackedProductController, decoration: const InputDecoration(labelText: 'Tracked product ID')),
          TextField(controller: locationController, decoration: const InputDecoration(labelText: 'Location ID')),
          FilledButton(
            onPressed: loading ? null : runTestMode,
            child: const Text('Run test mode'),
          ),
          if (testModeData != null) ...[
            const Text('Raw vs parsed output (side-by-side)'),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Raw payload rounds'),
                      SelectableText(encoder.convert(testModeData!['rounds'] ?? [])),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Parsed fields (latest round)'),
                      SelectableText(
                        encoder.convert(((testModeData!['rounds'] as List).isNotEmpty)
                            ? (((testModeData!['rounds'] as List).last as Map<String, dynamic>)['payload'] ?? {})
                            : {}),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const Text('Inventory diffs'),
            SelectableText(encoder.convert(testModeData)),
          ],
        ],
      ),
    );
  }
}
