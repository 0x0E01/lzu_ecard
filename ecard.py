import encrypt
import requests
import json
import ocr
from lxml import  etree

class EcardHandler:
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.rsa = encrypt.encrypter()
    def login(self):
        self.sess = requests.Session()
        self.sess.get('https://ecard.lzu.edu.cn',timeout=60)

        ##获取验证码
        img = self.sess.get('https://ecard.lzu.edu.cn/jcaptcha.jpg',timeout=60)
        f = open('cap.jpg', 'w+b')
        f.write(img.content)
        f.close()
        
        self.sess.headers['X-Requested-With'] = 'XMLHttpRequest'
        ##获取远程公钥信息
        key = self.sess.post('https://ecard.lzu.edu.cn/publiccombo/keyPair',timeout=60)
        key_json = json.loads(key.text)
        str_e = key_json['publicKeyMap']['exponent']
        str_m = key_json['publicKeyMap']['modulus']
        ##加密登陆用户帐号密码
        enc_name = self.rsa.enc(str_e, str_m, self.username)
        enc_pass = self.rsa.enc(str_e, str_m, self.password)

        code = ocr.img_to_str('cap.jpg')
        print('验证码识别为: %s' %(code))

        datas = {'username': enc_name, 'password': enc_pass, 'jcaptchacode': code}

        page = self.sess.post('https://ecard.lzu.edu.cn/lzulogin', data=datas,timeout=60)
        self.sess.headers.pop('X-Requested-With')

        msg = json.loads(page.text)

        if msg['ajaxState'] == '3':
            return '登陆成功'
        else:
            return msg['msg']

    def get_balance(self):
        con = self.sess.get('https://ecard.lzu.edu.cn/',timeout=60)
        doc = etree.HTML(con.text)
        balances = doc.xpath('//div[@class="balance-panel col-md-6"]/p/text()')

        if 'login' in con.url:
            return 80000
        if len(balances) == 0:
            return 90000
        else:
            str_balance = balances[0]

        str_balance = str_balance.replace('\t', '').replace('\n', '').replace('\r', '')
        self.balance = float(str_balance)
        return self.balance



    def get_quick_pay_info(self):
        con = self.sess.get('https://ecard.lzu.edu.cn/',timeout=60)
        doc = etree.HTML(con.text)

        ##第一步，获取eWalletId和cardAccNum并post到topUp
        ##0是校园卡，1是电子钱包，目前不用
        eWalletId = doc.xpath('//div[@class="operation"]/input[@id="eWalletId"]/@value')[0]
        cardAccNum = doc.xpath('//div[@class="operation"]/input[@id="cardAccNum"]/@value')[0]
        ##获取签约银行卡数目
        cardNum = doc.xpath('//div[@class="bank-info col-md-4"]/h4/em/text()')[0]

        self.cardInfo = {'eWalletId':eWalletId,'cardAccNum':cardAccNum,'cardNum':cardNum}
        return self.cardInfo

    def get_bank_info(self,bank):
        info = {
            '中国工商银行':{'name':'ICBC','id':'4'},
            '邮政储蓄':{'name':'PSBC','id':'2'},
            '中国银行':{'name':'BC','id':'1'}
        }
        if bank in info:
            return info[bank]
        else:
            return None


    def charge(self,str_value):
        info = self.get_quick_pay_info()

        if int(self.cardInfo['cardAccNum']) <1:
            return '银行卡未绑定'
        #银行卡没绑定

        datas = {
            'eWalletId':self.cardInfo['eWalletId'],
            'cardAccNum':self.cardInfo['cardAccNum']
        }
        #Topup界面获取银行卡详细信息
        self.sess.headers['X-Requested-With'] = 'XMLHttpRequest'
        con = self.sess.post('https://ecard.lzu.edu.cn/topUp', data=datas,timeout=60)
        doc = etree.HTML(con.text)
        ##解析Topup页面
        bankcardId = doc.xpath('//div[@class="pay-box quick-pay"]/label/input/@value')[0]
        bankcardCompany = doc.xpath('//div[@class="pay-box quick-pay"]/label/i/@title')[0]
        bankcardMask = doc.xpath('//div[@class="pay-box quick-pay"]/label/i/span/text()')[0]

        #构造确认页面请求数据
        bankinfo = self.get_bank_info(bankcardCompany)
        datas = {
            'cardAccNum': self.cardInfo['cardAccNum'],
            'eWalletId': self.cardInfo['eWalletId'],
            'eWalletName': u'校园卡',
            'dayLimit': '1000',
            'oneLimit': '300',
            'moneyMax': '900',
            'continueTopUpMoney': '300',
            'bankCardNum': bankcardId,
            'bankCardNumWithAsterisk': bankcardMask,
            'bankId': bankinfo['id'],
            'logoFileName': bankinfo['name']
        }
        con = self.sess.post('https://ecard.lzu.edu.cn/topUp/confirm', data=datas,timeout=60)
        doc = etree.HTML(con.text)

        ##获取交易Token
        token = doc.xpath('//input[@name="token"]/@value')[0]

        ##获取远程公钥模数m和公钥指数e
        con = self.sess.post('https://ecard.lzu.edu.cn/publiccombo/keyPair',timeout=60)
        key_json = json.loads(con.text)
        str_e = key_json['publicKeyMap']['exponent']
        str_m = key_json['publicKeyMap']['modulus']

        ##生成RSA公钥，NO_PADDING方式加密交易密码
        enc_pass = self.rsa.enc(str_e,str_m,self.password)
        datas = {'paypassword': enc_pass}
        page = con = self.sess.post('https://ecard.lzu.edu.cn/publiccombo/checkpaypwd', data=datas,timeout=60)

        ##TODO: ajaxState = 3 校验成功
        msg = json.loads(page.text)

        if not msg['ajaxState'] == '3':
            return msg['msg']

        ##构造充值请求数据
        datas ={
            'cardAccNum': self.cardInfo['cardAccNum'],
            'eWalletId': self.cardInfo['eWalletId'],
            'bankCardNum': bankcardId,
            'bankId': bankinfo['id'],
            'money':str_value,
            'token':token
        }
        con = self.sess.post('https://ecard.lzu.edu.cn/topUp/quickPay',data=datas,timeout=60)

        ##解析充值结果页数据
        doc = etree.HTML(con.text)
        result = doc.xpath('//div[@class="result-info"]/p/strong/text()')[0].replace('\t', '').replace('\n', '').replace('\r', '')
        return result
