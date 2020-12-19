import uuid

from core import plugin, model
from core.models import conduct, trigger, webui
from plugins.viewonce.models import action

class _viewonce(plugin._plugin):
    version = 0.1

    def install(self):
        # Register models
        model.registerModel("viewonce","_viewonce","_document","plugins.viewonce.models.viewonce")
        model.registerModel("viewonceSet","_viewonceSet","_action","plugins.viewonce.models.action")
        model.registerModel("viewonceGet","_viewonceGet","_action","plugins.viewonce.models.action")
        model.registerModel("viewonceCleanup","_viewonceCleanup","_action","plugins.viewonce.models.action")

        c = conduct._conduct().new("viewonceCore")
        c = conduct._conduct().getAsClass(id=c.inserted_id)[0]
        t = trigger._trigger().new("viewonceCore")
        t = trigger._trigger().getAsClass(id=t.inserted_id)[0]
        a = action._viewonceCleanup().new("viewonceCore")
        a = action._viewonceCleanup().getAsClass(id=a.inserted_id)[0]
        c.triggers = [t._id]
        flowTriggerID = str(uuid.uuid4())
        flowActionID = str(uuid.uuid4())
        c.flow = [
            {
                "flowID" : flowTriggerID,
                "type" : "trigger",
                "triggerID" : t._id,
                "next" : [
                    {"flowID": flowActionID, "logic": True }
                ]
            },
            {
                "flowID" : flowActionID,
                "type" : "action",
                "actionID" : a._id,
                "next" : []
            }
        ]
        webui._modelUI().new(c._id,{ "ids":[ { "accessID":"0","delete": True,"read": True,"write": True } ] },flowTriggerID,0,0,"")
        webui._modelUI().new(c._id,{ "ids":[ { "accessID":"0","delete": True,"read": True,"write": True } ] },flowActionID,100,0,"")
        c.acl = { "ids":[ { "accessID":"0","delete": True,"read": True,"write": True } ] }
        c.enabled = True
        c.update(["triggers","flow","enabled","acl"])
        t.acl = { "ids":[ { "accessID":"0","delete": True,"read": True,"write": True } ] }
        t.schedule = "60-90s"
        t.enabled = True
        t.update(["schedule","enabled","acl"])
        a.acl = { "ids":[ { "accessID":"0","delete": True,"read": True,"write": True } ] }
        a.enabled = True
        a.update(["enabled","acl"])

        return True

    def uninstall(self):
        # deregister models
        model.deregisterModel("viewonce","_viewonce","_document","plugins.viewonce.models.viewonce")
        model.deregisterModel("viewonceSet","_viewonceSet","_action","plugins.viewonce.models.action")
        model.deregisterModel("viewonceGet","_viewonceGet","_action","plugins.viewonce.models.action")
        model.deregisterModel("viewonceCleanup","_viewonceCleanup","_action","plugins.viewonce.models.action")
        return True

    def upgrade(self,LatestPluginVersion):
        pass
        # if self.version < 0.2:
