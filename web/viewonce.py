import urllib
import json
from flask import Blueprint, render_template, request

from core import api
from plugins.viewonce.models import viewonce

pluginPages = Blueprint('viewoncePages', __name__, template_folder="templates")

@pluginPages.route("/",methods=["GET"])
def mainPage():
    return render_template("set.html", CSRF=api.g.sessionData["CSRF"])

@pluginPages.route("/",methods=["POST"])
def setViewonce():
    data = json.loads(api.request.data)
    expiry = int(data["expiry"])
    accessCount = int(data["accessCount"])
    viewonceData = data["message"]
    _id, token, encData = viewonce._viewonce().new(viewonceData,expiry,accessCount)
    return { "uri" : "{0}/?token={1}&encData={2}".format(_id,urllib.parse.quote_plus(token),urllib.parse.quote_plus(encData)) }, 200

@pluginPages.route("/<viewonceID>/",methods=["GET"])
def __PUBLIC__getViewonce(viewonceID):
    viewonceItem =  viewonce._viewonce().getAsClass(id=viewonceID)
    if len(viewonceItem) == 1:
        token = request.args.get('token')
        encData = request.args.get('encData')
        viewonceData = viewonceItem[0].getData(token, encData)
        if viewonceData:
            return render_template("show.html", message=viewonceData)
        else:
            return render_template("show.html", message="ERROR : The message you are looking for does not exist!")
    return render_template("show.html", message="ERROR : The message you are looking for does not exist!")
