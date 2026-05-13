import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/app_state.dart';

class AuthScreen extends StatefulWidget { const AuthScreen({super.key}); @override State<AuthScreen> createState() => _AuthScreenState(); }
class _AuthScreenState extends State<AuthScreen> {
  final email = TextEditingController(); final password = TextEditingController(); bool register = false;
  @override Widget build(BuildContext context) => Scaffold(body: Center(child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 420), child: Card(child: Padding(padding: const EdgeInsets.all(24), child: Column(mainAxisSize: MainAxisSize.min, children: [Text(register ? 'Create account' : 'Welcome back', style: Theme.of(context).textTheme.headlineSmall), TextField(controller: email, decoration: const InputDecoration(labelText: 'Email')), TextField(controller: password, decoration: const InputDecoration(labelText: 'Password'), obscureText: true), const SizedBox(height: 16), FilledButton(onPressed: () async { final api = context.read<AppState>().api; if (register) await api.signup(email.text, password.text, 'Demo User'); await api.login(email.text, password.text); if (context.mounted) Navigator.pushReplacementNamed(context, '/dashboard'); }, child: Text(register ? 'Register & Login' : 'Login')), TextButton(onPressed: () => setState(() => register = !register), child: Text(register ? 'Have an account?' : 'Create an account'))])))));
}
