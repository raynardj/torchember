# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/helper.ipynb (unless otherwise specified).

__all__ = ['color', 'tint']

# Cell

from types import MethodType
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class tint(object):
    def __init__(self, cname):
        self.start = getattr(color,cname.upper())

    def __call__(self, txt):
        return f"{self.start}{txt}{color.END}"

    def __add__(self,txt):
        return self.__call__(txt)

    def __or__(self,txt):
        print(self.__call__(txt))
        return self

for c in ["purple","green","red","blue","yellow","bold","underline","cyan"]:
    setattr(color, c, tint(c))