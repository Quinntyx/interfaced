from __future__ import annotations
import __init__ as interfaced
from typing import Self
passed = 0

class TestInterface (metaclass=interfaced.Interface) :
    def foo (self, a : int) -> TestInterface : pass
    def bar (self, a : int) -> Self : pass
    @interfaced.default
    def baz (self, a : int) -> Self : return self
    # note that Self here and TestInterface have different semantics, as you can return 
    # self in both but cannot return another TestInterface unless the interface 
    # specifies the broader TestInterface as the return type

class TestA (TestInterface) :
    def foo (self, a : int) -> TestInterface :
        return self
    def bar (self, a : int) -> Self : 
        return self

assert issubclass(TestA, TestInterface)
passed += 1

class TestB (TestInterface) :
    def foo (self, a : int) -> TestB :
        return self
    def bar (self, a : int) -> Self : 
        return self

assert not issubclass(TestB, TestInterface)
passed += 1

class TestC (TestInterface) :
    def foo (self, a : int) -> TestInterface :
        return TestA()
    def bar (self, a : int) -> Self :
        return self

assert issubclass(TestC, TestInterface)
passed += 1

class TestD (TestInterface) :
    def foo (self, a : int) -> TestInterface :
        return TestA()
    def bar (self, a : int) -> Self :
        return self
    def baz (self, a : int) -> Self :
        print("Overrode default method")
        return self

assert issubclass(TestD, TestInterface)
passed += 1

class TestE :
    def foo (self, a : int) -> TestInterface :
        return TestA()
    def bar (self, a : int) -> Self :
        return self
    def baz (self, a : int) -> Self :
        print("Overrode default method")
        return self

assert issubclass(TestE, TestInterface)
passed += 1

try : 
    TestInterface()
    print("Failed 1 test.")
except :
    passed += 1

print(f"Passed {passed} tests.")
