# 体育馆预约助手 - 主程序
# Gymnasium Reservation Assistant - Main Program
# 
# 程序简介：
# 该程序是一个基于Tkinter的GUI应用，用于自动化体育馆场地预约流程
# 通过图形界面提供直观的操作方式，支持多账号配置管理和实时预约监控
# 
# 核心功能模块：
# 
# 1. 配置管理模块
#    - 多用户配置文件管理
#    - 配置文件自动同步与备份
#    - 配置变更实时监控
# 
# 2. 账号管理模块
#    - 账号信息安全存储
#    - 登录状态管理
#    - 日志文件管理
# 
# 3. 预约设置模块
#    - 预约时间、场地、场地类型等参数设置
#    - 余票实时查询
#    - 高级预约策略配置
# 
# 4. GUI界面模块
#    - 直观的单页面操作界面
#    - 实时状态显示
#    - 友好的错误提示
# 
# 5. 预约执行模块
#    - 自动化预约流程执行
#    - 多种运行模式支持（完整预约、只登录、查询余票）
#    - 异常情况处理与重试机制
# 
# 使用技术栈：
# - Python 3.x
# - Tkinter (GUI框架)
# - Playwright (网页自动化)
# - JSON (配置文件格式)
# 
# 项目结构：
# - main.py          : 主程序入口和GUI实现
# - launcher.py      : 依赖管理和启动脚本
# - pages/           : 页面对象模式实现
# - scripts/         : 核心业务逻辑脚本
# - utils/           : 工具函数集合
# - config/          : 配置文件目录
# 
# 开发说明：
# 该程序采用模块化设计，便于扩展和维护
# 支持自定义配置和高级功能扩展
# 日志系统便于问题追踪和调试
# 
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import webbrowser
from datetime import datetime
import sys
from unittest import mock
from utils.logger import setup_logger

logger = setup_logger(__name__)

class App:
    def __init__(self, root, config_path=None):
        self.root = root
        self.root.title("体育馆预约助手")
        self.root.geometry("1000x800")  # 调整窗口大小以确保所有内容都能完全显示
        
        # 创建一个主框架，替代标签页
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        # 输入框的内容存储
        self.account_entries = {}
        self.settings_entries = {}
        self.advanced_settings_entries = {}
        
        # 当前配置文件路径
        self.current_config_file = None
        
        # 初始化所有内容到一个页面
        self.setup_ui()
        
        # 加载配置
        if config_path:
            self.load_settings(config_path)
        else:
            self.load_default_settings()
        
        # 启动监控settings.json变化的线程
        self.monitor_settings_json_changes()
        
        logger.info("GUI initialized successfully")

    def get_config_file_path(self, username):
        """根据用户名获取配置文件路径"""
        return os.path.join('config', f'settings_{username}.json')

    def get_last_used_config_path(self):
        """获取上一次使用的配置文件路径"""
        last_used_path = os.path.join('config', 'last_used.json')
        if os.path.exists(last_used_path):
            try:
                with open(last_used_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('last_used_config', None)
            except Exception as e:
                logger.error(f"Failed to read last_used.json: {str(e)}")
        return None
    
    def save_last_used_config_path(self, config_path):
        """保存上一次使用的配置文件路径"""
        try:
            last_used_path = os.path.join('config', 'last_used.json')
            os.makedirs('config', exist_ok=True)
            with open(last_used_path, 'w', encoding='utf-8') as f:
                json.dump({'last_used_config': config_path}, f, indent=4)
            logger.info(f"Saved last used config path: {config_path}")
        except Exception as e:
            logger.error(f"Failed to save last_used.json: {str(e)}")
    
    def sync_settings_files(self, source_path, target_path):
        """将源配置文件同步到目标配置文件"""
        try:
            if os.path.exists(source_path):
                with open(source_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=4)
                logger.debug(f"Synced config from {source_path} to {target_path}")
        except Exception as e:
            logger.error(f"Failed to sync config files: {str(e)}")
    
    def load_default_settings(self):
        """加载默认配置"""
        try:
            last_used_config = self.get_last_used_config_path()
            default_path = os.path.join('config', 'settings.json')
            
            # 如果有上一次使用的配置文件，将其同步到settings.json
            if last_used_config and os.path.exists(last_used_config):
                logger.info(f"Using last used config: {last_used_config}")
                self.sync_settings_files(last_used_config, default_path)
            
            # 检查默认配置文件是否存在且有效
            if os.path.exists(default_path):
                try:
                    with open(default_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    
                    # 获取用户名并检查是否有效
                    username = settings.get('username', '').strip()
                    if username:
                        # 创建用户专用配置文件
                        new_path = self.get_config_file_path(username)
                        os.makedirs('config', exist_ok=True)
                        
                        try:
                            with open(new_path, 'w', encoding='utf-8') as f:
                                json.dump(settings, f, indent=4)
                            
                            logger.info(f"Created new config file: {new_path}")
                            self.load_settings(new_path)
                            return
                        except (PermissionError, IOError) as e:
                            logger.error(f"Failed to create new config file: {str(e)}")
                            # 创建失败时加载默认配置
                            self.load_settings(default_path)
                            return
                    else:
                        # 无有效用户名时加载默认配置
                        self.load_settings(default_path)
                        return
                except json.JSONDecodeError:
                    logger.error(f"Default config file is invalid JSON: {default_path}")
                    # 配置文件无效时初始化空配置
            # 配置文件不存在或无效时初始化空配置
            self.load_settings()
        except Exception as e:
            logger.error(f"Error handling default config: {str(e)}")
            # 确保在任何错误情况下都有一个可用的配置状态
            self.load_settings()

    def monitor_settings_json_changes(self):
        """监控settings.json文件的变化并同步到对应学号的配置文件"""
        try:
            default_path = os.path.join('config', 'settings.json')
            if os.path.exists(default_path):
                with open(default_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 检查是否有有效的用户名
                username = settings.get('username', '').strip()
                if username:
                    # 同步到对应学号的配置文件
                    user_config_path = self.get_config_file_path(username)
                    self.sync_settings_files(default_path, user_config_path)
                    logger.debug(f"Synced settings.json to {user_config_path} based on username: {username}")
                    
                    # 更新当前配置文件路径
                    if not self.current_config_file or self.current_config_file == default_path:
                        self.current_config_file = user_config_path
                        # 保存上一次使用的配置文件路径
                        self.save_last_used_config_path(user_config_path)
                        # 更新界面显示
                        if hasattr(self, 'current_config_label'):
                            file_name = os.path.basename(self.current_config_file)
                            self.current_config_label.config(text=f"当前配置文件：{file_name}")
        except Exception as e:
            logger.error(f"Failed to monitor settings.json changes: {str(e)}")
        
        # 每1秒检查一次
        self.root.after(1000, self.monitor_settings_json_changes)
    

    
    def load_settings(self, file_path=None):
        """加载配置"""
        try:
            logger.info("loading configuration...")
                
            # 如果提供了文件路径，使用它；否则使用当前配置文件
            if file_path:
                self.current_config_file = file_path
                # 保存上一次使用的配置文件路径
                self.save_last_used_config_path(file_path)
            elif not self.current_config_file:
                # 如果没有当前配置文件且没有提供路径，返回空配置
                logger.info("No config file specified, using empty configuration")
                # 更新当前配置文件标签
                if hasattr(self, 'current_config_label'):
                    self.current_config_label.config(text="当前配置文件：无")
                return
            
            with open(self.current_config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # 加载账号信息
            for key, entry in self.account_entries.items():
                if key in settings:
                    # 清除输入框中原有的内容；
                    # 0 表示从第一个字符开始；
                    # tk.END 表示到最后一个字符结束
                    entry.delete(0, tk.END) 
                    # 把配置文件中的值插入到输入框中；
                    # 0 表示从最前面插入；
                    entry.insert(0, settings[key])
            
            # 加载预约设置
            for key, entry in self.settings_entries.items():
                if key in settings:
                    entry.delete(0, tk.END)
                    entry.insert(0, settings[key])

            # 加载预约高级设置
            for key, entry in self.advanced_settings_entries.items():
                if key in settings:
                    entry.delete(0, tk.END)
                    entry.insert(0, settings[key])
                    
            # 更新当前配置文件标签
            if hasattr(self, 'current_config_label'):
                # 只显示文件名
                file_name = os.path.basename(self.current_config_file)
                self.current_config_label.config(text=f"当前配置文件：{file_name}")
                    
            logger.info(f"configuration loaded successfully from {self.current_config_file}")
            
            # 将当前配置文件同步到settings.json
            default_path = os.path.join('config', 'settings.json')
            self.sync_settings_files(self.current_config_file, default_path)
            
            # 如果当前配置文件是settings.json，同步到对应学号的配置文件
            if self.current_config_file == default_path:
                self.monitor_settings_json_changes()
            
        except json.JSONDecodeError:
            logger.error(f"the configuration file {self.current_config_file} is not valid JSON")
            messagebox.showerror("错误", "配置文件格式错误，请检查文件内容")
        except FileNotFoundError:
            logger.error(f"configuration file {self.current_config_file} not found")
            messagebox.showerror("错误", "配置文件不存在")
        except PermissionError:
            logger.error(f"permission denied when reading {self.current_config_file}")
            messagebox.showerror("错误", "读取配置文件权限不足")
        except Exception as e:
            logger.error(f"error in loading config: {str(e)}")
            messagebox.showerror("错误", f"加载配置失败：{str(e)}")

    def save_account(self):
        """保存账号信息"""
        try:
            logger.info("saving account information...")
            
            # 获取当前输入的账号信息
            username = self.account_entries['username'].get().strip()
            password = self.account_entries['password'].get()
            pay_pass = self.account_entries['pay_pass'].get()
            
            # 验证用户名不为空
            if not username:
                messagebox.showwarning("警告", "用户名不能为空")
                return
            
            # 读取现有配置或创建新配置
            settings = {}
            if self.current_config_file and os.path.exists(self.current_config_file):
                with open(self.current_config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            # 更新账号信息
            account_settings = {
                'username': username,
                'password': password,
                'pay_pass': pay_pass
            }
            settings.update(account_settings)
            
            # 确定新的配置文件路径（使用用户名）
            new_config_path = self.get_config_file_path(username)
            default_path = os.path.join('config', 'settings.json')
            
            # 保存配置文件
            try:
                os.makedirs('config', exist_ok=True)
                with open(new_config_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=4)
                
                # 同时将配置同步到settings.json
                self.sync_settings_files(new_config_path, default_path)
                
                # 保存上一次使用的配置文件路径
                self.save_last_used_config_path(new_config_path)
            except PermissionError:
                logger.error(f"permission denied when saving account to {new_config_path}")
                messagebox.showerror("错误", "保存账号信息失败：权限不足")
                return
            except IOError as e:
                logger.error(f"IO error when saving account to {new_config_path}: {str(e)}")
                messagebox.showerror("错误", f"保存账号信息失败：{str(e)}")
                return
            
            # 更新当前配置文件路径
            self.current_config_file = new_config_path
            
            # 更新当前配置文件标签
            if hasattr(self, 'current_config_label'):
                file_name = os.path.basename(self.current_config_file)
                self.current_config_label.config(text=f"当前配置文件：{file_name}")
            
            logger.info(f"account saved to {new_config_path}")
        except Exception as e:
            logger.error(f"failed to save account: {str(e)}")

    def auto_save_account_on_key(self, event=None):
        """在按键释放时自动保存账号信息"""
        # 只在按下Enter键时保存
        if event and event.keysym == 'Return':
            self.auto_save_account()

    def auto_save_account(self, event=None):
        """自动保存账号信息"""
        self.save_account()

    def save_settings(self):
        """保存预约设置"""
        try:                
            # 检查是否有当前配置文件
            if not self.current_config_file:
                # 尝试从用户名获取配置文件路径
                username = self.account_entries['username'].get().strip()
                if not username:
                    raise ValueError("请先设置用户名")
                
                self.current_config_file = self.get_config_file_path(username)
            
            # 读取现有配置
            settings = {}
            if os.path.exists(self.current_config_file):
                with open(self.current_config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            # 获取并验证预约设置
            date = self.settings_entries['date'].get().strip()
            time_slot = self.settings_entries['time_slot'].get().strip()
            venue_display = self.settings_entries['venue'].get().strip()
            court_display = self.settings_entries['court'].get().strip()
            
            # 将显示值转换为内部值
            # 场馆类型："A - 健身房" -> "A"
            venue = venue_display[0] if venue_display else ""
            
            # 场地选择："内场" -> "in"，"外场" -> "out"
            court_mapping = {"内场": "in", "外场": "out"}
            court = court_mapping.get(court_display, "") if court_display else ""

            # 高级设置
            viewable = self.advanced_settings_entries['viewable'].get().strip()
            wait_timeout_seconds = self.advanced_settings_entries['wait_timeout_seconds'].get().strip()
            
            if not date or not time_slot or not venue or not viewable or not wait_timeout_seconds:
                raise ValueError("除了场地选择其他所有输入框不能为空")
            
            # 更新预约设置
            appointment_settings = {
                'date': date,
                'time_slot': time_slot,
                'venue': venue,
                'court': court,
                'viewable': viewable,
                'wait_timeout_seconds': wait_timeout_seconds
            }
            settings.update(appointment_settings)
            
            # 保存更新后的配置
            os.makedirs('config', exist_ok=True)
            with open(self.current_config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            
            # 同时将配置同步到settings.json
            default_path = os.path.join('config', 'settings.json')
            self.sync_settings_files(self.current_config_file, default_path)
            
            logger.info(f"appointment settings saved to {self.current_config_file}")
            
        except Exception as e:
            logger.error(f"failed to save appointment settings: {str(e)}")

    def auto_save_settings_on_key(self, event=None):
        """在按键释放时自动保存预约设置"""
        # 只在按下Enter键时保存
        if event and event.keysym == 'Return':
            self.auto_save_settings()

    def auto_save_settings(self, event=None):
        """自动保存预约设置"""
        self.save_settings()

    def clear_cookies(self, show_message=True):
        """清除cookie和存储的登录状态"""
        try:
            cookie_files = ['cookies.json', 'storage.json']
            for file in cookie_files:
                path = os.path.join('config', file)
                if os.path.exists(path):
                    os.remove(path)
            logger.info("login state cleared")
            if show_message:
                messagebox.showinfo("成功", "已清除登录状态！")
        except Exception as e:
            messagebox.showerror("错误", f"清除登录状态失败：{str(e)}")

    def clear_logs(self):
        """清除日志文件"""
        try:
            log_path = os.path.join('logs')
            if os.path.exists(log_path):
                for file in os.listdir(log_path):
                    file_path = os.path.join(log_path, file)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        continue
                logger.info("logs cleared")
                messagebox.showinfo("成功", "已清除日志！")
        except Exception as e:
            logger.error(f"failed to clear logs: {str(e)}")
            messagebox.showerror("错误", f"清除日志失败：{str(e)}")

    def select_config_file(self):
        """选择配置文件"""
        from tkinter import filedialog
        
        # 打开文件对话框，选择settings_*.json文件
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            initialdir=os.path.join(os.getcwd(), 'config'),
            filetypes=[("JSON files", "settings_*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            # 自动保存当前设置
            self.save_account()
            self.save_settings()
            # 清除登录状态（不显示消息框）
            self.clear_cookies(show_message=False)
            # 加载选择的配置文件
            self.load_settings(file_path)
            logger.info(f"Switched to config file: {file_path}")

    def setup_ui(self):
        """设置UI界面，将所有内容合并到一个页面"""
        # 创建顶部框架，用于放置账号设置和预约设置
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # 创建左侧框架，用于放置账号设置
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 创建右侧框架，用于放置预约设置
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # 创建账号设置部分（放在左侧）
        self.setup_account_tab(left_frame)
        
        # 创建预约设置部分（放在右侧）
        self.setup_settings_tab(right_frame)
        
        # 创建运行控制部分（放在底部）
        self.setup_run_section(self.main_frame)
    
    def setup_account_tab(self, parent_frame):
        """账号设置部分"""
        # 创建账号设置框架
        account_frame = ttk.LabelFrame(parent_frame, text="账号设置")
        account_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # 创建主框架（account_frame的child，但是是控件而不是容器）
        main_frame = ttk.Frame(account_frame)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # 账号切换功能区
        switch_frame = ttk.LabelFrame(main_frame, text="账号切换")
        switch_frame.pack(fill='x', padx=10, pady=10)
        
        # 文件选择按钮
        ttk.Button(switch_frame, text="选择配置文件", command=self.select_config_file).pack(side='left', padx=10, pady=10)
        
        # 当前配置文件显示
        self.current_config_label = ttk.Label(switch_frame, text="当前配置文件：无")
        self.current_config_label.pack(side='left', padx=10, pady=10)

        # 账号设置
        settings = {
            "username": ("用户名", None),
            "password": ("密码", None),
            "pay_pass": ("支付密码", None)
        }

        self.account_entries = {}
        for key, (label, _) in settings.items():
            frame = ttk.Frame(main_frame)
            frame.pack(fill='x', pady=5) # fill='x' 表示这个容器会水平填满可用空间，所以下一个frame自动换行
            
            ttk.Label(frame, text=label, width=10).pack(side='left', padx=5) 
            entry = ttk.Entry(frame, width=30)
            if key in ["password", "pay_pass"]:
                entry.config(show="*")
            entry.pack(side='left', padx=5)
            self.account_entries[key] = entry

        # justify='left'控件内部文本的对齐方式
        # side='left'控件本身在父容器中的排列方向

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20) #默认居中
        
        # 清除cookie和日志按钮
        ttk.Button(button_frame, text="清除登录状态", command=self.clear_cookies).pack(side='left', padx=10)
        ttk.Button(button_frame, text="清除日志", command=self.clear_logs).pack(side='left', padx=10)
        
        # 为账号信息输入字段添加自动保存事件监听器
        for key, entry in self.account_entries.items():
            entry.bind("<FocusOut>", self.auto_save_account)
            entry.bind("<KeyRelease>", self.auto_save_account_on_key)
            entry.bind("<<ComboboxSelected>>", self.auto_save_account)

        # 注意事项和官网链接已移至页面底部

    def setup_settings_tab(self, parent_frame):
        """预约设置部分"""
        settings_frame = ttk.LabelFrame(parent_frame, text="预约设置")
        settings_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # 创建主框架
        main_frame = ttk.Frame(settings_frame)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # 创建左侧设置框架
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 创建右侧说明框架
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='y')
        
        # 创建预约设置输入框
        self.settings_entries = {}
        row = 0
        
        # 预约日期下拉框
        frame = ttk.Frame(left_frame)
        frame.grid(row=row, column=0, sticky='ew', pady=2)
        ttk.Label(frame, text="预约日期", width=10).pack(side='left', padx=(0, 5))
        date_combobox = ttk.Combobox(frame, width=18, values=["today", "tomorrow"])
        date_combobox.pack(side='left', padx=5)
        self.settings_entries["date"] = date_combobox
        ttk.Label(frame, text="(today/tomorrow)").pack(side='left', padx=5)
        row += 1
        
        # 时间段下拉框
        frame = ttk.Frame(left_frame)
        frame.grid(row=row, column=0, sticky='ew', pady=2)
        ttk.Label(frame, text="时间段", width=10).pack(side='left', padx=(0, 5))
        # 生成08:00-09:00到21:00-22:00的时间段选项
        time_slots = []
        for hour in range(8, 22):
            start_time = f"{hour:02d}:00"
            end_time = f"{hour+1:02d}:00"
            time_slots.append(f"{start_time}-{end_time}")
        time_combobox = ttk.Combobox(frame, width=18, values=time_slots)
        time_combobox.pack(side='left', padx=5)
        self.settings_entries["time_slot"] = time_combobox
        ttk.Label(frame, text="(选择预约时间段)").pack(side='left', padx=5)
        row += 1
        
        # 场馆类型下拉框
        frame = ttk.Frame(left_frame)
        frame.grid(row=row, column=0, sticky='ew', pady=2)
        ttk.Label(frame, text="场馆类型", width=10).pack(side='left', padx=(0, 5))
        self.venue_combobox = ttk.Combobox(frame, width=18, values=["A - 健身房", "B - 羽毛球场", "C - 篮球场"])
        self.venue_combobox.pack(side='left', padx=5)
        self.settings_entries["venue"] = self.venue_combobox
        ttk.Label(frame, text="(选择场馆类型)").pack(side='left', padx=5)
        row += 1
        
        # 场地选择下拉框
        self.court_frame = ttk.Frame(left_frame)
        self.court_frame.grid(row=row, column=0, sticky='ew', pady=2)
        ttk.Label(self.court_frame, text="场地选择", width=10).pack(side='left', padx=(0, 5))
        court_combobox = ttk.Combobox(self.court_frame, width=18, values=["内场", "外场"])
        court_combobox.pack(side='left', padx=5)
        self.settings_entries["court"] = court_combobox
        ttk.Label(self.court_frame, text="(选择场地类型)").pack(side='left', padx=5)
        
        # 添加场馆类型选择事件监听器
        # 场馆选择变化时不需要特殊处理，场地选择框将始终显示

        # 高级选项输入框
        adsettings={
            "viewable": ("显示浏览器", "(yes/no)"),
            "wait_timeout_seconds": ("刷新间隔", "(如1.5秒)")
        }
        self.advanced_settings_entries={}

        row+=10
        frame = ttk.Frame(left_frame)
        frame.grid(row=row, column=0, sticky='ew', pady=10)
        ttk.Label(frame, text="高级选项", font=('Helvetica', 10, 'bold') ,width=15).pack(side='left', padx=(0,10))

        row += 1
        for key, (label, hint) in adsettings.items():
            frame = ttk.Frame(left_frame)
            frame.grid(row=row, column=0, sticky='ew', pady=2)
            
            ttk.Label(frame, text=label, width=10).pack(side='left', padx=(0, 5))
            
            entry = ttk.Entry(frame, width=20)
            entry.pack(side='left', padx=5)
            self.advanced_settings_entries[key] = entry
            
            ttk.Label(frame, text=hint).pack(side='left', padx=5)
            row += 1


        # 为预约设置和高级设置输入字段添加自动保存事件监听器
        for key, entry in self.settings_entries.items():
            entry.bind("<FocusOut>", self.auto_save_settings)
            entry.bind("<KeyRelease>", self.auto_save_settings_on_key)
            entry.bind("<<ComboboxSelected>>", self.auto_save_settings)
        
        for key, entry in self.advanced_settings_entries.items():
            entry.bind("<FocusOut>", self.auto_save_settings)
            entry.bind("<KeyRelease>", self.auto_save_settings_on_key)
            entry.bind("<<ComboboxSelected>>", self.auto_save_settings)
        
        # 添加查询当日有票时间段的按钮和文本框
        row += 1
        # 查询按钮
        ttk.Button(left_frame, text="查询当日有票的时间段", command=self.query_leftover_timeslots).grid(row=row, column=0, pady=10)
        
        # 结果显示文本框
        row += 1
        self.leftover_textbox = tk.Text(left_frame, width=50, height=10, wrap=tk.WORD)
        self.leftover_textbox.grid(row=row, column=0, padx=10, pady=10)
        # 初始提示信息
        self.leftover_textbox.insert(tk.END, "点击'查询当日有票的时间段'按钮开始查询...")
        
        # 高级设置说明已移至页面底部

    def setup_run_section(self, parent_frame):
        """运行控制部分"""
        run_frame = ttk.LabelFrame(parent_frame, text="运行控制")
        run_frame.pack(fill='x', padx=20, pady=10)
        
        # 运行按钮
        button_frame = ttk.Frame(run_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="开始抢票", command=lambda: self.run_script(1)).pack(side='left', padx=10)
        # 只登录按钮
        ttk.Button(button_frame, text="只登录", command=lambda: self.run_script(2)).pack(side='left', padx=10)
        
        # 添加合并后的说明部分
        self.setup_instructions_section(parent_frame)

    def run_script(self, mode):
        """运行脚本"""
        # 检查是否有当前配置文件
        if not self.current_config_file:
            # 尝试从用户名获取配置文件路径
            username = self.account_entries['username'].get().strip()
            if not username:
                messagebox.showerror("错误", "请先设置用户名并保存账号信息")
                return
            
            self.current_config_file = self.get_config_file_path(username)
            
            # 检查配置文件是否存在
            if not os.path.exists(self.current_config_file):
                messagebox.showerror("错误", "配置文件不存在，请先保存账号信息")
                return
        
        # 读取配置
        try:
            with open(self.current_config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except Exception as e:
            logger.error(f"failed to read config: {str(e)}")
            messagebox.showerror("错误", f"读取配置文件失败：{str(e)}")
            return
        
        # 导入对应的脚本模块
        script_map = {
            1: ("scripts.main_script", "抢票"),
            2: ("scripts.login_script", "登录"),
            3: ("scripts.leftover_script", "余票查询")
        }
        
        module_name, script_name = script_map.get(mode, (None, "未知"))
        if not module_name:
            messagebox.showerror("错误", f"无效的模式: {mode}")
            return
        
        # 动态导入脚本模块
        try:
            import importlib
            module = importlib.import_module(module_name)
            script_main = module.main
        except ImportError as e:
            logger.error(f"Error importing {module_name}: {str(e)}")
            messagebox.showerror("错误", f"导入脚本模块失败：{str(e)}")
            return
        
        # 保存原始的sys.argv
        original_argv = sys.argv.copy()
        
        try:
            # 模拟命令行参数
            sys.argv = ['script.py', f'--config={self.current_config_file}']
            if settings.get('viewable', 'yes').lower() == 'yes' and (mode == 1 or mode == 2):
                sys.argv.append('--headed')
            
            logger.info(f"running {script_name} script with args: {sys.argv[1:]}")
            
            # 调用脚本的main函数
            exit_code = script_main()
            
            # 判断执行结果并显示相应的messagebox
            if mode == 1:  # 如果是完整预约模式
                if exit_code == 0:
                    messagebox.showinfo("成功", "抢票成功！")
                else:
                    messagebox.showerror("失败", "抢票失败，请查看日志了解详情。")
            # 只登录模式不显示messagebox提示
        except Exception as e:
            logger.error(f"Error running {script_name} script: {str(e)}")
            messagebox.showerror("错误", f"执行{script_name}脚本时出错：{str(e)}")
        finally:
            # 恢复原始的sys.argv
            sys.argv = original_argv
            
            # 如果是查询模式，读取结果文件并显示
            if mode == 3:
                self.display_leftover_timeslots()
    
    def setup_instructions_section(self, parent_frame):
        """合并显示注意事项、官网链接和高级设置说明"""
        instructions_frame = ttk.LabelFrame(parent_frame, text="使用说明与注意事项")
        instructions_frame.pack(fill='x', padx=20, pady=10)
        
        # 创建内容框架
        content_frame = ttk.Frame(instructions_frame)
        content_frame.pack(fill='x', padx=20, pady=10)
        
        # 注意事项
        note_frame = ttk.Frame(content_frame)
        note_frame.pack(fill='x', pady=(0, 5))
        ttk.Label(note_frame, text="注意事项", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        note_text = """
1. 所有修改都会自动保存
2. 所有信息都会保存在本地settings_学号.json文件中，不会上传到网络，请勿分享此文件
3. 详细说明请查看README.md文件  
        """
        ttk.Label(note_frame, text=note_text, justify='left').pack(anchor='w')
        
        # 官网链接
        link_frame = ttk.Frame(content_frame)
        link_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(link_frame, text="官网下载最新版：", font=('Helvetica', 10, 'bold')).pack(side='left')
        link_label = ttk.Label(link_frame, text="https://github.com/Kingvonlikecoding/gym-ticket-autobuy", foreground="blue", cursor="hand2")
        link_label.pack(side='left')
        
        # 点击链接打开网页
        def open_link(event):
            webbrowser.open_new("https://github.com/Kingvonlikecoding/gym-ticket-autobuy")
        
        # 绑定点击事件
        link_label.bind("<Button-1>", open_link)

    def query_leftover_timeslots(self):
        """查询当日有票的时间段"""
        # 清空结果文本框
        self.leftover_textbox.delete(1.0, tk.END)
        self.leftover_textbox.insert(tk.END, "正在查询当日有票的时间段...")
        self.leftover_textbox.update()
        
        # 运行查询脚本
        self.run_script(3)
    
    def display_leftover_timeslots(self):
        """显示查询到的有票时间段"""
        # 确保config目录存在
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        result_file = os.path.join(config_dir, 'leftover_result.json')
        
        try:
            # 检查文件是否存在
            if not os.path.exists(result_file):
                self.leftover_textbox.delete(1.0, tk.END)
                self.leftover_textbox.insert(tk.END, "查询失败：未找到结果文件")
                return
            
            # 读取结果
            with open(result_file, 'r', encoding='utf-8') as f:
                leftover_timeslots = json.load(f)
            
            # 显示结果
            self.leftover_textbox.delete(1.0, tk.END)
            
            if leftover_timeslots is None or not leftover_timeslots:
                self.leftover_textbox.insert(tk.END, "当日没有可预订的时间段")
            else:
                self.leftover_textbox.insert(tk.END, "当日有票的时间段：\n")
                for i, timeslot in enumerate(leftover_timeslots, 1):
                    self.leftover_textbox.insert(tk.END, f"{i}. {timeslot}\n")
                    
        except Exception as e:
            logger.error(f"failed to display leftover timeslots: {str(e)}")
            self.leftover_textbox.delete(1.0, tk.END)
            self.leftover_textbox.insert(tk.END, f"查询失败：{str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists(result_file):
                try:
                    os.remove(result_file)
                except:
                    pass

def launch_app(config_path=None):
    """启动应用"""
    logger.info("starting application...")
    root = tk.Tk()
    app = App(root, config_path)
    root.mainloop()

if __name__ == "__main__":
    from pathlib import Path
    cur_path = Path(__file__).parent
    os.chdir(cur_path)
    launch_app()
