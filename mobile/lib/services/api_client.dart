import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/product.dart';

class ApiClient {
  ApiClient({this.baseUrl = const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000/api/v1')});
  final String baseUrl;
  String? token;

  Map<String, String> get _headers => {'Content-Type': 'application/json', if (token != null) 'Authorization': 'Bearer $token'};

  Future<void> login(String email, String password) async {
    final response = await http.post(Uri.parse('$baseUrl/auth/login'), headers: _headers, body: jsonEncode({'email': email, 'password': password}));
    if (response.statusCode >= 400) throw Exception('Login failed: ${response.body}');
    token = jsonDecode(response.body)['access_token'];
  }

  Future<void> signup(String email, String password, String fullName) async {
    final response = await http.post(Uri.parse('$baseUrl/auth/signup'), headers: _headers, body: jsonEncode({'email': email, 'password': password, 'full_name': fullName}));
    if (response.statusCode >= 400) throw Exception('Signup failed: ${response.body}');
  }

  Future<List<Product>> search(String query) async {
    final response = await http.get(Uri.parse('$baseUrl/tracking/search?q=${Uri.encodeQueryComponent(query)}'), headers: _headers);
    if (response.statusCode >= 400) throw Exception('Search failed: ${response.body}');
    return (jsonDecode(response.body) as List).map((item) => Product.fromJson(item)).toList();
  }
}
