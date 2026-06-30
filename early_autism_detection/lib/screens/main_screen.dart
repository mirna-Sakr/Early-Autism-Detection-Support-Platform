import 'package:flutter/material.dart';
import '../data/models/child_profile.dart';
import '../widgets/profile_avatar.dart';
import 'recommendations_screen.dart';

class MainScreen extends StatefulWidget {
  final ChildProfile profile;

  const MainScreen({
    super.key,
    required this.profile,
  });

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  late ChildProfile _profile;

  @override
  void initState() {
    super.initState();
    _profile = widget.profile;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Home'),
        backgroundColor: Colors.grey.shade800,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.grey.shade50,
              Colors.white,
            ],
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    LayoutBuilder(builder: (context, constr) {
                      final w = constr.maxWidth;
                      final avatarRadius = w < 360
                          ? 34.0
                          : w < 600
                              ? 40.0
                              : 48.0;
                      return Column(
                        children: [
                          ProfileAvatar(
                            imageUrl: _profile.imageUrl,
                            radius: avatarRadius,
                          ),
                          const SizedBox(height: 10),
                          Text(
                            'Welcome, ${_profile.name}',
                            style: TextStyle(
                              fontSize: avatarRadius * 0.5,
                              fontWeight: FontWeight.bold,
                              color: Colors.grey.shade800,
                            ),
                          ),
                        ],
                      );
                    }),
                  ],
                ),
              ),
              const SizedBox(height: 40),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  LayoutBuilder(builder: (context, constr) {
                    final width = constr.maxWidth;
                    final btnSize = width < 360
                        ? 72.0
                        : width < 600
                            ? 90.0
                            : 110.0;
                    return Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _buildIconButton(
                          context,
                          icon: Icons.analytics,
                          label: 'Track\nBehavior',
                          color: Colors.grey.shade600,
                          size: btnSize,
                          onTap: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text(
                                    'Use the bottom tabs to view dashboard and activities.'),
                              ),
                            );
                          },
                        ),
                        _buildIconButton(
                          context,
                          icon: Icons.recommend,
                          label: 'Recommend\nActivities',
                          color: Colors.grey.shade500,
                          size: btnSize,
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => RecommendationsScreen(
                                  childId: _profile.id,
                                ),
                              ),
                            );
                          },
                        ),
                        _buildIconButton(
                          context,
                          icon: Icons.person,
                          label: 'Child\nProfile',
                          color: Colors.grey.shade700,
                          size: btnSize,
                          onTap: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text(
                                    'Use the bottom Profile tab to view this child account.'),
                              ),
                            );
                          },
                        ),
                      ],
                    );
                  }),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildIconButton(
    BuildContext context, {
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
    double size = 90,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: color.withOpacity(0.2),
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                ),
              ],
            ),
            child: Icon(
              icon,
              size: size * 0.5,
              color: color,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: size * 0.14,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
