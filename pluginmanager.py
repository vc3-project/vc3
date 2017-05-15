__author__ = "Jose Caballero"
__copyright__ = "2017 Jose Caballero"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.12"
__maintainer__ = "Jose Caballero"
__email__ = "jcaballero@bnl.gov"
__status__ = "Production"


'''
Module to import plugin classes and to initialize them.
Example:
To get an instance of a plugin class "myplugin" in module
        package/plugins/typeA/kindB/myplugin.py
that expects and integer as input to the __init__() method:
 
>>> from pluginmanager import getplugin
>>> pluginobj = getplugin(['package', 'plugins', 'typeA', 'kindB'], 'myplugin', 3)
'''

import logging
import logging.handlers
import traceback

from pprint import pprint

class NullHandler(logging.Handler):
    ''' 
    This handler does nothing. It's intended to be used to avoid the
    "No handlers could be found for logger XXX" one-off warning. This is
    important for library code, which may contain code to log events. If a user
    of the library does not configure logging, the one-off warning might be
    produced; to avoid this, the library developer simply needs to instantiate
    a NullHandler and add it to the top-level logger of the library module or
    package.
    ''' 
    def handle(self, record):
        pass

    def emit(self, record):
        pass

    def createLock(self):
        self.lock = None


class PluginManagerImportFailure(Exception):
    '''
    Exception to be raised when importing the module fails
    '''
    def __init__(self, name, msg):
        '''
        Inputs
        ----------
        - name: the name of the class 
        - msg: the message raised during the attempt to import the class
        '''
        errormsg = "Failed to import plugin class {name} with error message: {msg}"
        self.value = errormsg.format(name=name, msg=msg)

    def __str__(self):
        return repr(self.value)


class PluginManagerInitFailure(Exception):
    '''
    Exception to be raised when initializing the plugin fails 
    '''
    def __init__(self, name, msg):
        '''
        Inputs
        ----------
        - name: the name of the class 
        - msg: the message raised during the attempt to initialize the plugin
        '''
        errormsg = "Failed to initialize plugin {name} with error message: {msg}"
        self.value = errormsg.format(name=name, msg=msg)

    def __str__(self):
        return repr(self.value)


def getpluginlist(paths, namelist, *k, **kw):
    '''
    Provides a list of initialized plugin objects. 

    Inputs
    ------
    - paths: list of subdirectories from where to import the plugin(s)
        Example:
            ["plugins", "databases", "mysql"]
            will import a plugin called mysql in module <package>/plugins/databases/mysql.py
    - namelist: list of plugins to be delivered
    - *k, **kw: arbitrary input options for the plugin's __init__() method

    Output
    ------
    a list of plugin objects

    Notes
    -----
    - Assumes the name of each plugin is also
        - the name of the module
        - the name of the single class in that module
    - Assumes all plugins in the list need the same input options
    '''
    log = logging.getLogger('getpluginlist')
    log.addHandler(NullHandler())
    log.debug('Starting')
    plist = []
    for name in namelist:
        po = getplugin(paths, name, *k, **kw)
        plist.append(po)
        log.debug('retrieved plugin %s' %name)
    log.info('delivering list of plugins %s' %plist)
    return plist


def getplugin(paths, name, *k, **kw):
    ''' 
    Provides a single initialized plugin object. 

    Inputs
    ------
    - paths: list of subdirectories from where to import the plugin(s)
        Example:
            ["plugins", "databases", "mysql"]
            will import a plugin called mysql in module <package>/plugins/databases/mysql.py
    - name: name of the plugin to be imported
    - *k, **kw: arbitrary input options for the plugin's __init__() method

    Output
    ------
    a plugin object

    Notes
    -----
    * Assumes the name of the plugin is also
        -- the name of the module
        -- the name of the single class in that module
    * A PluginManagerInitFailure exception is raised in case of failure
    '''
    log = logging.getLogger('getplugin')
    log.addHandler(NullHandler())
    log.debug('Starting')
    ko = getpluginclass(paths, name)
    try:
        po = ko(*k, **kw)
    except Exception, ex:
        log.error(ex)
        raise PluginManagerInitFailure(name, ex)

    log.debug('delivering plugin object %s' %po)
    return po

    
def getpluginclass(paths, name):
    '''
    Provides a plugin class, not yet initialized. 

    Inputs
    ------
    - paths: list of subdirectories from where to import the plugin(s)
        Example:
            ["plugins", "databases", "mysql"]
            will import a plugin called mysql in module <package>/plugins/databases/mysql.py
    - name: name of the plugin to be imported

    Output
    ------
    a plugin class (not an object)

    Notes
    -----
    * Assumes the name of the plugin is also
        -- the name of the module
        -- the name of the single class in that module
    * A PluginManagerImportFailure exception is raised in case of failure
    '''
    log = logging.getLogger('getpluginclass')
    log.addHandler(NullHandler())
    log.debug('Starting')

    ppath = '.'.join(paths)
    ppath = ppath + '.' + name
    log.debug('import class from path %s' %ppath)
    
    try:
        plugin_module = __import__(ppath, globals(), locals(), name)
    except Exception, ex:
        log.error(ex)
        raise PluginManagerImportFailure(name, ex)

    plugin_class = getattr(plugin_module, name)
    log.debug("delivering plugin class %s" % name)
    return plugin_class
