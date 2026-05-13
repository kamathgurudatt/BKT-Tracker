import 'package:flutter/material.dart';
import '../widgets/sentinel_scaffold.dart';

class DashboardScreen extends StatelessWidget { const DashboardScreen({super.key}); @override Widget build(BuildContext context) => SentinelScaffold(title: 'Dashboard', child: ListView(children: [const ListTile(leading: Icon(Icons.verified), title: Text('Live data only'), subtitle: Text('Dashboard metrics populate after real Blinkit endpoint responses are received.')), FilledButton.icon(onPressed: () => Navigator.pushNamed(context, '/debug'), icon: const Icon(Icons.bug_report), label: const Text('Open Debug Monitoring Mode'))])); }
