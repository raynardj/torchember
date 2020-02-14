import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from torchember.utils import get_ember_list,get_ember_df

"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")

from flask_appbuilder import IndexView,expose

class indexView(IndexView):
    index_template = "index.html"
    route_base = "/"

    @expose("/",methods=["GET"])
    def index(self):
        # inspect environment to offer search suggest
        ember_list = get_ember_list()
        if ember_list==None:
            return self.render_template("index.html",ember_list=ember_list)
        else:
            df = get_ember_df(ember_list)
            return self.render_template("index.html", ember_list=df.to_dict(orient="record"))

db = SQLA(app)
appbuilder = AppBuilder(app, db.session,indexview=indexView)


"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""

from . import views
