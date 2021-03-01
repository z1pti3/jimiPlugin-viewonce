import time
import urllib
from core.models import action
from core import auth, db, helpers

from plugins.viewonce.models import viewonce

class _viewonceSet(action._action):
    viewonceData = str()
    expiry= int()
    accessCount = 1

    def run(self,data,persistentData,actionResult):
        viewonceData = helpers.evalString(self.viewonceData,{"data" : data})
        _id, token, encData = viewonce._viewonce().new(viewonceData,self.expiry,self.accessCount)
        if _id:
            actionResult["result"] = True
            actionResult["rc"] = 0
            actionResult["uri"] = "/plugin/viewonce/{0}/?token={1}&encData={2}".format(_id,urllib.parse.quote_plus(token),urllib.parse.quote_plus(encData))
            actionResult["_id"] = _id
            actionResult["token"] =  token
            actionResult["encData"] =  encData
            return actionResult 

        actionResult["result"] = False
        actionResult["rc"] = 403
        return actionResult 


class _viewonceGet(action._action):
    viewonceID = str()
    token= str()
    encData = str()

    def run(self,data,persistentData,actionResult):
        viewonceID = helpers.evalString(self.viewonceID,{"data" : data})
        token = helpers.evalString(self.token,{"data" : data})
        encData = helpers.evalString(self.encData,{"data" : data})
        viewonceItem =  viewonce._viewonce().getAsClass(id=viewonceID)
        if len(viewonceItem) == 1:
            viewonceData = viewonceItem[0].getData(token, encData)
            if viewonceData:
                actionResult["result"] = True
                actionResult["rc"] = 0
                actionResult["viewonceData"] = viewonceData
                return actionResult 
            else:
                actionResult["result"] = False
                actionResult["rc"] = 403
                return actionResult 

        actionResult["result"] = False
        actionResult["rc"] = 404
        return actionResult 

class _viewonceCleanup(action._action):

    def run(self,data,persistentData,actionResult):
        viewonce._viewonce().api_delete(query={ "expiry" : { "$ne" : 0 }, "expiry" : { "$lt" : time.time() } })
        actionResult["result"] = True
        actionResult["rc"] = 0
        return actionResult 