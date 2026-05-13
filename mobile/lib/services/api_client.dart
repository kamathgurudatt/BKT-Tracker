import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../models/product.dart';

class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient({this.baseUrl = const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000/api/v1')});
  final String baseUrl;
  String? token;

  Map<String, String> get _headers => {'Content-Type': 'application/json', if (token != null) 'Authorization': 'Bearer $token'};

  Future<void> login(String email, String password) async {
    final response = await _send(() => http.post(Uri.parse('$baseUrl/auth/login'), headers: _headers, body: jsonEncode({'email': email, 'password': password})));
    token = response['access_token'] as String?;
    if (token == null || token!.isEmpty) {
      throw const ApiException('Login response did not include an access token.');
    }
  }

  Future<void> signup(String email, String password, String fullName) async {
    await _send(() => http.post(Uri.parse('$baseUrl/auth/signup'), headers: _headers, body: jsonEncode({'email': email, 'password': password, 'full_name': fullName})));
  }

  Future<List<Product>> search(String query) async {
    final response = await _send(() => http.get(Uri.parse('$baseUrl/tracking/search?q=${Uri.encodeQueryComponent(query)}'), headers: _headers));
    if (response is! List) {
      throw const ApiException('Search response was not a list of products.');
    }
    return response.map((item) => Product.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<Map<String, dynamic>> debugMonitoring() async {
    final response = await _send(() => http.get(Uri.parse('$baseUrl/debug/monitoring'), headers: _headers));
    if (response is! Map<String, dynamic>) {
      throw const ApiException('Debug response was not an object.');
    }
    return response;
  }

  Future<dynamic> _send(Future<http.Response> Function() request) async {
    try {
      final response = await request().timeout(const Duration(seconds: 20));
      final body = response.body.isEmpty ? null : jsonDecode(response.body);
      if (response.statusCode >= 400) {
        throw ApiException(_extractError(body, response.statusCode), statusCode: response.statusCode);
      }
      return body;
    } on ApiException {
      rethrow;
    } on TimeoutException {
      throw const ApiException('Request timed out. Check that the backend is running and reachable.');
    } on SocketException {
      throw ApiException('Cannot connect to backend at $baseUrl. Start Docker Compose or update API_BASE_URL.');
    } on FormatException {
      throw const ApiException('Server returned an invalid response. Please check backend logs.');
    } catch (error) {
      throw ApiException('Unexpected error: $error');
    }
  }

  String _extractError(dynamic body, int statusCode) {
    if (body is Map<String, dynamic>) {
      final detail = body['detail'];
      if (detail is String && detail.isNotEmpty) return detail;
      if (detail is List && detail.isNotEmpty) {
        return detail.map((item) => item is Map<String, dynamic> ? (item['msg'] ?? item).toString() : item.toString()).join('\n');
      }
      final message = body['message'];
      if (message is String && message.isNotEmpty) return message;
    }
    return 'Request failed with HTTP $statusCode.';
  }
}
