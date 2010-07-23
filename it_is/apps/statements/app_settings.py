from os import path 

from django.conf import settings

"""
Settings specific to the ``statements`` application are defined here.
"""

_project_settings_registry = []

def _get_setting(project_setting_name, default=None, required=False):
    project_setting_name = "STATEMENTS_%s" % project_setting_name
    _project_settings_registry.insert(0, project_setting_name)
    if required and not default:
            assert hasattr(settings, project_setting_name), (
                "The following setting is required to use the scaffold "                    
                "application in your project: %s"
            ) %  project_setting_name
    return getattr(settings, project_setting_name, default)

HERE = path.normpath(path.dirname(__file__))

COLOR_DATA_FILE_PATH = _get_setting('COLOR_DATA_FILE_PATH',     
    default = HERE
)
