import 'repositories/app_repository.dart';
import 'repositories/api_app_repository.dart';
import 'repositories/mock_app_repository.dart';
import 'api_app_repository.dart';
/// Global access to the active data source.
///
/// Default: [MockAppRepository] (local demo data).
/// When your API is ready, call once at app startup:
///
/// ```dart
/// RepositoryProvider.useApiRepository(baseUrl: 'https://canned-appear-gloater.ngrok-free.dev');
/// ```
class RepositoryProvider {
  static _repository = ApiAppRepository(baseUrl: 'https://canned-appear-gloater.ngrok-free.dev');

  static AppRepository get repository => _repository;

  static void useMockRepository() {
    _repository = MockAppRepository();
  }

  static void useApiRepository({required String baseUrl}) {
    _repository = ApiAppRepository(baseUrl: baseUrl);
  }
}
