#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常用操作模块 - Common Operations Module
提供游戏目录、模组目录、配置目录和存档目录的快速访问功能
Provides quick access to game directory, mod directory, config directory and save directory
"""

import os
import sys
import subprocess
import platform
import time
import zipfile
from datetime import datetime
from pathlib import Path

class CommonOperations:
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.system = platform.system()
        
        # 游戏相关路径常量 - Game related path constants
        self.EPIC_CODE_NAME = "Project_Plague"
        self.GAME_EXEC_DEFAULT = "Project_Plague.exe"
        self.GAME_EXEC_EPIC = "WUCHANG_EGS.exe"
        self.GAME_EXEC_XBOX = "gamelaunchhelper.exe"
        
        # 获取系统路径 - Get system paths
        self.localappdata = os.path.expandvars("%LOCALAPPDATA%")
        
    def get_translations(self, language="en"):
        """获取翻译文本 - Get translation texts"""
        translations = {
            "en": {
                "menu_title": "📁 Common Operations",
                "open_game_dir": "🎮 Open Game Directory",
                "open_mod_dir": "📦 Open ~mods Directory", 
                "open_config_dir": "⚙️ Open Game Config Directory",
                "open_save_dir": "💾 Open Game Save Directory",
                "backup_save": "💾 Backup Game Save",
                "back_to_main": "🔙 Back to Main Menu",
                "game_dir_not_found": "❌ Game directory not found. Please run the program in the game root directory.",
                "mod_dir_not_found": "❌ Mod directory not found. Please check config: {}",
                "config_dir_not_found": "❌ Game config directory not found.",
                "save_dir_not_found": "❌ Game save directory not found.",
                "opening_directory": "📂 Opening directory: {}",
                "directory_opened": "✅ Directory opened successfully.",
                "failed_to_open": "❌ Failed to open directory: {}",
                "invalid_choice": "❌ Invalid choice. Please try again.",
                "press_enter": "Press Enter to continue...",
                "auto_detect_game": "🔍 Auto-detecting game directory...",
                "game_found": "✅ Game found: {}",
                "game_not_found": "❌ Game not found in common locations.",
                "config_path": "configuration file path",
                "backup_creating": "📦 Creating backup...",
                "backup_success": "✅ Backup created successfully: {}",
                "backup_failed": "❌ Backup failed: {}",
                "backup_dir_not_found": "❌ Save directory not found."
            },
            "zh_cn": {
                "menu_title": "📁 常用操作",
                "open_game_dir": "🎮 打开游戏目录",
                "open_mod_dir": "📦 打开~mods目录",
                "open_config_dir": "⚙️ 打开游戏设置目录", 
                "open_save_dir": "💾 打开游戏存档目录",
                "backup_save": "💾 备份游戏存档",
                "back_to_main": "🔙 返回主菜单",
                "game_dir_not_found": "❌ 未找到游戏目录。请将程序放在游戏根目录运行。",
                "mod_dir_not_found": "❌ 未找到模组目录。请检查配置：{}",
                "config_dir_not_found": "❌ 未找到游戏设置目录。",
                "save_dir_not_found": "❌ 未找到游戏存档目录。",
                "opening_directory": "📂 正在打开目录：{}",
                "directory_opened": "✅ 目录打开成功。",
                "failed_to_open": "❌ 打开目录失败：{}",
                "invalid_choice": "❌ 无效选择，请重试。",
                "press_enter": "按回车键继续...",
                "auto_detect_game": "🔍 自动检测游戏目录中...",
                "game_found": "✅ 找到游戏：{}",
                "game_not_found": "❌ 在常见位置未找到游戏。",
                "config_path": "配置文件路径",
                "backup_creating": "📦 正在创建备份...",
                "backup_success": "✅ 备份创建成功：{}",
                "backup_failed": "❌ 备份失败：{}",
                "backup_dir_not_found": "❌ 未找到存档目录。"
            }
        }
        return translations.get(language, translations["en"])
    
    def open_directory(self, directory_path, t):
        """打开目录 - Open directory"""
        try:
            if not os.path.exists(directory_path):
                return False, f"{directory_path}"
                
            print(t["opening_directory"].format(directory_path))
            
            if self.system == "Windows":
                # 在Windows上，explorer有时会返回非零退出状态但实际成功打开
                # 使用shell=True和不检查返回码的方式
                subprocess.Popen(["explorer", directory_path], shell=True)
                # 给一点时间让explorer启动
                time.sleep(0.5)
            elif self.system == "Darwin":  # macOS
                subprocess.run(["open", directory_path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", directory_path], check=True)
                
            print(t["directory_opened"])
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def get_game_directory(self):
        """获取游戏目录 - Get game directory"""
        # 直接从配置文件中获取游戏目录 - Get game directory directly from config
        if self.config_manager:
            game_dir = self.config_manager.config.get('game_directory', '')
            if game_dir and os.path.exists(game_dir):
                return game_dir
        
        # 如果配置中没有或路径无效，返回None - Return None if not in config or invalid
        return None
    
    def _is_valid_game_directory(self, directory):
        """验证是否为有效的游戏目录 - Validate if it's a valid game directory"""
        if not os.path.exists(directory):
            return False
            
        # 检查是否存在游戏可执行文件 - Check if game executable exists
        executables = [self.GAME_EXEC_DEFAULT, self.GAME_EXEC_EPIC, self.GAME_EXEC_XBOX]
        for exe in executables:
            if os.path.exists(os.path.join(directory, exe)):
                return True
                
        # 检查是否存在 Project_Plague 文件夹 - Check if Project_Plague folder exists
        project_plague_dir = os.path.join(directory, self.EPIC_CODE_NAME)
        if os.path.exists(project_plague_dir):
            return True
            
        return False
    
    def _auto_detect_game_directory(self):
        """自动检测游戏目录 - Auto-detect game directory"""
        # Steam 常见路径 - Common Steam paths
        steam_paths = [
            "C:\\Program Files (x86)\\Steam\\steamapps\\common\\WUCHANG Fallen Feathers",
            "D:\\Steam\\steamapps\\common\\WUCHANG Fallen Feathers",
            "E:\\Steam\\steamapps\\common\\WUCHANG Fallen Feathers",
            "F:\\Steam\\steamapps\\common\\WUCHANG Fallen Feathers"
        ]
        
        # Epic Games 常见路径 - Common Epic Games paths
        epic_paths = [
            "C:\\Program Files\\Epic Games\\WUCHANG Fallen Feathers",
            "D:\\Epic Games\\WUCHANG Fallen Feathers",
            "E:\\Epic Games\\WUCHANG Fallen Feathers",
            "F:\\Epic Games\\WUCHANG Fallen Feathers"
        ]
        
        # Xbox Game Pass 路径 - Xbox Game Pass paths
        xbox_paths = [
            os.path.join(self.localappdata, "Packages", "505GAMESS.P.A.WuchangPCGP_*")
        ]
        
        all_paths = steam_paths + epic_paths + xbox_paths
        
        for path in all_paths:
            if "*" in path:
                # 处理通配符路径 - Handle wildcard paths
                import glob
                matching_paths = glob.glob(path)
                for matching_path in matching_paths:
                    if self._is_valid_game_directory(matching_path):
                        return matching_path
            else:
                if self._is_valid_game_directory(path):
                    return path
        
        return None
    
    def get_mod_directory(self):
        """获取模组目录 - Get mod directory"""
        # 从配置中获取游戏目录和目标目录 - Get game directory and target directory from config
        if not self.config_manager:
            return None
            
        game_dir = self.config_manager.config.get('game_directory', '')
        target_dir = self.config_manager.config.get('target_directory', '')
        
        if not game_dir or not target_dir:
            return None
            
        # 组合完整的模组目录路径 - Combine full mod directory path
        mod_dir = os.path.join(game_dir, target_dir)
        
        # 如果目录不存在，尝试创建 - If directory doesn't exist, try to create it
        if not os.path.exists(mod_dir):
            try:
                os.makedirs(mod_dir, exist_ok=True)
            except:
                pass
                
        return mod_dir if os.path.exists(mod_dir) else None
    
    def get_config_directory(self):
        """获取游戏配置目录 - Get game config directory"""
        # Windows 配置路径 - Windows config path
        config_dir = os.path.join(self.localappdata, self.EPIC_CODE_NAME, "Saved", "Config", "Windows")
        
        # Xbox 配置路径 - Xbox config path
        xbox_config_dir = os.path.join(self.localappdata, self.EPIC_CODE_NAME, "Saved", "Config", "WinGDK")
        
        # 优先返回存在的目录 - Return existing directory first
        if os.path.exists(config_dir):
            return config_dir
        elif os.path.exists(xbox_config_dir):
            return xbox_config_dir
        else:
            # 返回默认路径，即使不存在 - Return default path even if it doesn't exist
            return config_dir
    
    def get_save_directory(self):
        """获取游戏存档目录 - Get game save directory"""
        # Windows 存档路径 - Windows save path
        save_dir = os.path.join(self.localappdata, self.EPIC_CODE_NAME, "Saved")
        
        # Xbox 存档路径 - Xbox save path
        xbox_save_base = os.path.join(self.localappdata, "Packages")
        xbox_save_pattern = "505GAMESS.P.A.WuchangPCGP_*"
        
        # 优先返回存在的目录 - Return existing directory first
        if os.path.exists(save_dir):
            return save_dir
        else:
            # 查找 Xbox 存档目录 - Find Xbox save directory
            import glob
            xbox_dirs = glob.glob(os.path.join(xbox_save_base, xbox_save_pattern))
            for xbox_dir in xbox_dirs:
                xbox_save_dir = os.path.join(xbox_dir, "SystemAppData", "wgs")
                if os.path.exists(xbox_save_dir):
                    return xbox_save_dir
            
            # 返回默认路径，即使不存在 - Return default path even if it doesn't exist
            return save_dir
    
    def show_menu(self, language="en"):
        """显示常用操作菜单 - Show common operations menu"""
        t = self.get_translations(language)
        
        while True:
            print("\n" + "="*50)
            print(t["menu_title"])
            print("="*50)
            print(f"1. {t['open_game_dir']}")
            print(f"2. {t['open_mod_dir']}")
            print(f"3. {t['open_config_dir']}")
            print(f"4. {t['open_save_dir']}")
            print(f"5. {t['backup_save']}")
            print(f"0. {t['back_to_main']}")
            print("="*50)
            
            try:
                choice = input("请选择操作 / Please select an option: ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    self._handle_open_game_directory(t)
                elif choice == "2":
                    self._handle_open_mod_directory(t)
                elif choice == "3":
                    self._handle_open_config_directory(t)
                elif choice == "4":
                    self._handle_open_save_directory(t)
                elif choice == "5":
                    self._handle_backup_save_directory(t)
                else:
                    print(t["invalid_choice"])
                    input(t["press_enter"])
                    # 清屏准备重新显示菜单 - Clear screen to redisplay menu
                    os.system('cls' if os.name == 'nt' else 'clear')
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input(t["press_enter"])
    
    def _handle_open_game_directory(self, t):
        """处理打开游戏目录 - Handle opening game directory"""
        print(t["auto_detect_game"])
        game_dir = self.get_game_directory()
        
        if game_dir:
            print(t["game_found"].format(game_dir))
            success, error = self.open_directory(game_dir, t)
            if not success:
                print(t["failed_to_open"].format(error))
        else:
            print(t["game_dir_not_found"])
        
        input(t["press_enter"])
        # 清屏准备重新显示菜单 - Clear screen to redisplay menu
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _handle_open_mod_directory(self, t):
        """处理打开模组目录 - Handle opening mod directory"""
        mod_dir = self.get_mod_directory()
        
        if mod_dir:
            success, error = self.open_directory(mod_dir, t)
            if not success:
                print(t["failed_to_open"].format(error))
        else:
            print(t["mod_dir_not_found"].format(t.get("config_path", "config path")))
        
        input(t["press_enter"])
        # 清屏准备重新显示菜单 - Clear screen to redisplay menu
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _handle_open_config_directory(self, t):
        """处理打开配置目录 - Handle opening config directory"""
        config_dir = self.get_config_directory()
        
        if config_dir and os.path.exists(config_dir):
            success, error = self.open_directory(config_dir, t)
            if not success:
                print(t["failed_to_open"].format(error))
        else:
            print(t["config_dir_not_found"])
        
        input(t["press_enter"])
        # 清屏准备重新显示菜单 - Clear screen to redisplay menu
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _handle_open_save_directory(self, t):
        """处理打开存档目录 - Handle opening save directory"""
        save_dir = self.get_save_directory()
        
        if save_dir and os.path.exists(save_dir):
            success, error = self.open_directory(save_dir, t)
            if not success:
                print(t["failed_to_open"].format(error))
        else:
            print(t["save_dir_not_found"])
        
        input(t["press_enter"])
        # 清屏准备重新显示菜单 - Clear screen to redisplay menu
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _handle_backup_save_directory(self, t):
        """处理备份存档目录 - Handle backing up save directory"""
        save_dir = self.get_save_directory()
        
        if not save_dir or not os.path.exists(save_dir):
            print(t["backup_dir_not_found"])
            input(t["press_enter"])
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        
        try:
            print(t["backup_creating"])
            
            # 生成备份文件名 - Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            backup_filename = f"Wuchang_Game_Saved-{timestamp}.zip"
            backup_path = os.path.join(save_dir, backup_filename)
            
            # 创建zip文件 - Create zip file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(save_dir):
                    for file in files:
                        # 跳过已存在的备份文件 - Skip existing backup files
                        if file.endswith('.zip') and file.startswith('Wuchang_Game_Saved-'):
                            continue
                        
                        file_path = os.path.join(root, file)
                        # 计算相对路径 - Calculate relative path
                        arcname = os.path.relpath(file_path, save_dir)
                        zipf.write(file_path, arcname)
            
            print(t["backup_success"].format(backup_path))
            
        except Exception as e:
            print(t["backup_failed"].format(str(e)))
        
        input(t["press_enter"])
        # 清屏准备重新显示菜单 - Clear screen to redisplay menu
        os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """测试函数 - Test function"""
    operations = CommonOperations()
    operations.show_menu("zh_cn")

if __name__ == "__main__":
    main()