# 机械动力·蛙创studio 开发者生态仓库

这个仓库提供面向附属包开发者的 MCP 和公开 SDK。附属包依赖机械动力·蛙创studio 主包运行。

## 下载

- `mcp/wacreate-mcp.exe`：Windows 单文件 MCP，可直接由支持 stdio 的 MCP 客户端启动。
- GitHub Releases：下载带版本号的 EXE 和 SDK 压缩包。
- `sdk/`：公开 API 门面、示例、精选模型与开发贴图。

## MCP 配置

```json
{
  "mcpServers": {
    "wacreate-developer": {
      "command": "C:/MCP/wacreate-mcp.exe",
      "args": []
    }
  }
}
```

## 开放边界

仓库公开附属包开发所需的 API 合同、工具、示例和精选资源。机械网络、流体、物流、持久化、性能调度、完整机器逻辑、官方完整资源和独家算法继续由付费主包提供。

## 许可证

本仓库使用 `LICENSE-CN.md` 中的非商用社区条款草案。没有选择 MIT、BSD、GPL 等标准许可证，因为本项目明确限制商业再分发和独立运行。正式商业授权以项目所有者发布的版本为准。
