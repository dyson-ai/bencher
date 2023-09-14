# from typing import Any
import dispy
# import param
import random
import numpy as np
import param

import bencher as bch
import logging


# class C(param.Parameterized):
class C():
    def __init__(self, i=0, n=0):
        self.i = i
        self.n = n
        np.ones([1])
        self.a =param.Boolean()


    def show(self):
        print('%s: %.2f' % (self.i, self.n))
    def __call__(self,**kwargs) :
        return dict(n=self.n,a=self.a)



class BasicParam(param.Parameterized):

    var1 = param.Number()

    def __call__(self, **kwargs):
        var1 = kwargs.get("var1", 0)

        return var1
