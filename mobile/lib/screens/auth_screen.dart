import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/app_state.dart';
import '../services/api_client.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  static const _internalDeviceMode = bool.fromEnvironment('INTERNAL_DEVICE_MODE', defaultValue: true);

  final _formKey = GlobalKey<FormState>();
  final apiBaseUrl = TextEditingController();
  bool loading = false;
  bool apiUrlEdited = false;
  String? error;

  @override
  void initState() {
    super.initState();
    if (_internalDeviceMode) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _connect());
    }
  }

  @override
  void dispose() {
    apiBaseUrl.dispose();
    super.dispose();
  }

  Future<void> _connect() async {
    FocusScope.of(context).unfocus();
    if (!_internalDeviceMode && !_formKey.currentState!.validate()) {
      setState(() => error = 'Please fix the highlighted backend URL.');
      return;
    }

    setState(() {
      loading = true;
      error = null;
    });

    try {
      final state = context.read<AppState>();
      if (!_internalDeviceMode) {
        await state.updateApiBaseUrl(apiBaseUrl.text);
      }
      await state.api.currentUser();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Connected to internal backend.')));
        Navigator.pushReplacementNamed(context, '/dashboard');
      }
    } on ApiException catch (exception) {
      if (mounted) {
        setState(() => error = exception.message);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(exception.message)));
      }
    } catch (exception) {
      final message = 'Backend connection failed: $exception';
      if (mounted) {
        setState(() => error = message);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      }
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  String? _validateApiBaseUrl(String? value) {
    final url = value?.trim() ?? '';
    if (url.isEmpty) return 'Backend API URL is required.';
    final uri = Uri.tryParse(url);
    if (uri == null || !uri.hasScheme || uri.host.isEmpty) return 'Enter a valid URL, for example http://192.168.1.10:8000/api/v1.';
    if (uri.scheme != 'http' && uri.scheme != 'https') return 'URL must start with http:// or https://.';
    if (!uri.path.endsWith('/api/v1')) return 'Backend URL should end with /api/v1.';
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final stateApiBaseUrl = context.watch<AppState>().apiBaseUrl;
    if (!apiUrlEdited && apiBaseUrl.text != stateApiBaseUrl) {
      apiBaseUrl.text = stateApiBaseUrl;
    }

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('Internal access', style: Theme.of(context).textTheme.headlineSmall),
                        const SizedBox(height: 16),
                        const ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: Icon(Icons.verified_user_outlined),
                          title: Text('No app credentials required'),
                          subtitle: Text('No password login is required. The app only verifies backend availability using /auth/me.'),
                        ),
                        const SizedBox(height: 8),
                        if (!_internalDeviceMode) ...[
                          TextFormField(
                            controller: apiBaseUrl,
                            decoration: const InputDecoration(
                              labelText: 'Backend API URL',
                              helperText: 'Use your hosted HTTPS backend URL (or developer override).',
                              prefixIcon: Icon(Icons.dns_outlined),
                            ),
                            keyboardType: TextInputType.url,
                            onChanged: (_) => apiUrlEdited = true,
                            validator: _validateApiBaseUrl,
                          ),
                          const SizedBox(height: 12),
                        ] else
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.cloud_done_outlined),
                            title: const Text('Using managed backend'),
                            subtitle: Text(stateApiBaseUrl),
                          ),
                        if (error != null) ...[
                          const SizedBox(height: 12),
                          Text(error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                        ],
                        const SizedBox(height: 16),
                        FilledButton.icon(
                          onPressed: loading ? null : _connect,
                          icon: loading
                              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                              : const Icon(Icons.verified_user_outlined),
                          label: Text(loading ? 'Connecting…' : 'Continue'),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
