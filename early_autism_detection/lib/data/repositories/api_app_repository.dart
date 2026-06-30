import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/app_notification.dart';
import '../models/assessment_result.dart';
import '../models/child_profile.dart';
import '../models/parent_session.dart';
import '../models/recommendation.dart';
import 'app_repository.dart';

class ApiAppRepository implements AppRepository {
  final String baseUrl;
  final http.Client _client;

  ApiAppRepository({required this.baseUrl, http.Client? client})
      : _client = client ?? http.Client();

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  void _checkResponse(http.Response response) {
    if (response.statusCode >= 400) {
      try {
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(body['detail'] ?? 'Request failed');
      } catch (_) {
        throw Exception('Request failed (${response.statusCode})');
      }
    }
  }

  @override
  Future<ParentSession> loginParent({
    required String email,
    required String password,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: _headers,
      body: jsonEncode({'email': email, 'password': password}),
    );
    _checkResponse(response);
    return ParentSession.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  @override
  Future<ParentSession> signUpParent({
    required String name,
    required String email,
    required String password,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/auth/signup'),
      headers: _headers,
      body: jsonEncode({'name': name, 'email': email, 'password': password}),
    );
    _checkResponse(response);
    return ParentSession.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  @override
  Future<List<ChildProfile>> getChildren(String parentId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/parents/$parentId/children'),
      headers: _headers,
    );
    _checkResponse(response);
    final list = jsonDecode(response.body) as List<dynamic>;
    return list
        .map((e) => ChildProfile.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  @override
  Future<ChildProfile> addChild({
    required String parentId,
    required String name,
    required DateTime birthDate,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/parents/$parentId/children'),
      headers: _headers,
      body: jsonEncode({
        'name': name,
        'birth_date': birthDate.toIso8601String(),
      }),
    );
    _checkResponse(response);
    return ChildProfile.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  @override
  Future<ChildProfile> getProfile(String childId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/children/$childId'),
      headers: _headers,
    );
    _checkResponse(response);
    return ChildProfile.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  @override
  Future<ChildProfile> updateProfile(ChildProfile profile) async {
    final response = await _client.put(
      Uri.parse('$baseUrl/children/${profile.id}'),
      headers: _headers,
      body: jsonEncode({
        'name': profile.name,
        'birth_date': profile.birthDate.toIso8601String(),
      }),
    );
    _checkResponse(response);
    return ChildProfile.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  @override
  Future<AssessmentResult> getAssessment(String childId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/children/$childId/assessment'),
      headers: _headers,
    );
    _checkResponse(response);
    return AssessmentResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  @override
  Future<List<Recommendation>> getRecommendations({
    required String childId,
    required double level,
  }) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/children/$childId/recommendations'),
      headers: _headers,
    );
    _checkResponse(response);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    final list = body['recommendations'] as List<dynamic>;
    return list
        .map((e) => Recommendation.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  @override
  Future<AppNotification> getDailyReminder(String childId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/children/$childId/notifications/daily'),
      headers: _headers,
    );
    _checkResponse(response);
    return AppNotification.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }
}
