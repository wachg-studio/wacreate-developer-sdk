# -*- coding: utf-8 -*-
"""Stable public facade for WACreate add-ons.

Add-ons should depend on this module's constants and helpers instead of
importing implementation facets or reaching into runtime caches.  The facade
is deliberately small: the authoritative state remains in the registered
WACreate systems.
"""

from __future__ import unicode_literals

import re
import math


CORE_ID = "wacreate"
CORE_VERSION = "0.0.31"
PUBLIC_API_VERSION = 1
SERVER_SYSTEM_NAME = "WACreateServerSystem"
CLIENT_SYSTEM_NAME = "WACreateClientSystem"
NAMESPACE = "Script_NeteaseModAeQXOhXR"

# These names are the compatibility contract consumed by documentation and
# the future developer MCP.  The implementations remain on the registered
# systems so add-ons never need private runtime imports.
PUBLIC_SERVER_METHODS = (
    "GetPublicApiInfo", "RegisterAddon", "GetRegisteredAddons",
    "RegisterMechanicalComponent", "RegisterWrenchHandler",
    "RegisterWrenchRemoveHandler", "RegisterBasinDirectPlacementItem",
    "RegisterBasinAccessProvider", "RegisterCompactingRecipe",
    "RegisterMixingRecipe", "GetBasinFluidEndpointFaces",
    "ReadBasinFluidEndpoint", "InsertBasinFluidEndpoint",
    "ExtractBasinFluidEndpoint", "SnapshotBasinFluidEndpoint",
    "RestoreBasinFluidEndpoint", "ReadBasinProcessingContents",
    "CanApplyBasinProcessingRecipe", "ApplyBasinProcessingRecipe",
    "MarkMechanicalDirty", "GetMechanicalState", "GetMechanicalFacing",
)
PUBLIC_CLIENT_METHODS = (
    "GetPublicApiInfo", "RegisterGogglesProvider",
    "RegisterGogglesSuppressedBlock", "RegisterFaceHintProvider",
    "RegisterFluidDisplayName", "RegisterMechanicalVisualSpec",
    "GetMechanicalVisualSpec", "GetMechanicalVisualAngle",
)

PUBLIC_API_CATALOG = {
    "mechanical": {
        "RegisterMechanicalComponent": {
            "stability": "stable",
            "summary": "注册附属包机械节点及其轴、齿轮和应力规格。",
            "required": ["blockName", "spec"],
            "notes": "spec.shaftMode=omni 可用于六向机械枢纽；六个正交面都会成为轴端。",
        },
        "MarkMechanicalDirty": {
            "stability": "stable",
            "summary": "方块或附属状态改变后请求机械网络重建。",
            "required": ["key"],
        },
        "GetMechanicalState": {
            "stability": "stable",
            "summary": "读取脱离内部缓存的机械节点状态快照。",
            "required": ["key"],
        },
    },
    "processing": {
        "RegisterCompactingRecipe": {
            "stability": "stable",
            "summary": "注册动力盆压块配方。",
            "required": ["recipe"],
        },
        "RegisterMixingRecipe": {
            "stability": "stable",
            "summary": "注册动力盆搅拌配方。",
            "required": ["recipe"],
        },
        "ApplyBasinProcessingRecipe": {
            "stability": "stable",
            "summary": "原子地消耗动力盆输入并提交加工输出。",
            "required": ["key", "recipe"],
        },
    },
    "fluids": {
        "ReadBasinFluidEndpoint": {
            "stability": "stable",
            "summary": "读取动力盆流体端点快照。",
            "required": ["key"],
        },
        "InsertBasinFluidEndpoint": {
            "stability": "stable",
            "summary": "向动力盆端点输入流体并返回实际数量。",
            "required": ["key", "fluid", "amount"],
        },
        "ExtractBasinFluidEndpoint": {
            "stability": "stable",
            "summary": "从动力盆端点抽取流体并返回实际数量。",
            "required": ["key", "fluid", "amount"],
        },
    },
    "client": {
        "RegisterMechanicalVisualSpec": {
            "stability": "stable",
            "summary": "注册附属包实体骨骼的机械旋转轴、动画变量和停转回弹参数。rotationFrame=world 时所有骨骼共享网络世界轴角度。",
            "required": ["blockName", "spec"],
        },
        "GetMechanicalVisualSpec": {
            "stability": "stable",
            "summary": "读取当前生效的机械视觉规格，用于附属包注册审计和方向诊断。",
            "required": ["blockName"],
        },
        "RegisterGogglesProvider": {
            "stability": "stable",
            "summary": "为附属方块提供护目镜信息。",
            "required": ["blockName", "providerNamespace", "providerSystem"],
        },
        "RegisterFluidDisplayName": {
            "stability": "stable",
            "summary": "注册流体的客户端显示名称。",
            "required": ["fluidId", "displayName"],
        },
    },
}

_ADDON_ID = re.compile(r"^[a-z0-9][a-z0-9_.-]{1,63}$")


def normalize_mechanical_visual_spec(spec):
    """Validate the small public animation schema without engine imports."""
    try:
        if not isinstance(spec, dict) or not isinstance(spec.get("parts"), dict):
            return None
        rotationFrame = str(spec.get("rotationFrame", "local") or "local").lower()
        if rotationFrame not in ("local", "world"):
            return None
        parts = {}
        for name, part in spec["parts"].items():
            if not isinstance(part, dict) or part.get("visualAxis") not in ("x", "y", "z"):
                return None
            prefix = str(part.get("prefix", ""))
            if not re.match(r"^variable\.[a-z][a-z0-9_]*$", prefix):
                return None
            sign = float(part.get("modelSign", 1.0))
            if math.isnan(sign) or math.isinf(sign) or sign == 0 or abs(sign) > 32:
                return None
            # World-frame bones are authored in the same Bedrock parent frame.
            # Per-face signs here are a common source of “flip another sign”
            # patches, so reject them at the public boundary instead of
            # silently accepting an ambiguous contract.
            if rotationFrame == "world" and abs(sign - 1.0) > 0.000001:
                return None
            if part.get("source", "visual") != "visual":
                return None
            parts[str(name)] = {"source": "visual", "visualAxis": part["visualAxis"],
                                "modelSign": sign, "prefix": prefix}
        if not parts or len(parts) > 64:
            return None
        bounce = spec.get("stopBounce", {})
        raw_ticks = bounce.get("ticks", 10)
        if isinstance(raw_ticks, bool) or int(raw_ticks) != raw_ticks:
            return None
        ticks = int(raw_ticks)
        degrees = float(bounce.get("degrees", 4.0))
        if ticks < 1 or ticks > 100 or math.isnan(degrees) or math.isinf(degrees) or not 0 <= degrees <= 45:
            return None
        axis = spec.get("visualAxis", "y")
        offset = spec.get("offsetMode", "axis_phase")
        if axis not in ("x", "y", "z") or offset not in ("none", "axis_phase"):
            return None
        result = {"visualAxis": axis, "offsetMode": offset, "modelSign": 1.0,
                "parts": parts, "stopBounce": {"ticks": ticks, "degrees": degrees, "mode": "bounce"}}
        if "rotationFrame" in spec:
            result["rotationFrame"] = rotationFrame
        return result
    except (ValueError, TypeError, AttributeError, OverflowError):
        return None


def api_info():
    """Return JSON-compatible API metadata for an add-on manifest or MCP."""
    return {
        "id": CORE_ID,
        "version": CORE_VERSION,
        "apiVersion": PUBLIC_API_VERSION,
        "serverSystem": SERVER_SYSTEM_NAME,
        "clientSystem": CLIENT_SYSTEM_NAME,
        "serverMethods": list(PUBLIC_SERVER_METHODS),
        "clientMethods": list(PUBLIC_CLIENT_METHODS),
        "catalog": PUBLIC_API_CATALOG,
    }


def missing_core_message(addon_id=None, minimum_version=None):
    """Return the user-facing dependency hint used by add-on templates."""
    name = str(addon_id or "此附属包")
    requirement = str(minimum_version or CORE_VERSION)
    return (
        u"§c%s需要WACreate主包才能运行。§r\n"
        u"请先安装并启用WACreate主包（最低版本%s），"
        u"然后重新加载世界。" % (name, requirement)
    )


def _system(api, name):
    try:
        return api.GetSystem(NAMESPACE, name)
    except Exception:
        return None


def get_server_system(server_api):
    """Return the running core server system, or ``None`` if it is absent."""
    return _system(server_api, SERVER_SYSTEM_NAME)


def get_client_system(client_api):
    """Return the running core client system, or ``None`` if it is absent."""
    return _system(client_api, CLIENT_SYSTEM_NAME)


def validate_addon_id(addon_id):
    """Validate a stable add-on id before registering it with the core."""
    return bool(_ADDON_ID.match(str(addon_id or "")))


def register_addon(server_system, addon_id, version="0.0.0",
                   api_version=PUBLIC_API_VERSION, name=None):
    """Register add-on metadata through the public server-system method."""
    if server_system is None or not validate_addon_id(addon_id):
        return False
    method = getattr(server_system, "RegisterAddon", None)
    if not callable(method):
        return False
    return bool(method({
        "id": str(addon_id),
        "version": str(version or "0.0.0"),
        "apiVersion": int(api_version),
        "name": u"%s" % (name or addon_id),
    }))


__all__ = [
    "CORE_ID", "CORE_VERSION", "PUBLIC_API_VERSION", "NAMESPACE",
    "SERVER_SYSTEM_NAME", "CLIENT_SYSTEM_NAME", "PUBLIC_SERVER_METHODS",
    "PUBLIC_CLIENT_METHODS", "PUBLIC_API_CATALOG", "api_info",
    "missing_core_message", "get_server_system", "get_client_system",
    "validate_addon_id", "register_addon",
    "normalize_mechanical_visual_spec",
]
