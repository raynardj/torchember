# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/10_torch_ember_core.ipynb (unless otherwise specified).

__all__ = ['moduleTrack', 'get_stats', 'torchEmber']

# Cell
from types import MethodType
from torch import is_tensor
from datetime import datetime
from .helper import color,emberTracker
from .utils import io_cleaner
from functools import partial
import os
import numpy as np

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
            rt+=f'\n\t[Outputs]{",".join(list(k+" "+str(list(v.shape)) for k,v in self.output_dt.items()))}'
        return rt

def get_stats(tensor):
    """
    The default statistic method, it will capture
    shape of the tensor
    mean, std, max, min of the tensor
    this will return a dictionary
    """
    return {"shape":list(tensor.shape),
            "mean":tensor.float().mean().item(),
            "std":tensor.float().std().item(),
            "max":tensor.float().max().item(),
            "min":tensor.float().min().item(),
            "cnt_zero": ((tensor>-1e-10) & (tensor < 1e-10)).sum().item(),
            "zero_pct": float(((tensor>-1e-10) & (tensor < 1e-10)).sum().item())/np.prod(tensor.shape)}



class torchEmber(object):
    def __init__(self, model, verbose = False):
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

        self.legit_ttypes = ["in","out","weight","grad"]
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
        self.t(dict_) # logging a line of dict
        return dict_

    def record_input(self,mt):
        """
        Record the input tensors of the moduleTrack
        """
        for k,tensor in mt.input_dt.items():
            try:
                extra_data= {"module":mt.name,"ts":self.t.ts,"ttype":"input","tname":k}
                if self.record_extra: self.add_extra_info(extra_data)
                self.record_in_core(tensor, extra_data)
            except:
                pass

    def record_output(self,mt):
        """
        Record the output tensors of the moduleTrack
        """
        for k,tensor in mt.output_dt.items():
            try:
                extra_data = {"module":mt.name,"ts":self.t.ts,"ttype":"output","tname":k}
                if self.record_extra:self.add_extra_info(extra_data)
                self.record_out_core(tensor,extra_data)
            except:
                pass


    def record_model_inner(self,mt,dname='weight'):
        """
        record the weight and grad of the moduleTrack
        specify weight or grad in dname
        """
        i = 0
        for p in mt.module.parameters():
            extra_data={"module":mt.name,"ts":self.t.ts,
                        "ttype":dname,"tname":f"{dname}_{i}"}
            if self.record_extra: self.add_extra_info(extra_data)
            if dname=='grad':self.record_grad_core(p.grad, extra_data)
            else : self.record_weight_core(p.data, extra_data)
            i+=1

    def record_weight(self):
        for m in self.model.modules():
            if len(list(m.modules()))==1: self.record_model_inner(m.module_tracker)

    def record_grad(self):
        """
        Record the grads of the weights of the modeuleTrack
        """
        for m in self.model.modules():
            if len(list(m.modules()))==1: self.record_model_inner(m.module_tracker,dname='grad')

    def log_model(self):
        """
        Write down measurements about the model, weights and grads
        It's equal to:
        self.record_weight()
        self.record_grad()
        """
        self.record_weight()
        self.record_grad()

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

            input_dt = dict(zip(mt.vars[:len(args)],args))
            input_dt.update(kwargs)
            mt.input_dt = io_cleaner(**input_dt)

            self.record_input(mt)
            self.current_mt = mt
            if mt.root_module: self.mt_log=[]
            self.mt_log.append(f"enter {mt.name}")

            # ------execution of the function------
            outputs = f(*args,**kwargs)
            # ------execution of the function------

            self.mt_log.append(f"exit {mt.name}")
            if is_tensor(outputs):
                output_dt = {"output":outputs}
            elif type(outputs) in [list,tuple,set]:
                output_dt = dict(enumerate(outputs))
            elif type(outputs) == dict:
                output_dt = outputs
            else:
                output_dt = dict()
            mt.output_dt = io_cleaner(**output_dt)

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