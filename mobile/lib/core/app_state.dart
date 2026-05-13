import 'dart:async';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/product.dart';
import '../services/api_client.dart';

class AppState extends ChangeNotifier {
  AppState() {
    unawaited(loadSettings());
  }

  static const _apiBaseUrlPreferenceKey = 'api_base_url';

  final ApiClient api = ApiClient();
  ThemeMode themeMode = ThemeMode.system;
  List<Product> searchResults = [];
  bool loading = false;
  bool settingsLoaded = false;
  String? errorMessage;

  String get apiBaseUrl => api.baseUrl;

  Future<void> loadSettings() async {
    final preferences = await SharedPreferences.getInstance();
    final savedApiBaseUrl = preferences.getString(_apiBaseUrlPreferenceKey);
    if (savedApiBaseUrl != null && savedApiBaseUrl.trim().isNotEmpty) {
      api.updateBaseUrl(savedApiBaseUrl);
    }
    settingsLoaded = true;
    notifyListeners();
  }

  Future<void> updateApiBaseUrl(String value) async {
    final normalized = ApiClient.normalizeBaseUrl(value);
    api.updateBaseUrl(normalized);
    final preferences = await SharedPreferences.getInstance();
    await preferences.setString(_apiBaseUrlPreferenceKey, normalized);
    errorMessage = null;
    notifyListeners();
  }

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
