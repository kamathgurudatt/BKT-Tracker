import 'package:flutter/material.dart';

class SplashScreen extends StatefulWidget { const SplashScreen({super.key}); @override State<SplashScreen> createState() => _SplashScreenState(); }
class _SplashScreenState extends State<SplashScreen> {
  @override void initState() { super.initState(); Future.delayed(const Duration(milliseconds: 800), () => Navigator.pushReplacementNamed(context, '/dashboard')); }
  @override Widget build(BuildContext context) => const Scaffold(body: Center(child: Column(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.bolt, size: 72, color: Colors.green), Text('Blinkit Stock Sentinel', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)), Text('Educational inventory monitoring')])));
}
