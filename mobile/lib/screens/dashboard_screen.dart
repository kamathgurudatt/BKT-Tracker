import 'package:flutter/material.dart';
import '../widgets/sentinel_scaffold.dart';

class DashboardScreen extends StatelessWidget { const DashboardScreen({super.key}); @override Widget build(BuildContext context) => SentinelScaffold(title: 'Dashboard', child: GridView.count(crossAxisCount: 2, children: [for (final item in const [('Tracked', '24'), ('Restocks', '8'), ('Price drops', '3'), ('Locations', '5')]) Card(child: Center(child: Column(mainAxisSize: MainAxisSize.min, children: [Text(item.$2, style: Theme.of(context).textTheme.headlineMedium), Text(item.$1)])))])); }
