class ParentSession {
  final String parentId;
  final String name;
  final String email;
  final String? token;

  const ParentSession({
    required this.parentId,
    required this.name,
    required this.email,
    this.token,
  });

  factory ParentSession.fromJson(Map<String, dynamic> json) {
    return ParentSession(
      parentId: json['parent_id'] as String? ?? json['parentId'] as String,
      name: json['name'] as String,
      email: json['email'] as String,
      token: json['token'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'parent_id': parentId,
        'name': name,
        'email': email,
        'token': token,
      };
}
