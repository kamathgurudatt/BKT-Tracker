import 'package:flutter/material.dart';
import '../widgets/sentinel_scaffold.dart';
class LocationsScreen extends StatelessWidget { const LocationsScreen({super.key}); @override Widget build(BuildContext context) => const SentinelScaffold(title: 'Multi-location Selector', child: Center(child: Text('Create locations through the API or app flow to validate real location-specific availability.'))); }
