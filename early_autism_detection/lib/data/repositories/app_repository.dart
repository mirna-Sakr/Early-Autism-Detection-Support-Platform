import '../models/app_notification.dart';
import '../models/assessment_result.dart';
import '../models/child_profile.dart';
import '../models/parent_session.dart';
import '../models/recommendation.dart';

abstract class AppRepository {
  Future<ParentSession> loginParent({
    required String email,
    required String password,
  });

  Future<ParentSession> signUpParent({
    required String name,
    required String email,
    required String password,
  });

  Future<List<ChildProfile>> getChildren(String parentId);

  Future<ChildProfile> addChild({
    required String parentId,
    required String name,
    required DateTime birthDate,
  });

  Future<ChildProfile> getProfile(String childId);

  Future<ChildProfile> updateProfile(ChildProfile profile);

  Future<AssessmentResult> getAssessment(String childId);

  Future<List<Recommendation>> getRecommendations({
    required String childId,
    required double level,
  });

  Future<AppNotification> getDailyReminder(String childId);
}
