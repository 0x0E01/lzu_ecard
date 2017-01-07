import execjs

class encrypter:
    def __init__(self):
        ##读取文件
        file = open('security.js','r')
        script = file.read()
        file.close()
        self.context = execjs.compile(script)

    def enc(self,e,m,str):
        enc_str = self.context.call("encrypt",e,m,str)
        return enc_str