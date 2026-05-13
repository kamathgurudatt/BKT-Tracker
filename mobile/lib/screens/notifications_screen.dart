import 'package:flutter/material.dart';
import '../widgets/sentinel_scaffold.dart';
class NotificationsScreen extends StatelessWidget { const NotificationsScreen({super.key}); @override Widget build(BuildContext context) => const SentinelScaffold(title: 'Notification Center', child: Center(child: Text('Notifications appear only after genuine live inventory changes are confirmed.'))); }
