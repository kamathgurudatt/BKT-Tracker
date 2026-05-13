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
  String? error;
  bool loading = false;

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
      title: 'Debug Monitoring Mode',
      child: ListView(
        children: [
          FilledButton.icon(
            onPressed: loading ? null : load,
            icon: const Icon(Icons.refresh),
            label: const Text('Refresh live debug state'),
          ),
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
              'location_id',
              'request_status',
              'last_detected_change_type',
            ])
              ListTile(
                title: Text(key),
                subtitle: SelectableText('${debugData[key]}'),
              ),
            const Text('Raw stock response'),
            SelectableText(encoder.convert(debugData['raw_stock_response'] ?? {})),
            const Text('Request headers used'),
            SelectableText(encoder.convert(debugData['request_headers_used'] ?? {})),
            const Text('Failed requests'),
            SelectableText(encoder.convert(debugData['failed_requests'] ?? [])),
          ],
        ],
      ),
    );
  }
}
