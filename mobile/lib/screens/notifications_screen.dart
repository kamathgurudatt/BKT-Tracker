import 'package:flutter/material.dart';
import '../widgets/sentinel_scaffold.dart';
class NotificationsScreen extends StatelessWidget { const NotificationsScreen({super.key}); @override Widget build(BuildContext context) => const SentinelScaffold(title: 'Notification Center', child: Column(children: [ListTile(leading: Icon(Icons.notifications), title: Text('Amul Butter is back in stock in Andheri West')), ListTile(leading: Icon(Icons.price_change), title: Text('iPhone 16 price dropped by ₹1500 in Powai'))])); }
