---
Plugin Manager
---

Module to simplify plugin instantiation and configuration. Handles plugin dispatch, config. Model is plugins are kept in hierarchy by 'category', beneath category are types:

\<package\>/plugins/\<category\>/[\<type\>/\<subtype\>/].py


---
Deployment
---

**As root**:

    $ git clone https://github.com/bnl-sdcc/plugin-manager.git
    $ cd plugin-manager
    $ python setup.py bdist_rpm
    $ rpm -Uhv dist/plugin-manager-<version>.noarch.rpm

**As user:**

    $ git clone https://github.com/bnl-sdcc/plugin-manager.git
    $ cd plugin-manager
    $ python setup.py install --home=$HOME
    $ export PYTHONPATH=$HOME/lib/python:$PYTHONPATH


