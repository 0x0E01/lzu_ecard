import ecard
import time
import os

class Schedualer:
	def __init__(self,username,password,money_max):
		self.handler = ecard.EcardHandler(username,password)
		self.money_max = money_max
	def log(self,msg):
		t = time.localtime()
		str_time = "%s-%s %s:%s:%s" %(t[1],t[2],t[3],t[4],t[5])
		print("[%s] %s" %(str_time,msg))

#	def is_server_available(self):
#		try:
#			self.handler.sess.get("http://ecard.lzu.edu.cn/")
#		except Exception:
#
#		return True


	def can_charge(self):
		t = time.localtime()
		h = t[3]

		if h<22 or h >6:
			return True
		else:
			return False

	def run(self):
		##一直运行直到遇到重大异常再退出

		flag = False

		for i in range(0, 5):
			self.log("尝试第%d/5次登陆" % (i + 1))
			login_res = self.handler.login()
			self.log(login_res)

			if '验证码' in login_res:
				continue
			if '成功' in login_res:
				flag = True
				break

		if not flag:
			return "登陆失败,验证码识别故障"

		#余额轮询
		while True:
			balance = self.handler.get_balance()
			self.log("余额信息:%.2f 元" % (balance))

			if balance > 10000:
				return "余额查询失败,会话失效"


			if balance < self.money_max:
				if not self.can_charge():
					self.log("非充值时间段，不执行充值")
					time.sleep(60)
					continue

				money = self.money_max - balance
				str_money = "%.2f" % (money)

				self.log("预计充值: %s 元" % (str_money))
				charge_res = self.handler.charge(str_money)

				if '成功' not in charge_res:
					self.log("充值失败: %s" % (charge_res))
				else:
					self.log("充值成功: %s 元" % (str_money))

			time.sleep(60)
