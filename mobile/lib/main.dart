import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/app_state.dart';
import 'screens/analytics_screen.dart';
import 'screens/auth_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/debug_screen.dart';
import 'screens/locations_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/product_detail_screen.dart';
import 'screens/search_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/splash_screen.dart';
import 'screens/wishlist_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(ChangeNotifierProvider(create: (_) => AppState(), child: const SentinelApp()));
}

class SentinelApp extends StatelessWidget {
  const SentinelApp({super.key});

  @override
  Widget build(BuildContext context) {
    final mode = context.watch<AppState>().themeMode;
    return MaterialApp(
      title: 'Blinkit Stock Sentinel',
      debugShowCheckedModeBanner: false,
      themeMode: mode,
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.green), useMaterial3: true),
      darkTheme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.green, brightness: Brightness.dark), useMaterial3: true),
      initialRoute: '/',
      routes: {
        '/': (_) => const SplashScreen(),
        '/auth': (_) => const AuthScreen(),
        '/dashboard': (_) => const DashboardScreen(),
        '/search': (_) => const SearchScreen(),
        '/wishlist': (_) => const WishlistScreen(),
        '/detail': (_) => const ProductDetailScreen(),
        '/locations': (_) => const LocationsScreen(),
        '/analytics': (_) => const AnalyticsScreen(),
        '/notifications': (_) => const NotificationsScreen(),
        '/settings': (_) => const SettingsScreen(),
        '/debug': (_) => const DebugScreen(),
      },
    );
  }
}
