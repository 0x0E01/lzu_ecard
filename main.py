import ecard
import time
import schedual

money_max = 30.00
username = '校园卡号'
password = '密码'


s = schedual.Schedualer(username,password,money_max)
while True:

	try:
		s.log("调度器启动....")
		msg = s.run()
		s.log("调度器已退出,将休眠10分钟,原因： %s" % (msg))
	except Exception as e:
		s.log("网络异常,调度器退出，将休眠10分钟:")
		s.log("错误详情: %s" %(str(e)))
	time.sleep(600)
