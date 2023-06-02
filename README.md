# interfaced
Python library implementing Interfaces as an alternative semantic to ABCs.

ABCs (Abstract Base Classes) allow you to implement Abstract Methods, which demand subclasses implement them. 

Interfaced provides interfaces with subjectively much-improved semantics as opposed to the way ABCs work. 

## Semantics

To declare an interface, simply use the Interface metaclass provided by this library. 

```py
class TestInterface (metaclass=interfaced.Interface) :
    def foo (self, a : int) -> TestInterface : pass
    def bar (self, a : int) -> Self : pass
    @interfaced.default
    def baz (self, a : int) -> Self : return self
```

This interface declares three methods: 
- foo, which takes an int and returns TestInterface
- bar, which takes an int and returns typing.Self
- baz, which takes an int and returns typing.Self and is declared as `@interfaced.default`

Now, let's suppose we implement TestInterface into a class TestA: 
```py
class TestA (TestInterface) :
    def foo (self, a : int) -> TestInterface :
        return self
    def bar (self, a : int) -> Self : 
        return self
```

TestA is a subclass of TestInterface because it defines both foo and bar. Notice it does not have to define baz
because it inherits the default behavior from the TestInterface. 

Let's suppose we implement TestInterface into another class, TestB.
```py
class TestB (TestInterface) :
    def foo (self, a : int) -> TestB :
        return self
    def bar (self, a : int) -> Self : 
        return self
```
TestB is *NOT* a valid implementation of TestInterface, because it returns TestB when the interface demands that
it return self. 

This is an important distinction to make: If a method in the interface returns typing.Self, subclasses should
also return typing.Self, and if a method in an interface specifically returns the interface, subclasses should
also annotate a return type of that interface. This means that one interface implementer could return another
implementer of the same interface for any method that returns the interface, but if it returns Self, then it 
can only return itself. 

However, the real power of the interfaces provided by this module is in this: 
```py
class TestC :
    def foo (self, a : int) -> TestInterface :
        return TestA()
    def bar (self, a : int) -> Self :
        return self
    def baz (self, a : int) -> Self :
        print("Overrode default method")
        return self
```
This doesn't look like it inherits from the interface, yet `issubclass(TestC, TestInterface)` evaluates to true. 
This is because interfaces provide a way to apply types to *other peoples'* code, without needing to modify it. 
In this way, interfaces provided by this library behave the way Go interfaces do. 

Notice that because TestC does not inherit from TestInterface explicitly, it is required to implement `baz` 
internally in addition to the non-default methods of the interface. This is to ensure that all classes 
implementing the interface have all methods that the interface has accessible on them. 

It's worth noting that you can always override default methods in explicit inheritance as well, if you would like
to. 

## A Word of Warning
- Interfaces must be base classes. They cannot inherit from other interfaces, or other classes, or risk undefined 
behavior. 
- Because of the way this is implemented, interface collision simply isn't an issue; Whichever interface you 
implement the method for if there are duplicate methods inherited is the one considered implemented by the base
class. However, even if an interface is improperly implemented, inheriting will bestow access to the default 
methods of that interface. 
- It is important to remember that subclassing an interface *does not* mean `isinstance(yourclass, Interface)` 
will return true. You cannot use this with logic that checks subclassing the way it is traditionally applied. 
To access traditional python basing behavior on a , see `interfaced#bases`. 
- For defaults to work propertly, all other decorators must follow it. 


## On Naming
Interfaces are python classes, so they follow Python class naming guidelines. However, as special classes, they
should be named to indicate their state, and represent that they should not be initialized. 

Therefore, I propose that in addition to PEP when naming interfaces they should be named in one of two ways, with
one vastly preferred over the other. 

1. Interfaces should be defined as adjectives, like JSONSerializable. 
2. In cases where this isn't possible or doesn't make sense, the class name should end in Interface, like 
TestInterface did in the examples. 

These naming conventions aren't something I can enforce, but seeing as this is something that behaves different
semantically from the rest of python, I felt some conventions should exist. 

## Disclaimer
This project is currently still in early stages and should not be used in production code until at least release
1.0.0. Until 1.0.0, there may also be breaking changes in semantics. 
