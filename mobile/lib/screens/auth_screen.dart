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
  static const _internalEmail = String.fromEnvironment('INTERNAL_USER_EMAIL', defaultValue: 'internal.device@blinkitsentinel.app');
  static const _internalPassword = String.fromEnvironment('INTERNAL_USER_PASSWORD', defaultValue: 'InternalDevice@123');

  final _formKey = GlobalKey<FormState>();
  final apiBaseUrl = TextEditingController();
  final email = TextEditingController();
  final password = TextEditingController();
  bool register = false;
  bool loading = false;
  bool apiUrlEdited = false;
  String? error;

  @override
  void initState() {
    super.initState();
    if (_internalDeviceMode) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _autoLoginInternalDevice());
    }
  }

  @override
  void dispose() {
    apiBaseUrl.dispose();
    email.dispose();
    password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    FocusScope.of(context).unfocus();
    if (!_formKey.currentState!.validate()) {
      setState(() => error = 'Please fix the highlighted fields.');
      return;
    }

    setState(() {
      loading = true;
      error = null;
    });

    try {
      final state = context.read<AppState>();
      await state.updateApiBaseUrl(apiBaseUrl.text);
      final api = state.api;
      if (register) {
        await api.signup(email.text.trim(), password.text, 'Blinkit Stock Sentinel User');
      }
      await api.login(email.text.trim(), password.text);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(register ? 'Account created. Logged in successfully.' : 'Logged in successfully.')),
        );
        Navigator.pushReplacementNamed(context, '/dashboard');
      }
    } on ApiException catch (exception) {
      if (mounted) {
        setState(() => error = exception.message);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(exception.message)));
      }
    } catch (exception) {
      final message = 'Authentication failed: $exception';
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

  Future<void> _autoLoginInternalDevice() async {
    if (loading) return;
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final state = context.read<AppState>();
      final api = state.api;
      try {
        await api.signup(_internalEmail, _internalPassword, 'Internal Device User');
      } on ApiException {
        // User may already exist; continue with login.
      }
      await api.login(_internalEmail, _internalPassword);
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/dashboard');
      }
    } on ApiException catch (exception) {
      if (mounted) {
        setState(() => error = exception.message);
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

  String? _validateEmail(String? value) {
    final emailText = value?.trim() ?? '';
    if (emailText.isEmpty) return 'Email is required.';
    if (!RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(emailText)) return 'Enter a valid email address.';
    return null;
  }

  String? _validatePassword(String? value) {
    final passwordText = value ?? '';
    if (passwordText.isEmpty) return 'Password is required.';
    if (passwordText.length < 8) return 'Password must be at least 8 characters.';
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
                        Text(
                          register ? 'Create account' : 'Welcome back',
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 16),
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
                        ],
                        if (_internalDeviceMode) ...[
                          const ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: Icon(Icons.verified_user_outlined),
                            title: Text('Internal device mode enabled'),
                            subtitle: Text('Using preconfigured Railway backend and device account.'),
                          ),
                          const SizedBox(height: 8),
                        ],
                        if (!_internalDeviceMode) TextFormField(
                          controller: email,
                          decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email_outlined)),
                          keyboardType: TextInputType.emailAddress,
                          autofillHints: const [AutofillHints.email],
                          validator: _validateEmail,
                        ),
                        if (!_internalDeviceMode) const SizedBox(height: 12),
                        if (!_internalDeviceMode) TextFormField(
                          controller: password,
                          decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock_outline)),
                          obscureText: true,
                          autofillHints: const [AutofillHints.password],
                          validator: _validatePassword,
                        ),
                        if (error != null) ...[
                          const SizedBox(height: 12),
                          Text(error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                        ],
                        const SizedBox(height: 16),
                        if (!_internalDeviceMode) FilledButton(
                          onPressed: loading ? null : _submit,
                          child: loading
                              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                              : Text(register ? 'Register & Login' : 'Login'),
                        ),
                        if (!_internalDeviceMode) TextButton(
                          onPressed: loading ? null : () => setState(() => register = !register),
                          child: Text(register ? 'Have an account?' : 'Create an account'),
                        ),
                        if (_internalDeviceMode && loading)
                          const Padding(
                            padding: EdgeInsets.only(top: 8),
                            child: CircularProgressIndicator(strokeWidth: 2),
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
