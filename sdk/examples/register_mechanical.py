from wacreate_sdk import public_api
ADDON_ID = "example_addon"
MACHINE_BLOCK = "example_addon:generator"
def register(core):
    if not public_api.register_addon(core, ADDON_ID, "0.1.0", name="示例附属包"):
        return False
    return bool(core.RegisterMechanicalComponent(MACHINE_BLOCK, {"kind":"source","powered":True,"axisMode":"facing","shaftMode":"axis","stressCapacity":128.0}))
