####Realesed Under GPL License


####运行需求:

* python3-requests
* python3-pyexecjs + 任意js解析如nodejs
* python3-josn
* python-lxml
* Tessertact二进制工具

####工作说明：
* 自动识别验证码和充值
* 指定money_max,校园卡号,支付password即可
* 需要签约银行卡
* 30秒检测一次

####提示：
* 可能用来暴力破解校园卡系统的用户支付密码
* 在远程服务器上运行此脚本main.py
* 使用screen保留会话
* 如果想手动识别验证码，自己改代码login逻辑,服务器上的验证码scp下来即可	
