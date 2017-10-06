#!/bin/env python

__author__ = "John Hover"
__copyright__ = "2017 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.1"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"

import logging

class InfoEntity(object):
    '''
    Template for Information entities. Common functions. 
    Classes that inherit from InfoEntity must set class variables to describe handling. 

    '''
    infokey = 'unset'
    infoattributes = []
    intattributes = []
    validvalues = {}

    def __setattr__(self, name, value):
        '''
        _difflist   List of (info)attributes that have been changed (not just 
                    initialized once.  
        '''
        log = logging.getLogger()        
        if name in self.__class__.infoattributes:
            try:
                diffmap = self._diffmap
            except AttributeError:
                diffmap = {}
                for at in self.__class__.infoattributes:
                    diffmap[at] = 0
                object.__setattr__(self,'_diffmap', diffmap)
            diffmap[name] += 1
            log.debug('infoattribute %s' % name)            
        else:
            log.debug('non-infoattribute %s' % name)
        object.__setattr__(self, name, value)


    def getDiffInfo(self):
        '''
        Return a list of info attributes which have been set > 1 time. 
        '''
        retlist = []
        try:
            diffmap = self._diffmap
        except AttributeError:
            pass
        for a in diffmap.keys():
            if diffmap[a] > 1:
                retlist.append(a)
        return retlist

        
    def __repr__(self):
        s = "%s( " % self.__class__.__name__
        for a in self.__class__.infoattributes:
            val = getattr(self, a, None)
            if isinstance(val, str) or isinstance(val, unicode):
                if len(val) > 80:
                    s+="%s=%s... " % (a, val[:25] )
                else:
                    s+="%s=%s " % (a, val )
            else:
                s+="%s=%s " % (a, val )
        s += ")"
        return s    

    def makeDictObject(self, newonly=False):
        '''
        Converts this Python object to attribute dictionary suitable for addition to existing dict 
        intended to be converted back to JSON. Uses <obj>.name as key:
        '''
        d = {}
        d[self.name] = {}
        if newonly:
            # only copy in values that have been re-set after initialization
            difflist = self.getDiffInfo()
            for attrname in difflist:
                d[self.name][attrname] = getattr(self, attrname)
        else:
            # copy in all infoattribute values
            for attrname in self.infoattributes:
                d[self.name][attrname] = getattr(self, attrname)
        self.log.debug("Returning dict: %s" % d)
        return d    

    def setState(self, newstate):
        self.log.debug("%s object name=%s %s ->%s" % (self.__class__.__name__, self.name, self.state, newstate) )
        self.state = newstate
    
    def store(self, infoclient):
        '''
        Stores this Info Entity in the provided infoclient info tree. 
        '''
        keystr = self.__class__.infokey
        validvalues = self.__class__.validvalues
        for keyattr in validvalues.keys():
            validlist = validvalues[keyattr]
            attrval = getattr(self, keyattr) 
            if attrval not in validlist:
                self.log.warning("%s entity has invalid value '%s' for attribute '%s' " % (self.__class__.__name__,
                                                                                           attrval,                                                                                            keyattr) )
        #resources = infoclient.getdocumentobject(key=keystr)
        da = self.makeDictObject()
        self.log.debug("Dict obj: %s" % da)
        infoclient.storedocumentobject(da, key=keystr)

    def addAcl(self, aclstring):
        pass    

    def removeAcl(self, aclstring):
        pass

    @classmethod
    def objectFromDict(cls, dict):
        '''
        Returns an initialized Entity object from dictionary. 
        Input: Dict:
        { <name> : 
            {
                "name" : "<name>",
                "att1" : "<val1>"  
            }
        }
        '''
        log = logging.getLogger()
        log.debug("Making object from dictionary...")
        name = dict.keys()[0]
        d = dict[name]
        args = {}
        for key in cls.infoattributes:
            try:
                args[key] = d[key]
            except KeyError, e:
                args[key] = None
                log.warning("Document object does not have a '%s' key" % e.args[0])
        for key in cls.intattributes:
            try:
                if args[key] is not None:
                    args[key] = int(args[key])
            except KeyError, e:
                log.warning("Document object does not have a '%s' key" % e.args[0])
        eo = cls(**args)
        log.debug("Successfully made object from dictionary, returning...")
        return eo

