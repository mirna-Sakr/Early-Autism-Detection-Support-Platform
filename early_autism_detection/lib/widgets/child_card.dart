import 'package:flutter/material.dart';
import '../data/models/child_profile.dart';
import '../theme/app_theme.dart';
import 'profile_avatar.dart';

class ChildCard extends StatelessWidget {
  final ChildProfile child;
  final VoidCallback onTap;
  final bool isSelected;

  const ChildCard({
    super.key,
    required this.child,
    required this.onTap,
    this.isSelected = false,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 250),
      curve: Curves.easeOutCubic,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(24),
          child: Ink(
            decoration: BoxDecoration(
              color: isSelected
                  ? AppColors.primary.withOpacity( 0.08)
                  : AppColors.surface,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(
                color: isSelected ? AppColors.primary : Colors.grey.shade200,
                width: isSelected ? 2 : 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primary.withOpacity( 0.08),
                  blurRadius: 16,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  ProfileAvatar(
                    imageUrl: child.imageUrl,
                    radius: 32,
                    backgroundColor: AppColors.primary.withOpacity( 0.12),
                    iconColor: AppColors.primary,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          child.name,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${child.age} years old',
                          style: const TextStyle(
                            fontSize: 14,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    Icons.arrow_forward_ios_rounded,
                    size: 18,
                    color: isSelected ? AppColors.primary : AppColors.navInactive,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
