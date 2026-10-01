from wacreate_sdk import public_api
VISUAL_SPEC = {"rotationFrame":"world","parts":{"shaft":{"source":"visual","visualAxis":"y","modelSign":1.0,"prefix":"variable.example_generator_shaft"}},"stopBounce":{"ticks":10,"degrees":4.0,"mode":"bounce"}}
def register_visual(core):
    return bool(core.RegisterMechanicalVisualSpec("example_addon:generator", VISUAL_SPEC))
