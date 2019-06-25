---
TO DO List
---

* potential idea: create a separate set of classes to request a plugin class
  or a plugin object when the class name is not the same as the module name.

* potential idea: implement a Factory class.
  It would keep track of objects already delivered, so a second instance of 
  the same plugin is not created.
  The class would inherited from PluginManager, and use the same methods, 
  but with a dictionary/list to record list of plugins already created.

* FIXME? is it a good idea to have 2 interfaces at the same time for the 
  methods getXYZ(). Right now, both a dictionary of paths and a string, are
  allowed. 
  It breaks rule 19 http://programmer.97things.oreilly.com/wiki/index.php/Convenience_Is_not_an_-ility 
  Maybe separate them into different methods?
  Maybe use just one and forget about the another? 
