import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class AutismQuoteCard extends StatefulWidget {
  final String childName;

  const AutismQuoteCard({super.key, required this.childName});

  static const _quotes = [
    (
      'Every child is a different kind of flower, and all together make this world a beautiful garden.',
      '— Unknown'
    ),
    (
      'Autism is not a disability, it\'s a different ability.',
      '— Stuart Duncan'
    ),
    (
      'It takes a village to raise a child. It takes a child with autism to raise the consciousness of the village.',
      '— Elaine Hall'
    ),
    (
      'Early detection opens doors to early intervention — and early intervention changes lives.',
      '— Early Detection Team'
    ),
  ];

  @override
  State<AutismQuoteCard> createState() => _AutismQuoteCardState();
}

class _AutismQuoteCardState extends State<AutismQuoteCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fade;
  late int _quoteIndex;

  @override
  void initState() {
    super.initState();
    _quoteIndex = DateTime.now().day % AutismQuoteCard._quotes.length;
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    );
    _fade = CurvedAnimation(parent: _controller, curve: Curves.easeOut);
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final quote = AutismQuoteCard._quotes[_quoteIndex];

    return FadeTransition(
      opacity: _fade,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 24),
        padding: const EdgeInsets.all(28),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppColors.primary.withOpacity( 0.12),
              AppColors.secondary.withOpacity( 0.08),
            ],
          ),
          borderRadius: BorderRadius.circular(28),
          border: Border.all(
            color: AppColors.primary.withOpacity( 0.2),
          ),
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity( 0.15),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.format_quote_rounded,
                color: AppColors.primary,
                size: 32,
              ),
            ),
            const SizedBox(height: 20),
            Text(
              quote.$1,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 17,
                height: 1.6,
                fontStyle: FontStyle.italic,
                color: AppColors.textPrimary,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              quote.$2,
              style: const TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 20),
            Text(
              'Supporting ${widget.childName}\'s journey',
              style: TextStyle(
                fontSize: 13,
                color: AppColors.primary.withOpacity( 0.8),
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
