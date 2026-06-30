import 'dart:math' as math;

import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class LoginBackground extends StatelessWidget {
  final Widget child;

  const LoginBackground({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Color(0xFF1B4965),
                Color(0xFF2A9D8F),
                Color(0xFF457B9D),
              ],
            ),
          ),
        ),
        CustomPaint(painter: _PuzzlePatternPainter()),
        Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.black.withOpacity(0.1),
                Colors.black.withOpacity(0.35),
              ],
            ),
          ),
        ),
        Positioned(
          top: -50,
          left: -40,
          child: Icon(
            Icons.family_restroom_rounded,
            size: 190,
            color: Colors.white.withOpacity(0.06),
          ),
        ),
        Positioned(
          bottom: 70,
          right: -20,
          child: Icon(
            Icons.child_care_rounded,
            size: 160,
            color: Colors.white.withOpacity(0.05),
          ),
        ),
        SafeArea(child: child),
      ],
    );
  }
}

class _PuzzlePatternPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final colors = [
      AppColors.puzzleBlue,
      AppColors.puzzleTeal,
      AppColors.puzzleGold,
      AppColors.puzzleCoral,
    ];
    final random = math.Random(42);
    for (var i = 0; i < 18; i++) {
      final paint = Paint()
        ..color = colors[i % colors.length].withOpacity(0.12)
        ..style = PaintingStyle.fill;
      final x = random.nextDouble() * size.width;
      final y = random.nextDouble() * size.height;
      final pieceSize = 30.0 + random.nextDouble() * 40;
      canvas.drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromCenter(
            center: Offset(x, y),
            width: pieceSize,
            height: pieceSize * 0.85,
          ),
          const Radius.circular(6),
        ),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
