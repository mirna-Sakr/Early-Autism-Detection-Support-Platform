import 'repositories/app_repository.dart';
import 'repositories/api_app_repository.dart';
import 'repositories/mock_app_repository.dart';

/// Global access to the active data source.
///
/// Default: [MockAppRepository] (local demo data).
/// When your API is ready, call once at app startup:
///
/// ```dart
/// RepositoryProvider.useApiRepository(baseUrl: 'https://your-api.com');
/// ```
class RepositoryProvider {
  static AppRepository _repository = MockAppRepository();

  static AppRepository get repository => _repository;

  static void useMockRepository() {
    _repository = MockAppRepository();
  }

  static void useApiRepository({required String baseUrl}) {
    _repository = ApiAppRepository(baseUrl: baseUrl);
  }
}
