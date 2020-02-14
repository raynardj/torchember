from flask_appbuilder import BaseView,expose
from flask import request,jsonify
from torchember.utils import emberReader
import json

class emberReadView(BaseView):
    route_base = "/eread"

    @expose("/structure/", methods=["GET","POST"])
    def structure(self):
        data = json.loads(request.data)
        name = data["name"]
        er = emberReader(name)
        try:
            return jsonify({"data":er.structure,"success":True,"status":200})
        except Exception as e:
            return jsonify({"data":str(e), "success":False,"status":500, })