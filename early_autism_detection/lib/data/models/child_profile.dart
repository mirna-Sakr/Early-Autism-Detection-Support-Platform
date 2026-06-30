class ChildProfile {
  final String id;
  final String parentId;
  final String name;
  final DateTime birthDate;
  final String? imageUrl;
  final DateTime? lastAssessment;

  const ChildProfile({
    required this.id,
    required this.parentId,
    required this.name,
    required this.birthDate,
    this.imageUrl,
    this.lastAssessment,
  });

  int get age {
    final now = DateTime.now();
    var years = now.year - birthDate.year;
    if (now.month < birthDate.month ||
        (now.month == birthDate.month && now.day < birthDate.day)) {
      years--;
    }
    return years < 0 ? 0 : years;
  }

  ChildProfile copyWith({
    String? id,
    String? parentId,
    String? name,
    DateTime? birthDate,
    String? imageUrl,
    DateTime? lastAssessment,
  }) {
    return ChildProfile(
      id: id ?? this.id,
      parentId: parentId ?? this.parentId,
      name: name ?? this.name,
      birthDate: birthDate ?? this.birthDate,
      imageUrl: imageUrl ?? this.imageUrl,
      lastAssessment: lastAssessment ?? this.lastAssessment,
    );
  }

  factory ChildProfile.fromJson(Map<String, dynamic> json) {
    return ChildProfile(
      id: json['id'] as String? ??
          json['person_id'] as String? ??
          json['personId'] as String,
      parentId: json['parent_id'] as String? ?? json['parentId'] as String,
      name: json['name'] as String,
      birthDate: DateTime.parse(
        json['birth_date'] as String? ?? json['birthDate'] as String,
      ),
      imageUrl: json['image_url'] as String? ?? json['imageUrl'] as String?,
      lastAssessment: json['last_assessment'] != null
          ? DateTime.parse(json['last_assessment'] as String)
          : json['lastAssessment'] != null
              ? DateTime.parse(json['lastAssessment'] as String)
              : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'parent_id': parentId,
        'name': name,
        'birth_date': birthDate.toIso8601String(),
        'age': age,
        'image_url': imageUrl,
        'last_assessment': lastAssessment?.toIso8601String(),
      };
}
