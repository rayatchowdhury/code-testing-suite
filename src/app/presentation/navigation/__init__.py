"""
Navigation package for the Code Testing Suite.

Provides injectable navigation router to replace singleton NavigationService.
"""

from src.app.presentation.navigation.router import NavigationRouter

__all__ = ["NavigationRouter"]
