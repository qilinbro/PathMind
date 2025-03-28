"""
页面组件导出模块
"""

from .dashboard import create_dashboard_tab
from .assessment import create_assessment_tab
from .learning_paths import create_learning_paths_tab
from .content_viewer import create_content_viewer_tab
from .adaptive_test import create_adaptive_test_tab
from .analytics import create_analytics_tab

__all__ = [
    'create_dashboard_tab',
    'create_assessment_tab',
    'create_learning_paths_tab',
    'create_content_viewer_tab',
    'create_adaptive_test_tab',
    'create_analytics_tab'
]
