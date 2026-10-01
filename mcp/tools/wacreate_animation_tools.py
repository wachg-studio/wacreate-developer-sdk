# -*- coding: utf-8 -*-
"""Animation generation used by the existing WACreate MCP server."""

import ast
import hashlib
import json
import math
import re
from pathlib import Path


def dumps(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def axis_for_name(name):
    name = re.sub(r"[^a-z0-9]", "", name.lower())
    for suffix, axis in (("north", "z"), ("south", "z"), ("west", "x"),
                         ("east", "x"), ("down", "y"), ("up", "y")):
        if name.endswith(suffix):
            return axis
    return {"n": "z", "s": "z", "w": "x", "e": "x", "d": "y", "u": "y"}.get(name[-1:])


def resolve_groups(geometry, groups):
    bones = {bone["name"]: bone for bone in geometry["bones"]}
    if groups is None:
        groups = {}
        for name in bones:
            if not name.lower().startswith(("axis", "shaft")):
                continue
            axis = axis_for_name(name)
            if axis is None:
                raise ValueError("无法从骨骼 %s 推断旋转轴，请用 groups 指定 axis" % name)
            groups[name] = {"bones": [name], "axis": axis, "sign": 1.0}
    if not isinstance(groups, dict) or not groups:
        raise ValueError("未找到 axis*/shaft* 传动骨骼，请提供 groups")
    selected, result, tokens = set(), [], set()
    for name, data in groups.items():
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", name):
            raise ValueError("分组名必须是字母开头的字母/数字/下划线")
        if name.lower() in tokens:
            raise ValueError("分组名大小写冲突：%s" % name)
        tokens.add(name.lower())
        if not isinstance(data, dict) or data.get("axis") not in ("x", "y", "z"):
            raise ValueError("分组 %s 必须提供 axis=x/y/z" % name)
        names = data.get("bones")
        if not isinstance(names, list) or not names:
            raise ValueError("分组 %s 的 bones 必须是非空数组" % name)
        sign = float(data.get("sign", 1.0))
        if not math.isfinite(sign) or sign == 0 or abs(sign) > 32:
            raise ValueError("sign 必须是非零有限数字，绝对值不超过 32")
        for bone in names:
            if bone not in bones or bone in selected:
                raise ValueError("骨骼不存在或重复分组：%s" % bone)
            selected.add(bone)
        result.append({"name": name, "bones": names, "axis": data["axis"], "sign": sign})
    # Rotating a parent and its child with the same group would double motion.
    for name in selected:
        parent, seen = bones[name].get("parent"), set()
        while parent:
            if parent in seen or parent not in bones:
                raise ValueError("骨骼层级循环或缺少父骨骼：%s" % name)
            if parent in selected:
                raise ValueError("父子骨骼不能重复驱动，请仅选择父分组：%s / %s" % (parent, name))
            seen.add(parent)
            parent = bones[parent].get("parent")
    return result


def client_source(machine_id, spec):
    return '''# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import mod.client.extraClientApi as clientApi

MACHINE_BLOCK = %r
VISUAL_SPEC = %r


class MechanicalAnimationClientSystem(clientApi.GetClientSystemCls()):
    def __init__(self, namespace, systemName):
        clientApi.GetClientSystemCls().__init__(self, namespace, systemName)
        self.registered = False
        self.retry_ticks = 19
        self.registration_audit_ticks = 0
        self.last_error = None
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            "OnScriptTickClient", self, self.OnTick)

    def OnTick(self, args=None):
        self.retry_ticks += 1
        if not self.registered and self.retry_ticks < 20:
            return
        if self.registered:
            self.registration_audit_ticks += 1
            if self.registration_audit_ticks < 100:
                return
            self.registration_audit_ticks = 0
        else:
            self.retry_ticks = 0
        try:
            from Script_NeteaseModAeQXOhXR.public_api import get_client_system
            core = get_client_system(clientApi)
            method = getattr(core, "RegisterMechanicalVisualSpec", None)
            if not callable(method):
                raise RuntimeError("Enable a WACreate core supporting RegisterMechanicalVisualSpec")
            if self.registered:
                audit = getattr(core, "GetMechanicalVisualSpec", None)
                if callable(audit):
                    current = audit(MACHINE_BLOCK)
                    if current == VISUAL_SPEC:
                        self.last_error = None
                        return
            self.registered = bool(method(MACHINE_BLOCK, VISUAL_SPEC))
            if not self.registered:
                raise RuntimeError("WACreate rejected animation groups")
            self.last_error = None
        except Exception as error:
            if str(error) != self.last_error:
                print("[WACreate animation] " + str(error))
                self.last_error = str(error)

    def Destroy(self):
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                              "OnScriptTickClient", self, self.OnTick)
''' % (machine_id, spec)


def bind_client(source, addon_id, module, system_name):
    """Insert into a single Mod.Binding class, preserving existing code."""
    tree = ast.parse(source)
    def has_decorator(node, name):
        return any(isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                   and isinstance(d.func.value, ast.Name) and d.func.value.id == "Mod"
                   and d.func.attr == name for d in node.decorator_list)
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and has_decorator(n, "Binding")]
    if len(classes) != 1:
        raise ValueError("modMain.py 必须有唯一 Mod.Binding 类；可关闭 integrate_client 后手动接入")
    cls = classes[0]
    edits, lines = [], source.splitlines(keepends=True)
    system_path = "Script_%s.%s.MechanicalAnimationClientSystem" % (addon_id, module)
    marker = "# WACreate animation: " + system_name
    api = "wacreateAnimationClientApi"
    register = '%s.RegisterSystem(%r, %r, %r)' % (api, addon_id, system_name, system_path)
    destroy = ('system = %s.GetSystem(%r, %r)\n'
               'if system is not None:\n    system.Destroy()') % (api, addon_id, system_name)
    for decorator, method_name, statement in (
        ("InitClient", "wacreate_animation_init", register),
        ("DestroyClient", "wacreate_animation_destroy", destroy),
    ):
        hooks = [n for n in cls.body if isinstance(n, ast.FunctionDef) and has_decorator(n, decorator)]
        if len(hooks) > 1:
            raise ValueError("多个 %s 生命周期入口，请手动接入" % decorator)
        hook = hooks[0] if hooks else None
        if hook and marker in ''.join(lines[hook.lineno - 1:hook.end_lineno]):
            continue
        if hook:
            indent = " " * (hook.col_offset + 4)
            body = "\n" + indent + marker + "\n" + "\n".join(indent + s for s in statement.splitlines()) + "\n"
            # Insert after the docstring, before any early return.
            first = hook.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                at = first.end_lineno
            else:
                at = first.lineno - 1
            edits.append((at, body))
        else:
            indent = " " * (cls.col_offset + 4)
            body = '\n' + indent + '@Mod.%s()\n' % decorator + indent + 'def %s(self):\n' % method_name
            body += indent + '    ' + marker + '\n'
            body += '\n'.join(indent + '    ' + s for s in statement.splitlines()) + '\n'
            edits.append((cls.end_lineno, body))
    if not any(isinstance(n, ast.Import) and any(a.asname == api for a in n.names) for n in tree.body):
        # Insert after module docstring and future imports; keep Python 2 compatibility.
        at = 0
        for n in tree.body:
            if isinstance(n, ast.ImportFrom) and n.module == '__future__':
                at = n.end_lineno
            elif isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                at = n.end_lineno
            else:
                break
        if at == 0:
            at = next((i for i, line in enumerate(lines) if not line.startswith('#') and line.strip()), 0)
        edits.append((at, '\nimport mod.client.extraClientApi as ' + api + '\n'))
    for at, body in sorted(edits, key=lambda item: item[0], reverse=True):
        lines.insert(at, body)
    result = ''.join(lines)
    ast.parse(result)
    return result


def generate_bundle(root, addon_id, machine_id, groups=None, entity_path=None,
                    model_path=None, bounce_ticks=10, bounce_degrees=4.0,
                    integrate_client=True, dry_run=True, force=False, rotation_frame="local"):
    root = Path(root).resolve()
    def local(path):
        path = Path(path)
        path = (root / path).resolve() if not path.is_absolute() else path.resolve()
        if root not in path.parents:
            raise ValueError("路径必须在附属包输出目录中")
        return path
    behaviors, resources = sorted(root.glob('behavior_pack_*')), sorted(root.glob('resource_pack_*'))
    if len(behaviors) != 1 or len(resources) != 1:
        raise ValueError("要求唯一 behavior_pack_* / resource_pack_*，避免写入错误包")
    behavior, resource = behaviors[0], resources[0]
    if rotation_frame not in ("local", "world"):
        raise ValueError("rotation_frame 必须是 local/world")
    if rotation_frame == "world":
        for path in (behavior / 'netease_blocks').glob('*.json'):
            block = json.loads(path.read_text(encoding='utf-8-sig')).get('minecraft:block', {})
            if block.get('description', {}).get('identifier') == machine_id and 'netease:face_directional' in block.get('components', {}):
                raise ValueError("world 模型不能启用 netease:face_directional：请先移除原生朝向旋转")
    if entity_path:
        entity_path = local(entity_path)
    else:
        candidates = []
        for path in (resource / 'entity').glob('*.json'):
            data = json.loads(path.read_text(encoding='utf-8-sig'))
            if data.get('minecraft:client_entity', {}).get('description', {}).get('identifier') == machine_id + '_entity':
                candidates.append(path)
        if len(candidates) != 1:
            raise ValueError("找不到唯一 client_entity，请指定 entity_path")
        entity_path = candidates[0]
    entity = json.loads(entity_path.read_text(encoding='utf-8-sig'))
    description = entity['minecraft:client_entity']['description']
    geometry_id = description['geometry']['default']
    if model_path:
        model_path = local(model_path)
        data = json.loads(model_path.read_text(encoding='utf-8-sig'))
        found = [g for g in data.get('minecraft:geometry', []) if g['description']['identifier'] == geometry_id]
    else:
        found = []
        for path in (resource / 'models' / 'entity').glob('*.json'):
            data = json.loads(path.read_text(encoding='utf-8-sig'))
            for g in data.get('minecraft:geometry', []):
                if g['description']['identifier'] == geometry_id:
                    model_path = path
                    found.append(g)
    if len(found) != 1:
        raise ValueError("模型与 geometry.default 不匹配或 identifier 重复")
    resolved = resolve_groups(found[0], groups)
    if rotation_frame == "world":
        if any(group['sign'] != 1.0 for group in resolved):
            raise ValueError("world 模型不接受逐面 sign 校准")
        bones = {bone['name']: bone for bone in found[0]['bones']}
        for group in resolved:
            for name in group['bones']:
                while name:
                    bone = bones[name]
                    if any(float(v) != 0.0 for v in bone.get('rotation', [0, 0, 0])):
                        raise ValueError("world 分组骨骼及父骨骼必须无静态旋转：" + name)
                    name = bone.get('parent')
    if isinstance(bounce_ticks, bool) or int(bounce_ticks) != bounce_ticks or not 1 <= bounce_ticks <= 100:
        raise ValueError("bounce_ticks 必须为 1..100 的整数")
    if not math.isfinite(float(bounce_degrees)) or not 0 <= bounce_degrees <= 45:
        raise ValueError("bounce_degrees 必须为 0..45")
    token = re.sub(r'[^a-z0-9_]', '_', machine_id.lower()) + '_' + hashlib.sha256(machine_id.encode()).hexdigest()[:8]
    animation_id = 'animation.%s.mechanical_spin' % token
    bone_tracks, parts, defaults = {}, {}, []
    for group in resolved:
        prefix = 'variable.wacreate_%s_%s_angle' % (token, group['name'].lower())
        parts[group['name']] = {'source': 'visual', 'visualAxis': group['axis'],
                                 'modelSign': group['sign'], 'prefix': prefix}
        rotation = [0.0, 0.0, 0.0]
        rotation['xyz'.index(group['axis'])] = '(%s_%s ?? 0.0) + (%s_speed_%s ?? 0.0) * (variable.wacreate_frame_time ?? 0.0)' % (prefix, group['axis'], prefix, group['axis'])
        for bone in group['bones']:
            bone_tracks[bone] = {'rotation': rotation}
        for suffix in ('_x', '_y', '_z', '_speed_x', '_speed_y', '_speed_z'):
            defaults.append(prefix + suffix + ' = 0.0;')
    spec = {'visualAxis': 'y', 'offsetMode': 'axis_phase', 'modelSign': 1.0,
            'stopBounce': {'ticks': int(bounce_ticks), 'degrees': float(bounce_degrees), 'mode': 'bounce'},
            'parts': parts}
    if rotation_frame == "world":
        spec['rotationFrame'] = 'world'
    animation = {'format_version': '1.8.0', 'animations': {animation_id: {
        'loop': True, 'animation_length': 1.0,
        'anim_time_update': 'variable.wacreate_angle_new = (variable.wacreate_angle_serial ?? 0.0) != (variable.wacreate_angle_last_serial ?? 0.0); variable.wacreate_frame_time = variable.wacreate_angle_new ? 0.0 : (variable.wacreate_frame_time ?? 0.0) + query.delta_time; variable.wacreate_frame_time = (variable.wacreate_frame_time ?? 0.0) > 2.0 ? 2.0 : (variable.wacreate_frame_time ?? 0.0); variable.wacreate_angle_last_serial = (variable.wacreate_angle_serial ?? 0.0);',
        'bones': bone_tracks}}}
    alias = 'wacreate_spin_' + token
    animations = description.setdefault('animations', {})
    if alias in animations and animations[alias] != animation_id:
        raise ValueError("动画别名冲突")
    animations[alias] = animation_id
    scripts = description.setdefault('scripts', {})
    initialize, animate = scripts.setdefault('initialize', []), scripts.setdefault('animate', [])
    if not isinstance(initialize, list) or not isinstance(animate, list):
        raise ValueError("scripts.initialize/animate 必须为数组")
    for statement in defaults:
        if statement not in initialize:
            initialize.append(statement)
    if alias not in animate:
        animate.append(alias)
    module, system_name = 'animation_' + token, 'MechanicalAnimation_' + token
    package = behavior / ('Script_' + addon_id)
    animation_path = resource / 'animations' / (token + '.animation.json')
    client_path = package / (module + '.py')
    modmain_path = package / 'modMain.py'
    registration = 'clientApi.RegisterSystem(%r, %r, %r)' % (addon_id, system_name, 'Script_%s.%s.MechanicalAnimationClientSystem' % (addon_id, module))
    files = {animation_path: dumps(animation), client_path: client_source(machine_id, spec), entity_path: dumps(entity)}
    if integrate_client:
        files[modmain_path] = bind_client(modmain_path.read_text(encoding='utf-8-sig'), addon_id, module, system_name)
    conflicts = [str(p) for p, text in files.items() if p.exists() and p.read_text(encoding='utf-8-sig') != text]
    report = {'ok': True, 'dryRun': bool(dry_run), 'groups': resolved, 'animationId': animation_id,
              'files': [str(p) for p in files], 'conflicts': conflicts, 'visualSpec': spec,
              'clientIntegrated': bool(integrate_client), 'registration': registration,
              'requiresClientMethod': 'RegisterMechanicalVisualSpec',
              'notes': ['旋转角度和停转回弹由主包客户端统一驱动，不使用自转计时模拟动力',
                        '自动分组按骨骼名推断轴；任意命名或旋转父骨骼应传 groups 明确局部轴',
                        '未进行网易游戏内验证；旧主包必须包含新增客户端注册接口']}
    if dry_run:
        return report
    if conflicts and not force:
        raise FileExistsError('写入将修改已有文件，请传 force=true；冲突：' + ', '.join(conflicts))
    # Preflight all writes, then roll back the bundle on an I/O failure.
    original = {p: p.read_bytes() if p.exists() else None for p in files}
    changed = []
    try:
        for p, text in files.items():
            local(p)
            if p.exists() and p.read_text(encoding='utf-8-sig') == text:
                continue
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding='utf-8', newline='\n')
            changed.append(p)
    except Exception:
        for p in reversed(changed):
            if original[p] is None:
                p.unlink()
            else:
                p.write_bytes(original[p])
        raise
    report['written'] = [str(p) for p in changed]
    return report
