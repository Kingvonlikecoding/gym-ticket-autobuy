import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)

class App:
    def __init__(self, root):
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
        
        # 初始化页面为3个标签页
        self.setup_account_tab()
        self.setup_settings_tab()
        self.setup_run_tab()
        
        # 加载配置
        self.load_settings()
        logger.info("GUI initialized successfully")

    def load_settings(self):
        """加载配置"""
        try:
            logger.info("loading configuration...")
                
            with open('config/settings.json', 'r', encoding='utf-8') as f:
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
                    
            logger.info("configuration loaded successfully")
            
        except json.JSONDecodeError:
            logger.error("the configuration file is not valid JSON")
        except Exception as e:
            logger.error(f"error in loading config: {str(e)}")

    def save_account(self):
        """保存账号信息"""
        try:
            # 读取现有配置
            settings = {}
            if os.path.exists('config/settings.json'):
                with open('config/settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            # 获取并验证账号设置
            username = self.account_entries['username'].get().strip()
            # .get() 是 Tkinter 控件的方法，用于获取控件中的文本
            password = self.account_entries['password'].get().strip()
            pay_pass = self.account_entries['pay_pass'].get().strip()
            
            if not username or not password or not pay_pass:
                logger.info("账号信息不能为空")
                raise ValueError("账号信息不能为空")
            
            # 更新账号设置
            account_settings = {
                'username': username,
                'password': password,
                'pay_pass': pay_pass
            }
            settings.update(account_settings)
            
            # 保存更新后的配置
            os.makedirs('config', exist_ok=True)
            with open('config/settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            
            logger.info("account saved")
            messagebox.showinfo("成功", "账号信息保存成功！")
            
        except Exception as e:
            logger.error(f"failed to save account: {str(e)}")
            messagebox.showerror("错误", f"保存账号信息失败：{str(e)}")

    def save_settings(self):
        """保存预约设置"""
        try:                
            # 读取现有配置
            settings = {}
            if os.path.exists('config/settings.json'):
                with open('config/settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            # 获取并验证预约设置
            date = self.settings_entries['date'].get().strip()
            time_slot = self.settings_entries['time_slot'].get().strip()
            venue = self.settings_entries['venue'].get().strip()
            court = self.settings_entries['court'].get().strip()

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
            with open('config/settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            
            logger.info("appointment settings saved")
            messagebox.showinfo("成功", "预约设置保存成功！")
            
        except Exception as e:
            logger.error(f"failed to appointment settings: {str(e)}")
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

    def setup_account_tab(self):
        """账号设置标签页"""
        # ttk.Frame 容器（标签页实例）
        account_frame = ttk.Frame(self.notebook)
        self.notebook.add(account_frame, text="账号设置")

        # 创建主框架（account_frame的child，但是是控件而不是容器）
        main_frame = ttk.LabelFrame(account_frame, text="账号信息")
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

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
            entry = ttk.Entry(frame, width=30) # 输入框
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

        # 说明文本
        note_text = """
            注意事项：
            1. 更换账号时请点击"清除登录状态"，否则可能自动登录之前的账号
            2. 所有信息都会保存在本地settings.json文件中，不会上传到网络，请勿分享此文件
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
        settings = {
            "date": ("预约日期", "(today/tomorrow)"),
            "time_slot": ("时间段", "(如:21:00-22:00)"),
            "venue": ("场馆类型", "(A/B/C)"),
            "court": ("场地选择", "(in/out)")
            }
        
        self.settings_entries = {}
        row = 0
        for key, (label, hint) in settings.items():
            frame = ttk.Frame(left_frame)
            frame.grid(row=row, column=0, sticky='ew', pady=2)
            # 控件在单元格内水平扩展（e = east，w = west）
            
            ttk.Label(frame, text=label, width=10).pack(side='left', padx=(0, 5))
            
            entry = ttk.Entry(frame, width=20)
            entry.pack(side='left', padx=5)
            self.settings_entries[key] = entry
            
            ttk.Label(frame, text=hint).pack(side='left', padx=5)
            
            row += 1

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
        ttk.Button(left_frame, text="保存预约设置", command=self.save_settings).grid(row=row, column=0, pady=20)
        
        # 在右侧添加使用说明
        ttk.Label(right_frame, text="使用说明", font=('Helvetica', 10, 'bold')).pack(pady=(0, 5))
        usage_text = """
            1. 除了场地选择其他所有输入框都必须填写

            2. 场馆类型说明：
            A - 健身房
            B - 羽毛球场
            C - 篮球场

            3. 场地选择说明：
             仅在选择篮球场(C)时需要
            - in  - 室内篮球场
            - out - 天台篮球场

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
        ttk.Button(run_frame, text="开始运行", command=self.run_script).pack(pady=5)

    def run_script(self):
        """运行脚本"""
        try:        
            # 获取设置（是否要显示浏览器）
            with open('config/settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 根据viewable设置运行命令
            cmd = ['uv', 'run', 'python', '-m', 'pytest', './tests/test_main.py']
            if settings.get('viewable', 'yes').lower() == 'yes':
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
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # 行缓冲
            )
            
            capture_log = False
            while process.poll() is None:
                # 读取输出
                for line in process.stdout:
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

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop() # “无限循环”，持续监听和处理用户与界面的交互事件
