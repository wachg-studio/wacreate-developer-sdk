# -*- coding: utf-8 -*-
"""WACreate developer MCP.

This server exposes documentation and local scaffolding helpers for third
party add-ons.  It deliberately does not expose core source files or execute
generated code.  Run it with stdio when connecting it to an MCP-capable
developer agent::

    python tools/wacreate_mcp_server.py
"""

from __future__ import unicode_literals

import json
import os
import re
import shutil
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_INFO = json.loads((ROOT / "tools" / "public_api_catalog.json").read_text(encoding="utf-8"))
CORE_VERSION = PUBLIC_INFO["version"]
PUBLIC_API_VERSION = PUBLIC_INFO["apiVersion"]
PUBLIC_API_CATALOG = PUBLIC_INFO["catalog"]
def api_info():
    return json.loads(json.dumps(PUBLIC_INFO))
def missing_core_message(addon_id=None, minimum_version=None):
    return "需要启用机械动力·蛙创studio主包 >= %s：%s" % (minimum_version or CORE_VERSION, addon_id or "附属包")
def validate_addon_id(value):
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9_.-]{1,63}", str(value or "")))


CORE_BEHAVIOR_UUID = "a94c5ffd-b621-4f1e-af3d-78ca2e0d3b7d"
CORE_RESOURCE_UUID = "24f71408-5083-4a6a-8708-631bcb7a6ee0"
MCP_ASSET_ROOT = ROOT / "tools" / "mcp_assets"


MCP = FastMCP("wacreate-developer")
_NAMESPACE_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{1,31}$")
_MACHINE_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{1,47}:[a-z0-9][a-z0-9_.-]{1,63}$")

MACHINE_CAPABILITY_CATALOG = {
    "ports": {
        "mechanical": "接入主包应力/转速网络，使用 RegisterMechanicalComponent",
        "item": "输入、输出或缓存物品；物流实现由附属包负责",
        "fluid": "输入、输出或缓存流体；可与主包流体 API/自有容器连接",
        "redstone": "红石启停、模式切换和安全联锁",
        "data": "传感器、仪表、无线或多方块内部端口",
    },
    "roles": {
        "source": "发电/动力源",
        "consumer": "耗能机器",
        "relay": "传动、变压、分配或换向",
        "storage": "电池、飞轮、压力罐等容量型节点",
        "processor": "带输入、输出、时间和配方的机器",
    },
    "validation": [
        "端口名称唯一且方向明确",
        "容量、消耗和转速为有限非负数",
        "处理配方的输入/输出不能同时为空",
        "world 坐标动画不能与 netease:face_directional 混用",
    ],
}


# These are deliberately curated developer-facing assets.  The catalog only
# exposes stable logical IDs and local paths inside the MCP package; it does
# not expose the core pack's absolute filesystem layout.
DEVELOPER_ASSET_CATALOG = {
    "shaft": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/shaft.png",
        "description": "基础传动杆",
    },
    "shaft_shadow": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/shaft_shadow.png",
        "description": "传动杆阴影层",
    },
    "andesite_encased_shaft": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/andesite_encased_shaft.png",
        "description": "安山合金机壳传动杆",
    },
    "brass_encased_shaft": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/brass_encased_shaft.png",
        "description": "黄铜机壳传动杆",
    },
    "cogwheel": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/cogwheel.png",
        "description": "小齿轮",
    },
    "cogwheel_shadow": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/cogwheel_shadow.png",
        "description": "小齿轮阴影层",
    },
    "large_cogwheel": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/large_cogwheel.png",
        "description": "大齿轮",
    },
    "large_cogwheel_shadow": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/large_cogwheel_shadow.png",
        "description": "大齿轮阴影层",
    },
    "andesite_encased_cogwheel": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/andesite_encased_cogwheel.png",
        "description": "安山合金机壳小齿轮",
    },
    "brass_encased_cogwheel": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/brass_encased_cogwheel.png",
        "description": "黄铜机壳小齿轮",
    },
    "andesite_encased_large_cogwheel": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/andesite_encased_large_cogwheel.png",
        "description": "安山合金机壳大齿轮",
    },
    "brass_encased_large_cogwheel": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/brass_encased_large_cogwheel.png",
        "description": "黄铜机壳大齿轮",
    },
    "brass_casing": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/brass_casing.png",
        "description": "黄铜机壳",
    },
    "copper_casing": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/copper_casing.png",
        "description": "铜机壳",
    },
    "gearbox": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/Gearbox.png",
        "description": "齿轮箱主体",
    },
    "gearbox_shadow": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/Gearbox_shadow.png",
        "description": "齿轮箱阴影层",
    },
    "vertical_gearbox_shadow": {
        "category": "mechanical", "kind": "block",
        "source": "textures/blocks/Gearboxshu_shadow.png",
        "description": "立式齿轮箱阴影层",
    },
    "encased_pipe": {
        "category": "fluid", "kind": "block",
        "source": "textures/blocks/encased_pipe.png",
        "description": "机壳管道",
    },
    "encased_fluid_pipe_atlas": {
        "category": "fluid", "kind": "block",
        "source": "textures/blocks/encased_fluid_pipe_atlas.png",
        "description": "机壳流体管道图集",
    },
    "fluid_pipe_atlas": {
        "category": "fluid", "kind": "block",
        "source": "textures/blocks/fluid_pipe_atlas.png",
        "description": "流体管道图集",
    },
    "transparent": {
        "category": "utility", "kind": "block",
        "source": "textures/blocks/wacreate_transparent.png",
        "description": "透明占位纹理",
    },
    "shaft_icon": {
        "category": "icon", "kind": "item",
        "source": "textures/items/generated_icons/shaft.png",
        "description": "传动杆物品图标",
    },
    "gearbox_icon": {
        "category": "icon", "kind": "item",
        "source": "textures/items/generated_icons/gearbox.png",
        "description": "齿轮箱物品图标",
    },
    "gearshift_icon": {
        "category": "icon", "kind": "item",
        "source": "textures/items/generated_icons/gearshift.png",
        "description": "齿轮换向器物品图标",
    },
}


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _add_pack_dependency(path, uuid):
    """Add an idempotent dependency to a behavior/resource pack manifest."""
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    dependency = {"uuid": uuid, "version": [int(part) for part in CORE_VERSION.split(".")]}
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, list):
        dependencies = []
    if not any(isinstance(item, dict) and item.get("uuid") == uuid for item in dependencies):
        dependencies.append(dependency)
    data["dependencies"] = dependencies
    path.write_text(_json(data) + "\n", encoding="utf-8", newline="\n")


def _safe_dir(value):
    path = Path(value).expanduser().resolve()
    if path == Path(path.anchor):
        raise ValueError("拒绝使用文件系统根目录作为输出目录")
    return path


def _find_core_resource_pack():
    """Find the local core resource pack that seeds the curated MCP assets."""
    candidates = sorted(ROOT.glob("resource_pack_*/textures"))
    for textures in candidates:
        if (textures / "blocks" / "shaft.png").is_file():
            return textures.parent
    return None


def _asset_path(asset_id):
    record = DEVELOPER_ASSET_CATALOG.get(str(asset_id))
    if record is None:
        raise KeyError("未知开发资源：%s" % asset_id)
    path = MCP_ASSET_ROOT / record["source"]
    # The catalog is source-controlled; this check protects future edits from
    # accidentally escaping the MCP asset directory.
    if path.resolve().parent != MCP_ASSET_ROOT.resolve() and MCP_ASSET_ROOT.resolve() not in path.resolve().parents:
        raise ValueError("资源路径越界：%s" % asset_id)
    return path


def _asset_dimensions(path):
    try:
        with Image.open(str(path)) as image:
            return [int(image.width), int(image.height)]
    except Exception:
        return None


def _asset_catalog_result(category=None):
    assets = []
    for asset_id in sorted(DEVELOPER_ASSET_CATALOG):
        record = DEVELOPER_ASSET_CATALOG[asset_id]
        if category and record["category"] != str(category):
            continue
        path = _asset_path(asset_id)
        assets.append({
            "id": asset_id,
            "category": record["category"],
            "kind": record["kind"],
            "description": record["description"],
            "path": record["source"].replace("\\", "/"),
            "available": path.is_file(),
            "dimensions": _asset_dimensions(path) if path.is_file() else None,
        })
    return assets


def _merge_texture_registry(path, registry_key, entries, force=False):
    """Merge namespaced texture_data entries without replacing user data."""
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    else:
        data = {"resource_pack_name": "vanilla", "texture_data": {}}
    texture_data = data.get("texture_data")
    if not isinstance(texture_data, dict):
        texture_data = {}
    for key, entry in entries.items():
        if key in texture_data and texture_data[key] != entry and not force:
            raise FileExistsError("纹理注册名冲突：%s" % key)
        texture_data[key] = entry
    data["texture_data"] = texture_data
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json(data) + "\n", encoding="utf-8", newline="\n")


def _install_assets(root, asset_ids, namespace, force=False):
    resource_dirs = sorted(root.glob("resource_pack_*/"))
    resource = resource_dirs[0] if resource_dirs else root / "resource_pack_developer_assets"
    terrain_entries = {}
    item_entries = {}
    written = []
    skipped = []
    for asset_id in asset_ids:
        record = DEVELOPER_ASSET_CATALOG[asset_id]
        source = _asset_path(asset_id)
        if not source.is_file():
            raise FileNotFoundError("MCP 内置资源尚未导出：%s" % asset_id)
        destination = resource / record["source"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if destination.read_bytes() == source.read_bytes():
                skipped.append(str(destination))
            elif not force:
                raise FileExistsError("目标贴图已存在：%s；如需覆盖请显式传 force=true" % destination)
            else:
                shutil.copy2(str(source), str(destination))
                written.append(str(destination))
        else:
            shutil.copy2(str(source), str(destination))
            written.append(str(destination))
        texture_path = Path(record["source"]).with_suffix("").as_posix()
        registry_name = "%s:%s" % (namespace, asset_id)
        entry = {"textures": texture_path}
        if record["kind"] == "item":
            item_entries[registry_name] = entry
        else:
            terrain_entries[registry_name] = entry

    if terrain_entries:
        path = resource / "textures" / "terrain_texture.json"
        _merge_texture_registry(path, "terrain", terrain_entries, force=force)
        written.append(str(path))
    if item_entries:
        path = resource / "textures" / "item_texture.json"
        _merge_texture_registry(path, "item", item_entries, force=force)
        written.append(str(path))
    mapping_path = root / "mcp_developer_assets.json"
    mapping = {
        "namespace": namespace,
        "assets": [{"id": asset_id, "key": "%s:%s" % (namespace, asset_id),
                     "path": DEVELOPER_ASSET_CATALOG[asset_id]["source"].replace("\\", "/")}
                    for asset_id in asset_ids],
    }
    if mapping_path.exists() and not force:
        try:
            old = json.loads(mapping_path.read_text(encoding="utf-8-sig"))
        except Exception:
            old = None
        if old != mapping:
            raise FileExistsError("资源映射已存在：%s；如需更新请显式传 force=true" % mapping_path)
        skipped.append(str(mapping_path))
    else:
        _write(mapping_path, _json(mapping) + "\n", force=True)
        written.append(str(mapping_path))
    return resource, written, skipped


def _write(path, content, force=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise FileExistsError("文件已存在：%s；如需覆盖请显式传 force=true" % path)
    path.write_text(content, encoding="utf-8", newline="\n")


def _template_manifest(addon_id, machine_id, display_name):
    return {
        "id": addon_id,
        "name": display_name,
        "version": "0.1.0",
        "apiVersion": PUBLIC_API_VERSION,
        "requires": {"wacreate": ">=%s,<0.1.0" % CORE_VERSION},
        "entrypoints": {
            "server": "scripts.mechanical_extension:register",
            "client": "scripts.mechanical_extension:register_client",
        },
        "content": {"mechanicalComponents": [machine_id]},
    }


def _mechanical_source(addon_id, machine_id, display_name):
    block_name = machine_id
    return '''# -*- coding: utf-8 -*-
"""{display} mechanical component example.

The core owns the network solver.  This add-on only supplies a public
component specification and optional provider callbacks.
"""

from __future__ import unicode_literals

from Script_NeteaseModAeQXOhXR import public_api

ADDON_ID = {addon!r}
MACHINE_BLOCK = {block!r}
MACHINE_NAME = {name!r}
ADDON_SYSTEM_NAME = "{addon}ServerSystem"


def get_source_speed(key):
    # Return a signed RPM value for a powered source, or 0 for a consumer.
    return 0.0


def get_stress_capacity(key):
    return 128.0


def register(core_system):
    """Call once during the add-on server-system initialization."""
    if core_system is None:
        return False
    if not public_api.register_addon(core_system, ADDON_ID, "0.1.0", name=MACHINE_NAME):
        return False
    return bool(core_system.RegisterMechanicalComponent(
        MACHINE_BLOCK,
        {{
            "kind": "machine",
            "powered": True,
            "axisMode": "facing",
            "shaftMode": "axis",
            "axisRelay": True,
            "stressImpact": 8.0,
            "stressCapacity": 128.0,
        }},
        providerNamespace=ADDON_ID,
        providerSystem=ADDON_SYSTEM_NAME,
        sourceResolver="GetSourceSpeed",
        stressCapacityResolver="GetStressCapacity",
    ))


def register_client(core_system):
    """Register client-side visual hooks here after adding a model."""
    return core_system is not None
'''.format(addon=addon_id, block=block_name, name=display_name,
           display=display_name)


def _normalize_machine_design(machine_id, display_name, design):
    """Validate a data-only machine contract used by the generic scaffold."""
    if not isinstance(design, dict):
        design = {}
    roles = design.get("roles", ["consumer"])
    if isinstance(roles, str):
        roles = [roles]
    allowed_roles = set(MACHINE_CAPABILITY_CATALOG["roles"])
    if not isinstance(roles, list) or not roles or any(str(role) not in allowed_roles for role in roles):
        raise ValueError("roles 必须是 source/consumer/relay/storage/processor 的非空数组")
    ports = design.get("ports", [])
    if not isinstance(ports, list):
        raise ValueError("ports 必须是数组")
    normalized_ports = []
    names = set()
    kinds = set(MACHINE_CAPABILITY_CATALOG["ports"])
    directions = set(("input", "output", "bidirectional"))
    for port in ports:
        if not isinstance(port, dict):
            raise ValueError("每个 port 必须是对象")
        name = str(port.get("name", ""))
        kind = str(port.get("kind", ""))
        direction = str(port.get("direction", "bidirectional"))
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,31}", name) or name in names:
            raise ValueError("port.name 必须唯一且使用小写字母/数字/下划线")
        if kind not in kinds or direction not in directions:
            raise ValueError("port.kind 或 port.direction 无效")
        names.add(name)
        item = {"name": name, "kind": kind, "direction": direction}
        if "capacity" in port:
            capacity = float(port["capacity"])
            if capacity < 0 or capacity != capacity or capacity == float("inf"):
                raise ValueError("port.capacity 必须是有限非负数")
            item["capacity"] = capacity
        normalized_ports.append(item)
    power = design.get("power", {})
    if not isinstance(power, dict):
        raise ValueError("power 必须是对象")
    power_out = {}
    for key in ("rpm", "stressCapacity", "stressImpact", "energyCapacity", "energyPerTick"):
        if key in power:
            value = float(power[key])
            if value < 0 or value != value or value == float("inf"):
                raise ValueError("power.%s 必须是有限非负数" % key)
            power_out[key] = value
    power_out["system"] = str(power.get("system", "mechanical"))
    recipes = design.get("recipes", [])
    if not isinstance(recipes, list):
        raise ValueError("recipes 必须是数组")
    normalized_recipes = []
    for recipe in recipes:
        if not isinstance(recipe, dict) or not recipe.get("id"):
            raise ValueError("每个 recipe 必须有 id")
        inputs = recipe.get("inputs", [])
        outputs = recipe.get("outputs", [])
        if not isinstance(inputs, list) or not isinstance(outputs, list) or not inputs or not outputs:
            raise ValueError("recipe.inputs 和 recipe.outputs 都必须为非空数组")
        duration = float(recipe.get("duration", 1.0))
        if duration <= 0 or duration != duration or duration == float("inf"):
            raise ValueError("recipe.duration 必须是正数")
        normalized_recipes.append({"id": str(recipe["id"]), "inputs": inputs,
                                   "outputs": outputs, "duration": duration})
    visual = design.get("visual", {})
    if not isinstance(visual, dict):
        raise ValueError("visual 必须是对象")
    frame = str(visual.get("rotationFrame", "local"))
    if frame not in ("local", "world"):
        raise ValueError("visual.rotationFrame 必须是 local/world")
    return {
        "schemaVersion": 1,
        "machineId": machine_id,
        "displayName": display_name,
        "roles": [str(role) for role in roles],
        "ports": normalized_ports,
        "power": power_out,
        "recipes": normalized_recipes,
        "inventory": dict(design.get("inventory", {})) if isinstance(design.get("inventory", {}), dict) else {},
        "fluids": dict(design.get("fluids", {})) if isinstance(design.get("fluids", {}), dict) else {},
        "visual": {"rotationFrame": frame, "geometry": str(visual.get("geometry", ""))},
        "events": list(design.get("events", [])) if isinstance(design.get("events", []), list) else [],
    }


def _generic_machine_source(addon_id, contract):
    return '''# -*- coding: utf-8 -*-
"""Generated public-API scaffold; gameplay remains owned by this add-on."""
from __future__ import unicode_literals
from Script_NeteaseModAeQXOhXR import public_api

ADDON_ID = {addon!r}
MACHINE_BLOCK = {machine!r}
DESIGN = {design!r}

def register(core_system):
    if core_system is None:
        return False
    if not public_api.register_addon(core_system, ADDON_ID, "0.1.0", name={name!r}):
        return False
    if "mechanical" not in [p["kind"] for p in DESIGN["ports"]]:
        return True
    roles = set(DESIGN["roles"])
    return bool(core_system.RegisterMechanicalComponent(MACHINE_BLOCK, {{
        "kind": "source" if "source" in roles else "machine",
        "powered": "source" in roles,
        "axisMode": "facing",
        "shaftMode": "omni" if "relay" in roles else "axis",
        "axisRelay": "relay" in roles,
        "stressCapacity": DESIGN["power"].get("stressCapacity", 0.0),
        "stressImpact": DESIGN["power"].get("stressImpact", 0.0),
    }}))

def register_client(core_system):
    return core_system is not None
'''.format(addon=addon_id, machine=contract["machineId"],
           name=contract["displayName"], design=repr(contract))


def _dependency_guard(addon_id, minimum_version):
    message = missing_core_message(addon_id, minimum_version)
    return '''# -*- coding: utf-8 -*-
"""Small compatibility shim shipped with an add-on.

The main pack cannot display this message when it is absent, so the add-on
must run this check before importing any core-dependent implementation.
"""

from __future__ import unicode_literals

ADDON_ID = {addon!r}
MINIMUM_CORE_VERSION = {minimum!r}
MISSING_CORE_MESSAGE = {message!r}


def missing_core_message():
    return MISSING_CORE_MESSAGE


def require_core(server_api):
    """Return the core server system, or None after emitting a clear hint."""
    try:
        from Script_NeteaseModAeQXOhXR.public_api import get_server_system
        system = get_server_system(server_api)
    except Exception:
        system = None
    if system is not None:
        return system
    # The exact command API varies between NetEase runtime versions.  Keep
    # this fallback conservative and let the add-on provide player context.
    print("[WACreate] " + MISSING_CORE_MESSAGE.replace("\\n", " "))
    return None


def notify_missing_core(server_api, player_id=None):
    """Try to show the hint to one player, while retaining a log fallback."""
    if player_id is None:
        print("[WACreate] " + MISSING_CORE_MESSAGE.replace("\\n", " "))
        return False
    try:
        level_id = server_api.GetLevelId()
        command = server_api.GetEngineCompFactory().CreateCommand(level_id)
        command.SetCommand(
            u"/title @s actionbar %s" % MISSING_CORE_MESSAGE.replace("\\n", " "),
            player_id)
        return True
    except Exception:
        print("[WACreate] " + MISSING_CORE_MESSAGE.replace("\\n", " "))
        return False
'''.format(addon=addon_id, minimum=minimum_version, message=message)


def _six_way_cubes():
    """Return an original-style layered casing with six separated shaft hubs.

    The top and bottom casing are four rails rather than solid plates.  This
    leaves a clean central opening for the vertical hubs and ensures that
    touching faces do not become strict AABB intersections.
    """
    return [
        ("core", [-14, 2, 2], [12, 12, 12], "body"),
        ("frame_top_left", [-16, 0, 0], [6, 2, 16], "frame"),
        ("frame_top_right", [-6, 0, 0], [6, 2, 16], "frame"),
        ("frame_top_mid_north", [-10, 0, 0], [4, 2, 6], "frame"),
        ("frame_top_mid_south", [-10, 0, 10], [4, 2, 6], "frame"),
        ("frame_bottom_left", [-16, 14, 0], [6, 2, 16], "frame"),
        ("frame_bottom_right", [-6, 14, 0], [6, 2, 16], "frame"),
        ("frame_bottom_mid_north", [-10, 14, 0], [4, 2, 6], "frame"),
        ("frame_bottom_mid_south", [-10, 14, 10], [4, 2, 6], "frame"),
        ("frame_west_upper", [-16, 2, 2], [2, 4, 12], "frame"),
        ("frame_west_lower", [-16, 10, 2], [2, 4, 12], "frame"),
        ("frame_west_mid_north", [-16, 6, 2], [2, 4, 4], "frame"),
        ("frame_west_mid_south", [-16, 6, 10], [2, 4, 4], "frame"),
        ("frame_east_upper", [-2, 2, 2], [2, 4, 12], "frame"),
        ("frame_east_lower", [-2, 10, 2], [2, 4, 12], "frame"),
        ("frame_east_mid_north", [-2, 6, 2], [2, 4, 4], "frame"),
        ("frame_east_mid_south", [-2, 6, 10], [2, 4, 4], "frame"),
        ("frame_north_left", [-14, 2, 0], [4, 12, 2], "frame"),
        ("frame_north_right", [-6, 2, 0], [4, 12, 2], "frame"),
        ("frame_north_mid_lower", [-10, 2, 0], [4, 4, 2], "frame"),
        ("frame_north_mid_upper", [-10, 10, 0], [4, 4, 2], "frame"),
        ("frame_south_left", [-14, 2, 14], [4, 12, 2], "frame"),
        ("frame_south_right", [-6, 2, 14], [4, 12, 2], "frame"),
        ("frame_south_mid_lower", [-10, 2, 14], [4, 4, 2], "frame"),
        ("frame_south_mid_upper", [-10, 10, 14], [4, 4, 2], "frame"),
        ("hub_west", [-18, 6, 6], [4, 4, 4], "hub"),
        ("hub_east", [-2, 6, 6], [4, 4, 4], "hub"),
        ("hub_north", [-10, 6, -2], [4, 4, 4], "hub"),
        ("hub_south", [-10, 6, 14], [4, 4, 4], "hub"),
        ("hub_down", [-10, -2, 6], [4, 4, 4], "hub"),
        ("hub_up", [-10, 14, 6], [4, 4, 4], "hub"),
    ]


def _boxes_overlap(left, right):
    for axis in range(3):
        left_min = left[1][axis]
        left_max = left_min + left[2][axis]
        right_min = right[1][axis]
        right_max = right_min + right[2][axis]
        if min(left_max, right_max) <= max(left_min, right_min):
            return False
    return True


def _uv_rectangles(cube_count):
    faces = ("down", "east", "north", "south", "up", "west")
    rectangles = {}
    for index in range(cube_count * len(faces)):
        col = index % 16
        row = index // 16
        rectangles[index] = ([col * 16, row * 16], [16, 16])
    return rectangles, faces


def _legacy_six_way_models():
    cubes = _six_way_cubes()
    uv, faces = _uv_rectangles(len(cubes))
    bones_block = []
    bones_entity = []
    uv_index = 0
    for name, origin, size, material in cubes:
        block_uv = {}
        entity_uv = {}
        for face in faces:
            coords, uv_size = uv[uv_index]
            block_uv[face] = {"texture": 0, "uv": coords, "uv_size": uv_size}
            entity_uv[face] = {"uv": coords, "uv_size": uv_size}
            uv_index += 1
        common = {
            "name": name,
            "pivot": [-8, 8, 8],
            "rotation": [0, 0, 0],
            "cubes": [{"origin": origin, "size": size, "uv": block_uv}],
        }
        bones_block.append(common)
        bones_entity.append({
            "name": name,
            "pivot": [-8, 8, 8],
            "rotation": [0, 0, 0],
            "cubes": [{"origin": origin, "size": size, "uv": entity_uv}],
        })
    block_model = {
        "format_version": "1.13.0",
        "netease:block_geometry": {"description": {
            "identifier": "six_way_gearbox:gearbox_6way",
            "item_texture": "six_way_gearbox:gearbox_6way",
            "textures": ["six_way_gearbox:gearbox_6way"],
            "textures_descriptions": [{"length": 256, "width": 256}],
            "use_ao": True,
        }, "bones": bones_block},
    }
    entity_model = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{"description": {
            "identifier": "geometry.six_way_gearbox",
            "texture_width": 256, "texture_height": 256,
            "visible_bounds_width": 2.5, "visible_bounds_height": 2.5,
            "visible_bounds_offset": [0, 0.5, 0],
        }, "bones": bones_entity}],
    }
    return block_model, entity_model


def _six_way_axis_bone(name, include_texture=False):
    """Return one vertical axle with a short collar and stepped shaft."""
    def uv_map(kind):
        if kind == "collar":
            mapping = {
                "down": {"uv": [40, 16], "uv_size": [-4, 4]},
                "east": {"uv": [8, 28], "uv_size": [4, 1]},
                "north": {"uv": [24, 8], "uv_size": [4, 1]},
                "south": {"uv": [24, 12], "uv_size": [4, 1]},
                "up": {"uv": [14, 24], "uv_size": [4, 4]},
                "west": {"uv": [12, 28], "uv_size": [4, 1]},
            }
        else:
            mapping = {
                "down": {"uv": [40, 16], "uv_size": [-4, 4]},
                "east": {"uv": [8, 28], "uv_size": [4, 4]},
                "north": {"uv": [24, 8], "uv_size": [4, 4]},
                "south": {"uv": [24, 12], "uv_size": [4, 4]},
                "up": {"uv": [14, 24], "uv_size": [4, 4]},
                "west": {"uv": [12, 28], "uv_size": [4, 4]},
            }
        return ({face: dict(data, texture=0) for face, data in mapping.items()}
                if include_texture else mapping)
    top = name == "axisU"
    # Keep the complete exposed length at six units so it lines up with the
    # visible length of the original horizontal axle ends.
    collar_y = 16 if top else -1
    shaft_y = 17 if top else -6
    return {
        "cubes": [
            {
            "origin": [-11, collar_y, 5],
            "pivot": [-8, 8, 8],
            "rotation": [0, 0, 0],
            "size": [4, 1, 4],
            "uv": uv_map("collar"),
            },
            {
            "origin": [-10, shaft_y, 6],
            "pivot": [-8, 8, 8],
            "rotation": [0, 0, 0],
            "size": [4, 5, 4],
            "uv": uv_map("shaft"),
            },
        ],
        "name": name,
        "parent": "Gearbox",
        "pivot": [-8, 8, 8],
        "rotation": [0, 0, 0],
    }


def _six_way_models():
    """Clone the shipped gearbox model and add the two missing vertical axles.

    Keeping the original 64x64 UV layout is deliberate: the visual language,
    bevels, and pixel shading stay identical to the main pack.  The two added
    bones reuse the original shaft face regions instead of introducing a new
    atlas with unrelated seams.
    """
    entity_path = ROOT / "resource_pack_LuDNiK2f" / "models" / "entity" / "gearbox_entity.json"
    block_path = ROOT / "resource_pack_LuDNiK2f" / "models" / "netease_block" / "gearbox.json"
    if not entity_path.is_file() or not block_path.is_file():
        return _legacy_six_way_models()

    entity_model = json.loads(entity_path.read_text(encoding="utf-8-sig"))
    entity_geometry = entity_model["minecraft:geometry"][0]
    entity_geometry["description"]["identifier"] = "geometry.six_way_gearbox"
    entity_geometry["bones"].extend([
        _six_way_axis_bone("axisD"),
        _six_way_axis_bone("axisU"),
    ])

    block_model = json.loads(block_path.read_text(encoding="utf-8-sig"))
    block_geometry = block_model["netease:block_geometry"]
    block_geometry["description"].update({
        "identifier": "six_way_gearbox:gearbox_6way",
        "item_texture": "six_way_gearbox:gearbox_6way",
        "textures": ["six_way_gearbox:gearbox_6way"],
    })
    block_geometry["bones"].extend([
        _six_way_axis_bone("axisD", include_texture=True),
        _six_way_axis_bone("axisU", include_texture=True),
    ])
    return block_model, entity_model


def _legacy_six_way_texture(path):
    """Build a 256px atlas from the original gearbox texture regions."""
    source_path = MCP_ASSET_ROOT / "textures" / "blocks" / "Gearbox.png"
    if not source_path.is_file():
        source_path = ROOT / "resource_pack_LuDNiK2f" / "textures" / "blocks" / "Gearbox.png"
    source = Image.open(str(source_path)).convert("RGBA")
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    crops = {
        "body": source.crop((0, 0, 16, 16)),
        "frame": source.crop((16, 0, 32, 16)),
        "hub": source.crop((24, 20, 40, 36)),
    }
    faces = ("down", "east", "north", "south", "up", "west")
    for index, (_name, _origin, _size, material) in enumerate(_six_way_cubes()):
        for face_index, _face in enumerate(faces):
            tile_index = index * len(faces) + face_index
            col = tile_index % 16
            row = tile_index // 16
            tile = crops[material].resize((16, 16), Image.Resampling.NEAREST)
            draw = ImageDraw.Draw(tile)
            # Preserve the original pixel style while adding a small face
            # bevel so the new atlas reads clearly on all six orientations.
            draw.line((0, 0, 15, 0), fill=(210, 210, 210, 150), width=1)
            draw.line((0, 0, 0, 15), fill=(150, 150, 150, 130), width=1)
            draw.line((0, 15, 15, 15), fill=(35, 35, 35, 170), width=1)
            draw.line((15, 0, 15, 15), fill=(25, 25, 25, 170), width=1)
            image.paste(tile, (col * 16, row * 16))
    image.save(str(path), "PNG")


def _six_way_texture(path):
    """Copy the original gearbox texture so the cloned UVs remain exact."""
    source_path = MCP_ASSET_ROOT / "textures" / "blocks" / "Gearbox.png"
    if not source_path.is_file():
        source_path = ROOT / "resource_pack_LuDNiK2f" / "textures" / "blocks" / "Gearbox.png"
    if not source_path.is_file():
        return _legacy_six_way_texture(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(source_path), str(path))


def _six_way_server_source(addon_id, machine_id, display_name):
    return '''# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mod.server.extraServerApi as serverApi

MOD_NAMESPACE = {addon!r}
SYSTEM_NAME = "SixWayGearboxServerSystem"
MACHINE_BLOCK = {machine!r}


class SixWayGearboxServerSystem(serverApi.GetServerSystemCls()):
    """Small independent bridge; the WACreate core owns network state."""

    def __init__(self, namespace, systemName):
        serverApi.GetServerSystemCls().__init__(self, namespace, systemName)
        self.integrated = False
        self.retry_ticks = 0
        self.last_error = None
        self.ListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            "OnScriptTickServer", self, self.OnTick)
        self._try_integrate()

    def OnTick(self, args=None):
        if not self.integrated:
            self.retry_ticks += 1
            if self.retry_ticks >= 20:
                self.retry_ticks = 0
                self._try_integrate()

    def Destroy(self):
        self.UnListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            "OnScriptTickServer", self, self.OnTick)

    def _try_integrate(self):
        try:
            from Script_NeteaseModAeQXOhXR.public_api import get_server_system, register_addon
            core = get_server_system(serverApi)
            if core is None:
                raise RuntimeError("WACreate core unavailable; enable the core pack and reload")
            if not register_addon(core, MOD_NAMESPACE, "0.1.0", name={name!r}):
                raise RuntimeError("WACreate rejected add-on metadata; check API version")
            self.integrated = bool(core.RegisterMechanicalComponent(
                MACHINE_BLOCK,
                {{
                    "kind": "gearbox",
                    "powered": False,
                    "axisMode": "fixed_y",
                    "shaftMode": "omni",
                    "axisRelay": True,
                    "placementMode": "auto_connect",
                    "gearboxAxis": "y",
                    "stressImpact": 0.0,
                }},
            ))
            if not self.integrated:
                raise RuntimeError("WACreate rejected six-way mechanical registration")
        except Exception as error:
            message = str(error)
            if message != self.last_error:
                print("[six_way_gearbox] " + message)
                self.last_error = message
            return False
        self.last_error = None
        return self.integrated
'''.format(addon=addon_id, machine=machine_id, name=display_name)


def _six_way_modmain_source(addon_id):
    return '''# -*- coding: utf-8 -*-
from mod.common.mod import Mod
import mod.server.extraServerApi as serverApi


MOD_NAMESPACE = {addon!r}
SERVER_SYSTEM_NAME = "SixWayGearboxServerSystem"
SERVER_SYSTEM_PATH = "Script_{addon}.serverSystem.SixWayGearboxServerSystem"


@Mod.Binding(name=MOD_NAMESPACE, version="0.1.0")
class SixWayGearboxMod(object):

    @Mod.InitServer()
    def init_server(self):
        serverApi.RegisterSystem(MOD_NAMESPACE, SERVER_SYSTEM_NAME, SERVER_SYSTEM_PATH)
'''.format(addon=addon_id)


@MCP.tool()
def wacreate_add_mechanical_animations(output_dir, addon_id, machine_id,
                                      groups=None, entity_path=None, model_path=None,
                                      bounce_ticks=10, bounce_degrees=4.0,
                                      integrate_client=True, dry_run=True, force=False,
                                      rotation_frame="local"):
    """按传动骨骼分组生成旋转动画、主包停转回弹规格并接入客户端入口。"""
    if not validate_addon_id(str(addon_id or "")):
        return _json({"ok": False, "error": "addon_id 格式无效"})
    if not _MACHINE_RE.fullmatch(str(machine_id or "")):
        return _json({"ok": False, "error": "machine_id 必须是 namespace:block_name"})
    if not re.fullmatch(r"[a-z][a-z0-9_]{1,63}", str(addon_id)):
        return _json({"ok": False, "error": "动画脚本 addon_id 必须可用于 Python 包名"})
    try:
        from tools.wacreate_animation_tools import generate_bundle
    except ImportError:
        from wacreate_animation_tools import generate_bundle
    try:
        return _json(generate_bundle(
            _safe_dir(output_dir), str(addon_id), str(machine_id),
            groups=groups, entity_path=entity_path, model_path=model_path,
            bounce_ticks=bounce_ticks, bounce_degrees=bounce_degrees,
            integrate_client=bool(integrate_client), dry_run=bool(dry_run),
            force=bool(force), rotation_frame=rotation_frame))
    except Exception as error:
        return _json({"ok": False, "error": str(error)})


@MCP.tool()
def wacreate_api_catalog(category=None):
    """查询公共 API、版本、稳定级别和参数摘要。"""
    result = api_info()
    result["catalog"] = PUBLIC_API_CATALOG
    if category:
        result["catalog"] = PUBLIC_API_CATALOG.get(str(category), {})
    return _json(result)


@MCP.tool()
def wacreate_asset_catalog(category=None):
    """查询 MCP 内置的可复用机械、流体和物品贴图。"""
    category = str(category) if category else None
    valid_categories = sorted(set(item["category"] for item in DEVELOPER_ASSET_CATALOG.values()))
    if category and category not in valid_categories:
        return _json({"ok": False, "error": "未知资源分类", "categories": valid_categories})
    assets = _asset_catalog_result(category)
    return _json({"ok": True, "version": 1, "categories": valid_categories,
                  "assets": assets})


@MCP.tool()
def wacreate_export_developer_assets(category=None, force=False):
    """从本地主包导出精选贴图到 MCP 自带资源目录。"""
    category = str(category) if category else None
    selected = [asset_id for asset_id, record in DEVELOPER_ASSET_CATALOG.items()
                if not category or record["category"] == category]
    if category and not selected:
        return _json({"ok": False, "error": "未知资源分类"})
    try:
        source_pack = _find_core_resource_pack()
        if source_pack is None:
            return _json({"ok": False, "error": "找不到用于导出的主包资源目录"})
        written = []
        skipped = []
        for asset_id in selected:
            record = DEVELOPER_ASSET_CATALOG[asset_id]
            source = source_pack / record["source"]
            destination = MCP_ASSET_ROOT / record["source"]
            if not source.is_file():
                return _json({"ok": False, "error": "主包缺少资源：%s" % record["source"]})
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists() and not force:
                if destination.read_bytes() != source.read_bytes():
                    return _json({"ok": False, "error": "MCP 资源已存在且内容不同：%s；请传 force=true" % destination})
                skipped.append(str(destination))
            else:
                shutil.copy2(str(source), str(destination))
                written.append(str(destination))
        manifest = {"version": 1, "assets": _asset_catalog_result(category)}
        manifest_path = MCP_ASSET_ROOT / "asset_manifest.json"
        _write(manifest_path, _json(manifest) + "\n", force=True)
        written.append(str(manifest_path))
        return _json({"ok": True, "root": str(MCP_ASSET_ROOT),
                      "written": written, "skipped": skipped,
                      "count": len(selected)})
    except Exception as error:
        return _json({"ok": False, "error": str(error)})


@MCP.tool()
def wacreate_install_developer_assets(output_dir, asset_ids=None,
                                      category="mechanical", namespace="wacreate_dev",
                                      force=False):
    """把 MCP 内置贴图安装到附属包资源包并生成命名空间注册。"""
    namespace = str(namespace or "")
    if not _NAMESPACE_RE.match(namespace):
        return _json({"ok": False, "error": "namespace 格式无效"})
    try:
        if asset_ids is None:
            selected = [asset_id for asset_id, record in DEVELOPER_ASSET_CATALOG.items()
                        if not category or record["category"] == str(category)]
        elif isinstance(asset_ids, (list, tuple)):
            selected = [str(asset_id) for asset_id in asset_ids]
        else:
            return _json({"ok": False, "error": "asset_ids 必须是数组"})
        if not selected:
            return _json({"ok": False, "error": "没有选择任何资源"})
        unknown = [asset_id for asset_id in selected if asset_id not in DEVELOPER_ASSET_CATALOG]
        if unknown:
            return _json({"ok": False, "error": "未知开发资源：%s" % ", ".join(unknown)})
        root = _safe_dir(output_dir)
        resource, written, skipped = _install_assets(root, selected, namespace, force=bool(force))
        return _json({"ok": True, "root": str(root), "resourcePack": str(resource),
                      "namespace": namespace, "assets": selected,
                      "written": written, "skipped": skipped})
    except Exception as error:
        return _json({"ok": False, "error": str(error)})


@MCP.tool()
def wacreate_missing_core_prompt(addon_id, minimum_version=None):
    """生成可复制到附属包的主包依赖提示和检查代码。"""
    addon_id = str(addon_id or "")
    if not validate_addon_id(addon_id):
        return _json({"ok": False, "error": "addon_id 格式无效"})
    minimum = str(minimum_version or CORE_VERSION)
    return _json({
        "ok": True,
        "message": missing_core_message(addon_id, minimum),
        "pythonFile": "scripts/dependency_guard.py",
        "python": _dependency_guard(addon_id, minimum),
    })


@MCP.tool()
def wacreate_validate_geometry(model_path):
    """检查几何盒体是否真正相交，以及 UV 矩形是否重叠。"""
    try:
        path = Path(model_path).expanduser().resolve()
        data = json.loads(path.read_text(encoding="utf-8"))
        cubes = []

        def walk(value, location=""):
            if isinstance(value, dict):
                if isinstance(value.get("origin"), list) and isinstance(value.get("size"), list):
                    cubes.append((location, value))
                for key, child in value.items():
                    walk(child, location + "/" + str(key))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, location + "/" + str(index))

        walk(data)
        geometry_overlaps = []
        for index, left in enumerate(cubes):
            for right in cubes[index + 1:]:
                left_box = (left[0], left[1]["origin"], left[1]["size"])
                right_box = (right[0], right[1]["origin"], right[1]["size"])
                if _boxes_overlap(left_box, right_box):
                    geometry_overlaps.append([left[0], right[0]])

        uv_entries = []
        for location, cube in cubes:
            uv = cube.get("uv")
            if not isinstance(uv, dict):
                continue
            for face, face_uv in uv.items():
                if not isinstance(face_uv, dict):
                    continue
                coords = face_uv.get("uv")
                size = face_uv.get("uv_size")
                if not (isinstance(coords, list) and isinstance(size, list) and len(coords) >= 2 and len(size) >= 2):
                    continue
                x1, x2 = sorted((float(coords[0]), float(coords[0]) + float(size[0])))
                y1, y2 = sorted((float(coords[1]), float(coords[1]) + float(size[1])))
                uv_entries.append((location + "/" + face, x1, y1, x2, y2))
        uv_overlaps = []
        for index, left in enumerate(uv_entries):
            for right in uv_entries[index + 1:]:
                if min(left[3], right[3]) > max(left[1], right[1]) and min(left[4], right[4]) > max(left[2], right[2]):
                    uv_overlaps.append([left[0], right[0]])
        return _json({
            "ok": not geometry_overlaps and not uv_overlaps,
            "cubes": len(cubes),
            "uvRectangles": len(uv_entries),
            "geometryOverlaps": geometry_overlaps,
            "uvOverlaps": uv_overlaps,
        })
    except Exception as error:
        return _json({"ok": False, "error": str(error)})


@MCP.tool()
def wacreate_create_six_way_gearbox(output_dir, addon_id="six_way_gearbox",
                                    machine_id="six_way_gearbox:gearbox_6way",
                                    display_name="六向齿轮箱", force=False):
    """生成六向齿轮箱的行为包、资源包、模型、纹理和配方。"""
    if not validate_addon_id(str(addon_id or "")):
        return _json({"ok": False, "error": "addon_id 格式无效"})
    if not _MACHINE_RE.match(str(machine_id or "")):
        return _json({"ok": False, "error": "machine_id 必须是 namespace:block_name"})
    try:
        root = _safe_dir(output_dir)
        behavior_dirs = sorted(root.glob("behavior_pack_*/"))
        resource_dirs = sorted(root.glob("resource_pack_*/"))
        if not behavior_dirs or not resource_dirs:
            return _json({"ok": False, "error": "目标目录需要已有 behavior_pack_* 和 resource_pack_* 清单"})
        behavior = behavior_dirs[0]
        resource = resource_dirs[0]
        machine = str(machine_id)
        block_model, entity_model = _six_way_models()
        block_json = {
            "format_version": "1.10.0",
            "minecraft:block": {"components": {
                "minecraft:block_light_absorption": {"value": 1},
                "minecraft:destroy_time": {"value": 1.5},
                "netease:aabb": {"clip": [{"min": [0, 0, 0], "max": [1, 1, 1]}],
                                  "collision": [{"min": [0, 0, 0], "max": [1, 1, 1]}]},
                "netease:block_entity": {"client_tick": True, "movable": False, "tick": True},
                "netease:listen_block_remove": {"value": True},
                "netease:neighborchanged_sendto_script": {"value": True},
                "netease:tier": {"digger": "pickaxe"},
            }, "description": {"category": "create_wachg", "identifier": machine}},
        }
        recipe = {
            "format_version": "1.12",
            "minecraft:recipe_shaped": {
                "description": {"identifier": machine},
                "tags": ["crafting_table"],
                "pattern": ["SCS", "CRC", "SCS"],
                "key": {"C": {"item": "wacreate:block"}, "S": {"item": "wacreate:shaft"}, "R": {"item": "wacreate:andesite_alloy"}},
                "result": {"item": machine, "count": 1},
            },
        }
        blocks = {
            "format_version": [1, 1, 0],
            machine: {"client_entity": {
                "block_icon": machine,
                "destroyed_textures": machine,
                "hand_model_use_client_entity": True,
                "identifier": machine + "_entity",
            }, "netease_model": "", "sound": "wood", "textures": machine},
        }
        terrain = {"resource_pack_name": "vanilla", "texture_data": {
            machine: {"textures": "textures/blocks/six_way_gearbox"},
        }}
        items = {"resource_pack_name": "vanilla", "texture_data": {
            machine: {"textures": "textures/blocks/six_way_gearbox"},
        }}
        entity = {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
            "identifier": machine + "_entity", "materials": {"default": "entity_alphatest"},
            "textures": {"default": "textures/blocks/six_way_gearbox"},
            "geometry": {"default": "geometry.six_way_gearbox"},
            "render_controllers": ["controller.render.default"],
        }}}
        files = {
            behavior / "netease_blocks" / "six_way_gearbox.json": block_json,
            behavior / "recipes" / "six_way_gearbox.json": recipe,
            resource / "blocks.json": blocks,
            resource / "textures" / "terrain_texture.json": terrain,
            resource / "textures" / "item_texture.json": items,
            resource / "models" / "netease_block" / "six_way_gearbox.json": block_model,
            resource / "models" / "entity" / "six_way_gearbox.json": entity_model,
            resource / "entity" / "six_way_gearbox_entity.json": entity,
            behavior / ("Script_%s" % str(addon_id)) / "__init__.py": "# Six-way gearbox add-on package.\n",
            behavior / ("Script_%s" % str(addon_id)) / "modMain.py": _six_way_modmain_source(str(addon_id)),
            behavior / ("Script_%s" % str(addon_id)) / "serverSystem.py": _six_way_server_source(str(addon_id), machine, str(display_name)),
        }
        written = []
        for path, data in files.items():
            content = data if path.suffix == ".py" else _json(data) + "\n"
            _write(path, content, bool(force))
            written.append(str(path))
        behavior_manifest = behavior / "manifest.json"
        resource_manifest = resource / "manifest.json"
        _add_pack_dependency(behavior_manifest, CORE_BEHAVIOR_UUID)
        _add_pack_dependency(resource_manifest, CORE_RESOURCE_UUID)
        written.extend([str(behavior_manifest), str(resource_manifest)])
        studio_path = root / "studio.json"
        if studio_path.is_file():
            studio = json.loads(studio_path.read_text(encoding="utf-8-sig"))
            studio["CodeEnable"] = True
            studio["NameSpace"] = str(addon_id)
            studio["EditName"] = str(display_name)
            studio_path.write_text(_json(studio) + "\n", encoding="utf-8", newline="\n")
            written.append(str(studio_path))
        texture_path = resource / "textures" / "blocks" / "six_way_gearbox.png"
        if texture_path.exists() and not force:
            raise FileExistsError("文件已存在：%s；如需覆盖请显式传 force=true" % texture_path)
        texture_path.parent.mkdir(parents=True, exist_ok=True)
        _six_way_texture(texture_path)
        written.append(str(texture_path))
        # Keep the generated template's manifest aligned with the concrete block.
        manifest_path = root / "addon_manifest.json"
        manifest = _template_manifest(str(addon_id), machine, str(display_name))
        manifest["content"]["mechanicalComponents"] = [machine]
        _write(manifest_path, _json(manifest) + "\n", bool(force))
        written.append(str(manifest_path))
        geometry_path = resource / "models" / "entity" / "six_way_gearbox.json"
        geometry_report = json.loads(wacreate_validate_geometry(str(geometry_path)))
        # The shipped gearbox intentionally reuses UV rectangles and lets
        # casing/axle pieces meet.  Keep that original visual contract while
        # exposing the strict report so callers can make their own policy
        # decision instead of silently treating the reuse as a defect.
        geometry_report["strictOk"] = bool(geometry_report.get("ok"))
        geometry_report["visualReference"] = "original_gearbox"
        return _json({"ok": bool(written), "files": written,
                      "geometry": geometry_report,
                      "mode": "omni", "requiresCoreApi": PUBLIC_API_VERSION})
    except Exception as error:
        return _json({"ok": False, "error": str(error)})


@MCP.tool()
def wacreate_machine_capability_catalog():
    """返回可组合的通用机械扩展能力，而不是某个具体时代的玩法模板。"""
    return _json({"ok": True, "schemaVersion": 1,
                  "capabilities": MACHINE_CAPABILITY_CATALOG,
                  "note": "MCP 生成合同和校验骨架；附属包仍需实现具体方块、配方、网络和客户端 UI。"})


@MCP.tool()
def wacreate_validate_machine_design(machine_id, display_name, design=None):
    """校验一个可组合的机械扩展合同，不写入文件。"""
    try:
        if not _MACHINE_RE.match(str(machine_id or "")):
            return _json({"ok": False, "error": "machine_id 必须是 namespace:block_name"})
        if not display_name:
            return _json({"ok": False, "error": "display_name 不能为空"})
        contract = _normalize_machine_design(str(machine_id), str(display_name), design)
        return _json({"ok": True, "contract": contract,
                      "capabilities": sorted(set(contract["roles"]) | set(p["kind"] for p in contract["ports"]))})
    except Exception as error:
        return _json({"ok": False, "error": str(error)})


@MCP.tool()
def wacreate_create_machine_extension(output_dir, addon_id, machine_id,
                                      display_name, design=None, force=False):
    """生成任意机械动力扩展的声明式合同、公共 API 桥接和实现骨架。"""
    addon_id = str(addon_id or "")
    if not validate_addon_id(addon_id):
        return _json({"ok": False, "error": "addon_id 格式无效"})
    try:
        if not _MACHINE_RE.match(str(machine_id or "")):
            return _json({"ok": False, "error": "machine_id 必须是 namespace:block_name"})
        contract = _normalize_machine_design(str(machine_id), str(display_name), design)
        root = _safe_dir(output_dir)
        manifest = _template_manifest(addon_id, machine_id, display_name)
        manifest["entrypoints"] = {"server": "scripts.machine_extension:register",
                                    "client": "scripts.machine_extension:register_client"}
        files = {
            "addon_manifest.json": _json(manifest) + "\n",
            "machine_design.json": _json(contract) + "\n",
            "scripts/__init__.py": "# Generated WACreate machine extension.\n",
            "scripts/dependency_guard.py": _dependency_guard(addon_id, CORE_VERSION),
            "scripts/machine_extension.py": _generic_machine_source(addon_id, contract),
            "scripts/machine_runtime.py": (
                "# Implement ports, recipes, inventories, fluids and UI here.\n"
                "# Keep core access behind public_api; do not import private systems.\n"
                "DESIGN_FILE = 'machine_design.json'\n"),
            "behavior_pack/README.md": "# 行为包\n\n根据 machine_design.json 添加方块、配方和事件。\n",
            "resource_pack/README.md": "# 资源包\n\n添加模型、贴图、动画；world 坐标动画不能混用原生朝向旋转。\n",
            "README.md": ("# %s\n\n需要 WACreate >= %s，公共 API v%s。\n\n"
                          "该目录是通用机械扩展骨架，不限定为电力、蒸汽或物流主题。\n"
                          "先运行 wacreate_validate_machine_design，再实现 machine_runtime.py。\n" %
                          (display_name, CORE_VERSION, PUBLIC_API_VERSION)),
        }
        written = []
        for relative, content in files.items():
            path = root / relative
            _write(path, content, bool(force))
            written.append(str(path))
        return _json({"ok": True, "root": str(root), "files": written,
                      "contract": contract,
                      "next": ["添加自己的方块/实体 JSON、模型、贴图和配方",
                               "实现 machine_runtime.py 的端口、库存和处理状态",
                               "用 wacreate_validate_addon 检查公共 API 边界"]})
    except Exception as error:
        return _json({"ok": False, "error": str(error)})


@MCP.tool()
def wacreate_create_mechanical_template(output_dir, addon_id, machine_id,
                                         display_name, force=False):
    """创建一个机械附属包骨架；默认拒绝覆盖已有文件。"""
    addon_id = str(addon_id or "")
    machine_id = str(machine_id or "")
    if not validate_addon_id(addon_id):
        return _json({"ok": False, "error": "addon_id 格式无效"})
    if not _MACHINE_RE.match(machine_id):
        return _json({"ok": False, "error": "machine_id 必须是 namespace:block_name"})
    if not display_name:
        return _json({"ok": False, "error": "display_name 不能为空"})
    try:
        root = _safe_dir(output_dir)
        files = {
            "addon_manifest.json": _json(_template_manifest(addon_id, machine_id, display_name)) + "\n",
            "scripts/__init__.py": "# Generated WACreate add-on package.\n",
            "scripts/dependency_guard.py": _dependency_guard(addon_id, CORE_VERSION),
            "scripts/mechanical_extension.py": _mechanical_source(addon_id, machine_id, display_name),
            "behavior_pack/README.md": (
                "# 行为包资源\n\n"
                "在这里放置 %s 的方块定义，并保持资源 ID 为附属包自己的 namespace。\n" % machine_id),
            "resource_pack/README.md": (
                "# 资源包\n\n"
                "在这里放置模型、材质和动画；不要复制 WACreate 主包模型。\n"),
            "README.md": (
                "# %s\n\n"
                "需要 WACreate 主包 >= %s，公共 API v%s。\n\n"
                "启动时先调用 scripts.dependency_guard.require_core，再调用 "
                "scripts.mechanical_extension.register。\n" %
                (display_name, CORE_VERSION, PUBLIC_API_VERSION)),
        }
        written = []
        for relative, content in files.items():
            path = root / relative
            _write(path, content, bool(force))
            written.append(str(path))
    except Exception as error:
        return _json({"ok": False, "error": str(error)})
    return _json({
        "ok": True,
        "root": str(root),
        "files": written,
        "next": [
            "实现附属包自己的 server system，并让名称与 ADDON_SYSTEM_NAME 一致",
            "在资源包中添加自己的模型、材质和方块定义",
            "将 RegisterMechanicalComponent 的 spec 调整为真实机械行为",
            "运行 wacreate_validate_addon 检查依赖和内部 API 误用",
        ],
    })


@MCP.tool()
def wacreate_add_missing_core_prompt(addon_dir, addon_id, minimum_version=None,
                                     force=False):
    """向已有附属包写入标准主包缺失提示 shim。"""
    addon_id = str(addon_id or "")
    if not validate_addon_id(addon_id):
        return _json({"ok": False, "error": "addon_id 格式无效"})
    try:
        root = _safe_dir(addon_dir)
        path = root / "scripts" / "dependency_guard.py"
        _write(path, _dependency_guard(addon_id, str(minimum_version or CORE_VERSION)), bool(force))
    except Exception as error:
        return _json({"ok": False, "error": str(error)})
    return _json({"ok": True, "file": str(path), "message": missing_core_message(addon_id, minimum_version or CORE_VERSION)})


@MCP.tool()
def wacreate_validate_addon(addon_dir):
    """检查附属包清单、公共 API 依赖、内部导入和缺失提示 shim。"""
    try:
        root = _safe_dir(addon_dir)
        manifest_path = root / "addon_manifest.json"
        issues = []
        warnings = []
        manifest = {}
        if not manifest_path.is_file():
            issues.append("缺少 addon_manifest.json")
        else:
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception as error:
                issues.append("addon_manifest.json 无法解析：%s" % error)
        if manifest:
            addon_id = manifest.get("id")
            if not validate_addon_id(addon_id):
                issues.append("manifest.id 格式无效")
            if int(manifest.get("apiVersion", -1)) != PUBLIC_API_VERSION:
                issues.append("apiVersion 不匹配")
            if "wacreate" not in (manifest.get("requires") or {}):
                issues.append("缺少 requires.wacreate")
        source_files = list(root.rglob("*.py")) if root.exists() else []
        joined = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in source_files)
        for private_name in ("wacreateServerSystem", "wacreateClientSystem", "system_facets", "runtime_persistence"):
            if private_name in joined:
                issues.append("检测到内部实现导入或引用：%s" % private_name)
        if not (root / "scripts" / "dependency_guard.py").is_file():
            warnings.append("缺少 scripts/dependency_guard.py，无法在主包缺失时给出标准提示")
        if not source_files:
            warnings.append("未发现 Python 附属包入口")
        return _json({"ok": not issues, "issues": issues, "warnings": warnings,
                      "root": str(root), "filesScanned": len(source_files)})
    except Exception as error:
        return _json({"ok": False, "error": str(error)})


if __name__ == "__main__":
    MCP.run()
