class BehaviorMetrics {
  final double eyeContactPercentage;
  final double socialInteractionPercentage;
  final DateTime? lastUpdated;

  const BehaviorMetrics({
    required this.eyeContactPercentage,
    required this.socialInteractionPercentage,
    this.lastUpdated,
  });

  double get overallPercentage =>
      (eyeContactPercentage + socialInteractionPercentage) / 2;

  factory BehaviorMetrics.fromJson(Map<String, dynamic> json) {
    return BehaviorMetrics(
      eyeContactPercentage:
          (json['eye_contact'] ?? json['eyeContactPercentage'] as num)
              .toDouble(),
      socialInteractionPercentage: (json['social_interaction'] ??
              json['socialInteractionPercentage'] as num)
          .toDouble(),
      lastUpdated: json['last_updated'] != null
          ? DateTime.parse(json['last_updated'] as String)
          : json['lastUpdated'] != null
              ? DateTime.parse(json['lastUpdated'] as String)
              : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'eye_contact': eyeContactPercentage,
      'social_interaction': socialInteractionPercentage,
      'last_updated': lastUpdated?.toIso8601String(),
    };
  }
}
