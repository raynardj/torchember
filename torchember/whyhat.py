# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/why_hat.ipynb (unless otherwise specified).

__all__ = ['md5hash', 'RichColumn', 'RichDF']

# Cell
import pandas as pd
import numpy as np
from pathlib import Path
import os
import json
from .core import color
from .helper import tracker

# Cell
from hashlib import md5
from datetime import datetime
def md5hash(x):
    return md5(x.encode()).hexdigest()

class RichColumn(object):
    """
    A pandas series manager
    """
    def __init__(self,column, is_y = False,min_occur = 5, is_emb = True,hidden_size=50):
        self.col = column
        self.col.rc = self
        self.name = self.col.name
        self.min_occur = min_occur
        self.hidden_size = hidden_size
        self.is_emb =  is_emb
        self.is_y = is_y
        self.use = True
        self.is_conti = True
        self.defined = False

    def kill(self):
        """
        set column to kill mode, that it would not be involved in the learning
        """
        self.defined = True
        self.use = False

    def conti(self):
        """
        set column to contineous data
        """
        self.defined = True
        self.is_conti = True

    def disc(self):
        """
        set column to discrete data
        """
        self.defined = True
        self.is_conti = False

    def is_number(self):
        """
        Is this column's data type in any form of number
        """
        return self.col.dtype in (int,float,
                              np.float16,np.float32,np.float64,np.float64,
                              np.int0,np.int8,np.int16,np.int32,np.int64)

    def __bool__(self):
        """
        is this column going to join the learning
        """
        return self.use

    def __len__(self):
        """
        width of column when entering the model, or used as target
        """
        if self.is_conti:
            return 1
        else:
            if self.is_emb:
                return self.hidden_size
            else:
                width = len(self.top_freq)
                width =1 if width==2 else width
                return width

    def __repr__(self,):
        return f"<Rich Column:{self.name}>"

    def top_freq_(self):
        freq = self.freq()
        self.top_freq = freq[freq[self.name]>=self.min_occur].reset_index()
        return self.top_freq

    def freq(self):
        return pd.DataFrame(data=self.col.value_counts())

    @property
    def conf_dict(self):
        return dict((i,getattr(self,i)) for i in ["name","defined","is_conti","is_y","is_emb","use"])

    def set_conf(self,conf_dict):
        for k,v in conf_dict.items():
            setattr(self,k,v)
        return self

class RichDF(object):
    """
    A pandas dataframe manager
    """
    def __init__(self,df,fname=None):
        self.df = df
        self.columns = dict()
        if fname==None:
            fname=f"why_hat_{self.ts_str}"
        self.t = tracker("torchember",fname)
        self.t.data = self.t.log_path
        for colname in self.df:
            self.columns.update({colname:RichColumn(df[colname])})

    @property
    def ts_str(self):
        return datetime.now().strftime("%m%d_%H%M%S")

    @property
    def col_conf(self):
        return dict((k,{"use":v.use,"is_cont":v.is_conti}) for k,v in self.columns.items())

    def kill(self,colname):
        self.df[colname].rc.kill()

    def conti(self,colname):
        self.df[colname].rc.conti()

    def disc(self,colname):
        self.df[colname].rc.disc()

    def save_col(self,rcol):
        self.t[md5hash(rcol.name)]=rcol.conf_dict

    def set_col(self,rcol):
        if rcol.defined:
            print(f"{rcol.name} defined, use:{rcol.use}, contineus?:{rcol.is_conti}")
        print(color.bold("="*30))
        print(color.cyan(rcol.name))
        print(color.red(f"number? {rcol.is_number()}"))
        print(rcol.top_freq_().head(5))

        print(color.red("Is this a [C]ontineous, [D]iscrete or a column we do[N]'t need? default N"))
        x = input().lower()
        if x=="c":
            rcol.conti()
            print(color.blue(f"{rcol.name} set to contineous data"))
            self.save_col(rcol)
        elif x =="d":
            rcol.disc()
            print(color.blue(f"{rcol.name} set to discrite data"))
            self.save_col(rcol)
        elif (x =="") or (x=="n"):
            rcol.kill()
            print(color.blue(f"{rcol.name} will not be involved in learning"))
            self.save_col(rcol)
        else:
            print(color.yellow(f"option [{x}] not found, try Again?"))

    def save(self,colname):
        col=self.df[colname]
        self.t[md5hash(colname)] = col.rc.conf_dict

    def tour(self):
        """
        Go through column 1 by 1 to decide the processing for its data
        """
        for colname in self.df:
            col = self.df[colname]
            current = self.t[md5hash(colname)]
            if current != None:
                col.rc.set_conf(current)
            if col.rc.defined==False:
                self.set_col(col.rc)

    def set_y(self, *colnames):
        """
        set columns to y
        all the columns that use==True and is_y==False will be treated as x
        """
        for colname in colnames:
            rc = self.columns[colname]
            rc.is_y = True
            rc.use = True

    def set_x(self, *colnames):
        """
        set columns to x
        of course,every columns' default status is x,
        so you don't have to set this if you accidentally set x to y
        """
        for colname in colnames:
            rc = self.columns[colname]
            rc.use = True
            rc.is_y = False