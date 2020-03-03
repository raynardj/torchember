# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/torch_ember_core.ipynb (unless otherwise specified).

__all__ = ['tracker', 'emberTracker', 'moduleTrack', 'get_stats', 'torchEmber']

# Cell
import os
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
import torch
from .helper import color
from functools import partial

class tracker(object):
    def __init__(self, libname, fname):
        self.libname = libname
        self.fname = fname
        self.home = Path(os.environ['HOME'])
        self.dir = self.home/f".{libname}"
        self.dir.mkdir(exist_ok = True)
        self.data = self.dir/"data"
        self.data.mkdir(exist_ok = True)
        self.log = self.dir/"log"
        self.log.mkdir(exist_ok = True)
        self.log_path = self.log/self.fname
        self.log_path.mkdir(exist_ok=True)
        self.marked = {}
        self.mark(init="00")

    def __repr__(self):
        return f"<{self.libname}:{self.fname}>"

    def mkdir(self, path):
        Path(path).mkdir(exist_ok=True)

    def __setitem__(self, fname,dict_):
        with open(self.data/f"{fname}.json","w") as f: f.write(json.dumps(dict_, indent = 2))


    def __getitem__(self,fname):
        return json.loads(open(self.data/f"{fname}.json","r").read())

    def logging(self,line):
        with open(self.log_file,"a") as f :f.write(line+"\n")
        return self.log_file

    def mark(self,**kwargs):
        self.marked.update(kwargs)
        file_name = "_".join(f"{k}-{v}" for k,v in self.marked.items())
        self.log_file = self.log_path/f"{file_name}.log"

    def __call__(self,dict_):
        """
        add a dictionary to log
        """
        self.logging(json.dumps(dict_))
        return self

    def lines(self):
        return list(json.loads(i) for i in open(self.log_file).read().split("\n")[:-1])

    @property
    def ts(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def df(self):
        return pd.DataFrame(self.lines())

class emberTracker(tracker):
    def __init__(self, fname):
        super().__init__("torchember",fname)
        self.latest = self.log/f"{fname}_latest"
        self.latest_lines = ""

    def logging(self,line):
        with open(self.log_file,"a") as f : f.write(line+"\n")
        self.latest_lines+=(line+"\n")
        return self.log_file

    def refresh(self):
        """
        lastest always contain the record of the latest batch
        """
        with open(self.latest,"w") as f :  f.write(self.latest_lines)
        self.latest_lines = ""
        return self.latest

    def latest_line_list(self):
        return list(json.loads(i) for i in open(self.latest).read().split("\n")[:-1])

    @property
    def latest_df(self):
        return pd.DataFrame(self.latest_line_list())


# Cell
from types import MethodType
from datetime import datetime

class moduleTrack(object):
    def __init__(self,module, name=None, root_module = False):
        self.module = module
        module.module_tracker = self

        self.base_module = True if len(list(module.modules()))==1 else False
        self.root_module = root_module

        self.name = name if name else module.__class__.__name__
        #self.name = f'{name}_tracker' if name else f'{module.__class__.__name__}_tracker'
        self.id = id(module)
        self.children = []

    def __repr__(self):
        rt = f"<{self.name} @ {hex(self.id)}>"
        if hasattr(self,"input_dt"):
            rt+=f'\n\t[Inputs]{",".join(list(k+" "+str(list(v.shape)) for k,v in self.input_dt.items()))}'
        if hasattr(self,"output_dt"):
            rt+=f'\n\t[Outputs]{",".join(list(str(list(v.shape)) for v in self.output_dt))}'
        return rt

def get_stats(tensor):
    """
    The default statistic method, it will capture
    shape of the tensor
    mean, std, max, min of the tensor
    this will return a dictionary
    """
    def list_prod(l):
        result=1
        for i in l:
            result*=i
        return result
    return {"shape":list(tensor.shape),
            "mean":tensor.mean().item(),
            "std":tensor.std().item(),
            "max":tensor.max().item(),
            "min":tensor.min().item(),
            "cnt_zero": ((tensor>-1e-10) & (tensor < 1e-10)).sum().item(),
            "zero_pct": float(((tensor>-1e-10) & (tensor < 1e-10)).sum().item())/list_prod(tensor.shape)}



class torchEmber(object):
    def __init__(self, model, verbose = True):
        color.green|"start analyzing model"
        self.modules = dict()
        self.verbose = verbose
        self.model = model

        if hasattr(model,"disarm"):
            model.disarm()

        self.model_name = self.model.__class__.__name__

        fname = f"{self.model_name}_{self.ts_str}"
        self.fname = fname

        self.t = emberTracker(fname)
        self.current_mt = None
        self.mt_log = []
        self.record_extra = False

        self.arm()

        self.legit_ttypes = ["in","out","weight"]
        for ttype in self.legit_ttypes: self.set_metric(ttype)(get_stats)

        if self.verbose:
            color.green|f"[INFO][{self.ts_str}]Creating meta data"
        self.t[f"base_{fname}"]={"start":self.t.ts,
                                 "user":os.environ["USER"]}
        self.t[f"vis_{fname}"] = {"vis_type":"standard"}
        self.t[f"structure_{fname}"] = self.mod_tree()

    def mark(self,**kwargs):
        self.t.mark(**kwargs)

    def parse_module(self,model, name, root_module = False):
        name = f"{name}({model.__class__.__name__})"
        mt = moduleTrack(model, name, root_module)
        self.modules[name]= mt
        model.forward = self.module_register(name,model)

        for cname,children in model.named_children():
            children_mt = self.parse_module(children,f"{name}.{cname}" )
            children_mt.parent = mt
            mt.children.append(children_mt)
        return mt

    def mod_tree(self):
        """
        Return the tree of module
        """
        return self.mod_tree_parse(self.model.module_tracker)

    def mod_tree_parse(self,mt):
        rt = {"name":mt.name, "short":mt.name.split(".")[-1]}
        if len(mt.children)>0:
            rt.update({"children":list(self.mod_tree_parse(i) for i in mt.children)})
        return rt


    @property
    def ts_str(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @property
    def ts(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def arm(self):
        """
        arming the tracing function to self.model
        """
        if self.verbose:
            color.yellow|f"[ARMING][START]{self.ts}"
        self.parse_module(self.model,"model", root_module = True)
        if self.verbose:
            color.yellow|f"[ARMING][SUCCESS]{self.ts}"

    def disarm(self):
        """remove the tracing function"""
        for m in self.modules.values():
            if self.verbose:
                color.blue|f"[DISARM][{m.name}]{self.ts}"
            self.recover(m)
        color.blue|f"[DISARM][DONE]{self.ts}"

    def recover(self, m):
        if hasattr(m.module.forward,"former"):
            m.module.forward = m.module.forward.former

    def rearm(self):
        self.disarm()
        self.arm()

    def reg_check(self,m):
        """
        register check
        """
        if hasattr(m.forward,"armed"):
            if m.forward.armed:
                return False
        return True

    def set_metric(self, ttype):
        assert ttype in self.legit_ttypes, f"ttype has to be one of {str(self.ttypes)}"
        def deco(f):
            setattr(self,f"record_{ttype}_core",self.record_core(f))
            return f
        return deco

    def add_record(f):
        def _inner(self, f_name): return partial(f, self, f_name)
        return _inner

    @add_record
    def record_core(self, f_name, tensor, extra_data):
        """
        extra_data: dict
        """
        dict_= f_name(tensor)
        dict_.update(extra_data)
        self.t(dict_)
        return dict_

    def record_input(self,mt):
        """
        Record the input tensors of the moduleTrack
        """
        for k,tensor in mt.input_dt.items():
            extra_data= {"module":mt.name,"ts":self.t.ts,"ttype":"input","tname":k}
            if self.record_extra: self.add_extra_info(extra_data)
            self.record_in_core(tensor, extra_data)

    def record_output(self,mt):
        """
        Record the output tensors of the moduleTrack
        """
        for i in range(len(mt.output_dt)):
            tensor = mt.output_dt[i]
            extra_data = {"module":mt.name,"ts":self.t.ts,"ttype":"output","tname":f"output_{i}"}
            if self.record_extra:self.add_extra_info(extra_data)
            self.record_out_core(tensor,extra_data)

    def record_weight(self,mt):
        """
        Record the weights of the moduleTrack
        """
        if mt.base_module:
            i = 0
            for p in mt.module.parameters():
                extra_data={"module":mt.name,"ts":self.t.ts,
                                            "ttype":"weight","tname":f"weight_{i}"}
                if self.record_extra: self.add_extra_info(extra_data)
                self.record_weight_core(p.data, extra_data)
                if p.requires_grad and (p.grad!= None):
                    extra_data={"module":mt.name,"ts":self.t.ts,
                                            "ttype":"weight_grad","tname":f"grad_{i}"}
                    if self.record_extra: self.add_extra_info(extra_data)
                    self.record_weight_core(p.grad, extra_data)
                i+=1

    def add_extra(self, **kwargs):
        """
        Record the epoch # and batch #, in order to track the change of parameters over training process.
        After the model is armed, when users put model in training loop, have option to set it up.
        """
        self.record_extra = True
        self.extra_info={}
        for key, value in kwargs.items():
            self.extra_info.update({f'{key}': value})

    def add_extra_info(self,extra_data):
        extra_data.update(self.extra_info)

    def after_train(self):
        """
        reset record batch after training
        """
        if self.record_extra:
            self.record_extra=False
            self.extra_info = None


    def module_register(self,name,m):
        if self.reg_check(m) == False: return m.forward
        f = m.forward
        mt = self.modules[name]
        vs = f.__code__.co_varnames
        mt.vars = vs[1:]
        if self.verbose:
            color.cyan | f"[BUILD FORWARD][{name}]{self.ts}"
        def new_forward(*args,**kwargs):
            mt.input_dt = dict(zip(mt.vars[:len(args)],args))
            mt.input_dt.update(kwargs)

            self.record_input(mt)
            self.current_mt = mt
            if mt.root_module: self.mt_log=[]
            self.mt_log.append(f"enter {mt.name}")

            # ------execution of the function------
            outputs = f(*args,**kwargs)
            self.record_weight(mt)
            # ------execution of the function------

            self.mt_log.append(f"exit {mt.name}")

            if type(outputs) in [list,tuple]:
                mt.output_dt = [outputs]
            else:
                mt.output_dt = [outputs,]
            self.record_output(mt)

            if mt.root_module:
                self.t.refresh() # start a new "latest" file

            return outputs

        setattr(new_forward,"armed",True)
        setattr(new_forward,"former",f)

        def disarm(this):
            """
            Remove the trackers placed by torchember
            run model.disarm()
            """
            self.disarm()
            return this
        setattr(mt.module, "disarm",MethodType(disarm,mt.module))
        return new_forward