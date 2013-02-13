
import inspect

def lineno():
    #returns current line
    return inspect.currentframe().f_back.f_lineno

def validate_docstrings(o):
    ''' Docstrings are important because they describe how a function works. 
        This function checks an object and ensures it and its methods have
        docstrings'''
    
    if not hasattr(o, '__doc__') or o.__doc__ is None:
        err = "Class '%s' has no docstring!\n-> See %s:%s" % (o.__class__.__name__,
                                                              inspect.getsourcefile(o.__class__), 
                                                              inspect.getsourcelines(o.__class__)[1])
        raise Exception(err)
    
    for name, fn in inspect.getmembers(o, inspect.ismethod):
        if not hasattr(fn, '__doc__') or fn.__doc__ is None:
            err = "No docstring for '%s.%s()\n-> See %s:%s" % (o.__class__.__name__,
                                                             name,
                                                             inspect.getsourcefile(fn),
                                                             inspect.getsourcelines(fn)[1])
            raise Exception(err)
