# 自动化抢票的脚本

### 包含两个脚本：

1.`clickme.py`:

用于手动抢票以及配置

2.`for_scheduler.py`:

相当于`clickme.py`的精简版只能抢票，用于与windows自带的定时任务功能task scheduler配合，实现明天自动抢票


## 前期准备

在开始使用之前，请确保您已经安装了以下环境：

1.  **Python**: 确保你已经安装了 Python 3.10 或更高版本 ，并且Python在系统的 PATH 环境变量中

## 如何使用
1. **clickme.py**
>运行`clickme.py`文件（如提示以什么方式打开，则以python打开），将显示操作界面

2.  **for_scheduler.py**: 
>配合windows自带的定时任务功能task scheduler（或者其他定时执行任务的软件），设置定时任务，创建任务选择`for_scheduler.py`即可实现自动化。

## 注意事项

* 请不要分享settings.json文件，此文件包含你的账号密码的重要信息
* 请确保您的校园网络连接稳定
* 没票了或者没放票会报错
* 脚本运行过程中请勿关闭，运行时间长是因为等待放票

