import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/app_state.dart';
import '../widgets/sentinel_scaffold.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  bool loading = true;
  String? error;
  List<Map<String, dynamic>> availability = const [];
  List<Map<String, dynamic>> notifications = const [];

  @override
  void initState() {
    super.initState();
    Future.microtask(_load);
  }

  Future<void> _load() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final api = context.read<AppState>().api;
      final a = await api.analyticsAvailability();
      final n = await api.analyticsNotifications();
      if (mounted) {
        setState(() {
          availability = a;
          notifications = n;
        });
      }
    } catch (e) {
      if (mounted) setState(() => error = '$e');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  List<FlSpot> _spots() {
    if (availability.isEmpty) return const [FlSpot(0, 0)];
    return [
      for (var i = 0; i < availability.length; i++) FlSpot(i.toDouble(), (availability[i]['value'] as num?)?.toDouble() ?? 0),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return SentinelScaffold(
      title: 'Analytics',
      child: ListView(
        children: [
          FilledButton.icon(onPressed: loading ? null : _load, icon: const Icon(Icons.refresh), label: const Text('Refresh analytics')),
          const SizedBox(height: 12),
          Text('Live availability counts', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          if (loading) const LinearProgressIndicator(),
          if (error != null) Text(error!, style: const TextStyle(color: Colors.red)),
          SizedBox(
            height: 220,
            child: LineChart(
              LineChartData(
                lineBarsData: [LineChartBarData(spots: _spots(), isCurved: false)],
              ),
            ),
          ),
          const SizedBox(height: 8),
          if (availability.isEmpty)
            const ListTile(title: Text('No live analytics yet'), subtitle: Text('Track products and wait for worker polling to populate analytics.')),
          for (final point in availability.take(10))
            ListTile(
              leading: const Icon(Icons.analytics_outlined),
              title: Text((point['label'] ?? 'Unknown').toString()),
              subtitle: Text('In-stock observations: ${(point['value'] ?? 0).toString()}'),
            ),
          const Divider(),
          Text('Recent notifications', style: Theme.of(context).textTheme.titleLarge),
          if (notifications.isEmpty)
            const ListTile(title: Text('No notifications yet'), subtitle: Text('Notifications appear after live changes are detected.')),
          for (final n in notifications.take(10))
            ListTile(
              leading: const Icon(Icons.notifications_active_outlined),
              title: Text((n['title'] ?? 'Notification').toString()),
              subtitle: Text((n['body'] ?? '').toString()),
            ),
        ],
      ),
    );
  }
}
