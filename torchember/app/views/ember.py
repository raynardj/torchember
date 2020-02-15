from flask_appbuilder import BaseView,expose
from flask import request,jsonify
from torchember.utils import emberReader
import json

class emberReadView(BaseView):
    route_base = "/eread"

    @expose("/structure/", methods=["GET","POST"])
    def structure(self):
        er = self.request_to_er(request.data)
        try:
            return jsonify({"data":er.structure,"success":True,"status":200})
        except Exception as e:
            return jsonify({"data":str(e), "success":False,"status":500, })

    @expose("/latest/", methods=["GET","POST"])
    def latest(self):
        er = self.request_to_er(request.data)
        try:
            return jsonify({"data":
                {
                    "cols":list(er.t.latest_df.columns),
                    "latest":er.latest,
                    "vis":er.t[f"vis_{er.name}"],
                },
            "success":True,"status":200})
        except Exception as e:
            return jsonify({"data":str(e), "success":False,"status":500, })

    def request_to_er(self,request_data):
        data = json.loads(request_data)
        name = data["name"]
        er = emberReader(name)
        return er
        