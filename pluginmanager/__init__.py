"""
Package to import plugin classes and to initialize them.

Example:

To get an instance of a plugin class "myplugin" in module
        package/plugins/typeA/kindB/myplugin.py
that expects and integer as input to the __init__() method:
 
>>> from pluginmanager import PluginManager
>>> pm = PluginManager()
>>> pluginobj = pm.getplugin(['package', 'plugins', 'typeA', 'kindB'], 'myplugin', 3)
"""

__version__ = '1.0.0'

from pluginmanager import PluginManager

__all__ = ['PluginManager',
          ]
