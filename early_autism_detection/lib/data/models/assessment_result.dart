class AssessmentResult {
  final double level;
  final double confidenceScore;
  final String levelLabel;
  final DateTime? lastUpdated;

  const AssessmentResult({
    required this.level,
    required this.confidenceScore,
    required this.levelLabel,
    this.lastUpdated,
  });

  factory AssessmentResult.fromJson(Map<String, dynamic> json) {
    return AssessmentResult(
      level: (json['level'] as num).toDouble(),
      confidenceScore:
          (json['confidence_score'] ?? json['confidenceScore'] as num)
              .toDouble(),
      levelLabel: json['level_label'] as String? ??
          json['levelLabel'] as String? ??
          'Unknown',
      lastUpdated: json['last_updated'] != null
          ? DateTime.parse(json['last_updated'] as String)
          : null,
    );
  }

  int get confidencePercent => (confidenceScore * 100).round();
}
