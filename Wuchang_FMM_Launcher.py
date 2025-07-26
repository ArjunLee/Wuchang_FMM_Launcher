#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluffy Mod Manager 支持程序
自动监控并链接模组文件（PAK）到正确的游戏目录

Author: Arjun520
Version: 1.0.0
"""

import os
import sys
import json
import time
import shutil
import subprocess
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import Fore, Style, init
import configparser
from datetime import datetime
import hashlib
from common_operations import CommonOperations

# 初始化colorama
init()

# 定义emoji和颜色常量
EMOJI = {
    "LOGO": "🎮",
    "FILE": "📄",
    "LINK": "🔗",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "MONITOR": "👁️",
    "ARROW": "➜",
    "LANG": "🌐",
    "SETTINGS": "⚙️",
    "FOLDER": "📁",
    "ROCKET": "🚀",
    "STAR": "⭐",
    "GEAR": "⚙️",
    "MAGIC": "✨",
    "TARGET": "🎯"
}

class PAKManagerConfig:
    """配置管理类"""
    
    def __init__(self):
        # 设置配置文件目录到 %appdata%\WuchangFMMSupported
        self.config_dir = os.path.join(os.getenv('APPDATA'), 'WuchangFMMSupported')
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, "pak_manager_config.json")
        # 设置日志文件路径
        self.log_file = os.path.join(self.config_dir, "Wuchang_FMM_Launcher_monitor.log")
        self.config = self.load_config()
        self.translations = self.load_translations()
        self.current_language = self.config.get('language', 'zh_cn')
    
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "language": "zh_cn",
            "modmanager_path": "",
            "game_directory": os.getcwd(),
            "target_directory": "Project_Plague\\Content\\Paks\\~mods",
            "link_method": "hardlink",
            "auto_start_modmanager": True,
            "monitor_enabled": True,
            "log_level": "INFO"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置和用户配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} 配置文件加载失败，使用默认配置: {e}{Style.RESET_ALL}")
                return default_config
        else:
            return default_config
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 配置文件保存失败: {e}{Style.RESET_ALL}")
            return False
    
    def load_translations(self):
        """加载翻译文件"""
        translations = {
            "zh_cn": {
                "title": "Fluffy Mod Manager 支持程序",
                "version": "版本",
                "author": "作者: Arjun520",
                "menu": {
                    "title": "主菜单",
                    "setup_modmanager": "设置 Fluffy Mod Manager 路径",
                    "setup_modmanager_configured": "设置 Fluffy Mod Manager 目录",
                    "start_monitoring": "启动 FMM 并监控 Mod",
                    "stop_monitoring": "停止监控",
                    "view_links": "查看已创建的 Mod 链接",
                    "settings": "设置",
                    "common_operations": "常用操作",
                    "language": "切换语言",
                    "exit": "退出程序",
                    "invalid_choice": "无效选择，请重试"
                },
                "setup": {
                    "drag_drop_hint": "请拖放 Modmanager.exe 文件到此窗口，或输入完整路径:",
                    "path_saved": "Fluffy Mod Manager 路径已保存",
                    "path_invalid": "路径无效，请检查文件是否存在",
                    "auto_start": "是否自动启动 Fluffy Mod Manager? (y/n)"
                },
                "monitor": {
                    "starting": "正在启动 PAK 文件监控...",
                    "started": "PAK 文件监控已启动",
                    "stopped": "PAK 文件监控已停止",
                    "new_file_detected": "检测到新的 PAK 文件",
                    "link_created": "链接创建成功",
                    "link_failed": "链接创建失败",
                    "file_removed": "PAK 文件已删除，清理链接"
                },
                "link": {
                    "method_hardlink": "硬链接",
                    "method_symlink": "符号链接",
                    "method_copy": "文件复制",
                    "creating": "正在创建链接",
                    "success": "链接创建成功",
                    "failed": "链接创建失败",
                    "cleanup": "清理链接"
                },
                "settings": {
                    "title": "设置菜单",
                    "setup_path": "设置 Fluffy Mod Manager 路径",
                    "setup_method": "设置链接方法",
                    "setup_target": "设置目标目录",
                    "setup_autostart": "自动启动设置",
                    "view_config": "查看当前配置",
                    "return_menu": "返回主菜单",
                    "invalid_choice": "无效选择，请重试",
                    "continue_prompt": "按回车键继续...",
                    "choose_method": "选择链接方法",
                    "hardlink_desc": "硬链接 (推荐，性能最佳)",
                    "symlink_desc": "符号链接 (需要管理员权限)",
                    "copy_desc": "文件复制 (兼容性最好)",
                    "smart_desc": "智能模式 (自动降级)",
                    "choose_prompt": "请选择 (1-4):",
                    "method_set": "链接方法已设置为:",
                    "target_title": "设置目标目录",
                    "current_target": "当前目标目录:",
                    "target_hint": "相对于游戏根目录的路径，例如: Project_Plague\\Content\\Paks\\~mods",
                    "target_prompt": "输入新的目标目录 (留空保持不变):",
                    "target_updated": "目标目录已更新:",
                    "autostart_title": "自动启动 Fluffy Mod Manager 设置",
                    "current_setting": "当前设置:",
                    "enabled": "启用",
                    "disabled": "禁用",
                    "autostart_prompt": "是否启用自动启动? (y/n):",
                    "autostart_enabled": "自动启动已启用",
                    "autostart_disabled": "自动启动已禁用",
                    "setting_unchanged": "设置未更改"
                },
                "config": {
                    "title": "当前配置",
                    "language": "语言:",
                    "fmm_path": "Fluffy Mod Manager路径:",
                    "game_dir": "游戏目录:",
                    "target_dir": "目标目录:",
                    "link_method": "链接方法:",
                    "auto_start": "自动启动:",
                    "monitor_status": "监控状态:",
                    "not_set": "未设置",
                    "yes": "是",
                    "no": "否",
                    "running": "运行中",
                    "stopped": "已停止"
                },
                "language": {
                    "title": "选择语言 / Select Language",
                    "chinese": "中文 (简体)",
                    "english": "English",
                    "prompt": "请选择 / Please choose (1-2):",
                    "switched_cn": "语言已切换为中文",
                    "invalid": "无效选择 / Invalid choice"
                },
                "general": {
                    "choose_prompt": "请选择:",
                    "continue_prompt": "按回车键继续...",
                    "return_menu": "已返回主菜单",
                    "exit_thanks": "感谢使用！",
                    "program_exit": "程序已退出",
                    "program_error": "程序运行出错:",
                    "press_enter": "按回车键退出...",
                    "monitoring_running": "监控已在运行中",
                    "monitor_dir": "监控目录:",
                    "target_dir": "目标目录:",
                    "ctrl_c_hint": "按 Ctrl+C 返回主菜单",
                    "found_files": "发现 {count} 个现有PAK文件，正在处理...",
                    "fmm_started": "Fluffy Mod Manager 已启动",
                    "fmm_start_failed": "启动 Fluffy Mod Manager 失败:",
                    "fmm_not_configured": "Fluffy Mod Manager 路径未配置或文件不存在",
                    "cleanup_failed": "清理链接失败:",
                    "no_links": "暂无已创建的链接",
                    "link_status": "已创建的PAK文件链接",
                    "method": "方法:",
                    "time": "时间:",
                    "target": "目标:",
                    "unknown": "未知",
                    "setup_path_first": "请先设置 Fluffy Mod Manager 的路径",
                    "file_access_retry": "文件访问重试中...",
                    "permission_warning": "权限不足，但操作可能已成功"
                }
            },
            "en": {
                "title": "Fluffy Mod Manager Supported Programs",
                "version": "Version",
                "author": "Author: Arjun520",
                "menu": {
                    "title": "Main Menu",
                    "setup_modmanager": "Setup Fluffy Mod Manager Path",
                    "setup_modmanager_configured": "Setup Fluffy Mod Manager Directory",
                    "start_monitoring": "Launch FMM and Monitor Mods",
                    "stop_monitoring": "Stop Monitoring",
                    "view_links": "View Created Mod Links",
                    "settings": "Settings",
                    "common_operations": "Common Operations",
                    "language": "Switch Language",
                    "exit": "Exit",
                    "invalid_choice": "Invalid choice, please try again"
                },
                "setup": {
                    "drag_drop_hint": "Please drag and drop Modmanager.exe file to this window, or enter full path:",
                    "path_saved": "Fluffy Mod Manager path saved",
                    "path_invalid": "Invalid path, please check if file exists",
                    "auto_start": "Auto start Fluffy Mod Manager? (y/n)"
                },
                "monitor": {
                    "starting": "Starting PAK file monitoring...",
                    "started": "PAK file monitoring started",
                    "stopped": "PAK file monitoring stopped",
                    "new_file_detected": "New PAK file detected",
                    "link_created": "Link created successfully",
                    "link_failed": "Link creation failed",
                    "file_removed": "PAK file removed, cleaning up link"
                },
                "link": {
                    "method_hardlink": "Hard Link",
                    "method_symlink": "Symbolic Link",
                    "method_copy": "File Copy",
                    "creating": "Creating link",
                    "success": "Link created successfully",
                    "failed": "Link creation failed",
                    "cleanup": "Cleaning up link"
                },
                "settings": {
                    "title": "Settings Menu",
                    "setup_path": "Setup Fluffy Mod Manager Path",
                    "setup_method": "Setup Link Method",
                    "setup_target": "Setup Target Directory",
                    "setup_autostart": "Auto Start Settings",
                    "view_config": "View Current Configuration",
                    "return_menu": "Return to Main Menu",
                    "invalid_choice": "Invalid choice, please try again",
                    "continue_prompt": "Press Enter to continue...",
                    "choose_method": "Choose Link Method",
                    "hardlink_desc": "Hard Link (Recommended, Best Performance)",
                    "symlink_desc": "Symbolic Link (Requires Admin Rights)",
                    "copy_desc": "File Copy (Best Compatibility)",
                    "smart_desc": "Smart Mode (Auto Fallback)",
                    "choose_prompt": "Please choose (1-4):",
                    "method_set": "Link method set to:",
                    "target_title": "Setup Target Directory",
                    "current_target": "Current target directory:",
                    "target_hint": "Path relative to game root directory, e.g.: Project_Plague\\Content\\Paks\\~mods",
                    "target_prompt": "Enter new target directory (leave empty to keep current):",
                    "target_updated": "Target directory updated:",
                    "autostart_title": "Auto Start Fluffy Mod Manager Settings",
                    "current_setting": "Current setting:",
                    "enabled": "Enabled",
                    "disabled": "Disabled",
                    "autostart_prompt": "Enable auto start? (y/n):",
                    "autostart_enabled": "Auto start enabled",
                    "autostart_disabled": "Auto start disabled",
                    "setting_unchanged": "Setting unchanged"
                },
                "config": {
                    "title": "Current Configuration",
                    "language": "Language:",
                    "fmm_path": "Fluffy Mod Manager Path:",
                    "game_dir": "Game Directory:",
                    "target_dir": "Target Directory:",
                    "link_method": "Link Method:",
                    "auto_start": "Auto Start:",
                    "monitor_status": "Monitor Status:",
                    "not_set": "Not Set",
                    "yes": "Yes",
                    "no": "No",
                    "running": "Running",
                    "stopped": "Stopped"
                },
                "language": {
                    "title": "选择语言 / Select Language",
                    "chinese": "中文 (简体)",
                    "english": "English",
                    "prompt": "请选择 / Please choose (1-2):",
                    "switched_en": "Language switched to English",
                    "invalid": "无效选择 / Invalid choice"
                },
                "general": {
                    "choose_prompt": "Please choose:",
                    "continue_prompt": "Press Enter to continue...",
                    "return_menu": "Returned to main menu",
                    "exit_thanks": "Thank you for using it!",
                    "program_exit": "Program exited",
                    "program_error": "Program error:",
                    "press_enter": "Press Enter to exit...",
                    "monitoring_running": "Monitoring is already running",
                    "monitor_dir": "Monitor Directory:",
                    "target_dir": "Target Directory:",
                    "ctrl_c_hint": "Press Ctrl+C to return to main menu",
                    "found_files": "Found {count} existing PAK files, processing...",
                    "fmm_started": "Fluffy Mod Manager started",
                    "fmm_start_failed": "Failed to start Fluffy Mod Manager:",
                    "fmm_not_configured": "Fluffy Mod Manager path not configured or file does not exist",
                    "cleanup_failed": "Failed to cleanup link:",
                    "no_links": "No links created yet",
                    "link_status": "Created PAK File Links",
                    "method": "Method:",
                    "time": "Time:",
                    "target": "Target:",
                    "unknown": "Unknown",
                    "setup_path_first": "Please setup Fluffy Mod Manager path first",
                    "file_access_retry": "Retrying file access...",
                    "permission_warning": "Insufficient permissions, but operation may have succeeded"
                }
            }
        }
        return translations
    
    def get_text(self, key, **kwargs):
        """获取翻译文本"""
        try:
            keys = key.split('.')
            value = self.translations.get(self.current_language, {})
            for k in keys:
                value = value.get(k, key)
            return value.format(**kwargs) if kwargs else value
        except:
            return key
    
    def set_language(self, lang):
        """设置语言"""
        if lang in self.translations:
            self.current_language = lang
            self.config['language'] = lang
            self.save_config()
            return True
        return False

class PAKLogo:
    """Logo显示类"""
    
    @staticmethod
    def get_logo():
        """获取ASCII艺术字Logo"""
        logo = f"""{Fore.CYAN}
╔════════════════════════════════════════════════════════════════╗

  ██╗    ██╗██╗   ██╗ ██████╗██╗  ██╗ █████╗ ███╗   ██╗ ██████╗                   
  ██║    ██║██║   ██║██╔════╝██║  ██║██╔══██╗████╗  ██║██╔════╝ 
  ██║ █╗ ██║██║   ██║██║     ███████║███████║██╔██╗ ██║██║  ███╗ 
  ██║███╗██║██║   ██║██║     ██╔══██║██╔══██║██║╚██╗██║██║   ██║ 
  ╚███╔███╔╝╚██████╔╝╚██████╗██║  ██║██║  ██║██║ ╚████║╚██████╔╝ 
   ╚══╝╚══╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝                   
                                                                                               
                {Fore.YELLOW}🎮  FMM Supported v1.0.0 🎮{Fore.CYAN}
                                                                        
╚════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
        return logo
    
    @staticmethod
    def print_logo(config):
        """打印Logo和描述信息"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(PAKLogo.get_logo())
        print(f"{Fore.GREEN}{EMOJI['STAR']} {config.get_text('title')}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{EMOJI['INFO']} {config.get_text('version')}: 1.0.0{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{EMOJI['INFO']} {config.get_text('author')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 86}{Style.RESET_ALL}")

class PAKFileHandler(FileSystemEventHandler):
    """PAK文件事件处理器"""
    
    def __init__(self, pak_manager):
        self.pak_manager = pak_manager
        self.config = pak_manager.config
    
    def on_created(self, event):
        """文件创建事件"""
        if not event.is_directory and event.src_path.lower().endswith('.pak'):
            # 等待文件写入完成，增加重试机制
            max_retries = 5
            for i in range(max_retries):
                time.sleep(0.5)  # 减少单次等待时间但增加重试次数
                if os.path.exists(event.src_path):
                    try:
                        # 尝试打开文件确保写入完成
                        with open(event.src_path, 'rb') as f:
                            f.read(1)  # 读取一个字节测试文件是否可访问
                        break
                    except (PermissionError, OSError):
                        if i == max_retries - 1:
                            return  # 最后一次重试失败则放弃
                        continue
                else:
                    if i == max_retries - 1:
                        return  # 文件不存在则放弃
            
            print(f"\n{Fore.GREEN}{EMOJI['INFO']} {self.config.get_text('monitor.new_file_detected')}: {os.path.basename(event.src_path)}{Style.RESET_ALL}")
            self.pak_manager.create_pak_link(event.src_path)
    
    def on_deleted(self, event):
        """文件删除事件"""
        if not event.is_directory and event.src_path.lower().endswith('.pak'):
            print(f"\n{Fore.YELLOW}{EMOJI['WARNING']} {self.config.get_text('monitor.file_removed')}: {os.path.basename(event.src_path)}{Style.RESET_ALL}")
            self.pak_manager.cleanup_pak_link(event.src_path)

class PAKManager:
    """PAK文件管理器主类"""
    
    def __init__(self):
        self.config = PAKManagerConfig()
        self.observer = None
        self.monitoring = False
        # 设置链接注册表文件到配置目录
        self.link_registry_file = os.path.join(self.config.config_dir, "pak_links_registry.json")
        self.link_registry = self.load_link_registry()
        self.common_ops = CommonOperations(self.config)
        
        # 确保目标目录存在
        self.ensure_target_directory()
    
    def load_link_registry(self):
        """加载链接注册表"""
        if os.path.exists(self.link_registry_file):
            try:
                with open(self.link_registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_link_registry(self):
        """保存链接注册表"""
        try:
            with open(self.link_registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.link_registry, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 链接注册表保存失败: {e}{Style.RESET_ALL}")
    
    def ensure_target_directory(self):
        """确保目标目录存在"""
        target_dir = os.path.join(self.config.config['game_directory'], self.config.config['target_directory'])
        try:
            os.makedirs(target_dir, exist_ok=True)
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 目标目录已准备: {target_dir}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 无法创建目标目录: {e}{Style.RESET_ALL}")
    
    def create_pak_link(self, source_path):
        """创建PAK文件链接"""
        filename = os.path.basename(source_path)
        target_dir = os.path.join(self.config.config['game_directory'], self.config.config['target_directory'])
        target_path = os.path.join(target_dir, filename)
        
        print(f"{Fore.CYAN}{EMOJI['LINK']} {self.config.get_text('link.creating')}: {filename}{Style.RESET_ALL}")
        
        # 如果目标文件已存在，先删除
        if os.path.exists(target_path):
            max_retries = 3
            deleted = False
            for i in range(max_retries):
                try:
                    os.remove(target_path)
                    deleted = True
                    break
                except PermissionError as e:
                    if i == max_retries - 1:
                        print(f"{Fore.YELLOW}{EMOJI['WARNING']} 无法删除现有文件（权限不足），尝试继续创建链接: {e}{Style.RESET_ALL}")
                    else:
                        time.sleep(0.5)
                        continue
                except Exception as e:
                    if i == max_retries - 1:
                        print(f"{Fore.RED}{EMOJI['ERROR']} 无法删除现有文件: {e}{Style.RESET_ALL}")
                        return False
                    else:
                        time.sleep(0.5)
                        continue
        
        # 尝试创建链接
        link_method = self.config.config['link_method']
        success = False
        actual_method = ""
        
        if link_method == "hardlink":
            success, actual_method = self._try_hardlink(source_path, target_path)
        elif link_method == "symlink":
            success, actual_method = self._try_symlink(source_path, target_path)
        elif link_method == "copy":
            success, actual_method = self._try_copy(source_path, target_path)
        else:
            # 智能降级策略
            success, actual_method = self._try_smart_link(source_path, target_path)
        
        if success:
            # 记录链接信息
            self.link_registry[source_path] = {
                "target": target_path,
                "method": actual_method,
                "created_time": datetime.now().isoformat(),
                "file_hash": self._get_file_hash(source_path)
            }
            self.save_link_registry()
            
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('link.success')}: {filename} ({actual_method}){Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.config.get_text('link.failed')}: {filename}{Style.RESET_ALL}")
            return False
    
    def _try_hardlink(self, source, target):
        """尝试创建硬链接"""
        try:
            os.link(source, target)
            return True, self.config.get_text('link.method_hardlink')
        except (OSError, PermissionError):
            return False, ""
    
    def _try_symlink(self, source, target):
        """尝试创建符号链接"""
        try:
            os.symlink(source, target)
            return True, self.config.get_text('link.method_symlink')
        except (OSError, PermissionError):
            return False, ""
    
    def _try_copy(self, source, target):
        """尝试复制文件"""
        try:
            shutil.copy2(source, target)
            return True, self.config.get_text('link.method_copy')
        except Exception:
            return False, ""
    
    def _try_smart_link(self, source, target):
        """智能链接策略（硬链接 -> 符号链接 -> 复制）"""
        # 尝试硬链接
        success, method = self._try_hardlink(source, target)
        if success:
            return success, method
        
        # 尝试符号链接
        success, method = self._try_symlink(source, target)
        if success:
            return success, method
        
        # 最后尝试复制
        return self._try_copy(source, target)
    
    def _get_file_hash(self, filepath):
        """获取文件哈希值"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def cleanup_pak_link(self, source_path):
        """清理PAK文件链接"""
        if source_path in self.link_registry:
            target_path = self.link_registry[source_path]['target']
            try:
                if os.path.exists(target_path):
                    # 增加重试机制处理文件被占用的情况
                    max_retries = 3
                    for i in range(max_retries):
                        try:
                            os.remove(target_path)
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('link.cleanup')}: {os.path.basename(target_path)}{Style.RESET_ALL}")
                            break
                        except PermissionError as e:
                            if i == max_retries - 1:
                                # 最后一次重试失败，但不阻止注册表清理
                                print(f"{Fore.YELLOW}{EMOJI['WARNING']} 无法删除目标文件（权限不足），但已清理注册表: {os.path.basename(target_path)}{Style.RESET_ALL}")
                            else:
                                time.sleep(0.5)  # 等待后重试
                                continue
                        except Exception as e:
                            if i == max_retries - 1:
                                print(f"{Fore.RED}{EMOJI['ERROR']} {self.config.get_text('general.cleanup_failed')} {e}{Style.RESET_ALL}")
                            else:
                                time.sleep(0.5)
                                continue
                
                # 无论文件删除是否成功，都清理注册表记录
                del self.link_registry[source_path]
                self.save_link_registry()
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.config.get_text('general.cleanup_failed')} {e}{Style.RESET_ALL}")
    
    def start_monitoring(self):
        """开始监控PAK文件"""
        # 检查是否已设置Fluffy Mod Manager路径
        modmanager_path = self.config.config.get('modmanager_path', '')
        if not modmanager_path or not os.path.exists(modmanager_path):
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.config.get_text('general.setup_path_first')}{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}{self.config.get_text('general.continue_prompt')}{Style.RESET_ALL}")
            return
        
        if self.monitoring:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.config.get_text('general.monitoring_running')}{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}{EMOJI['MONITOR']} {self.config.get_text('monitor.starting')}{Style.RESET_ALL}")
        
        # 启动Modmanager.exe（如果配置了）
        if self.config.config.get('auto_start_modmanager') and self.config.config.get('modmanager_path'):
            self.start_modmanager()
        
        # 扫描现有PAK文件
        self.scan_existing_pak_files()
        
        # 启动文件监控
        self.observer = Observer()
        event_handler = PAKFileHandler(self)
        self.observer.schedule(event_handler, self.config.config['game_directory'], recursive=False)
        self.observer.start()
        self.monitoring = True
        
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('monitor.started')}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{EMOJI['INFO']} {self.config.get_text('general.monitor_dir')} {self.config.config['game_directory']}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{EMOJI['INFO']} {self.config.get_text('general.target_dir')} {os.path.join(self.config.config['game_directory'], self.config.config['target_directory'])}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.config.get_text('general.ctrl_c_hint')}{Style.RESET_ALL}")
    
    def stop_monitoring(self):
        """停止监控PAK文件"""
        if self.observer and self.monitoring:
            self.observer.stop()
            self.observer.join()
            self.monitoring = False
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('monitor.stopped')}{Style.RESET_ALL}")
    
    def scan_existing_pak_files(self):
        """扫描现有的PAK文件"""
        game_dir = self.config.config['game_directory']
        pak_files = [f for f in os.listdir(game_dir) if f.lower().endswith('.pak') and os.path.isfile(os.path.join(game_dir, f))]
        
        if pak_files:
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.config.get_text('general.found_files', count=len(pak_files))}{Style.RESET_ALL}")
            for pak_file in pak_files:
                source_path = os.path.join(game_dir, pak_file)
                if source_path not in self.link_registry:
                    self.create_pak_link(source_path)
    
    def start_modmanager(self):
        """启动Modmanager.exe"""
        modmanager_path = self.config.config.get('modmanager_path')
        if modmanager_path and os.path.exists(modmanager_path):
            try:
                subprocess.Popen([modmanager_path], cwd=os.path.dirname(modmanager_path))
                print(f"{Fore.GREEN}{EMOJI['ROCKET']} {self.config.get_text('general.fmm_started')}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.config.get_text('general.fmm_start_failed')} {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.config.get_text('general.fmm_not_configured')}{Style.RESET_ALL}")
    
    def setup_modmanager_path(self):
        """设置Fluffy Mod Manager路径"""
        print(f"\n{Fore.CYAN}{EMOJI['SETTINGS']} 设置 Fluffy Mod Manager 路径{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.config.get_text('setup.drag_drop_hint')}{Style.RESET_ALL}")
        
        path = input(f"{Fore.GREEN}{EMOJI['ARROW']} ").strip().strip('"')
        
        if path and os.path.exists(path) and path.lower().endswith('.exe'):
            self.config.config['modmanager_path'] = path
            self.config.save_config()
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('setup.path_saved')}: {path}{Style.RESET_ALL}")
            
            # 询问是否自动启动
            auto_start = input(f"{Fore.YELLOW}{self.config.get_text('setup.auto_start')} ").strip().lower()
            self.config.config['auto_start_modmanager'] = auto_start in ['y', 'yes', '是', 'true']
            self.config.save_config()
            
            return True
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.config.get_text('setup.path_invalid')}{Style.RESET_ALL}")
            return False
    
    def view_links(self):
        """查看已创建的链接"""
        print(f"\n{Fore.CYAN}{EMOJI['LINK']} {self.config.get_text('general.link_status')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}")
        
        if not self.link_registry:
            print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.config.get_text('general.no_links')}{Style.RESET_ALL}")
            return
        
        unknown_text = self.config.get_text('general.unknown')
        for i, (source, info) in enumerate(self.link_registry.items(), 1):
            filename = os.path.basename(source)
            method = info.get('method', unknown_text)
            created_time = info.get('created_time', unknown_text)
            target_exists = os.path.exists(info['target'])
            status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if target_exists else f"{Fore.RED}✗{Style.RESET_ALL}"
            
            print(f"{Fore.BLUE}{i:2d}.{Style.RESET_ALL} {status} {filename}")
            print(f"     {Fore.CYAN}{self.config.get_text('general.method')}{Style.RESET_ALL} {method}")
            print(f"     {Fore.CYAN}{self.config.get_text('general.time')}{Style.RESET_ALL} {created_time[:19] if created_time != unknown_text else created_time}")
            print(f"     {Fore.CYAN}{self.config.get_text('general.target')}{Style.RESET_ALL} {info['target']}")
            print()
    
    def show_settings(self):
        """显示设置菜单"""
        while True:
            PAKLogo.print_logo(self.config)
            print(f"\n{Fore.CYAN}{EMOJI['SETTINGS']} {self.config.get_text('settings.title')}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}1.{Style.RESET_ALL} {self.config.get_text('settings.setup_path')}")
            print(f"{Fore.GREEN}2.{Style.RESET_ALL} {self.config.get_text('settings.setup_method')}")
            print(f"{Fore.GREEN}3.{Style.RESET_ALL} {self.config.get_text('settings.setup_target')}")
            print(f"{Fore.GREEN}4.{Style.RESET_ALL} {self.config.get_text('settings.setup_autostart')}")
            print(f"{Fore.GREEN}5.{Style.RESET_ALL} {self.config.get_text('settings.view_config')}")
            print(f"{Fore.GREEN}0.{Style.RESET_ALL} {self.config.get_text('settings.return_menu')}")
            
            choice = input(f"\n{Fore.GREEN}{EMOJI['ARROW']} {self.config.get_text('general.choose_prompt')} ").strip()
            
            if choice == '1':
                self.setup_modmanager_path()
                input(f"\n{Fore.YELLOW}{self.config.get_text('settings.continue_prompt')}{Style.RESET_ALL}")
            elif choice == '2':
                self.setup_link_method()
                input(f"\n{Fore.YELLOW}{self.config.get_text('settings.continue_prompt')}{Style.RESET_ALL}")
            elif choice == '3':
                self.setup_target_directory()
                input(f"\n{Fore.YELLOW}{self.config.get_text('settings.continue_prompt')}{Style.RESET_ALL}")
            elif choice == '4':
                self.setup_auto_start()
                input(f"\n{Fore.YELLOW}{self.config.get_text('settings.continue_prompt')}{Style.RESET_ALL}")
            elif choice == '5':
                self.show_current_config()
                input(f"\n{Fore.YELLOW}{self.config.get_text('settings.continue_prompt')}{Style.RESET_ALL}")
            elif choice == '0':
                break
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.config.get_text('settings.invalid_choice')}{Style.RESET_ALL}")
                time.sleep(1)
    
    def setup_link_method(self):
        """设置链接方法"""
        print(f"\n{Fore.CYAN}{EMOJI['LINK']} {self.config.get_text('settings.choose_method')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1.{Style.RESET_ALL} {self.config.get_text('settings.hardlink_desc')}")
        print(f"{Fore.GREEN}2.{Style.RESET_ALL} {self.config.get_text('settings.symlink_desc')}")
        print(f"{Fore.GREEN}3.{Style.RESET_ALL} {self.config.get_text('settings.copy_desc')}")
        print(f"{Fore.GREEN}4.{Style.RESET_ALL} {self.config.get_text('settings.smart_desc')}")
        
        choice = input(f"\n{Fore.GREEN}{EMOJI['ARROW']} {self.config.get_text('settings.choose_prompt')} ").strip()
        
        methods = {
            '1': 'hardlink',
            '2': 'symlink', 
            '3': 'copy',
            '4': 'smart'
        }
        
        if choice in methods:
            self.config.config['link_method'] = methods[choice]
            self.config.save_config()
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('settings.method_set')} {methods[choice]}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.config.get_text('settings.invalid_choice')}{Style.RESET_ALL}")
    
    def setup_target_directory(self):
        """设置目标目录"""
        print(f"\n{Fore.CYAN}{EMOJI['FOLDER']} {self.config.get_text('settings.target_title')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.config.get_text('settings.current_target')} {self.config.config['target_directory']}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{self.config.get_text('settings.target_hint')}{Style.RESET_ALL}")
        
        new_dir = input(f"{Fore.GREEN}{EMOJI['ARROW']} {self.config.get_text('settings.target_prompt')} ").strip()
        
        if new_dir:
            self.config.config['target_directory'] = new_dir
            self.config.save_config()
            self.ensure_target_directory()
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('settings.target_updated')} {new_dir}{Style.RESET_ALL}")
    
    def setup_auto_start(self):
        """设置自动启动"""
        current = self.config.config.get('auto_start_modmanager', True)
        status_text = self.config.get_text('settings.enabled') if current else self.config.get_text('settings.disabled')
        print(f"\n{Fore.CYAN}{EMOJI['ROCKET']} {self.config.get_text('settings.autostart_title')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.config.get_text('settings.current_setting')} {status_text}{Style.RESET_ALL}")
        
        choice = input(f"{Fore.GREEN}{EMOJI['ARROW']} {self.config.get_text('settings.autostart_prompt')} ").strip().lower()
        
        if choice in ['y', 'yes', '是']:
            self.config.config['auto_start_modmanager'] = True
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('settings.autostart_enabled')}{Style.RESET_ALL}")
        elif choice in ['n', 'no', '否']:
            self.config.config['auto_start_modmanager'] = False
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('settings.autostart_disabled')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.config.get_text('settings.setting_unchanged')}{Style.RESET_ALL}")
            return
        
        self.config.save_config()
    
    def show_current_config(self):
        """显示当前配置"""
        print(f"\n{Fore.CYAN}{EMOJI['INFO']} {self.config.get_text('config.title')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 60}{Style.RESET_ALL}")
        
        config = self.config.config
        not_set = self.config.get_text('config.not_set')
        yes_text = self.config.get_text('config.yes')
        no_text = self.config.get_text('config.no')
        running_text = self.config.get_text('config.running')
        stopped_text = self.config.get_text('config.stopped')
        
        print(f"{Fore.BLUE}{self.config.get_text('config.language')}{Style.RESET_ALL} {config.get('language', not_set)}")
        print(f"{Fore.BLUE}{self.config.get_text('config.fmm_path')}{Style.RESET_ALL} {config.get('modmanager_path', not_set)}")
        print(f"{Fore.BLUE}{self.config.get_text('config.game_dir')}{Style.RESET_ALL} {config.get('game_directory', not_set)}")
        print(f"{Fore.BLUE}{self.config.get_text('config.target_dir')}{Style.RESET_ALL} {config.get('target_directory', not_set)}")
        print(f"{Fore.BLUE}{self.config.get_text('config.link_method')}{Style.RESET_ALL} {config.get('link_method', not_set)}")
        print(f"{Fore.BLUE}{self.config.get_text('config.auto_start')}{Style.RESET_ALL} {yes_text if config.get('auto_start_modmanager', False) else no_text}")
        print(f"{Fore.BLUE}{self.config.get_text('config.monitor_status')}{Style.RESET_ALL} {running_text if self.monitoring else stopped_text}")
    
    def show_common_operations(self):
        """显示常用操作菜单"""
        self.common_ops.show_menu(self.config.current_language)
    
    def switch_language(self):
        """切换语言"""
        print(f"\n{Fore.CYAN}{EMOJI['LANG']} {self.config.get_text('language.title')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1.{Style.RESET_ALL} {self.config.get_text('language.chinese')}")
        print(f"{Fore.GREEN}2.{Style.RESET_ALL} {self.config.get_text('language.english')}")
        
        choice = input(f"\n{Fore.GREEN}{EMOJI['ARROW']} {self.config.get_text('language.prompt')} ").strip()
        
        if choice == '1':
            self.config.set_language('zh_cn')
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('language.switched_cn')}{Style.RESET_ALL}")
        elif choice == '2':
            self.config.set_language('en')
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('language.switched_en')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.config.get_text('language.invalid')}{Style.RESET_ALL}")
    
    def show_main_menu(self):
        """显示主菜单"""
        while True:
            PAKLogo.print_logo(self.config)
            
            print(f"\n{Fore.CYAN}{EMOJI['GEAR']} {self.config.get_text('menu.title')}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'─' * 60}{Style.RESET_ALL}")
            
            # 动态显示菜单1，根据是否已配置路径显示不同文案和颜色
            modmanager_path = self.config.config.get('modmanager_path', '')
            if modmanager_path and os.path.exists(modmanager_path):
                # 已配置状态
                status_text = "已设置" if self.config.current_language == 'zh_cn' else "Set"
                menu1_text = f"{self.config.get_text('menu.setup_modmanager')} (✅ {status_text})"
                menu1_color = Style.RESET_ALL
            else:
                # 未配置状态
                status_text = "未设置" if self.config.current_language == 'zh_cn' else "Not Set"
                menu1_text = f"{self.config.get_text('menu.setup_modmanager')} (❌ {status_text})"
                menu1_color = Style.RESET_ALL
            
            print(f"{Fore.GREEN}1.{Style.RESET_ALL} {EMOJI['SETTINGS']} {menu1_color}{menu1_text}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}2.{Style.RESET_ALL} {EMOJI['MONITOR']} {self.config.get_text('menu.start_monitoring')}")
            print(f"{Fore.GREEN}3.{Style.RESET_ALL} {EMOJI['WARNING']} {self.config.get_text('menu.stop_monitoring')}")
            print(f"{Fore.GREEN}4.{Style.RESET_ALL} {EMOJI['LINK']} {self.config.get_text('menu.view_links')}")
            print(f"{Fore.GREEN}5.{Style.RESET_ALL} {EMOJI['SETTINGS']} {self.config.get_text('menu.settings')}")
            print(f"{Fore.GREEN}6.{Style.RESET_ALL} {EMOJI['FOLDER']} {self.config.get_text('menu.common_operations')}")
            print(f"{Fore.GREEN}7.{Style.RESET_ALL} {EMOJI['LANG']} {self.config.get_text('menu.language')}")
            print(f"{Fore.GREEN}0.{Style.RESET_ALL} {EMOJI['ERROR']} {self.config.get_text('menu.exit')}")
            
            choice = input(f"\n{Fore.GREEN}{EMOJI['ARROW']} {self.config.get_text('general.choose_prompt')} ").strip()
            
            if choice == '1':
                self.setup_modmanager_path()
                input(f"\n{Fore.YELLOW}{self.config.get_text('general.continue_prompt')}{Style.RESET_ALL}")
            elif choice == '2':
                try:
                    self.start_monitoring()
                    # 保持监控运行，直到用户按Ctrl+C
                    while self.monitoring:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.stop_monitoring()
                    print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {self.config.get_text('general.return_menu')}{Style.RESET_ALL}")
                    input(f"{self.config.get_text('general.continue_prompt')}")
            elif choice == '3':
                self.stop_monitoring()
                input(f"\n{Fore.YELLOW}{self.config.get_text('general.continue_prompt')}{Style.RESET_ALL}")
            elif choice == '4':
                self.view_links()
                input(f"\n{Fore.YELLOW}{self.config.get_text('general.continue_prompt')}{Style.RESET_ALL}")
            elif choice == '5':
                self.show_settings()
            elif choice == '6':
                self.show_common_operations()
            elif choice == '7':
                self.switch_language()
                input(f"\n{Fore.YELLOW}{self.config.get_text('general.continue_prompt')}{Style.RESET_ALL}")
            elif choice == '0':
                self.stop_monitoring()
                print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} {self.config.get_text('general.exit_thanks')}{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.config.get_text('menu.invalid_choice')}{Style.RESET_ALL}")
                time.sleep(1)

def main():
    """主函数"""
    pak_manager = None
    try:
        pak_manager = PAKManager()
        pak_manager.show_main_menu()
    except KeyboardInterrupt:
        if pak_manager:
            print(f"\n\n{Fore.YELLOW}{EMOJI['INFO']} {pak_manager.config.get_text('general.program_exit')}{Style.RESET_ALL}")
        else:
            print(f"\n\n{Fore.YELLOW}{EMOJI['INFO']} 程序已退出{Style.RESET_ALL}")
    except Exception as e:
        if pak_manager:
            print(f"\n{Fore.RED}{EMOJI['ERROR']} {pak_manager.config.get_text('general.program_error')} {e}{Style.RESET_ALL}")
            input(pak_manager.config.get_text('general.press_enter'))
        else:
            print(f"\n{Fore.RED}{EMOJI['ERROR']} 程序运行出错: {e}{Style.RESET_ALL}")
            input("按回车键退出...")

if __name__ == "__main__":
    main()