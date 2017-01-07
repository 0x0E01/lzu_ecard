import os

def img_to_str(imgname):
	os.system("tesseract %s cap_res 2>/dev/null" %(imgname))
	f = open('cap_res.txt','r')
	str = f.read()
		
	f.close()
	return str.replace('\r','').replace('\n','').replace(' ','')