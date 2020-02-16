# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/utils.ipynb (unless otherwise specified).

__all__ = ['check_existance', 'HOME', 'EMBER', 'DATA', 'LOG', 'get_ember_list', 'unpack_meta', 'get_ember_df',
           'emberReader']

# Cell
import os
from pathlib import Path
import json
import pandas as pd

# Cell
HOME = Path(os.environ["HOME"])
EMBER = HOME/".torchember"
DATA = EMBER/"data"
LOG = EMBER/"LOG"
def check_existance():
    if DATA.exists()==False:
        return False
    if LOG.exists()==False:
        return False
    else:
        return True


# Cell
def get_ember_list():
    if check_existance()== False:
        return None
    else:
        return  list(i for i in os.listdir(DATA) if i[:5]=="base_")

# Cell
def unpack_meta(fname):
    f = open(DATA/fname,"r")
    dict_ = json.loads(f.read())
    f.close()
    dict_["name"] = fname[5:-5]
    return dict_

def get_ember_df(ember_list):
    df = pd.DataFrame(list(unpack_meta(i) for i in ember_list))
    df = df.sort_values(by = "start",ascending = False)
    return df.reset_index().drop("index",axis=1)

# Cell
from .core import emberTracker

class emberReader(object):
    def __init__(self, name):
        self.name = name
        self.t = emberTracker(name)
        self.structure = self.t[f"structure_{self.name}"]
        self.base = self.t[f"base_{self.name}"]

    @property
    def latest(self):
        return self.t.latest_df.to_dict(orient = "record")