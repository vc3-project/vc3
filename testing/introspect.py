#!/bin/env python
#
#  Simple harness to test object -> Dict -> object transformations. 
#


class Parent(object):
    
    def __repr__(self):
        s = "%s(" % self.__class__.__name__
        for a in self.__class__.attributes:
            s+="%s=%s " % (a, getattr(self, a, None))
        s += ")"
        return s

    def makeDictObject(self):
        d = {}
        d[self.name] = {}
        for attrname in self.__class__.attributes:
            d[self.name][attrname] = getattr(self, attrname)
        print("Returning dict: %s" % d)
        return d

    @classmethod
    def objectFromDict(cls, dict):
        name = dict.keys()[0]
        print("name is %s" % name)
        d = dict[name]
        print("dict is %s" % d)
        clsname = cls.__name__
        print("clsname is %s" % cls)        
        args = {}
        for key in cls.attributes:
            args[key] = d[key]
        print(args)
        eo = cls(**args)
        return eo




class Child(Parent):
    attributes = [ 'name',
                   'att1',
                  ]
    
    def __init__(self, name, att1):
        self.name = name
        self.att1 = att1


if __name__ == '__main__':
    print("introspection")

    c = Child(name='myname',att1 = 'attvalue1')
    print("obj is %s " % c)
    do = c.makeDictObject()
    print("dictobj is %s " % do)
    cobj = Child.objectFromDict(do)
    print("cobj is %s " % cobj)
    




