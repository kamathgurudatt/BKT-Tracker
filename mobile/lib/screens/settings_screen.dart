import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/app_state.dart';
import '../services/api_client.dart';
import '../widgets/sentinel_scaffold.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  static const _internalDeviceMode = bool.fromEnvironment('INTERNAL_DEVICE_MODE', defaultValue: true);
  final apiBaseUrl = TextEditingController();
  bool initialized = false;

  @override
  void dispose() {
    apiBaseUrl.dispose();
    super.dispose();
  }

  Future<void> _saveApiBaseUrl() async {
    final url = apiBaseUrl.text.trim();
    final uri = Uri.tryParse(url);
    if (uri == null || !uri.hasScheme || uri.host.isEmpty || (uri.scheme != 'http' && uri.scheme != 'https')) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter a valid backend URL starting with http:// or https://.')));
      return;
    }
    if (!uri.path.endsWith('/api/v1')) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Backend URL should end with /api/v1.')));
      return;
    }
    await context.read<AppState>().updateApiBaseUrl(url);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Backend URL saved: ${ApiClient.normalizeBaseUrl(url)}')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    if (!initialized) {
      apiBaseUrl.text = state.apiBaseUrl;
      initialized = true;
    }
    return SentinelScaffold(
      title: 'Settings',
      child: ListView(
        children: [
          SwitchListTile(title: const Text('Dark mode'), value: state.themeMode == ThemeMode.dark, onChanged: state.toggleDarkMode),
          const SizedBox(height: 12),
          if (!_internalDeviceMode) ...[
            TextField(
              controller: apiBaseUrl,
              decoration: const InputDecoration(
                labelText: 'Backend API URL',
                helperText: 'Use your hosted HTTPS backend URL (production/staging), or developer override URL.',
                prefixIcon: Icon(Icons.dns_outlined),
              ),
              keyboardType: TextInputType.url,
            ),
            const SizedBox(height: 8),
            FilledButton.icon(onPressed: _saveApiBaseUrl, icon: const Icon(Icons.save), label: const Text('Save backend URL')),
            const Divider(height: 32),
          ] else
            const ListTile(
              leading: Icon(Icons.link_off),
              title: Text('Backend URL is managed centrally'),
              subtitle: Text('Internal device mode hides API override to enforce Railway backend usage.'),
            ),
          const ListTile(title: Text('Polling frequency'), subtitle: Text('Safe default: every 15 minutes')),
          const ListTile(title: Text('Notification types'), subtitle: Text('Restock, price drop, ETA improvement')),
          const ListTile(title: Text('Alert sensitivity'), subtitle: Text('Balanced')),
          FilledButton.icon(onPressed: () => Navigator.pushNamed(context, '/locations'), icon: const Icon(Icons.location_on), label: const Text('Preferred locations')),
        ],
      ),
    );
  }
}
