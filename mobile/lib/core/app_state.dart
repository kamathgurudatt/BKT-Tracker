import 'package:flutter/material.dart';
import '../models/product.dart';
import '../services/api_client.dart';

class AppState extends ChangeNotifier {
  final ApiClient api = ApiClient();
  ThemeMode themeMode = ThemeMode.system;
  List<Product> searchResults = [];
  bool loading = false;

  void toggleDarkMode(bool enabled) {
    themeMode = enabled ? ThemeMode.dark : ThemeMode.light;
    notifyListeners();
  }

  Future<void> search(String query) async {
    loading = true;
    notifyListeners();
    try {
      searchResults = await api.search(query);
    } finally {
      loading = false;
      notifyListeners();
    }
  }
}
