from __future__ import annotations
from inspect import signature
from types import FunctionType as function

def is_dunder (methodname : str) :
    return methodname.startswith('__') and methodname.endswith('__')

def get_defining_class (cls : type, methodname : str) :
    return '.'.join(getattr(cls, methodname).__code__.co_qualname.split('.')[:-1])

def get_non_dunder_attrs (cls : type) :
    return [getattr(cls, i) for i in dir(cls) if not is_dunder(i)]

def bases (cls : type, parent : type) :
    """
    Checks whether or not a particular class is a subclass of a particular parent. 
    
    Bypasses isinstance and issubclass checks, meaning it works in a traditional way on
    interfaces.

    Equivalent to the ClassSignature method. 
    """
    return ClassSignature(cls).bases(parent)


class PropertySignature :
    def __init__ (self, target : property) :
        self.property = target
        self.fget = signature(target.fget)
        self.fset = signature(target.fset)
        self.fdel = signature(target.fdel)


def universal_signature (obj) :
    """
    Returns a universal signature for the object. 
    If the object is a property returns a PropertySignature that serves as a compound
    signature object for that property's getter, setter, and deleter methods using 
    inspect.signature. 
    If the object is callable, returns inspect.signature of the object. 
    Else, returns the object itself (presumed static; can be directly checked for equality).
    """

    if isinstance(obj, property) : return PropertySignature(obj)
    if callable(obj) : return signature(obj)
    return obj

class ClassSignature :
    def __init__ (self, cls : type) :
        self.cls = cls
        self.attrs = get_non_dunder_attrs(cls)
        self.signatures = [universal_signature(i) for i in self.attrs]
        self.default_attrs = [i for i in self.attrs if hasattr(i, "__defaultmethod__")]
    
    def equals (self, target : ClassSignature | type) -> bool :
        """
        Checks if two class signatures have identical attribute signatures. Ignores
        differences in dunders. 
        """
        if isinstance(target, type) : target = ClassSignature(target)
        return self.signatures == target.signatures

    def bases (self, target : ClassSignature | type) -> bool :
        """
        Checks if this class signature bases (read: subclasses) another class.
        """
        if isinstance(target, type) : target = ClassSignature(target)
        return target.cls in self.cls.__bases__

    def implements (self, interface : ClassSignature | type) -> bool :
        """
        Checks if this class signature contains appropriate signatures to implement
        an interface. Returns True if all of the non-default attribute signatures in the 
        interface are present in this class signature.

        If this class signature does not subclass the interface, also checks that all
        default methods are implemented, as they would not otherwise be inherited. 
        """
        if isinstance(interface, type) : interface = ClassSignature(interface)
        if not self.bases(interface) : return self.contains(interface)

        for isig in interface.signatures :
            if isig not in self.signatures and isig not in interface.default_attrs :
                return False
        return True

    def contains (self, cls : ClassSignature | type) -> bool :
        """
        Checks if this class signature is a superset of (contains) the other class 
        signature. All attribute signatures in the other class signature must be present 
        in this class signature, but not vice versa, for this to return true. 
        """
        if isinstance(cls, type) : cls = ClassSignature(cls)
        for sig in cls.signatures :
            if sig not in self.signatures :
                return False
        return True
        

class Interface (type) :
    """
    Metaclass for creating interfaces. Interfaces do not require explicit subclassing
    for isinstance and issubclass to return true, instead opting to base this behavior
    on the signatures of the class and the interface parent class. Thus, so long as a
    class implements all of the methods in an interface with the same method signature,
    it counts as isinstance. 

    To create an interface, declare a class as such:
    ```
    class MyInterface (metaclass=Interface) :
        def my_custom_method (self, param1 : type1) -> type2 : pass

        @default
        def my_multiply_method (self, a : int, b : int) -> int :
            return a * b
    ```
    All explicit subclasses will be forced to override my_custom_method to satisfy
    interface isinstance checks. All implied interface implementers will have to implement
    both my_custom_method AND my_multiply_method to satisfy as interface isinstance checks,
    as they would not inherit the default behavior from the Interface.

    A word of warning: using strings as forward declarations does not evaluate to equal
    to using the type directly in an annotation as far as this module is concerned. For
    consistent behavior, use `from __future__ import annotations`. 
    """
    def __new__ (cls, name, bases, dct) :
        def default_initializer (*args, **kwargs) :
            raise TypeError("Attempted to initialize Interface")

        if '__init__' not in dct.keys() :
            dct['__init__'] = default_initializer
        return type.__new__(cls, name, bases, dct)

    def __instancecheck__ (cls, instance) :
        if len(cls.__bases__) != 1 : return super(cls).__instancecheck__(instance)
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__ (cls, subclass) :
        if len(cls.__bases__) != 1 : return super(cls).__subclasscheck__(subclass)
        return ClassSignature(subclass).implements(cls)
    

def default (func) :
    """
    Default decorator for interfaces. 
    """
    func.__defaultmethod__ = True
    return func
   
