import 'package:flutter/material.dart';
import '../data/models/assessment_result.dart';
import '../data/repository_provider.dart';
import '../theme/app_theme.dart';

class DashboardScreen extends StatefulWidget {
  final String childId;

  const DashboardScreen({super.key, required this.childId});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen>
    with SingleTickerProviderStateMixin {
  AssessmentResult? _assessment;
  bool _isLoading = true;
  String? _error;
  late AnimationController _animController;
  late Animation<double> _progressAnim;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );
    _progressAnim = CurvedAnimation(
      parent: _animController,
      curve: Curves.easeOutCubic,
    );
    _loadAssessment();
  }

  Future<void> _loadAssessment() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final result =
          await RepositoryProvider.repository.getAssessment(widget.childId);
      if (mounted) {
        setState(() {
          _assessment = result;
          _isLoading = false;
        });
        _animController.forward(from: 0);
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
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  Color _levelColor(double level) {
    if (level < 1.5) return AppColors.error;
    if (level < 2.5) return AppColors.warning;
    if (level < 3.5) return AppColors.secondary;
    return AppColors.success;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Dashboard')),
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
              onPressed: _loadAssessment,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    final assessment = _assessment!;
    final levelColor = _levelColor(assessment.level);

    return RefreshIndicator(
      onRefresh: _loadAssessment,
      color: AppColors.primary,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const SizedBox(height: 12),
            _buildLevelCard(assessment, levelColor),
            const SizedBox(height: 24),
            _buildConfidenceCard(assessment, levelColor),
          ],
        ),
      ),
    );
  }

  Widget _buildLevelCard(AssessmentResult assessment, Color levelColor) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(28),
        boxShadow: [
          BoxShadow(
            color: levelColor.withOpacity( 0.15),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: levelColor.withOpacity( 0.12),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.auto_graph_rounded, color: levelColor, size: 36),
          ),
          const SizedBox(height: 20),
          const Text(
            'Development Level',
            style: TextStyle(
              fontSize: 16,
              color: AppColors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 12),
          TweenAnimationBuilder<double>(
            tween: Tween(begin: 0, end: assessment.level),
            duration: const Duration(milliseconds: 1000),
            curve: Curves.easeOutCubic,
            builder: (context, value, _) {
              return Text(
                value.toStringAsFixed(1),
                style: TextStyle(
                  fontSize: 64,
                  fontWeight: FontWeight.bold,
                  color: levelColor,
                  height: 1,
                ),
              );
            },
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: levelColor.withOpacity( 0.12),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              assessment.levelLabel,
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: levelColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConfidenceCard(AssessmentResult assessment, Color levelColor) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppColors.primary.withOpacity( 0.08),
            AppColors.secondary.withOpacity( 0.06),
          ],
        ),
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: AppColors.primary.withOpacity( 0.15)),
      ),
      child: Column(
        children: [
          const Text(
            'Confidence Score',
            style: TextStyle(
              fontSize: 16,
              color: AppColors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 24),
          AnimatedBuilder(
            animation: _progressAnim,
            builder: (context, _) {
              final animatedValue =
                  assessment.confidenceScore * _progressAnim.value;
              return Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 160,
                    height: 160,
                    child: CircularProgressIndicator(
                      value: animatedValue,
                      strokeWidth: 14,
                      backgroundColor: Colors.grey.shade200,
                      valueColor:
                          const AlwaysStoppedAnimation<Color>(AppColors.primary),
                      strokeCap: StrokeCap.round,
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '${(animatedValue * 100).round()}%',
                        style: const TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const Text(
                        'AI Confidence',
                        style: TextStyle(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}
