import 'package:flutter/material.dart';

class SentinelScaffold extends StatelessWidget {
  const SentinelScaffold({super.key, required this.title, required this.child});
  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(title)),
    body: SafeArea(child: Padding(padding: const EdgeInsets.all(16), child: child)),
    bottomNavigationBar: NavigationBar(destinations: const [
      NavigationDestination(icon: Icon(Icons.dashboard), label: 'Home'),
      NavigationDestination(icon: Icon(Icons.search), label: 'Search'),
      NavigationDestination(icon: Icon(Icons.favorite), label: 'Wishlist'),
      NavigationDestination(icon: Icon(Icons.analytics), label: 'Analytics'),
      NavigationDestination(icon: Icon(Icons.settings), label: 'Settings'),
    ], onDestinationSelected: (index) {
      final routes = ['/dashboard', '/search', '/wishlist', '/analytics', '/settings'];
      Navigator.of(context).pushNamed(routes[index]);
    }),
  );
}
