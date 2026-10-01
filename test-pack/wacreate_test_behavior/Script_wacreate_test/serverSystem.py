# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import mod.server.extraServerApi as serverApi
MOD_NAMESPACE="wacreate_test"
MACHINE_BLOCK="wacreate_test:api_generator"
class WacreateTestServerSystem(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, systemName):
        serverApi.GetServerSystemCls().__init__(self, namespace, systemName)
        self.integrated=False; self.retry=0; self.last_error=None
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "OnScriptTickServer", self, self.OnTick)
        self._try_integrate()
    def OnTick(self, args=None):
        if not self.integrated:
            self.retry += 1
            if self.retry >= 20: self.retry=0; self._try_integrate()
    def _try_integrate(self):
        try:
            from Script_NeteaseModAeQXOhXR.public_api import get_server_system, register_addon
            core=get_server_system(serverApi)
            if core is None: raise RuntimeError("请启用机械动力·蛙创studio主包")
            if not register_addon(core, MOD_NAMESPACE, "0.1.0", name="公共 API 测试机"): raise RuntimeError("API版本不兼容")
            self.integrated=bool(core.RegisterMechanicalComponent(MACHINE_BLOCK, {"kind":"source","powered":True,"axisMode":"facing","shaftMode":"axis","stressCapacity":32.0,"stressImpact":0.0}))
        except Exception as error:
            message=str(error)
            if message!=self.last_error: print("[wacreate_test] "+message); self.last_error=message
