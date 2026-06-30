import 'package:flutter/material.dart';
import '../data/models/child_profile.dart';
import '../data/models/parent_session.dart';
import 'child_selection_screen.dart';
import 'dashboard_screen.dart';
import 'home_screen.dart';
import 'profile_screen.dart';
import 'recommendations_screen.dart';

class AppShell extends StatefulWidget {
  final ParentSession parent;
  final ChildProfile child;

  const AppShell({
    super.key,
    required this.parent,
    required this.child,
  });

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _currentIndex = 0;
  late ChildProfile _child;

  @override
  void initState() {
    super.initState();
    _child = widget.child;
  }

  void _switchChild() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => ChildSelectionScreen(parent: widget.parent),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      HomeScreen(child: _child, onSwitchChild: _switchChild),
      DashboardScreen(childId: _child.id),
      RecommendationsScreen(childId: _child.id),
      ProfileScreen(
        childId: _child.id,
        parent: widget.parent,
        onSwitchChild: _switchChild,
        onProfileUpdated: (updated) => setState(() => _child = updated),
      ),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) =>
            setState(() => _currentIndex = index),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.insights_outlined),
            selectedIcon: Icon(Icons.insights_rounded),
            label: 'Dashboard',
          ),
          NavigationDestination(
            icon: Icon(Icons.lightbulb_outline_rounded),
            selectedIcon: Icon(Icons.lightbulb_rounded),
            label: 'Activities',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline_rounded),
            selectedIcon: Icon(Icons.person_rounded),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}
