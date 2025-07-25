# Wuchang FMM Launcher

## [中文](README_CN.md) | [English](README.md)

![Banner](src/banner.jpg)

## 🎮 项目简介

**明末：渊虚之羽 FMM 启动器** 是专为《明末：渊虚之羽》游戏设计的 Fluffy Mod Manager 支持工具。提供自动 PAK 文件监控、智能链接管理和无缝模组管理功能。

## ✨ 主要特性

### 🔧 核心功能
- **🎯 自动 PAK 监控**: 实时检测新增 PAK 文件
- **🔗 智能链接**: 多种链接方式（硬链接、符号链接、文件复制）
- **⚙️ FMM 集成**: 与 Fluffy Mod Manager 无缝集成
- **🌐 多语言支持**: 中英文界面切换
- **📁 灵活配置**: 可自定义目标目录和设置

### 🛠️ 高级功能
- **🚀 自动启动**: 自动启动 Fluffy Mod Manager
- **📊 链接管理**: 查看和管理已创建的模组链接
- **🔄 实时监控**: 实时文件系统监控
- **💾 配置持久化**: 设置保存到 `%appdata%\WuchangFMMSupported`

## 📋 系统要求

- **Python**: 3.7 或更高版本
- **操作系统**: Windows 10/11
- **依赖库**: 
  - `watchdog` - 文件系统监控
  - `colorama` - 终端颜色支持

## 🚀 快速开始

### 方法一：手动安装

```bash
# 使用 conda 创建环境
conda create -n py313_env python=3.13 -y
conda activate py313_env

# 克隆仓库
git clone https://github.com/ArjunLee/Wuchang_FMM_Launcher.git
cd Wuchang_FMM_Launcher

# 安装依赖
pip install -r requirements.txt

# 运行程序
python Wuchang_FMM_Launcher.py
```

### 方法二：自动安装

1. **克隆仓库** 最新版本
2. **运行** `install_and_run.bat`
3. 脚本将自动：
   - 检查 Python 环境
   - 安装所需依赖
   - 启动应用程序

## 📖 使用指南

### 初始设置

1. **启动** 运行 `Wuchang_FMM_Launcher.py`
2. **配置** Fluffy Mod Manager 路径（菜单选项 1）

### 监控模组

1. **开始监控**（菜单选项 2）
2. **按 Ctrl+C** 停止监控

### 链接方法说明

| 方法 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| **硬链接** | 直接文件系统链接 | 性能最佳，无重复占用 | 仅限同一驱动器 |
| **符号链接** | 文件系统指针 | 支持跨驱动器 | 需要管理员权限 |
| **文件复制** | 物理文件复制 | 兼容性最好 | 占用更多磁盘空间 |
| **智能模式** | 自动降级 | 自动选择方法 | - |

## ⚙️ 配置说明

### 设置菜单

通过 **菜单选项 5** 访问：

- **🔧 Fluffy Mod Manager 路径**: 设置 FMM 可执行文件位置
- **🔗 链接方法**: 选择链接策略
- **📁 目标目录**: 设置模组安装目录
- **🚀 自动启动**: 配置 FMM 自动启动
- **📊 查看配置**: 显示当前设置

### 配置文件

设置保存在：`%appdata%\WuchangFMMSupported\pak_manager_config.json`

```json
{
    "language": "zh_cn",
    "modmanager_path": "C:\\Path\\To\\Modmanager.exe",
    "target_directory": "Project_Plague\\Content\\Paks\\~mods",
    "link_method": "hardlink",
    "auto_start_modmanager": true
}
```

## 🔧 从源码构建

### 前置要求

```bash
pip install pyinstaller watchdog colorama
```

### 构建可执行文件

```bash
# 使用 spec 文件（推荐）
pyinstaller Wuchang_FMM_Launcher.spec

# 或手动构建
pyinstaller --collect-all watchdog --collect-all colorama Wuchang_FMM_Launcher.py \
  --name "Wuchang FMM Launcher" --onefile --icon=src/exec.png \
  --version-file=Wuchang_FMM_Launcher-version_info.txt --clean
```

## 🐛 故障排除

### 常见问题

**问：出现 "No module named 'watchdog'" 错误**
- **答**：安装依赖：`pip install watchdog colorama`

**问：链接未自动创建**
- **答**：检查监控是否激活，目标目录是否存在

**问：权限拒绝错误**
- **答**：使用符号链接时需要以管理员身份运行

**问：Fluffy Mod Manager 无法启动**
- **答**：检查设置中的 FMM 路径是否正确

### 日志文件

监控日志保存在：`%appdata%\WuchangFMMSupported\pak_monitor.log`

## 🤝 贡献

欢迎贡献！请随时提交问题和拉取请求。

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 📞 支持

如需支持和咨询：
- **在 GitHub 创建 issue**
- **查看** 故障排除部分
- **查阅** 现有 issue 寻找解决方案

---

**注意**：这是一个非官方的模组工具，它与灵泽科技或任何官方开发团队无关。你应该谨记使用时经常备份你的存档，以防止数据丢失。