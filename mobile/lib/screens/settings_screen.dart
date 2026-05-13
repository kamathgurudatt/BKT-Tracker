import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';
import '../widgets/sentinel_scaffold.dart';
class SettingsScreen extends StatelessWidget { const SettingsScreen({super.key}); @override Widget build(BuildContext context) { final state = context.watch<AppState>(); return SentinelScaffold(title: 'Settings', child: ListView(children: [SwitchListTile(title: const Text('Dark mode'), value: state.themeMode == ThemeMode.dark, onChanged: state.toggleDarkMode), const ListTile(title: Text('Polling frequency'), subtitle: Text('Safe default: every 15 minutes')), const ListTile(title: Text('Notification types'), subtitle: Text('Restock, price drop, ETA improvement')), const ListTile(title: Text('Alert sensitivity'), subtitle: Text('Balanced')), FilledButton.icon(onPressed: () => Navigator.pushNamed(context, '/locations'), icon: const Icon(Icons.location_on), label: const Text('Preferred locations'))])); }}
