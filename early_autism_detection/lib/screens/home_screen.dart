import 'package:flutter/material.dart';
import '../data/models/child_profile.dart';
import '../theme/app_theme.dart';
import '../widgets/autism_quote_card.dart';
import '../widgets/profile_avatar.dart';

class HomeScreen extends StatelessWidget {
  final ChildProfile child;
  final VoidCallback onSwitchChild;

  const HomeScreen({
    super.key,
    required this.child,
    required this.onSwitchChild,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            AppColors.primary.withOpacity(0.08),
            AppColors.background,
          ],
        ),
      ),
      child: SafeArea(
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
                child: Row(
                  children: [
                    ProfileAvatar(
                      imageUrl: child.imageUrl,
                      radius: 28,
                      backgroundColor: AppColors.primary.withOpacity(0.12),
                      iconColor: AppColors.primary,
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Welcome back',
                            style: TextStyle(
                              fontSize: 13,
                              color: AppColors.textSecondary,
                            ),
                          ),
                          Text(
                            child.name,
                            style: const TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                              color: AppColors.textPrimary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: onSwitchChild,
                      icon: const Icon(Icons.swap_horiz_rounded),
                      tooltip: 'Switch child',
                      color: AppColors.primary,
                    ),
                  ],
                ),
              ),
            ),
            SliverFillRemaining(
              hasScrollBody: false,
              child: LayoutBuilder(builder: (context, constr) {
                final width = constr.maxWidth;
                final iconSize = width < 360
                    ? 32.0
                    : width < 600
                        ? 44.0
                        : 56.0;
                return Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.favorite_rounded,
                      size: iconSize * 0.8,
                      color: AppColors.puzzleCoral.withOpacity(0.7),
                    ),
                    const SizedBox(height: 24),
                    AutismQuoteCard(childName: child.name),
                    const SizedBox(height: 28),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(22),
                        decoration: BoxDecoration(
                          color: AppColors.surface,
                          borderRadius: BorderRadius.circular(24),
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.primary.withOpacity(0.08),
                              blurRadius: 18,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: const Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Your child dashboard is ready',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            SizedBox(height: 10),
                            Text(
                              'Use the bottom navigation to move between Dashboard, Activities, and Profile for your selected child.',
                              style: TextStyle(
                                fontSize: 14,
                                height: 1.6,
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: Wrap(
                        alignment: WrapAlignment.center,
                        spacing: 10,
                        children: [
                          _buildPuzzleDot(AppColors.puzzleBlue),
                          _buildPuzzleDot(AppColors.puzzleTeal),
                          _buildPuzzleDot(AppColors.puzzleGold),
                          _buildPuzzleDot(AppColors.puzzleCoral),
                        ],
                      ),
                    ),
                  ],
                );
              }),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPuzzleDot(Color color) {
    return Container(
      width: 12,
      height: 12,
      decoration: BoxDecoration(
        color: color.withOpacity(0.6),
        borderRadius: BorderRadius.circular(3),
      ),
    );
  }
}
