import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/app_state.dart';
import '../services/api_client.dart';
import '../widgets/sentinel_scaffold.dart';

class LocationsScreen extends StatefulWidget {
  const LocationsScreen({super.key});

  @override
  State<LocationsScreen> createState() => _LocationsScreenState();
}

class _LocationsScreenState extends State<LocationsScreen> {
  final _name = TextEditingController();
  final _pincode = TextEditingController();
  bool _loading = false;
  List<Map<String, dynamic>> _locations = const [];

  @override
  void initState() { super.initState(); _load(); }
  @override
  void dispose() { _name.dispose(); _pincode.dispose(); super.dispose(); }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      _locations = await context.read<AppState>().api.listLocations();
    } on ApiException catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } finally { if (mounted) setState(() => _loading = false); }
  }

  Future<void> _create() async {
    if (_name.text.trim().length < 2) return;
    try {
      await context.read<AppState>().api.createLocation(name: _name.text.trim(), pincode: _pincode.text.trim().isEmpty ? null : _pincode.text.trim());
      _name.clear(); _pincode.clear();
      await _load();
    } on ApiException catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    }
  }

  @override
  Widget build(BuildContext context) {
    return SentinelScaffold(
      title: 'Multi-location Selector',
      child: Column(children: [
        Row(children: [
          Expanded(child: TextField(controller: _name, decoration: const InputDecoration(labelText: 'Location name'))),
          const SizedBox(width: 8),
          SizedBox(width: 120, child: TextField(controller: _pincode, decoration: const InputDecoration(labelText: 'Pincode'))),
          const SizedBox(width: 8),
          FilledButton(onPressed: _create, child: const Text('Add')),
        ]),
        const SizedBox(height: 12),
        if (_loading) const LinearProgressIndicator(),
        Expanded(child: ListView.builder(itemCount: _locations.length, itemBuilder: (_, i){
          final l=_locations[i];
          return CheckboxListTile(value: false, onChanged: null, title: Text(l['name']?.toString()??'Location'), subtitle: Text('id: ${l['id']} • pincode: ${l['pincode'] ?? '-'}'));
        }))
      ]),
    );
  }
}
