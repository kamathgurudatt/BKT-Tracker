import 'package:flutter/material.dart';

import '../models/product.dart';
import '../services/api_client.dart';

class AppState extends ChangeNotifier {
  final ApiClient api = ApiClient();
  ThemeMode themeMode = ThemeMode.system;
  List<Product> searchResults = [];
  bool loading = false;
  String? errorMessage;

  void toggleDarkMode(bool enabled) {
    themeMode = enabled ? ThemeMode.dark : ThemeMode.light;
    notifyListeners();
  }

  void clearError() {
    errorMessage = null;
    notifyListeners();
  }

  Future<void> search(String query) async {
    final trimmed = query.trim();
    if (trimmed.length < 2) {
      errorMessage = 'Enter at least 2 characters to search.';
      notifyListeners();
      throw ApiException(errorMessage!);
    }

    loading = true;
    errorMessage = null;
    notifyListeners();
    try {
      searchResults = await api.search(trimmed);
      if (searchResults.isEmpty) {
        errorMessage = 'No live products returned for "$trimmed".';
      }
    } on ApiException catch (error) {
      errorMessage = error.message;
      rethrow;
    } catch (error) {
      errorMessage = 'Search failed: $error';
      rethrow;
    } finally {
      loading = false;
      notifyListeners();
    }
  }
}
