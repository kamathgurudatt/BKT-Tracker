import 'package:flutter/material.dart';

import 'services/api_client.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const BlinkitStockSentinelApp());
}

class BlinkitStockSentinelApp extends StatelessWidget {
  const BlinkitStockSentinelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Blinkit Stock Sentinel',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
        useMaterial3: true,
      ),
      home: const InternalConnectScreen(),
    );
  }
}

class InternalConnectScreen extends StatefulWidget {
  const InternalConnectScreen({super.key});

  @override
  State<InternalConnectScreen> createState() => _InternalConnectScreenState();
}

class _InternalConnectScreenState extends State<InternalConnectScreen> {
  final ApiClient _api = ApiClient();
  final TextEditingController _baseUrlController = TextEditingController();

  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _user;

  @override
  void initState() {
    super.initState();
    _baseUrlController.text = _api.baseUrl;
  }

  @override
  void dispose() {
    _baseUrlController.dispose();
    super.dispose();
  }

  Future<void> _verifyBackend() async {
    FocusScope.of(context).unfocus();
    setState(() {
      _loading = true;
      _error = null;
      _user = null;
    });

    try {
      final url = _baseUrlController.text.trim();
      if (!ApiClient.isValidBaseUrl(url)) {
        throw const ApiException('Please enter a valid http(s) backend URL.');
      }
      _api.updateBaseUrl(url);
      final user = await _api.currentUser();
      setState(() => _user = user);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = 'Unexpected error: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Blinkit Stock Sentinel')),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 520),
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: [
              const Card(
                child: ListTile(
                  leading: Icon(Icons.verified_user_outlined),
                  title: Text('Authentication-free internal access'),
                  subtitle: Text(
                    'This app does not use username/password. It verifies private-network access by calling /auth/me.',
                  ),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _baseUrlController,
                decoration: const InputDecoration(
                  labelText: 'API Base URL',
                  hintText: 'https://your-backend.example.com/api/v1',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: _loading ? null : _verifyBackend,
                icon: _loading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.cloud_done_outlined),
                label: Text(_loading ? 'Verifying...' : 'Verify backend via /auth/me'),
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
              ],
              if (_user != null) ...[
                const SizedBox(height: 16),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Connection successful', style: TextStyle(fontWeight: FontWeight.w700)),
                        const SizedBox(height: 8),
                        Text('Resolved internal user: ${_user!['email'] ?? _user!['id'] ?? 'unknown'}'),
                        const SizedBox(height: 4),
                        Text('Backend: ${_api.baseUrl}'),
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
