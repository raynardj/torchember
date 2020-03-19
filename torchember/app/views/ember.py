from flask_appbuilder import BaseView,expose
from flask import request,jsonify,Response
from torchember.utils import emberReader
import json
import sys
from pathlib import Path
from io import StringIO
import traceback
import markdown
from types import MethodType
import os

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

def color_func(cname):
    def func(self,txt):
        return f"{getattr(self,cname.upper())}{txt}{self.END}"
    func.__name__ = f"print_{cname}"
#     print(func(color,f"creating {cname}"))
    return func
for c in ["purple","green","red","blue","yellow","bold","underline","cyan"]:
    setattr(color, c, MethodType(color_func(c),color))

def get_error(e):
    """
    String format error massage and trace back
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    sio = StringIO()
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=100, file=sio)
    return sio.getvalue()

default_doc = """
### You can write the doc to for this api use the function doc string
"""

def api_wrap(f):
    def wraper(this,*args,**kwargs):
        request_info = {}

        try:request_info["data"]  = json.loads(request.data)
        except Exception as e:request_info["data"]  = {"load_json_error":str(e)}
        
        try:request_info["form"]  = request.form
        except:pass

        try:
            data=f(this,*args,**kwargs)
            rt={"data":data,"request":request_info,"success":True, "status":200}
        except Exception as e:
            print(color.red(get_error(e)))
            rt={"data":{"msg":get_error(e).replace("\n","&#10;")},"request":request_info,"success":False, "status":500}
        if request.method =="GET":
            doc = f.__doc__ if f.__doc__ else default_doc
            return this.render_template("api_data.html",data=json.dumps(rt,indent=2),
            doc=markdown.markdown(doc, extensions=['codehilite']))
        else:
            return jsonify(rt)
    return wraper

class emberReadView(BaseView):
    route_base = "/eread"

    @expose("/structure/", methods=["GET","POST"])
    @api_wrap
    def structure(self):
        er = self.request_to_er(request.data)
        return er.structure

    @expose("/latest/", methods=["GET","POST"])
    @api_wrap
    def latest(self):
        er = self.request_to_er(request.data)
        print(er.latest)
        return {"cols":list(er.t.latest_df.columns),
                "latest":er.latest,
                "vis":er.t[f"vis_{er.name}"],}

    def request_to_er(self,request_data):
        data = json.loads(request_data)
        name = data["name"]
        er = emberReader(name)
        return er

    @expose("/log_files/<dir_name>/")
    def log_files(self,dir_name):
        er = emberReader(dir_name)
        return Response(json.dumps(er.t.log_files))

    @expose("/log_files_api/",methods=["GET","POST"])
    @api_wrap
    def log_files_api(self):
        dir_name = json.loads(request.data)["dir_name"]
        er = emberReader(dir_name)
        return er.t.log_files

    @expose("/log_file/<dir_name>/<filename>/",methods=["GET","POST"])
    def log_file(self,dir_name, filename):
        er = emberReader(dir_name)
        return Response(er.read_log(filename))

    @expose("/download_log_file/<dir_name>/<filename>/",methods=["GET","POST"])
    def download_log_file(self,dir_name, filename):
        er = emberReader(dir_name)
        return Response(
            er.read_log(filename),
            mimetype="text/json",
            headers={"Content-disposition":
                 f"attachment; filename={dir_name}_{filename}.json"})