# WACreate 开发者 MCP

文件：`tools/wacreate_mcp_server.py`

该 MCP 面向附属包开发者和 AI 编程代理。它只读取公共 API 描述，或在调用者指定的目录中生成模板和校验文件，不读取主包闭源实现，也不执行生成的 Python。

## 启动

在项目根目录运行：

```powershell
python tools/wacreate_mcp_server.py
```

这是 stdio MCP 服务。连接器需要把它作为本地 MCP command 启动，工作目录建议设为项目根目录。`requirements.txt` 已包含 `mcp` 运行依赖；如果开发者环境未安装依赖，先执行：

```powershell
python -m pip install -r requirements.txt
```

## 工具

### `wacreate_machine_capability_catalog`

返回通用机械扩展合同支持的可组合能力：机械、物品、流体、红石和数据端口，
以及 source、consumer、relay、storage、processor 五类角色。它不把玩法限定为
电力时代；电力、蒸汽、航空、物流、农业机械和多方块设备都使用同一套声明边界。

### `wacreate_validate_machine_design`

校验一个不写文件的 `machine_design` 合同。合同包括 `roles`、`ports`、`power`、
`recipes`、`inventory`、`fluids` 和 `visual`。它检查端口唯一性、容量和处理时间的
数值边界、配方输入输出完整性以及动画坐标系约束。

### `wacreate_create_machine_extension`

根据合同生成通用附属包骨架。生成内容包括主包依赖清单、`machine_design.json`、
公共 API 注册桥接、运行时实现占位、行为包/资源包说明和缺失主包提示。它不生成
某个时代的完整玩法，也不读取主包闭源代码；开发者只需按合同补齐方块、模型、
配方、库存、流体和 UI 实现。

一个可覆盖“电力时代”或其它机械扩展的设计例子：

```json
{
  "roles": ["source", "relay", "storage", "processor"],
  "ports": [
    {"name": "shaft", "kind": "mechanical", "direction": "output"},
    {"name": "items_in", "kind": "item", "direction": "input", "capacity": 16},
    {"name": "fluid_out", "kind": "fluid", "direction": "output"}
  ],
  "power": {"rpm": 32, "stressCapacity": 128, "energyPerTick": 4},
  "recipes": [{"id": "demo:process", "inputs": [{"item": "demo:ore"}],
               "outputs": [{"item": "demo:ingot"}], "duration": 40}],
  "visual": {"rotationFrame": "world", "geometry": "geometry.demo"}
}
```

这个例子只是合同，不代表主包替附属包实现电力网络。附属包可以把 `energyPerTick`
映射到自己的电压/电流系统，同时复用主包的机械动力、动画注册和依赖提示能力。

### `wacreate_api_catalog`

查询主包版本、API 版本、服务端/客户端系统和公共方法目录。可传入 `category`：

- `mechanical`
- `processing`
- `fluids`
- `client`

结果包含稳定级别、用途和必需参数，适合 AI 在生成代码前查询。

### `wacreate_asset_catalog`

查询 MCP 内置的精选开发贴图。资源按 `mechanical`、`fluid`、`icon` 和
`utility` 分类，包含基础传动杆、安山合金/黄铜机壳传动杆、齿轮、机壳、
齿轮箱、管道图集以及常用物品图标。返回的是 MCP 内部的逻辑资源 ID 和尺寸，
不会返回主包绝对路径。

### `wacreate_export_developer_assets`

把主包资源目录中已经列入白名单的贴图复制到 `tools/mcp_assets/`，作为 MCP
自带资源。这个工具只会复制目录中的精选 PNG，不会导出主包代码、模型或其它
未登记文件；默认也不会覆盖内容不同的已有 MCP 资源，更新时才传
`force=true`。

### `wacreate_install_developer_assets`

把 MCP 内置贴图安装到附属包：

- `output_dir` 是附属包根目录；若存在 `resource_pack_*`，写入第一个资源包，
  否则创建 `resource_pack_developer_assets`；
- `asset_ids` 是 `wacreate_asset_catalog` 返回的 ID 数组；省略时按
  `category` 安装整类，默认是 `mechanical`；
- `namespace` 默认是 `wacreate_dev`，所有地形/物品纹理注册都会使用这个命名空间；
- 同时生成 `mcp_developer_assets.json`，记录逻辑 ID、注册名和相对路径；
- 默认拒绝覆盖不同内容的目标贴图或纹理注册，只有明确传 `force=true` 才覆盖。

例如，给附属包安装传动杆和两种机壳传动杆：

```text
wacreate_install_developer_assets(
  output_dir="D:/addons/electric_age",
  asset_ids=["shaft", "andesite_encased_shaft", "brass_encased_shaft"],
  namespace="electric_age"
)
```

安装后可在模型或方块定义中引用 `electric_age:shaft`、
`electric_age:brass_encased_shaft` 等注册名。贴图是复制到附属包中的独立文件，
附属包运行时不需要读取主包的文件路径。

### `wacreate_missing_core_prompt`

输入附属包 ID和最低主包版本，返回：

- 玩家可见的中文缺失主包提示；
- `scripts/dependency_guard.py` 的完整内容；
- 推荐的启动顺序。

主包不存在时，主包不能替附属包弹出提示，因此这个 shim 必须复制到附属包中。生成的 shim 提供 `notify_missing_core(server_api, player_id)`：有玩家上下文时尝试使用 actionbar 提示，没有玩家上下文时回退到日志。它不会尝试绕过主包依赖。

### `wacreate_create_mechanical_template`

在指定目录创建一个机械附属包骨架。参数：

- `output_dir`：输出目录；
- `addon_id`：小写附属包 ID，例如 `electric_age`；
- `machine_id`：命名空间方块 ID，例如 `electric_age:generator`；
- `display_name`：显示名称；
- `force`：是否覆盖已有文件，默认 `false`。

生成内容：

```text
addon_manifest.json
scripts/__init__.py
scripts/dependency_guard.py
scripts/mechanical_extension.py
behavior_pack/README.md
resource_pack/README.md
README.md
```

模板注册一个机械组件规格，并预留动力源转速和应力容量 provider。它不会假装生成了完整的网易方块定义或模型；开发者仍需添加自己的行为包 JSON、模型、材质和附属包 server system。

### `wacreate_add_missing_core_prompt`

给已经存在的附属包补写 `scripts/dependency_guard.py`。默认不覆盖已有文件，必须显式传 `force=true` 才覆盖。

### `wacreate_validate_addon`

检查：

- `addon_manifest.json` 是否存在且可解析；
- `id`、`apiVersion` 和 `requires.wacreate` 是否有效；
- 是否存在缺失主包提示 shim；
- 是否误用 `wacreateServerSystem`、`wacreateClientSystem`、`system_facets` 或 `runtime_persistence` 等内部实现；
- 是否发现 Python 入口文件。

它是静态检查，不是网易运行时验证。通过不代表方块 JSON、模型、事件时序和性能已经在游戏内正确。

### `wacreate_validate_geometry`

读取一个模型 JSON，检查所有 cube 的严格 AABB 相交和所有面 UV 矩形的严格重叠。只把真正相交的盒体和真正有面积交集的 UV 判为问题；仅仅共面接触或 UV 边界相接不会误报。它适合在提交模型前运行。

### `wacreate_create_six_way_gearbox`

生成一个完整的六向齿轮箱试验附属包。它会：

- 调用 `omni` 公共机械连接模式；
- 生成六个正交轴端的行为包方块定义；
- 生成行为包配方；
- 生成 Netease 方块模型和实体模型；
- 复制主包原版 64×64 `Gearbox.png`，保持原版像素风格和 UV 布局；
- 生成资源包 `blocks.json`、地形纹理和物品纹理注册；
- 生成独立的 `Script_<addon_id>` 注册桥接；
- 自动运行几何盒体和 UV 重叠检查，并在返回值的 `geometry.strictOk` 中保留严格结果；

该工具要求目标目录已经有 `behavior_pack_*` 和 `resource_pack_*` 清单。它默认不覆盖已有文件；重新生成时必须显式传 `force=true`。生成的模型直接复用主包齿轮箱的分层外壳、四个水平轴和原版 UV，再增加上下两个带轴颈的竖直轴，共 11 个 cube、64 个面 UV 区域。主包原模型存在有意的盒体接缝和 UV 复用，因此 `strictOk` 可能为 `false`；这表示严格检查结果，不表示模型文件生成失败。返回值会标记 `visualReference: "original_gearbox"`，需要完全零交叠的附属包应另行制作独立 UV 和无交叠网格。

### `wacreate_add_mechanical_animations`

给已有的机械实体接入主包驱动的传动杆动画。这个工具属于本 MCP 的机械扩展流程，不需要读取主包闭源模型或脚本。它会：

- 从 `minecraft:client_entity` 的 `geometry.default` 找到实体模型；
- 默认把名称以 `axis` 或 `shaft` 开头的骨骼按 `north/south/east/west/up/down`（或 `n/s/e/w/u/d`）推断为旋转分组，沿用主包世界轴符号；需要局部镜像时通过 `groups.sign` 显式覆盖；
- 生成资源包动画，并把动画别名加入实体的 `scripts.animate`；
- 为每个传动分组生成主包可识别的角度变量；动力变化时立即跟随，停止时按 `bounce_ticks` 和 `bounce_degrees` 做短促回弹；
- 生成附属包客户端注册桥接，并自动补进唯一的 `@Mod.InitClient` / `@Mod.DestroyClient` 入口；桥接启动时注册，之后低频审计 `GetMechanicalVisualSpec`，主包客户端实例重建时会自动补注册。

主要参数：

- `output_dir`、`addon_id`、`machine_id`：已有附属包目录、Python 包 ID 和机械方块 ID；
- `groups`：可选的显式分组字典，例如 `{"front":{"bones":["axisNorth"],"axis":"z","sign":1}}`。当骨骼命名不规范、或要旋转父骨骼时必须提供；同一父子链不能重复驱动；
- `rotation_frame`：默认 `local`；六向对称齿轮箱使用 `world`。此模式要求方块移除 `netease:face_directional`、分组与父骨骼没有静态旋转、所有 `sign=1`。MCP 会拒绝混用原生朝向旋转和固定世界轴动画，避免换放置方向后轴反转。
- `bounce_ticks`：停转回弹时长，1–100 tick；`bounce_degrees`：回弹幅度，0–45 度；
- `dry_run` 默认 `true`，先只返回将要生成的文件、分组、冲突和动画规格；确认报告后传 `dry_run=false` 写入；已有内容不同必须再传 `force=true`。

示例：

```text
wacreate_add_mechanical_animations(
  output_dir="C:/MCStudioDownload/work/.../691024150b2f44d5badd979430b261fc",
  addon_id="six_way_gearbox",
  machine_id="six_way_gearbox:gearbox_6way",
  rotation_frame="world",
  bounce_ticks=10,
  bounce_degrees=4,
  dry_run=false,
  force=true
)
```

该工具依赖主包客户端新增的稳定方法 `RegisterMechanicalVisualSpec` 和 `GetMechanicalVisualSpec`。MCP 会生成静态文件并检查 JSON、Python AST 和写入冲突，但不会假称已经通过网易游戏内的动力网络、客户端资源加载或帧动画验证；这些仍需在实际客户端中测试。

## 推荐的 AI 工作流

1. 先调用 `wacreate_api_catalog`，确认 API 版本和稳定入口。
2. 调用 `wacreate_create_mechanical_template` 创建骨架。
3. 修改自己的 `addon_manifest.json` 和机械规格。
4. 添加自己的 server/client system、方块定义、模型和配方。
5. 用 `wacreate_asset_catalog` 选择所需贴图，再用
   `wacreate_install_developer_assets` 安装到自己的资源包。
6. 调用 `wacreate_validate_addon` 检查依赖和内部 API 引用。
7. 对机械实体调用 `wacreate_add_mechanical_animations`（先 `dry_run=true`，确认后再写入）。
8. 在网易运行时中测试传动、区块重载、客户端资源和异常路径。

AI 生成的代码不能直接视为已验证代码。尤其是机械源、应力、持久化和客户端实体必须通过实际游戏测试。

## 安全边界

该 MCP 不提供任意文件读取、任意命令执行、主包源码导出、模型导出或绕过依赖检查的工具。模板写入操作默认拒绝覆盖已有文件，防止误伤开发者项目。若要接入远程网站，网站端还应增加用户认证、目录隔离、文件大小限制和恶意脚本扫描。
