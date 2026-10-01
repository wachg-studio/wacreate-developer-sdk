# -*- coding: utf-8 -*-
from mod.common.mod import Mod
import mod.server.extraServerApi as serverApi
MOD_NAMESPACE="wacreate_test"
SERVER_SYSTEM_NAME="WacreateTestServerSystem"
@Mod.Binding(name=MOD_NAMESPACE, version="0.1.0")
class WacreateTestMod(object):
    @Mod.InitServer()
    def init_server(self):
        serverApi.RegisterSystem(MOD_NAMESPACE, SERVER_SYSTEM_NAME, "Script_wacreate_test.serverSystem.WacreateTestServerSystem")
