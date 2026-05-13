import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../widgets/sentinel_scaffold.dart';
class AnalyticsScreen extends StatelessWidget { const AnalyticsScreen({super.key}); @override Widget build(BuildContext context) => SentinelScaffold(title: 'Analytics', child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Price movement', style: Theme.of(context).textTheme.titleLarge), SizedBox(height: 220, child: LineChart(LineChartData(lineBarsData: [LineChartBarData(spots: const [FlSpot(0, 120), FlSpot(1, 99), FlSpot(2, 105), FlSpot(3, 94)])]))), const ListTile(leading: Icon(Icons.local_fire_department), title: Text('Most restocked: Amul Butter')), const ListTile(leading: Icon(Icons.speed), title: Text('Fastest selling: iPhone 16'))])); }
