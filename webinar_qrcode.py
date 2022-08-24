import pymysql
import requests
import qrcode
import os

UPLOAD_FOLDER = '/tmp'
BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'
# UPLOAD_FOLDER = 'uploads'
# BASE_URL = 'http://127.0.0.1:5000/'
'''def connnect_userLibrary():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_user_library',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def connnect_userLibrary():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_user_library',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

def generateQRCode(liveId,meetingURL,user_id):
	encrypted_id = meetingURL
	
	connection = connnect_userLibrary()
	cursor = connection.cursor()
	# 
	if encrypted_id:
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=6,
			border=2,
		)
		qr.add_data(encrypted_id)
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white")
		filename = str(liveId)+'-webinar.png'
		image_link = os.path.join(UPLOAD_FOLDER,filename)
		img.save(image_link)
		# print(image_link)
		uploadURL = BASE_URL + 'aws_portal/awsResourceController/uploadToS3Bucket/{}'.format(user_id)
		headers = {"content-type": "multipart/form-data"}
		files = {'file':(filename, open(image_link, 'rb'))}
		uploadRes = requests.post(uploadURL,files=files).json()
		# print(uploadRes)
		qrcodeUrl = uploadRes.get('responseList')[0].get('FilePath')

		qrUpdate = ("""UPDATE `liveclass_mapping` SET `is_webinar` = 1 , `webinar_qrcode` = %s
			WHERE `liveclass_id` = %s""")

		cursor.execute(qrUpdate,(qrcodeUrl,liveId))
		os.remove(image_link)
		connection.commit()
		cursor.close()
		return qrcodeUrl
# generateQRCode(34,'123',2962)