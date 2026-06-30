import '../models/app_notification.dart';
import '../models/assessment_result.dart';
import '../models/child_profile.dart';
import '../models/parent_session.dart';
import '../models/recommendation.dart';
import 'app_repository.dart';

class MockAppRepository implements AppRepository {
  final Map<String, ParentSession> _parents = {};
  final Map<String, String> _passwords = {};
  final Map<String, List<String>> _parentChildren = {};
  final Map<String, ChildProfile> _children = {};
  final Map<String, AssessmentResult> _assessments = {};

  MockAppRepository() {
    _seedDefaultData();
  }

  void _seedDefaultData() {
    const parentId = 'PARENT001';
    _parents[parentId] = const ParentSession(
      parentId: parentId,
      name: 'Ahmed Hassan',
      email: 'parent@demo.com',
    );
    _passwords['parent@demo.com'] = 'demo123';
    _parentChildren[parentId] = ['CHILD001', 'CHILD002'];

    _children['CHILD001'] = ChildProfile(
      id: 'CHILD001',
      parentId: parentId,
      name: 'Sara',
      birthDate: DateTime(2021, 3, 15),
      lastAssessment: DateTime.now().subtract(const Duration(days: 2)),
    );
    _assessments['CHILD001'] = const AssessmentResult(
      level: 2.5,
      confidenceScore: 0.78,
      levelLabel: 'Progressing Well',
    );

    _children['CHILD002'] = ChildProfile(
      id: 'CHILD002',
      parentId: parentId,
      name: 'Omar',
      birthDate: DateTime(2023, 8, 20),
      lastAssessment: DateTime.now().subtract(const Duration(days: 5)),
    );
    _assessments['CHILD002'] = const AssessmentResult(
      level: 1.8,
      confidenceScore: 0.65,
      levelLabel: 'Developing',
    );
  }

  static const _allRecommendations = [
    Recommendation(
      id: '1',
      title: 'Occupational Therapy',
      description:
          'Enhances daily living skills, fine motor coordination, and sensory integration.',
    ),
    Recommendation(
      id: '2',
      title: 'Speech Therapy',
      description:
          'Improves verbal and nonverbal communication and language comprehension.',
    ),
    Recommendation(
      id: '3',
      title: 'Applied Behavior Analysis',
      description:
          'Uses data-driven strategies to reinforce positive behaviors.',
    ),
    Recommendation(
      id: '4',
      title: 'Sensory Integration Therapy',
      description:
          'Helps regulate sensory processing and environmental responses.',
    ),
    Recommendation(
      id: '5',
      title: 'Social Skills Training',
      description:
          'Develops interpersonal communication and cooperative play.',
    ),
    Recommendation(
      id: '6',
      title: 'Special Education Programs',
      description: 'Structured learning tailored to individual needs.',
    ),
    Recommendation(
      id: '7',
      title: 'Aquatic Therapy',
      description:
          'Supports motor development through therapeutic water movement.',
    ),
    Recommendation(
      id: '8',
      title: 'Art & Music Therapy',
      description:
          'Facilitates emotional expression and social engagement.',
    ),
  ];

  String _levelLabel(double level) {
    if (level < 1.5) return 'Needs Support';
    if (level < 2.5) return 'Developing';
    if (level < 3.5) return 'Progressing Well';
    return 'On Track';
  }

  @override
  Future<ParentSession> loginParent({
    required String email,
    required String password,
  }) async {
    await Future.delayed(const Duration(milliseconds: 400));
    if (_passwords[email] != password) {
      throw Exception('Invalid email or password');
    }
    return _parents.values.firstWhere((p) => p.email == email);
  }

  @override
  Future<ParentSession> signUpParent({
    required String name,
    required String email,
    required String password,
  }) async {
    await Future.delayed(const Duration(milliseconds: 400));
    if (_passwords.containsKey(email)) {
      throw Exception('Email already registered');
    }

    final parentId = 'PARENT${DateTime.now().millisecondsSinceEpoch}';
    final session = ParentSession(
      parentId: parentId,
      name: name,
      email: email,
    );
    _parents[parentId] = session;
    _passwords[email] = password;
    _parentChildren[parentId] = [];
    return session;
  }

  @override
  Future<List<ChildProfile>> getChildren(String parentId) async {
    await Future.delayed(const Duration(milliseconds: 300));
    final ids = _parentChildren[parentId] ?? [];
    return ids.map((id) => _children[id]!).toList();
  }

  @override
  Future<ChildProfile> addChild({
    required String parentId,
    required String name,
    required DateTime birthDate,
  }) async {
    await Future.delayed(const Duration(milliseconds: 300));
    final childId = 'CHILD${DateTime.now().millisecondsSinceEpoch}';
    final child = ChildProfile(
      id: childId,
      parentId: parentId,
      name: name,
      birthDate: birthDate,
      lastAssessment: DateTime.now(),
    );
    _children[childId] = child;
    _parentChildren.putIfAbsent(parentId, () => []).add(childId);
    _assessments[childId] = AssessmentResult(
      level: 1.0,
      confidenceScore: 0.5,
      levelLabel: _levelLabel(1.0),
    );
    return child;
  }

  @override
  Future<ChildProfile> getProfile(String childId) async {
    await Future.delayed(const Duration(milliseconds: 200));
    final profile = _children[childId];
    if (profile == null) throw Exception('Child not found');
    return profile;
  }

  @override
  Future<ChildProfile> updateProfile(ChildProfile profile) async {
    await Future.delayed(const Duration(milliseconds: 200));
    _children[profile.id] = profile;
    return profile;
  }

  @override
  Future<AssessmentResult> getAssessment(String childId) async {
    await Future.delayed(const Duration(milliseconds: 250));
    return _assessments[childId] ??
        const AssessmentResult(
          level: 0,
          confidenceScore: 0,
          levelLabel: 'Not Assessed',
        );
  }

  @override
  Future<List<Recommendation>> getRecommendations({
    required String childId,
    required double level,
  }) async {
    await Future.delayed(const Duration(milliseconds: 200));
    if (level <= 2) return _allRecommendations.sublist(0, 3);
    if (level <= 3) return _allRecommendations.sublist(0, 6);
    return List.from(_allRecommendations);
  }

  @override
  Future<AppNotification> getDailyReminder(String childId) async {
    await Future.delayed(const Duration(milliseconds: 150));
    final child = _children[childId];
    return AppNotification(
      id: 'daily_reminder',
      title: 'Daily Reminder',
      message: child != null
          ? "Time to check in on ${child.name}'s progress today."
          : 'Time for daily observation.',
    );
  }
}
