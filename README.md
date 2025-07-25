# Wuchang FMM Launcher

## [English](README.md) | [中文](README_CN.md)

![Banner](src/banner.jpg)

## 🎮 Overview

**Wuchang FMM Launcher** is a powerful support tool for Fluffy Mod Manager, designed specifically for the game "Wuchang: Fallen Feathers". It provides automatic PAK file monitoring, intelligent linking, and seamless mod management capabilities.

## ✨ Features

### 🔧 Core Functions
- **🎯 Automatic PAK Monitoring**: Real-time detection of new PAK files
- **🔗 Smart Linking**: Multiple linking methods (Hard Link, Symbolic Link, File Copy)
- **⚙️ Fluffy Mod Manager Integration**: Seamless integration with FMM
- **🌐 Multi-language Support**: Chinese and English interface
- **📁 Flexible Configuration**: Customizable target directories and settings

### 🛠️ Advanced Features
- **🚀 Auto-launch**: Automatically start Fluffy Mod Manager
- **📊 Link Management**: View and manage created mod links
- **🔄 Real-time Monitoring**: Live file system monitoring
- **💾 Configuration Persistence**: Settings saved to `%appdata%\WuchangFMMSupported`

## 📋 Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows 10/11
- **Dependencies**: 
  - `watchdog` - File system monitoring
  - `colorama` - Terminal color support

## 🚀 Quick Start

### Method 1: Manual Installation

```bash
# Create conda environment
conda create -n py313_env python=3.13 -y
conda activate py313_env

# Clone repository
git clone https://github.com/ArjunLee/Wuchang_FMM_Launcher.git
cd Wuchang_FMM_Launcher

# Install dependencies
pip install -r requirements.txt

# Run the application
python Wuchang_FMM_Launcher.py
```

### Method 2: Automatic Installation

1. **Clone** the latest release
2. **Run** `install_and_run.bat`
3. The script will automatically:
   - Check Python environment
   - Install required dependencies
   - Launch the application

## 📖 Usage Guide

### Initial Setup

1. **Launch** Run `Wuchang_FMM_Launcher.py`
2. **Configure** Fluffy Mod Manager path (Menu Option 1)

### Monitoring Mods

1. **Start Monitoring** (Menu Option 2)
2. **Press Ctrl+C** to stop monitoring

### Link Methods

| Method | Description | Pros | Cons |
|--------|-------------|------|------|
| **Hard Link** | Direct file system link | Best performance, no duplication | Same drive only |
| **Symbolic Link** | File system pointer | Cross-drive support | Requires admin rights |
| **File Copy** | Physical file copy | Maximum compatibility | Uses more disk space |
| **Smart Mode** | Auto-fallback | Automatic method selection | - |

## ⚙️ Configuration

### Settings Menu

Access via **Menu Option 5**:

- **🔧 Fluffy Mod Manager Path**: Set FMM executable location
- **🔗 Link Method**: Choose linking strategy
- **📁 Target Directory**: Set mod installation directory
- **🚀 Auto Start**: Configure FMM auto-launch
- **📊 View Configuration**: Display current settings

### Configuration File

Settings are stored in: `%appdata%\WuchangFMMSupported\pak_manager_config.json`

```json
{
    "language": "en",
    "modmanager_path": "C:\\Path\\To\\Modmanager.exe",
    "target_directory": "Project_Plague\\Content\\Paks\\~mods",
    "link_method": "hardlink",
    "auto_start_modmanager": true
}
```

## 🔧 Building from Source

### Prerequisites

```bash
pip install pyinstaller watchdog colorama
```

### Build Executable

```bash
# Using spec file (recommended)
pyinstaller Wuchang_FMM_Launcher.spec

# Or manual build
pyinstaller --collect-all watchdog --collect-all colorama Wuchang_FMM_Launcher.py \
  --name "Wuchang FMM Launcher" --onefile --icon=src/exec.png \
  --version-file=Wuchang_FMM_Launcher-version_info.txt --clean
```

## 🐛 Troubleshooting

### Common Issues

**Q: "No module named 'watchdog'" error**
- **A**: Install dependencies: `pip install watchdog colorama`

**Q: Links not created automatically**
- **A**: Check if monitoring is active and target directory exists

**Q: Permission denied errors**
- **A**: Run as administrator for symbolic links

**Q: Fluffy Mod Manager won't start**
- **A**: Verify the FMM path in settings

### Log Files

Monitoring logs are saved to: `%appdata%\WuchangFMMSupported\pak_monitor.log`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup

1. **Clone** the repository
2. **Install** dependencies: `pip install -r requirements.txt`
3. **Run** in development mode: `python Wuchang_FMM_Launcher.py`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Fluffy Mod Manager** team for the excellent modding tool
- **Wuchang: Fallen Feathers** community
- All contributors and testers

## 📞 Support

For support and questions:
- **Create an issue** on GitHub
- **Check** the troubleshooting section
- **Review** existing issues for solutions

---

**Note**: This is an unofficial modding tool and is not affiliated with Lingze Technology or any official development team. You should always backup your save files when using mods to prevent data loss.