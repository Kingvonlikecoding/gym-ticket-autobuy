import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)

class App:
    def __init__(self, root, config_path=None):
        self.root = root
        self.root.title("体育馆预约助手")
        self.root.geometry("900x650")  # 窗口大小
        
        # 创建一个标签页控件
        # 布局控件的三大主要方法：pack()，grid()，place()
        self.notebook = ttk.Notebook(root) 
        # expand=True	如果可用空间大于控件所需空间，则扩展控件以填充空间
        # fill='both'	在水平和垂直方向都填充可用空间
        # padx=10	控件与父容器之间左右留白 10 像素
        # pady=5	控件与父容器之间上下留白 5 像素
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # 输入框的内容存储
        self.account_entries = {}
        self.settings_entries = {}
        self.advanced_settings_entries = {}
        
        # 当前配置文件路径
        self.current_config_file = None
        
        # 初始化页面为3个标签页
        self.setup_account_tab()
        self.setup_settings_tab()
        self.setup_run_tab()
        
        # 加载配置
        if config_path:
            self.load_settings(config_path)
        else:
            self.load_default_settings()
        logger.info("GUI initialized successfully")

    def get_config_file_path(self, username):
        """根据用户名获取配置文件路径"""
        return os.path.join('config', f'settings_{username}.json')

    def load_default_settings(self):
        """加载默认配置"""
        try:
            # 首先检查是否存在默认的settings.json文件
            default_path = os.path.join('config', 'settings.json')
            if os.path.exists(default_path):
                try:
                    # 读取默认配置
                    with open(default_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    
                    # 如果有用户名，创建对应的settings_学号.json文件
                    if 'username' in settings and settings['username']:
                        username = settings['username'].strip()
                        if username:
                            new_path = self.get_config_file_path(username)
                            
                            # 创建新的配置文件
                            os.makedirs('config', exist_ok=True)
                            try:
                                with open(new_path, 'w', encoding='utf-8') as f:
                                    json.dump(settings, f, indent=4)
                                
                                logger.info(f"Created new config file: {new_path}")
                                
                                # 加载新创建的配置文件
                                self.load_settings(new_path)
                                return
                            except (PermissionError, IOError) as e:
                                logger.error(f"Failed to create new config file: {str(e)}")
                                # 如果创建新文件失败，尝试加载默认配置
                                self.load_settings(default_path)
                                return
                        else:
                            # 如果用户名为空，加载默认配置
                            self.load_settings(default_path)
                            return
                    else:
                        # 如果没有用户名，加载默认配置
                        self.load_settings(default_path)
                        return
                except json.JSONDecodeError:
                    logger.error(f"Default config file is invalid JSON: {default_path}")
                    # 如果默认配置文件格式错误，初始化空配置
                    self.load_settings()
            else:
                # 如果默认配置文件不存在，初始化空配置
                self.load_settings()
        except Exception as e:
            logger.error(f"Error handling default config: {str(e)}")
            # 确保在任何错误情况下都有一个可用的配置状态
            self.load_settings()

    def load_settings(self, file_path=None):
        """加载配置"""
        try:
            logger.info("loading configuration...")
                
            # 如果提供了文件路径，使用它；否则使用当前配置文件
            if file_path:
                self.current_config_file = file_path
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
            
            # 保存配置文件
            try:
                os.makedirs('config', exist_ok=True)
                with open(new_config_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=4)
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
            messagebox.showinfo("提示", "账号信息保存成功")
        except Exception as e:
            logger.error(f"failed to save account: {str(e)}")
            messagebox.showerror("错误", f"保存账号信息失败：{str(e)}")

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
            
            logger.info(f"appointment settings saved to {self.current_config_file}")
            messagebox.showinfo("成功", "预约设置保存成功！")
            
        except Exception as e:
            logger.error(f"failed to save appointment settings: {str(e)}")
            messagebox.showerror("错误", f"保存预约设置失败：{str(e)}")

    def clear_cookies(self):
        """清除cookie和存储的登录状态"""
        try:
            cookie_files = ['cookies.json', 'storage.json']
            for file in cookie_files:
                path = os.path.join('config', file)
                if os.path.exists(path):
                    os.remove(path)
            logger.info("login state cleared")
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
            # 确认是否切换账号
            if messagebox.askyesno("确认", "切换账号将加载新的配置信息，当前未保存的修改将丢失。是否继续？"):
                # 清除登录状态
                self.clear_cookies()
                # 加载选择的配置文件
                self.load_settings(file_path)
                logger.info(f"Switched to config file: {file_path}")
                messagebox.showinfo("成功", "账号切换成功！")

    def setup_account_tab(self):
        """账号设置标签页"""
        # ttk.Frame 容器（标签页实例）
        account_frame = ttk.Frame(self.notebook)
        self.notebook.add(account_frame, text="账号设置")

        # 创建主框架（account_frame的child，但是是控件而不是容器）
        main_frame = ttk.LabelFrame(account_frame, text="账号信息")
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

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
        
        # 保存和清除cookie按钮
        ttk.Button(button_frame, text="保存账号信息", command=self.save_account).pack(side='left', padx=10)
        ttk.Button(button_frame, text="清除登录状态", command=self.clear_cookies).pack(side='left', padx=10)
        ttk.Button(button_frame, text="清除日志", command=self.clear_logs).pack(side='left', padx=10)

        # 说明文本
        note_text = """
            注意事项：
            1. 更换账号时请点击"选择配置文件"按钮，系统会自动清除之前的登录状态
            2. 所有信息都会保存在本地settings_学号.json文件中，不会上传到网络，请勿分享此文件
            3. 切换账号前请确保已保存当前账号的修改
        """
        ttk.Label(main_frame, text=note_text, justify='left').pack(pady=20)

    def setup_settings_tab(self):
        """预约设置标签页"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="预约设置")
        
        # 创建主框架
        main_frame = ttk.Frame(settings_frame)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
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
        venue_combobox = ttk.Combobox(frame, width=18, values=["A - 健身房", "B - 羽毛球场", "C - 篮球场"])
        venue_combobox.pack(side='left', padx=5)
        self.settings_entries["venue"] = venue_combobox
        ttk.Label(frame, text="(选择场馆类型)").pack(side='left', padx=5)
        row += 1
        
        # 场地选择下拉框（默认隐藏）
        self.court_frame = ttk.Frame(left_frame)
        self.court_frame.grid(row=row, column=0, sticky='ew', pady=2)
        ttk.Label(self.court_frame, text="场地选择", width=10).pack(side='left', padx=(0, 5))
        court_combobox = ttk.Combobox(self.court_frame, width=18, values=["内场", "外场"])
        court_combobox.pack(side='left', padx=5)
        self.settings_entries["court"] = court_combobox
        ttk.Label(self.court_frame, text="(选择场地类型)").pack(side='left', padx=5)
        self.court_frame.grid_remove()  # 默认隐藏
        
        # 添加场馆类型选择事件监听器
        def on_venue_change(event):
            selected_venue = venue_combobox.get()
            if selected_venue == "C - 篮球场":
                self.court_frame.grid()  # 显示场地选择框
            else:
                self.court_frame.grid_remove()  # 隐藏场地选择框
                # 清除场地选择
                court_combobox.set("")
        
        venue_combobox.bind("<<ComboboxSelected>>", on_venue_change)

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


        # 添加保存按钮，因为没加sticky参数所以居中
        ttk.Button(left_frame, text="保存预约设置", command=self.save_settings).grid(row=row, column=0, pady=10)
        
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
        
        # 在右侧添加使用说明
        ttk.Label(right_frame, text="使用说明", font=('Helvetica', 10, 'bold')).pack(pady=(0, 5))
        usage_text = """
            ------高级设置------

            1. 显示浏览器：
            yes - 显示操作过程
            no  - 后台运行

            2. 刷新间隔：
            刷新在 即将放 明天的票 时触发
            ，间隔越小，刷新速度越快，但
            是有可能网速跟不上导致失败

            默认1.5秒，如果网络速度较慢
            ，失败了，可设置大一点
        """
        ttk.Label(right_frame, text=usage_text, justify='left').pack()

    def setup_run_tab(self):
        """运行标签页"""
        run_frame = ttk.Frame(self.notebook)
        self.notebook.add(run_frame, text="运行")
        
        # 创建日志文本框
        self.log_text = tk.Text(run_frame, height=20, width=100)
        self.log_text.pack(padx=5, pady=5)
        # 属于 App 类的一个成员变量，而不是局部变量
        
        # 运行按钮
        ttk.Button(run_frame, text="开始运行", command=lambda: self.run_script(1)).pack(pady=5)
        # 只登录按钮
        ttk.Button(run_frame, text="只登录", command=lambda: self.run_script(2)).pack(pady=5)

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
        
        cmd = ['uv', 'run', 'python', '-m', 'pytest']
        if mode == 1:
            cmd.append('./tests/test_main.py')
        elif mode == 2:
            cmd.append('./tests/test_login.py')
        elif mode == 3:
            cmd.append('./tests/test_leftover.py')
            
        # 添加当前配置文件路径作为参数
        cmd.append(f'--config={self.current_config_file}')
            
        if settings.get('viewable', 'yes').lower() == 'yes' and (mode == 1 or mode == 2):
            cmd.append('--headed') 
        
        # 清空日志文本框
        # 1.0：第 1 行（从 1 开始计数）第 0 个字符（即行首）开始
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"starting the program: {' '.join(cmd)}\n\n")
        self.log_text.update()

        logger.info(f"running command: {' '.join(cmd)}")
        
        # 使用Popen执行命令并实时获取输出,run是阻塞的
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1  # 行缓冲
        )
        
        try:
            capture_log = False
            while process.poll() is None:
                # 读取输出
                line = process.stdout.readline()
                # 开始捕获日志的标记
                if "Captured log call" in line:
                    capture_log = True
                    continue
                if capture_log:
                    # 结束捕获日志的标记
                    if "===" in line:
                        capture_log = False
                        continue
                    if capture_log:
                        self.log_text.insert(tk.END, line)
                        self.log_text.see(tk.END)
                        self.log_text.update()
            
        except Exception as e:
            logger.error(f"{' '.join(cmd)} run error: {str(e)}")
            messagebox.showerror("错误", f"运行脚本{' '.join(cmd)}失败：{str(e)}")
            self.log_text.insert(tk.END, f"\n{' '.join(cmd)} run error: {str(e)}\n")
            process.terminate()
            process.kill()
        finally:
            # 确保资源被释放
            process.stdout.close()
            
            # 如果是查询模式，读取结果文件并显示
            if mode == 3:
                self.display_leftover_timeslots()

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
