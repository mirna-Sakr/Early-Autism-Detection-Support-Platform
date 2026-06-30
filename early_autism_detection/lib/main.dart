import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'theme/app_theme.dart';
// import 'data/repository_provider.dart';

void main() {
  // Switch to API when backend is running:
  // RepositoryProvider.useApiRepository(baseUrl: 'http://10.0.2.2:8000');

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Early Autism Detection',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: const LoginScreen(),
    );
  }
}
