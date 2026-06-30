import 'package:flutter/material.dart';
import '../data/models/recommendation.dart';
import '../data/repository_provider.dart';
import '../theme/app_theme.dart';

class RecommendationsScreen extends StatefulWidget {
  final String childId;

  const RecommendationsScreen({super.key, required this.childId});

  @override
  State<RecommendationsScreen> createState() => _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen> {
  List<Recommendation>? _recommendations;
  double _level = 0;
  bool _isLoading = true;
  String? _error;

  static const _icons = [
    Icons.self_improvement_rounded,
    Icons.record_voice_over_rounded,
    Icons.psychology_rounded,
    Icons.spa_rounded,
    Icons.groups_rounded,
    Icons.school_rounded,
    Icons.pool_rounded,
    Icons.palette_rounded,
  ];

  static const _colors = [
    AppColors.puzzleBlue,
    AppColors.puzzleTeal,
    AppColors.primary,
    AppColors.puzzleGold,
    AppColors.secondary,
    AppColors.puzzleCoral,
    AppColors.primaryDark,
    AppColors.puzzleBlue,
  ];

  @override
  void initState() {
    super.initState();
    _loadRecommendations();
  }

  Future<void> _loadRecommendations() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final repo = RepositoryProvider.repository;
      final assessment = await repo.getAssessment(widget.childId);
      final recommendations = await repo.getRecommendations(
        childId: widget.childId,
        level: assessment.level,
      );

      if (mounted) {
        setState(() {
          _recommendations = recommendations;
          _level = assessment.level;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString().replaceFirst('Exception: ', '');
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          _isLoading ? 'Recommendations' : 'Level ${_level.toStringAsFixed(1)} Activities',
        ),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: AppColors.primary),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_error!, style: const TextStyle(color: AppColors.error)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadRecommendations,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    final recommendations = _recommendations!;

    return RefreshIndicator(
      onRefresh: _loadRecommendations,
      color: AppColors.primary,
      child: ListView.builder(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(20),
        itemCount: recommendations.length + 1,
        itemBuilder: (context, index) {
          if (index == 0) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 20),
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      AppColors.primary.withOpacity( 0.1),
                      AppColors.secondary.withOpacity( 0.08),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.lightbulb_rounded,
                      color: AppColors.primary,
                      size: 32,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Text(
                        'Personalized activities based on your child\'s development level',
                        style: TextStyle(
                          fontSize: 14,
                          color: AppColors.textPrimary.withOpacity( 0.8),
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          }

          final item = recommendations[index - 1];
          final color = _colors[(index - 1) % _colors.length];
          final icon = _icons[(index - 1) % _icons.length];

          return _buildRecommendationCard(item, index - 1, color, icon);
        },
      ),
    );
  }

  Widget _buildRecommendationCard(
    Recommendation item,
    int index,
    Color color,
    IconData icon,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity( 0.1),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity( 0.12),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: color, size: 26),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    item.description,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppColors.textSecondary,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
