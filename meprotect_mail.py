from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,date
from datetime import timedelta
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from pyfcm import FCMNotification
import requests
import pymysql
import smtplib
import imghdr
import io
import re
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import random
import string
import json, datetime
# from urllib.request import urlopen
# import urllib2
app = Flask(__name__)
cors = CORS(app)
meprotect_mail = Blueprint('meprotect_mail_api', __name__)
api = Api(meprotect_mail, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('CommunicationAPI', description='Email')

'''def mysql_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_communication',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def mysql_connection1():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_logindb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection'''

def mysql_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_communication',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def mysql_connection1():
    connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
                                 user='admin',
                                 password='cbdHoRPQPRfTdC0uSPLt',
                                 db='creamson_logindb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def meeprotect():
    connection = pymysql.connect(host='techdrive.xyz',
                                 user='techdrive_meprote',
                                 password='Webs_$#@!56',
                                 db='techdrive_meprotect',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def mobileprotection():
    connection = pymysql.connect(host='techdrive.xyz',
                                 user='techdrive_meprote',
                                 password='Webs_$#@!56',
                                 db='techdrive_mobileProtection',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

    
app.config['CORS_HEADERS'] = 'Content-Type'

EMAIL_ADDRESS = 'communications@creamsonservices.com'
EMAIL_PASSWORD = 'CReam7789%$intELLi'

devicetrack_model = api.model('devicetrack_model', {
	"toMail":fields.String(),
	"location":fields.String()
	})

intruder_model = api.model('intruder_model', {
	"toMail":fields.String(),
	"w_user": fields.String(),
	"w_image":fields.String(),
	"location":fields.String()
	})

meeprotectmail_model = api.model('meeprotectmail_model', {
	"toMail":fields.String(),
	"subject":fields.String(),
	"compose":fields.String()
	})

act_code = api.model('act_code', {
	"prod_id": fields.Integer(),
	"plan": fields.String(),
	"generate_no": fields.Integer(),
	"channel_users_id": fields.Integer()
    })

WalletTransferToChild = api.model('WalletTransferToChild', {
	"form_au_id": fields.Integer(),
	"to_au_id": fields.Integer(),
	"transfer_balance": fields.Integer()
    })

appmsg_model = api.model('appmsg_model', {
	"user_id": fields.Integer(),
	"title": fields.String(),
	"msg": fields.String()
    })

appmsgmodel = api.model('appmsgmodel', {
	"appmsgmodel":fields.List(fields.Nested(appmsg_model))
	})

walletdeduction = api.model('walletdeduction', {
	"user_id": fields.Integer(),
	"appname": fields.String()
	})

retappmsg = api.model('retappmsg', {
	"user_id": fields.Integer(),
	"appname": fields.String()
	})

walletdeductionV2 = api.model('walletdeductionV2', {
	"retcode": fields.String(),
	"appname": fields.String()
	})

retappmsgV2 = api.model('retappmsgV2', {
	"retcode": fields.String(),
	"appname": fields.String()
	})

protectionplan_model = api.model('protectionplan_model', {
	"ret_code": fields.String()
})

mail_protection_model = api.model('mail_protection_model', {
	"imei": fields.String(),
	"w_invno": fields.String(),
	"currdate": fields.String(),
	"w_invamt": fields.String(),
	"totlamt": fields.String(),
	"validity": fields.String(),
	"act_pack_code": fields.String(),
	"emailid": fields.String()
})

mail_unlock_feature_model = api.model('mail_unlock_feature_model', {
	"u_imei" : fields.String(),
	"validity": fields.String(),
	"emailid": fields.String()
})

#----------------------------------------------------------------------------#

BASE_URL = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/"

# BASE_URL = "http://127.0.0.1:5000/"

@name_space.route("/mailForIntruderSelfie")
class mailForIntruderSelfie(Resource):
	@api.expect(intruder_model)
	def post(self):

		details = request.get_json()

		toMail = details['toMail']
		w_user = details['w_user']
		w_image = details['w_image']
		location = details['location']

		res = 'sent'
		delRes = intruder_email(toMail,w_user,w_image,location)
		print(delRes)
		if delRes == 'Success':
			res = 'sent'
		else:
			res = []
		return ({"attributes": {"status_desc": "Communication Status",
									"status": "success"
									},
					"responseList":res}), status.HTTP_200_OK


def intruder_email(toMail,w_user,w_image,location):
	user_info = toMail
	res = 'Failure. Wrong MailId'

	if user_info:
		msg = MIMEMultipart()
		msg['Subject'] = 'Someone is trying to unlock your Phone'
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = user_info
		html = """<html>
                    <head>
                    <title>Meprotect.com</title>
                    </head>
                    <body>
                    <p>
                    Hello,<br><br>

                    %s is in emergency. photo %s and location %s.<br><br>
                    
                    Thank you for choosing MeeProtect>br><br><br>
                    
                    MeeProtect Support Team<br>
                      E-mail: - support@meeprotect.com<br>
                      Website: www.meeprotect.com<br>
                        
                      <small><b>Important Links:</b><br>
                      Web Dashboard: www.meeprotect.com/customer<br>
                      End User License Agreement: <a href='http://techdrive.xyz/MeeProtectEndUserLicenseAgreement.pdf'>Click To View</a><br>
                      Privacy Policy: <a href='http://techdrive.xyz/MeeProtectPrivacyPolicy.pdf'>Click To View </a></small></p><br>
                        
                      </body>
                </html>"""		
		message = html % (w_user,w_image,location)
		# print(message)
		part1 = MIMEText(message, 'html')
		msg.attach(part1)
		try:
			smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
			smtp.starttls()
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.sendmail(EMAIL_ADDRESS, user_info, msg.as_string())
			
			res = 'Success'
			sent = 'Y'
			
		except Exception as e:
			res = 'Failure'
			sent = 'N'
			# print(res)
		smtp.quit()
	
	return res
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
@name_space.route("/mailForPanic")
class mailForPanic(Resource):
	@api.expect(devicetrack_model)
	def post(self):

		details = request.get_json()

		toMail = details['toMail']
		location = details['location']

		res = 'sent'
		delRes = panic_email(toMail,location)
		if delRes == 'Success':
			res = 'sent'
		else:
			res = []
		return ({"attributes": {"status_desc": "Communication Status",
									"status": "success"
									},
					"responseList":res}), status.HTTP_200_OK


def panic_email(toMail,location):
	user_info = toMail
	res = 'Failure. Wrong MailId'

	if user_info:
		msg = MIMEMultipart()
		msg['Subject'] = 'Please Help'
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = user_info
		html = """<html>
                        <head>
                        <title>Meprotect.com</title>
                        </head>
                        <body>
                        <p>
                        Dear User,<br> 
                        
                        I am in danger.Please help.My location is %s.<br><br>
			            
			            Thank you for choosing MeeProtect>br><br><br>
                        
                        
                        
                        MeeProtect Support Team<br>
                          E-mail: - support@meeprotect.com<br>
                          Website: www.meeprotect.com<br>
                            
                          <small><b>Important Links:</b><br>
                          Web Dashboard: www.meeprotect.com/customer<br>
                          End User License Agreement: <a href='http://techdrive.xyz/MeeProtectEndUserLicenseAgreement.pdf'>Click To View</a><br>
                          Privacy Policy: <a href='http://techdrive.xyz/MeeProtectPrivacyPolicy.pdf'>Click To View </a></small></p><br>
                            
                          </body>
                            </html>"""
		message = html % (location)
		# print(message)
		part1 = MIMEText(message, 'html')
		msg.attach(part1)
		try:
			smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
			smtp.starttls()
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.sendmail(EMAIL_ADDRESS, user_info, msg.as_string())
			
			res = {"status":'Success'}
			sent = 'Y'
			
		except Exception as e:
			res = {"status":'Failure'}
			sent = 'N'
			# raise e
		smtp.quit()
	
	return res
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
@name_space.route("/mailForDeviceTrack")
class mailForDeviceTrack(Resource):
	@api.expect(devicetrack_model)
	def post(self):

		details = request.get_json()

		toMail = details['toMail']
		location = details['location']

		res = 'sent'
		delRes = send_email(toMail,location)
		if delRes == 'Success':
			res = 'sent'
		
		return ({"attributes": {"status_desc": "Communication Status",
									"status": "success"
									},
					"responseList":res}), status.HTTP_200_OK

#----------------------------------------------------------------------------#
@name_space.route("/mailForAddProtection")
class mailForAddProtection(Resource):
	@api.expect(mail_protection_model)
	def post(self):

		details = request.get_json()

		imei = details['imei']
		w_invno = details['w_invno']
		currdate = details['currdate']
		w_invamt = details['w_invamt']
		totlamt = details['totlamt']
		validity = details['validity']
		emailid = details['emailid']
		act_pack_code = details['act_pack_code']

		res = 'sent'
		delRes = send_email_protection(emailid,imei,w_invno,currdate,w_invamt,totlamt,validity,act_pack_code,emailid)
		if delRes == 'Success':
			res = 'sent'
		
		return ({"attributes": {"status_desc": "Communication Status",
									"status": "success"
									},
					"responseList":res}), status.HTTP_200_OK


#----------------------------------------------------------------------------#
@name_space.route("/mailForUnlockFeatures")
class mailForUnlockFeatures(Resource):
	@api.expect(mail_unlock_feature_model)
	def post(self):

		details = request.get_json()

		imei = details['u_imei']
		validity = details['validity']
		emailid = details['emailid']

		res = 'sent'
		delRes = send_email_unlock_feature(emailid,imei,validity)
		if delRes == 'Success':
			res = 'sent'
		
		return ({"attributes": {"status_desc": "Communication Status",
									"status": "success"
									},
					"responseList":res}), status.HTTP_200_OK


def send_email_unlock_feature(toMail,imei,validity):
	user_info = toMail
	res = 'Failure. Wrong MailId'

	if user_info:
		msg = MIMEMultipart()
		msg['Subject'] = 'Activate Unlock Feature'
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = user_info
		html = """<html>
                        <head>
                        <title>Meprotect.com</title>
                        </head>
                        <body>
                        <p>
                        Dear User,<br> 
                       	Thank you for choosing unlock feature . All feature has been activated for your device with the following details: IMEI : %s <br>
						Validity : %s
                        
                            
                        </body>
                        </html>"""
		message = html % (imei,validity)
		# print(message)
		part1 = MIMEText(message, 'html')
		msg.attach(part1)
		try:
			smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
			smtp.starttls()
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.sendmail(EMAIL_ADDRESS, user_info, msg.as_string())
			
			res = {"status":'Success'}
			sent = 'Y'
			
		except Exception as e:
			res = {"status":'Failure'}
			sent = 'N'
			# raise e
		smtp.quit()
	
	return res

def send_email_protection(toMail,imei,w_invno,currdate,w_invamt,totlamt,validity,act_pack_code,emailid):
	user_info = toMail
	res = 'Failure. Wrong MailId'

	if user_info:
		msg = MIMEMultipart()
		msg['Subject'] = 'Activate Protection Plus'
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = user_info
		html = """<html>
                        <head>
                        <title>Meprotect.com</title>
                        </head>
                        <body>
                        <p>
                        Dear User,<br> 
                        Thank you for choosing Protection Plus. Protection Plus has been activated for your device with the following details: <br>
                        IMEI : %s <br>
                        Invoice Number: %s <br>
                        Invoice Date: %s <br>
                        Invoice Amount: %s <br>
                        Total Amount paid: %s <br>
                        Validity : %s <br>
                        Package Code : %s
                        
                            
                        </body>
                        </html>"""
		message = html % (imei,w_invno,currdate,w_invamt,totlamt,validity,act_pack_code)
		# print(message)
		part1 = MIMEText(message, 'html')
		msg.attach(part1)
		try:
			smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
			smtp.starttls()
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.sendmail(EMAIL_ADDRESS, user_info, msg.as_string())
			
			res = {"status":'Success'}
			sent = 'Y'
			
		except Exception as e:
			res = {"status":'Failure'}
			sent = 'N'
			# raise e
		smtp.quit()
	
	return res



def send_email(toMail,location):
	user_info = toMail
	res = 'Failure. Wrong MailId'

	if user_info:
		msg = MIMEMultipart()
		msg['Subject'] = 'Device Location'
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = user_info
		html = """<html>
                        <head>
                        <title>Meprotect.com</title>
                        </head>
                        <body>
                        <p>
                        Dear User,<br> 
                        
                        Your device location is %s .<br><br>
                        
                      Thank you for choosing Meprotect<br><br><br>
                        
                        
                      MeeProtect Support Team<br>
                          E-mail: - support@meeprotect.com<br>
                          Website: www.meeprotect.com<br>
                            
                          <small><b>Important Links:</b><br>
                          Web Dashboard: www.meeprotect.com/customer<br>
                          End User License Agreement: <a href='http://techdrive.xyz/MeeProtectEndUserLicenseAgreement.pdf'>Click To View</a><br>
                          Privacy Policy: <a href='http://techdrive.xyz/MeeProtectPrivacyPolicy.pdf'>Click To View </a></small></p><br>
                            
                          </body>
                            </html>"""
		message = html % (location)
		# print(message)
		part1 = MIMEText(message, 'html')
		msg.attach(part1)
		try:
			smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
			smtp.starttls()
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.sendmail(EMAIL_ADDRESS, user_info, msg.as_string())
			
			res = {"status":'Success'}
			sent = 'Y'
			
		except Exception as e:
			res = {"status":'Failure'}
			sent = 'N'
			# raise e
		smtp.quit()
	
	return res
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
@name_space.route("/SendEmail")
class SendEmail(Resource):
	@api.expect(meeprotectmail_model)
	def post(self):

		details = request.get_json()

		toMail = details['toMail']
		# cc = details['ccMail']
		# bcc = details['bccMail']
		sub = details['subject']
		compose = details['compose']

		res = {"status":'Success'}
		delRes = email(toMail,sub,compose)
		if delRes == res:
			res = 'sent'
		else:
			res = []
		return ({"attributes": {"status_desc": "Communication Status",
									"status": "success"
									},
					"responseList":res}), status.HTTP_200_OK


def email(toMail,sub,compose):
	conn = meeprotect()
	cur = conn.cursor()
	user_info = toMail
	subject = sub
	com = compose
	res = 'Failure. Wrong MailId'

	if user_info:
		msg = MIMEMultipart()
		msg['Subject'] = subject
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = user_info
		html = compose
		message = html
		# print(message)
		email_query = ("""INSERT INTO `app_email`(`u_emailid`, `receipt_flag`) VALUES (%s,%s)""")
		email_data = (user_info,'Yes')
		cur.execute(email_query,email_data)
		part1 = MIMEText(message, 'html')
		msg.attach(part1)
		try:
			smtp = smtplib.SMTP('mail.creamsonservices.com', 587)
			smtp.starttls()
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.sendmail(EMAIL_ADDRESS, user_info, msg.as_string())
			
			res = {"status":'Success'}
			sent = 'Y'
			
		except Exception as e:
			res = {"status":'Failure'}
			sent = 'N'
			# raise e
		smtp.quit()
	
	return res
#----------------------------------------------------------------------------#
@name_space.route("/Subscriptiondtls/<string:emailid>")
class Subscriptiondtls(Resource):
	def get(self,emailid):

		conn = meeprotect()
		cur = conn.cursor()
		
		cur.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,
			`u_date_of_birth`,`u_aniversary`,`u_imei`,`u_device`,`u_date`,
			`u_mobile`,`u_ret_code`,`u_activ_code`,`u_pack_code`,`validity_start`,
			`validity_end` FROM `tbl_user` 
			WHERE u_email_id= %s and u_activ_code!=''""",(emailid))
		Subscriptiondtls = cur.fetchall()

		for i in range(len(Subscriptiondtls)):
			Subscriptiondtls[i]['u_date'] = Subscriptiondtls[i]['u_date'].isoformat()
			
			if Subscriptiondtls[i]['u_date_of_birth']=='0000-00-00':
				Subscriptiondtls[i]['u_date_of_birth'] = '0000-00-00'
			else:
				Subscriptiondtls[i]['u_date_of_birth'] = Subscriptiondtls[i]['u_date_of_birth'].isoformat()
			
			if Subscriptiondtls[i]['u_aniversary']=='0000-00-00':
				Subscriptiondtls[i]['u_aniversary'] = '0000-00-00'
			else:
				Subscriptiondtls[i]['u_aniversary'] = Subscriptiondtls[i]['u_aniversary'].isoformat()
				
			if Subscriptiondtls[i]['validity_start']=='0000-00-00':
				Subscriptiondtls[i]['validity_start'] = '0000-00-00'
			else:
				Subscriptiondtls[i]['validity_start'] = Subscriptiondtls[i]['validity_start'].isoformat()
				
			if Subscriptiondtls[i]['validity_end']=='0000-00-00':
				Subscriptiondtls[i]['validity_end'] = '0000-00-00'
			else:
				Subscriptiondtls[i]['validity_end'] = Subscriptiondtls[i]['validity_end'].isoformat()

		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Subscriptiondtls Details",
								"status": "success"
								},
				"responseList": Subscriptiondtls}), status.HTTP_200_OK



@name_space.route("/TotalActivationDtls/<int:channel_users_id>")
class TotalActivationDtls(Resource):
	def get(self,channel_users_id):

		conn = meeprotect()
		cursor = conn.cursor()
		detail = []
		details = []
		TotalActivationDtls = []

		channel_id = channel_users_id
		cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users` 
			WHERE `au_id`=%s""",(channel_id))
		ChannelDtls = cursor.fetchone()
		if ChannelDtls:
			cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
			   WHERE `au_parent`=%s""",(channel_id))
			ChannelChildDtls = cursor.fetchall()
			# print(ChannelChildDtls)
			if ChannelChildDtls:
				i = 0
				while(i<len(ChannelChildDtls)):

					channelid = ChannelChildDtls[i]['au_id']
					cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
					   WHERE `au_parent`=%s""",(channelid))
					ChannelDtl = cursor.fetchall()
					# print(ChannelDtl)
					if ChannelDtl == ():
						cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
						`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
						`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
						WHERE `u_ret_code`= %s""",format(ChannelChildDtls[i]['au_code']))
						ActivationDtls = cursor.fetchall()
						# print(ActivationDtls)
						if 	ActivationDtls:
							for j in range(len(ActivationDtls)):
								ActivationDtls[j]['u_date'] = ActivationDtls[j]['u_date'].isoformat()
								
								if ActivationDtls[j]['u_date_of_birth']=='0000-00-00':
									ActivationDtls[j]['u_date_of_birth'] = '0000-00-00'
								else:
									ActivationDtls[j]['u_date_of_birth'] = ActivationDtls[j]['u_date_of_birth'].isoformat()
								
								if ActivationDtls[j]['u_aniversary']=='0000-00-00':
									ActivationDtls[j]['u_aniversary'] = '0000-00-00'
								else:
									ActivationDtls[j]['u_aniversary'] = ActivationDtls[j]['u_aniversary'].isoformat()
									
								if ActivationDtls[j]['validity_start']=='0000-00-00':
									ActivationDtls[j]['validity_start'] = '0000-00-00'
								else:
									ActivationDtls[j]['validity_start'] = ActivationDtls[j]['validity_start'].isoformat()
									
								if ActivationDtls[j]['validity_end']=='0000-00-00':
									ActivationDtls[j]['validity_end'] = '0000-00-00'
								else:
									ActivationDtls[j]['validity_end'] = ActivationDtls[j]['validity_end'].isoformat()
							
							for k in range(len(ActivationDtls)):
								TotalActivationDtls.append(ActivationDtls[k])
							# print(TotalActivationDtls)
						i += 1
						continue
					else:
						for i in range(len(ChannelDtl)):
							cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
							`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
							`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
							WHERE `u_ret_code`= %s""",format(ChannelDtl[i]['au_code']))
							ActivationDtls = cursor.fetchall()
							# print(ActivationDtls)
							if 	ActivationDtls:
								for j in range(len(ActivationDtls)):
									ActivationDtls[j]['u_date'] = ActivationDtls[j]['u_date'].isoformat()
									
									if ActivationDtls[j]['u_date_of_birth']=='0000-00-00':
										ActivationDtls[j]['u_date_of_birth'] = '0000-00-00'
									else:
										ActivationDtls[j]['u_date_of_birth'] = ActivationDtls[j]['u_date_of_birth'].isoformat()
									
									if ActivationDtls[j]['u_aniversary']=='0000-00-00':
										ActivationDtls[j]['u_aniversary'] = '0000-00-00'
									else:
										ActivationDtls[j]['u_aniversary'] = ActivationDtls[j]['u_aniversary'].isoformat()
										
									if ActivationDtls[j]['validity_start']=='0000-00-00':
										ActivationDtls[j]['validity_start'] = '0000-00-00'
									else:
										ActivationDtls[j]['validity_start'] = ActivationDtls[j]['validity_start'].isoformat()
										
									if ActivationDtls[j]['validity_end']=='0000-00-00':
										ActivationDtls[j]['validity_end'] = '0000-00-00'
									else:
										ActivationDtls[j]['validity_end'] = ActivationDtls[j]['validity_end'].isoformat()
								
							for k in range(len(ActivationDtls)):
								TotalActivationDtls.append(ActivationDtls[k])
								# print(TotalActivationDtls)
							i += 1
							continue
			else:
				details = ChannelDtls['au_code']
				# print(details)
		else:
			TotalActivationDtls = []
		if details:
			cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
				`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
				`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
				WHERE `u_ret_code`=%s""",format(details))
			TotalActivationDtls = cursor.fetchall()
			# print(TotalActivationDtls)
				
			for i in range(len(TotalActivationDtls)):
				TotalActivationDtls[i]['u_date'] = TotalActivationDtls[i]['u_date'].isoformat()
				
				if TotalActivationDtls[i]['u_date_of_birth']=='0000-00-00':
					TotalActivationDtls[i]['u_date_of_birth'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['u_date_of_birth'] = TotalActivationDtls[i]['u_date_of_birth'].isoformat()
				
				if TotalActivationDtls[i]['u_aniversary']=='0000-00-00':
					TotalActivationDtls[i]['u_aniversary'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['u_aniversary'] = TotalActivationDtls[i]['u_aniversary'].isoformat()
					
				if TotalActivationDtls[i]['validity_start']=='0000-00-00':
					TotalActivationDtls[i]['validity_start'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['validity_start'] = TotalActivationDtls[i]['validity_start'].isoformat()
					
				if TotalActivationDtls[i]['validity_end']=='0000-00-00':
					TotalActivationDtls[i]['validity_end'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['validity_end'] = TotalActivationDtls[i]['validity_end'].isoformat()
		
		conn.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Activation Details",
	                                "status": "success"
                                },
				"responseList": TotalActivationDtls
	                 }), status.HTTP_200_OK



@name_space.route("/TodayActivationDtls/<int:channel_users_id>")
class TodayActivationDtls(Resource):
	def get(self,channel_users_id):

		conn = meeprotect()
		cursor = conn.cursor()
		detail = []
		details = []
		TotalActivationDtls = []
		today = date.today()

		channel_id = channel_users_id
		cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users` 
			WHERE `au_id`=%s""",(channel_id))
		ChannelDtls = cursor.fetchone()
		if ChannelDtls:
			cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
			   WHERE `au_parent`=%s""",(channel_id))
			ChannelChildDtls = cursor.fetchall()
			# print(ChannelChildDtls)
			if ChannelChildDtls:
				i = 0
				while(i<len(ChannelChildDtls)):

					channelid = ChannelChildDtls[i]['au_id']
					cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
					   WHERE `au_parent`=%s""",(channelid))
					ChannelDtl = cursor.fetchall()
					# print(ChannelDtl)
					if ChannelDtl == ():
						cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
						`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
						`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
						WHERE `u_date`=%s and `u_ret_code`=%s""",(today,format(ChannelChildDtls[i]['au_code'])))
						ActivationDtls = cursor.fetchall()
						# print(ActivationDtls)
						if ActivationDtls:
							for j in range(len(ActivationDtls)):
								ActivationDtls[j]['u_date'] = ActivationDtls[j]['u_date'].isoformat()
								
								if ActivationDtls[j]['u_date_of_birth']=='0000-00-00':
									ActivationDtls[j]['u_date_of_birth'] = '0000-00-00'
								else:
									ActivationDtls[j]['u_date_of_birth'] = ActivationDtls[j]['u_date_of_birth'].isoformat()
								
								if ActivationDtls[j]['u_aniversary']=='0000-00-00':
									ActivationDtls[j]['u_aniversary'] = '0000-00-00'
								else:
									ActivationDtls[j]['u_aniversary'] = ActivationDtls[j]['u_aniversary'].isoformat()
									
								if ActivationDtls[j]['validity_start']=='0000-00-00':
									ActivationDtls[j]['validity_start'] = '0000-00-00'
								else:
									ActivationDtls[j]['validity_start'] = ActivationDtls[j]['validity_start'].isoformat()
									
								if ActivationDtls[j]['validity_end']=='0000-00-00':
									ActivationDtls[j]['validity_end'] = '0000-00-00'
								else:
									ActivationDtls[j]['validity_end'] = ActivationDtls[j]['validity_end'].isoformat()
							
							for k in range(len(ActivationDtls)):
								TotalActivationDtls.append(ActivationDtls[k])
							# print(TotalActivationDtls)
						i += 1
						continue
					else:
						for i in range(len(ChannelDtl)):
							cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
							`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
							`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
							WHERE `u_date`=%s and `u_ret_code`= %s""",(today,format(ChannelDtl[i]['au_code'])))
							ActivationDtls = cursor.fetchall()
							# print(ActivationDtls)
							if 	ActivationDtls:
								for j in range(len(ActivationDtls)):
									ActivationDtls[j]['u_date'] = ActivationDtls[j]['u_date'].isoformat()
									
									if ActivationDtls[j]['u_date_of_birth']=='0000-00-00':
										ActivationDtls[j]['u_date_of_birth'] = '0000-00-00'
									else:
										ActivationDtls[j]['u_date_of_birth'] = ActivationDtls[j]['u_date_of_birth'].isoformat()
									
									if ActivationDtls[j]['u_aniversary']=='0000-00-00':
										ActivationDtls[j]['u_aniversary'] = '0000-00-00'
									else:
										ActivationDtls[j]['u_aniversary'] = ActivationDtls[j]['u_aniversary'].isoformat()
										
									if ActivationDtls[j]['validity_start']=='0000-00-00':
										ActivationDtls[j]['validity_start'] = '0000-00-00'
									else:
										ActivationDtls[j]['validity_start'] = ActivationDtls[j]['validity_start'].isoformat()
										
									if ActivationDtls[j]['validity_end']=='0000-00-00':
										ActivationDtls[j]['validity_end'] = '0000-00-00'
									else:
										ActivationDtls[j]['validity_end'] = ActivationDtls[j]['validity_end'].isoformat()
								
								for k in range(len(ActivationDtls)):
									TotalActivationDtls.append(ActivationDtls[k])
								# print(TotalActivationDtls)
							i += 1
							continue
			else:
				details = ChannelDtls['au_code']
				# print(details)
		else:
			TotalActivationDtls = []
		if details:
			cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
				`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
				`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
				WHERE `u_date`=%s and `u_ret_code`=%s""",(today,format(details)))
			TotalActivationDtls = cursor.fetchall()
			# print(TotalActivationDtls)
				
			for i in range(len(TotalActivationDtls)):
				TotalActivationDtls[i]['u_date'] = TotalActivationDtls[i]['u_date'].isoformat()
				
				if TotalActivationDtls[i]['u_date_of_birth']=='0000-00-00':
					TotalActivationDtls[i]['u_date_of_birth'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['u_date_of_birth'] = TotalActivationDtls[i]['u_date_of_birth'].isoformat()
				
				if TotalActivationDtls[i]['u_aniversary']=='0000-00-00':
					TotalActivationDtls[i]['u_aniversary'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['u_aniversary'] = TotalActivationDtls[i]['u_aniversary'].isoformat()
					
				if TotalActivationDtls[i]['validity_start']=='0000-00-00':
					TotalActivationDtls[i]['validity_start'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['validity_start'] = TotalActivationDtls[i]['validity_start'].isoformat()
					
				if TotalActivationDtls[i]['validity_end']=='0000-00-00':
					TotalActivationDtls[i]['validity_end'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['validity_end'] = TotalActivationDtls[i]['validity_end'].isoformat()
		
		conn.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Activation Details",
	                                "status": "success"
                                },
				"responseList": TotalActivationDtls
	                 }), status.HTTP_200_OK



@name_space.route("/UserBirthdayDtls/<int:channel_users_id>")
class UserBirthdayDtls(Resource):
	def get(self,channel_users_id):

		conn = meeprotect()
		cursor = conn.cursor()
		detail = []
		details = []
		TotalActivationDtls = []

		today = date.today()
		month = today.month
		day = today.day
		channel_id = channel_users_id
		cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users` 
			WHERE `au_id`=%s""",(channel_id))
		ChannelDtls = cursor.fetchone()
		if ChannelDtls:
			cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
			   WHERE `au_parent`=%s""",(channel_id))
			ChannelChildDtls = cursor.fetchall()
			# print(ChannelChildDtls)
			if ChannelChildDtls:
				i = 0
				while(i<len(ChannelChildDtls)):

					channelid = ChannelChildDtls[i]['au_id']
					cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
					   WHERE `au_parent`=%s""",(channelid))
					ChannelDtl = cursor.fetchall()
					# print(ChannelDtl)
					if ChannelDtl == ():
						cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
						`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
						`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
						WHERE MONTH(`u_date_of_birth`)=%s and 
						Day(`u_date_of_birth`)=%s and  `u_ret_code`= %s""",(month,day,format(ChannelChildDtls[i]['au_code'])))
						ActivationDtls = cursor.fetchall()
						# print(ActivationDtls)
						if 	ActivationDtls:
							for j in range(len(ActivationDtls)):
								ActivationDtls[j]['u_date'] = ActivationDtls[j]['u_date'].isoformat()
								
								if ActivationDtls[j]['u_date_of_birth']=='0000-00-00':
									ActivationDtls[j]['u_date_of_birth'] = '0000-00-00'
								else:
									ActivationDtls[j]['u_date_of_birth'] = ActivationDtls[j]['u_date_of_birth'].isoformat()
								
								if ActivationDtls[j]['u_aniversary']=='0000-00-00':
									ActivationDtls[j]['u_aniversary'] = '0000-00-00'
								else:
									ActivationDtls[j]['u_aniversary'] = ActivationDtls[j]['u_aniversary'].isoformat()
									
								if ActivationDtls[j]['validity_start']=='0000-00-00':
									ActivationDtls[j]['validity_start'] = '0000-00-00'
								else:
									ActivationDtls[j]['validity_start'] = ActivationDtls[j]['validity_start'].isoformat()
									
								if ActivationDtls[j]['validity_end']=='0000-00-00':
									ActivationDtls[j]['validity_end'] = '0000-00-00'
								else:
									ActivationDtls[j]['validity_end'] = ActivationDtls[j]['validity_end'].isoformat()
							
							for k in range(len(ActivationDtls)):
								TotalActivationDtls.append(ActivationDtls[k])
							# print(TotalActivationDtls)
						i += 1
						continue
					else:
						for i in range(len(ChannelDtl)):
							cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
							`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
							`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
							WHERE MONTH(`u_date_of_birth`)=%s and 
							Day(`u_date_of_birth`)=%s and `u_ret_code`= %s""",(month,day,format(ChannelDtl[i]['au_code'])))
							ActivationDtls = cursor.fetchall()
							# print(ActivationDtls)
							if 	ActivationDtls:
								for j in range(len(ActivationDtls)):
									ActivationDtls[j]['u_date'] = ActivationDtls[j]['u_date'].isoformat()
									
									if ActivationDtls[j]['u_date_of_birth']=='0000-00-00':
										ActivationDtls[j]['u_date_of_birth'] = '0000-00-00'
									else:
										ActivationDtls[j]['u_date_of_birth'] = ActivationDtls[j]['u_date_of_birth'].isoformat()
									
									if ActivationDtls[j]['u_aniversary']=='0000-00-00':
										ActivationDtls[j]['u_aniversary'] = '0000-00-00'
									else:
										ActivationDtls[j]['u_aniversary'] = ActivationDtls[j]['u_aniversary'].isoformat()
										
									if ActivationDtls[j]['validity_start']=='0000-00-00':
										ActivationDtls[j]['validity_start'] = '0000-00-00'
									else:
										ActivationDtls[j]['validity_start'] = ActivationDtls[j]['validity_start'].isoformat()
										
									if ActivationDtls[j]['validity_end']=='0000-00-00':
										ActivationDtls[j]['validity_end'] = '0000-00-00'
									else:
										ActivationDtls[j]['validity_end'] = ActivationDtls[j]['validity_end'].isoformat()
								
								for k in range(len(ActivationDtls)):
									TotalActivationDtls.append(ActivationDtls[k])								# print(TotalActivationDtls)
							i += 1
							continue
			else:
				details = ChannelDtls['au_code']
				# print(details)
		else:
			TotalActivationDtls = []
		if details:
			cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
				`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
				`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
				WHERE MONTH(`u_date_of_birth`)=%s and 
				Day(`u_date_of_birth`)=%s and  `u_ret_code`=%s""",(month,day,format(details)))
			TotalActivationDtls = cursor.fetchall()
			# print(TotalActivationDtls)
				
			for i in range(len(TotalActivationDtls)):
				TotalActivationDtls[i]['u_date'] = TotalActivationDtls[i]['u_date'].isoformat()
				
				if TotalActivationDtls[i]['u_date_of_birth']=='0000-00-00':
					TotalActivationDtls[i]['u_date_of_birth'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['u_date_of_birth'] = TotalActivationDtls[i]['u_date_of_birth'].isoformat()
				
				if TotalActivationDtls[i]['u_aniversary']=='0000-00-00':
					TotalActivationDtls[i]['u_aniversary'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['u_aniversary'] = TotalActivationDtls[i]['u_aniversary'].isoformat()
					
				if TotalActivationDtls[i]['validity_start']=='0000-00-00':
					TotalActivationDtls[i]['validity_start'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['validity_start'] = TotalActivationDtls[i]['validity_start'].isoformat()
					
				if TotalActivationDtls[i]['validity_end']=='0000-00-00':
					TotalActivationDtls[i]['validity_end'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['validity_end'] = TotalActivationDtls[i]['validity_end'].isoformat()
		
		conn.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Activation Details",
	                                "status": "success"
                                },
				"responseList": TotalActivationDtls
	                 }), status.HTTP_200_OK
		

@name_space.route("/UserAniversaryDtls/<int:channel_users_id>")
class UserAniversaryDtls(Resource):
	def get(self,channel_users_id):

		conn = meeprotect()
		cursor = conn.cursor()
		detail = []
		details = []
		TotalActivationDtls = []
		
		today = date.today()
		month = today.month
		day = today.day
		channel_id = channel_users_id
		cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users` 
			WHERE `au_id`=%s""",(channel_id))
		ChannelDtls = cursor.fetchone()
		if ChannelDtls:
			cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
			   WHERE `au_parent`=%s""",(channel_id))
			ChannelChildDtls = cursor.fetchall()
			# print(ChannelChildDtls)
			if ChannelChildDtls:
				i = 0
				while(i<len(ChannelChildDtls)):

					channelid = ChannelChildDtls[i]['au_id']
					cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
					   WHERE `au_parent`=%s""",(channelid))
					ChannelDtl = cursor.fetchall()
					# print(ChannelDtl)
					if ChannelDtl == ():
						cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
						`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
						`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
						WHERE MONTH(`u_aniversary`)=%s and 
						Day(`u_aniversary`)=%s and  `u_ret_code`= %s""",(month,day,format(ChannelChildDtls[i]['au_code'])))
						ActivationDtls = cursor.fetchall()
						# print(ActivationDtls)
						if 	ActivationDtls:
							for j in range(len(ActivationDtls)):
								ActivationDtls[j]['u_date'] = ActivationDtls[j]['u_date'].isoformat()
								
								if ActivationDtls[j]['u_date_of_birth']=='0000-00-00':
									ActivationDtls[j]['u_date_of_birth'] = '0000-00-00'
								else:
									ActivationDtls[j]['u_date_of_birth'] = ActivationDtls[j]['u_date_of_birth'].isoformat()
								
								if ActivationDtls[j]['u_aniversary']=='0000-00-00':
									ActivationDtls[j]['u_aniversary'] = '0000-00-00'
								else:
									ActivationDtls[j]['u_aniversary'] = ActivationDtls[j]['u_aniversary'].isoformat()
									
								if ActivationDtls[j]['validity_start']=='0000-00-00':
									ActivationDtls[j]['validity_start'] = '0000-00-00'
								else:
									ActivationDtls[j]['validity_start'] = ActivationDtls[j]['validity_start'].isoformat()
									
								if ActivationDtls[j]['validity_end']=='0000-00-00':
									ActivationDtls[j]['validity_end'] = '0000-00-00'
								else:
									ActivationDtls[j]['validity_end'] = ActivationDtls[j]['validity_end'].isoformat()
							
							for k in range(len(ActivationDtls)):
								TotalActivationDtls.append(ActivationDtls[k])
							# print(TotalActivationDtls)
						i += 1
						continue
					else:
						for i in range(len(ChannelDtl)):
							cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
							`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
							`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
							WHERE MONTH(`u_aniversary`)=%s and 
							Day(`u_aniversary`)=%s and `u_ret_code`= %s""",(month,day,format(ChannelDtl[i]['au_code'])))
							ActivationDtls = cursor.fetchall()
							# print(ActivationDtls)
							if 	ActivationDtls:
								for j in range(len(ActivationDtls)):
									ActivationDtls[j]['u_date'] = ActivationDtls[j]['u_date'].isoformat()
									
									if ActivationDtls[j]['u_date_of_birth']=='0000-00-00':
										ActivationDtls[j]['u_date_of_birth'] = '0000-00-00'
									else:
										ActivationDtls[j]['u_date_of_birth'] = ActivationDtls[j]['u_date_of_birth'].isoformat()
									
									if ActivationDtls[j]['u_aniversary']=='0000-00-00':
										ActivationDtls[j]['u_aniversary'] = '0000-00-00'
									else:
										ActivationDtls[j]['u_aniversary'] = ActivationDtls[j]['u_aniversary'].isoformat()
										
									if ActivationDtls[j]['validity_start']=='0000-00-00':
										ActivationDtls[j]['validity_start'] = '0000-00-00'
									else:
										ActivationDtls[j]['validity_start'] = ActivationDtls[j]['validity_start'].isoformat()
										
									if ActivationDtls[j]['validity_end']=='0000-00-00':
										ActivationDtls[j]['validity_end'] = '0000-00-00'
									else:
										ActivationDtls[j]['validity_end'] = ActivationDtls[j]['validity_end'].isoformat()
								
								for k in range(len(ActivationDtls)):
									TotalActivationDtls.append(ActivationDtls[k])
								# print(TotalActivationDtls)
							i += 1
							continue
			else:
				details = ChannelDtls['au_code']
				# print(details)
		else:
			TotalActivationDtls = []
		if details:
			cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
				`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
				`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
				WHERE MONTH(`u_aniversary`)=%s and 
				Day(`u_aniversary`)=%s and  `u_ret_code`=%s""",(month,day,format(details)))
			TotalActivationDtls = cursor.fetchall()
			# print(TotalActivationDtls)
				
			for i in range(len(TotalActivationDtls)):
				TotalActivationDtls[i]['u_date'] = TotalActivationDtls[i]['u_date'].isoformat()
				
				if TotalActivationDtls[i]['u_date_of_birth']=='0000-00-00':
					TotalActivationDtls[i]['u_date_of_birth'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['u_date_of_birth'] = TotalActivationDtls[i]['u_date_of_birth'].isoformat()
				
				if TotalActivationDtls[i]['u_aniversary']=='0000-00-00':
					TotalActivationDtls[i]['u_aniversary'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['u_aniversary'] = TotalActivationDtls[i]['u_aniversary'].isoformat()
					
				if TotalActivationDtls[i]['validity_start']=='0000-00-00':
					TotalActivationDtls[i]['validity_start'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['validity_start'] = TotalActivationDtls[i]['validity_start'].isoformat()
					
				if TotalActivationDtls[i]['validity_end']=='0000-00-00':
					TotalActivationDtls[i]['validity_end'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['validity_end'] = TotalActivationDtls[i]['validity_end'].isoformat()
		
		conn.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Activation Details",
	                                "status": "success"
                                },
				"responseList": TotalActivationDtls
	                 }), status.HTTP_200_OK


@name_space.route("/RetailerListDtls/<int:channel_users_id>")
class RetailerListDtls(Resource):
	def get(self,channel_users_id):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()
		
		cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,
			`au_parent`,`au_code`,`au_username`,`au_pass`  FROM 
			`tbl_channel_users` WHERE `au_id`=%s""",(channel_users_id))
		RetailerListDtls = cur.fetchone()
		
		if RetailerListDtls['au_parent']!= 0:
			cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,
			  `au_parent`,`au_code`,`au_username`,`au_pass`  FROM 
			  `tbl_channel_users` WHERE `au_id`=%s""",(RetailerListDtls['au_parent']))
			RetailerList = cur.fetchone()

			if RetailerList['au_parent']!= 0:
				cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,
				  `au_parent`,`au_code`,`au_username`,`au_pass`  FROM 
				  `tbl_channel_users` WHERE `au_id`=%s""",(RetailerList['au_parent']))
				Retailer = cur.fetchone()
		
		RetailerListdtls = [RetailerListDtls,RetailerList,Retailer]
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Retailer List Details",
								"status": "success"
								},
				"responseList": RetailerListdtls}), status.HTTP_200_OK



@name_space.route("/RetailerDashboardDtls/<int:channel_users_id>")
class RetailerDashboardDtls(Resource):
	def get(self,channel_users_id):

		conn = meeprotect()
		cursor = conn.cursor()
		detail = []
		detal = []
		detl = []
		det = []
		details = []

		today = date.today()
		month = today.month
		day = today.day
		channel_id = channel_users_id


		channel_id = channel_users_id
		cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users` 
			WHERE `au_id`=%s""",(channel_id))
		ChannelDtls = cursor.fetchone()
		if ChannelDtls:
			cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
			   WHERE `au_parent`=%s""",(channel_id))
			ChannelChildDtls = cursor.fetchall()
			# print(ChannelChildDtls)
			if ChannelChildDtls:
				i = 0
				while(i<len(ChannelChildDtls)):

					channelid = ChannelChildDtls[i]['au_id']
					cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
					   WHERE `au_parent`=%s""",(channelid))
					ChannelDtl = cursor.fetchall()
					# print(ChannelDtl)
					if ChannelDtl == ():
						# print(ChannelChildDtls[i]['au_code'])
						cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
							WHERE `u_ret_code`=%s""",format(ChannelChildDtls[i]['au_code'])) 
						totalActivation = cursor.fetchone()
						if totalActivation:
							# print("hi")
							ActNo = totalActivation['total']
							SUM = 0
							detail.append(ActNo)
							
							for ele in range(0, len(detail)):
								SUM = SUM + detail[ele]
								total = SUM
							
						else:
							total = 0

						cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
							WHERE `u_date`=%s and `u_ret_code`=%s""",(today,format(ChannelChildDtls[i]['au_code'])))
						todayAct = cursor.fetchone()
						if todayAct:
							todayActNo = todayAct['total']
							todaySUM = 0
							detal.append(todayActNo)
							for x in range(0, len(detal)):
								todaySUM = todaySUM + detal[x]
								todayActNo = todaySUM
								# print(todaySUM)
						else:
							todayActNo = 0

						cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
							WHERE MONTH(`u_date_of_birth`)=%s and 
		 					Day(`u_date_of_birth`)=%s and`u_ret_code`=%s""",(month,day,format(ChannelChildDtls[i]['au_code']))) 
						totalbdayUser = cursor.fetchone()
						if totalbdayUser:
							bdayUserActNo = totalbdayUser['total']
							bdayUserSUM = 0
							detl.append(bdayUserActNo)
							for j in range(0, len(detl)):
								bdayUserSUM = bdayUserSUM + detl[j]
								totalbdayUserNo = bdayUserSUM
								# print(bdayUserSUM)
						else:
							totalbdayUserNo = 0

						cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
							WHERE MONTH(`u_aniversary`)=%s and 
							Day(`u_aniversary`)=%s and `u_ret_code`=%s""",(month,day,format(ChannelChildDtls[i]['au_code'])))
						totalanvUser = cursor.fetchone()
						if totalanvUser:
							anvUserActNo = totalanvUser['total']
							anvUserSUM = 0
							det.append(anvUserSUM)
							for k in range(0, len(det)):
								anvUserSUM = anvUserSUM + det[k]
								totalanvUserNo = anvUserSUM
						else:
							totalanvUserNo = 0

						cursor.execute("""SELECT `wallet_id`,`channel_user_id`,`wallet_balance` 
					 		FROM `wallet_balance` WHERE `channel_user_id`=%s""",(channel_id))
						walletDtls = cursor.fetchone()
						if walletDtls:
							WalletBalance = walletDtls['wallet_balance']
							end_date = today + datetime.timedelta(days=WalletBalance)
							enddate = end_date.isoformat()
						else:
							WalletBalance = 0
							enddate = "" 
						i += 1
						continue
			
					else:
						for i in range(len(ChannelDtl)):
							cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
								WHERE `u_ret_code`=%s""",format(ChannelDtl[i]['au_code'])) 
							totalActivation = cursor.fetchone()
							if totalActivation:
								ActNo = totalActivation['total']
								SUM = 0
								detail.append(ActNo)
								for ele in range(0, len(detail)):
									SUM = SUM + detail[ele]
									total = SUM
								# print(SUM)
							else:
								Act = 0

							cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
								WHERE `u_date`=%s and `u_ret_code`=%s""",(today,format(ChannelChildDtls[i]['au_code'])))
							todayAct = cursor.fetchone()
							if todayAct:
								todayActNo = todayAct['total']
								todaySUM = 0
								detal.append(todayActNo)
								for x in range(0, len(detal)):
									todaySUM = todaySUM + detal[x]
									todayActNo = todaySUM
									# print(todaySUM)
							else:
								todayActNo = 0

							cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
								WHERE MONTH(`u_date_of_birth`)=%s and 
			 					Day(`u_date_of_birth`)=%s and`u_ret_code`=%s""",(month,day,format(ChannelChildDtls[i]['au_code']))) 
							totalbdayUser = cursor.fetchone()
							if totalbdayUser:
								bdayUserActNo = totalbdayUser['total']
								bdayUserSUM = 0
								detl.append(bdayUserActNo)
								for j in range(0, len(detl)):
									bdayUserSUM = bdayUserSUM + detl[j]
									totalbdayUserNo = bdayUserSUM
									# print(bdayUserSUM)
							else:
								bdayUser = 0

							cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
								WHERE MONTH(`u_aniversary`)=%s and 
								Day(`u_aniversary`)=%s and `u_ret_code`=%s""",(month,day,format(ChannelChildDtls[i]['au_code'])))
							totalanvUser = cursor.fetchone()
							if totalanvUser:
								anvUserActNo = totalanvUser['total']
								anvUserSUM = 0
								det.append(anvUserActNo)
								for k in range(0, len(det)):
									anvUserSUM = anvUserSUM + det[k]
									totalanvUserNo = anvUserSUM
							else:
								totalanvUserNo = 0

							cursor.execute("""SELECT `wallet_id`,`channel_user_id`,`wallet_balance` 
						 		FROM `wallet_balance` WHERE `channel_user_id`=%s""",(channel_id))
							walletDtls = cursor.fetchone()
							if walletDtls:
								WalletBalance = walletDtls['wallet_balance']
								end_date = today + datetime.timedelta(days=WalletBalance)
								enddate = end_date.isoformat()
							else:
								WalletBalance = 0
								enddate = ""
							i += 1
							continue
			
			else:
				details = ChannelDtls['au_code']
				# print(details)
		else:
			TotalActivationDtls = []
		if details:
			cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
				WHERE `u_ret_code`=%s""",format(details))
			totalActivation = cursor.fetchone()
			if totalActivation:
				totalActNo = totalActivation['total']
			else:
				totalActNo = 0
			
			cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
				WHERE `u_date`=%s and `u_ret_code`=%s""",(today,format(details)))
			todayAct = cursor.fetchone()
			if todayAct:
				todayActNo = todayAct['total']
			else:
				todayActNo = 0

			cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
				WHERE MONTH(`u_date_of_birth`)=%s and 
					Day(`u_date_of_birth`)=%s and`u_ret_code`=%s""",(month,day,format(details))) 
			totalbdayUser = cursor.fetchone()
			if totalbdayUser:
				totalbdayUserNo = totalbdayUser['total']
			else:
				totalbdayUserNo = 0

			cursor.execute("""SELECT count(DISTINCT(`u_email_id`))as total FROM `tbl_user` 
				WHERE MONTH(`u_aniversary`)=%s and 
				Day(`u_aniversary`)=%s and `u_ret_code`=%s""",(month,day,format(details)))
			totalanvUser = cursor.fetchone()
			if totalanvUser:
				totalanvUserNo = totalanvUser['total']
			else:
				totalanvUserNo = 0

			cursor.execute("""SELECT `wallet_id`,`channel_user_id`,`wallet_balance` 
		 		FROM `wallet_balance` WHERE `channel_user_id`=%s""",(channel_id))
			walletDtls = cursor.fetchone()
			if walletDtls:
				WalletBalance = walletDtls['wallet_balance']
				end_date = today + datetime.timedelta(days=WalletBalance)
				enddate = end_date.isoformat()
			else:
				WalletBalance = 0
				enddate = "" 
		

		if details:
			total = totalActNo
		return ({"attributes": {"status_desc": "Dashboard Details",
								"status": "success"
								},
				"responseList": {
								"totalActNo" : total,
			                    "todayActNo" : todayActNo,
			                    "totalbdayUserNo" : totalbdayUserNo,
			                    "totalanvUserNo" : totalanvUserNo,
			                    "WalletBalance" : WalletBalance,
			                    "end_date" : enddate,
			                    "totalsmsNo" : "1000"
							}
	            }), status.HTTP_200_OK




@name_space.route("/WalletBalance/<int:channel_users_id>")
class WalletBalance(Resource):
	def get(self,channel_users_id):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()
		
		cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,
			`au_parent`,`au_code`,`au_username`,`au_pass`  FROM 
			`tbl_channel_users` WHERE `au_id`=%s""",(channel_users_id))
		RetailerListDtls = cur.fetchone()
		
        
		if RetailerListDtls['au_parent']!= 0:
			cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,
			  `au_parent`,`au_code`,`au_username`,`au_pass`  FROM 
			  `tbl_channel_users` WHERE `au_id`=%s""",(RetailerListDtls['au_parent']))
			RetailerList = cur.fetchone()
			
			if RetailerList['au_parent']!= 0:
				cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,
				  `au_parent`,`au_code`,`au_username`,`au_pass`  FROM 
				  `tbl_channel_users` WHERE `au_id`=%s""",(RetailerList['au_parent']))
				Retailer = cur.fetchone()
				
		# cur.execute("""SELECT  count(`act_id`)as total  FROM `tbl_activations` 
		# 	WHERE `au_id`in (%s,%s,%s)""",(RetailerListDtls['au_id'],
		# 		RetailerList['au_id'],Retailer['au_id']))
		# totalGenAct = cur.fetchone()
		# totalGenActNo = totalGenAct['total']
		
		cur.execute("""SELECT SUM(`update_balance`)as total FROM `channel_wallet_transaction` 
			WHERE `au_id`in (%s,%s,%s)""",(RetailerListDtls['au_id'],
				RetailerList['au_id'],Retailer['au_id']))
		UsedWallet = cur.fetchone()
		UsedWalletBalance = int(UsedWallet['total'])
		
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Used Wallet Balance Details",
								"status": "success"
								},
				"responseList": {
								  "UsedWalletBalance": UsedWalletBalance
							    },
	            }), status.HTTP_200_OK



@name_space.route("/RetailerProducts")
class RetailerProducts(Resource):
	def get(self):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()
		
		cur.execute("""SELECT `prod_id`,`prod_name` FROM `retailer_products`""")
		RetailerProducts = cur.fetchall()
		
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Retailer Products Details",
								"status": "success"
								},
				"responseList": RetailerProducts
	            }), status.HTTP_200_OK



@name_space.route("/RetailerProductsPlan/<int:product_id>")
class RetailerProductsPlan(Resource):
	def get(self,product_id):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()
		
		cur.execute("""SELECT `plan_id`,`plan` FROM `retailer_products_plan` WHERE 
			`prod_id`=%s""",(product_id))
		RetailerProductPlans = cur.fetchall()
		
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Retailer Products Plan Details",
								"status": "success"
								},
				"responseList": RetailerProductPlans
	            }), status.HTTP_200_OK



@name_space.route("/GenerateActivationCode")
class GenerateActivationCode(Resource):
	@api.expect(act_code)
	def post(self):
		conn = meeprotect()
		cur = conn.cursor()
		details = request.get_json()

		today = datetime.datetime.now()
		
		exp_date = today + datetime.timedelta(days=1)
		exp_date = exp_date.isoformat()
		# print(exp_date)
		
		prod_id = details['prod_id']
		plan = details['plan']
		generate_no = details['generate_no']
		channel_users_id = details['channel_users_id']
		
		for i in range(generate_no):
			def get_random_alphaNumeric_string(stringLength=12):
			    lettersAndDigits = string.ascii_letters + string.digits
			    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))
			
			act_code = get_random_alphaNumeric_string()

			def get_random_digits(stringLength=12):
			    Digits = string.digits
			    return ''.join((random.choice(Digits) for i in range(stringLength)))
			
			serial_no = get_random_digits()
			
			activations_query = ("""INSERT INTO `tbl_activations`(`act_pack_code`, 
				`act_pack_id`, `act_code`, `act_type`, `is_used`, `au_id`, 
				`act_serial`,`code_active`,`code_expire`)  VALUES(%s,%s,%s,%s,
				%s,%s,%s,%s,%s)""")
			insert_data = (plan,prod_id,act_code,'active',0,channel_users_id,
				serial_no,today,exp_date)
			actdata = cur.execute(activations_query,insert_data)

		cur.execute("""SELECT `act_id`,`act_pack_code`,`act_pack_id`,`act_code`,
			`is_used`,`au_id` FROM `tbl_activations` WHERE `au_id`= %s and act_pack_id=%s
			and `is_used`=0 ORDER by `last_update_ts` desc limit %s""",(channel_users_id,prod_id,generate_no))
		ActivationCode = cur.fetchall()

		cur.execute("""SELECT `au_id`,`Added_balance`, `update_balance` FROM 
			`channel_wallet_transaction` WHERE `au_id`= %s ORDER BY 
			`transaction_id` DESC""",(channel_users_id))
		au_id = cur.fetchone()
		if au_id == None:

			transaction_query = ("""INSERT INTO `channel_wallet_transaction`(`au_id`,
				`previous_balance`,`Added_balance`, `update_balance`) VALUES(%s,
				%s,%s,%s)""")
			transaction_data = (channel_users_id,0,generate_no,generate_no)
			transactiondata = cur.execute(transaction_query,transaction_data)
		else:
			update_balance = au_id['update_balance'] + generate_no

			transaction_query = ("""INSERT INTO `channel_wallet_transaction`(`au_id`,
				`previous_balance`,`Added_balance`, `update_balance`) VALUES(%s,
				%s,%s,%s)""")
			transaction_data = (channel_users_id,au_id['update_balance'],
				generate_no,update_balance)
			transactiondata = cur.execute(transaction_query,transaction_data)

		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Generated Activation Code",
	                                "status": "success"
	                                },
				"responseList":ActivationCode
	                 }), status.HTTP_200_OK



@name_space.route("/MeeprotectProducts")
class MeeprotectProducts(Resource):
	def get(self):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()
		
		cur.execute("""SELECT `pack_id`,`pack_name`,`pack_code`,`pack_type`,
			`pack_price` FROM `tbl_packs`""")
		MeeprotectProducts = cur.fetchall()
		
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Meeprotect Products Details",
								"status": "success"
								},
				"responseList": MeeprotectProducts
	            }), status.HTTP_200_OK



@name_space.route("/MeeprotectRetailerProductPlans")
class MeeprotectRetailerProductPlans(Resource):
	def get(self):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()
		
		cur.execute("""SELECT `retailer_products`.`prod_id`,`prod_name`,`plan_id`,
			`plan`,`prod_price` FROM `retailer_products` INNER JOIN 
			`retailer_products_plan` on `retailer_products`.`prod_id` = 
			`retailer_products_plan`.`prod_id`""")
		ProductPlans = cur.fetchall()
		
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Meeprotect Product Plans Details",
								"status": "success"
								},
				"responseList": ProductPlans
	            }), status.HTTP_200_OK




@name_space.route("/TotalActivationDtlsByChnIdDate/<int:channel_users_id>/<string:start_date>/<string:end_date>")
class TotalActivationDtlsByChnIdDate(Resource):
	def get(self,channel_users_id,start_date,end_date):

		conn = meeprotect()
		cursor = conn.cursor()
		detail = []
		details = []
		TotalActivationDtls = []

		today = date.today()
		month = today.month
		day = today.day
		channel_id = channel_users_id
		cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users` 
			WHERE `au_id`=%s""",(channel_id))
		ChannelDtls = cursor.fetchone()
		if ChannelDtls:
			cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
			   WHERE `au_parent`=%s""",(channel_id))
			ChannelChildDtls = cursor.fetchall()
			# print(ChannelChildDtls)
			if ChannelChildDtls:
				i = 0
				while(i<len(ChannelChildDtls)):

					channelid = ChannelChildDtls[i]['au_id']
					cursor.execute("""SELECT `au_id`,`au_code` FROM `tbl_channel_users`
					   WHERE `au_parent`=%s""",(channelid))
					ChannelDtl = cursor.fetchall()
					# print(ChannelDtl)
					if ChannelDtl == ():
						cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
						`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
						`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
						WHERE `u_date` between %s and %s and `u_ret_code`= %s""",(start_date,end_date,format(ChannelChildDtls[i]['au_code'])))
						ActivationDtls = cursor.fetchall()
						# print(ActivationDtls)
						if 	ActivationDtls:
							for j in range(len(ActivationDtls)):
								ActivationDtls[j]['u_date'] = ActivationDtls[j]['u_date'].isoformat()
								
								if ActivationDtls[j]['u_date_of_birth']=='0000-00-00':
									ActivationDtls[j]['u_date_of_birth'] = '0000-00-00'
								else:
									ActivationDtls[j]['u_date_of_birth'] = ActivationDtls[j]['u_date_of_birth'].isoformat()
								
								if ActivationDtls[j]['u_aniversary']=='0000-00-00':
									ActivationDtls[j]['u_aniversary'] = '0000-00-00'
								else:
									ActivationDtls[j]['u_aniversary'] = ActivationDtls[j]['u_aniversary'].isoformat()
									
								if ActivationDtls[j]['validity_start']=='0000-00-00':
									ActivationDtls[j]['validity_start'] = '0000-00-00'
								else:
									ActivationDtls[j]['validity_start'] = ActivationDtls[j]['validity_start'].isoformat()
									
								if ActivationDtls[j]['validity_end']=='0000-00-00':
									ActivationDtls[j]['validity_end'] = '0000-00-00'
								else:
									ActivationDtls[j]['validity_end'] = ActivationDtls[j]['validity_end'].isoformat()
							
							for k in range(len(ActivationDtls)):
								TotalActivationDtls.append(ActivationDtls[k])
							# print(TotalActivationDtls)
						i += 1
						continue
					else:
						for i in range(len(ChannelDtl)):
							cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
							`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
							`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
							WHERE `u_date` between %s and %s and `u_ret_code`= %s""",(start_date,end_date,format(ChannelDtl[i]['au_code'])))
							ActivationDtls = cursor.fetchall()
							# print(ActivationDtls)
							if 	ActivationDtls:
								for j in range(len(ActivationDtls)):
									ActivationDtls[j]['u_date'] = ActivationDtls[j]['u_date'].isoformat()
									
									if ActivationDtls[j]['u_date_of_birth']=='0000-00-00':
										ActivationDtls[j]['u_date_of_birth'] = '0000-00-00'
									else:
										ActivationDtls[j]['u_date_of_birth'] = ActivationDtls[j]['u_date_of_birth'].isoformat()
									
									if ActivationDtls[j]['u_aniversary']=='0000-00-00':
										ActivationDtls[j]['u_aniversary'] = '0000-00-00'
									else:
										ActivationDtls[j]['u_aniversary'] = ActivationDtls[j]['u_aniversary'].isoformat()
										
									if ActivationDtls[j]['validity_start']=='0000-00-00':
										ActivationDtls[j]['validity_start'] = '0000-00-00'
									else:
										ActivationDtls[j]['validity_start'] = ActivationDtls[j]['validity_start'].isoformat()
										
									if ActivationDtls[j]['validity_end']=='0000-00-00':
										ActivationDtls[j]['validity_end'] = '0000-00-00'
									else:
										ActivationDtls[j]['validity_end'] = ActivationDtls[j]['validity_end'].isoformat()
								
								for k in range(len(ActivationDtls)):
									TotalActivationDtls.append(ActivationDtls[k])								# print(TotalActivationDtls)
							i += 1
							continue
			else:
				details = ChannelDtls['au_code']
				# print(details)
		else:
			TotalActivationDtls = []
		if details:
			cursor.execute("""SELECT `u_id`,`u_name`,`u_email_id`,`u_pass`,`image_url`,
				`u_date_of_birth`,`u_aniversary`,`u_date`,`u_mobile`,`u_ret_code`,`u_activ_code`,
				`validity_start`,`validity_end`,`u_pack_code` FROM `tbl_user` 
				WHERE `u_date` between %s and %s and `u_ret_code`=%s""",(start_date,end_date,format(details)))
			TotalActivationDtls = cursor.fetchall()
			# print(TotalActivationDtls)
				
			for i in range(len(TotalActivationDtls)):
				TotalActivationDtls[i]['u_date'] = TotalActivationDtls[i]['u_date'].isoformat()
				
				if TotalActivationDtls[i]['u_date_of_birth']=='0000-00-00':
					TotalActivationDtls[i]['u_date_of_birth'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['u_date_of_birth'] = TotalActivationDtls[i]['u_date_of_birth'].isoformat()
				
				if TotalActivationDtls[i]['u_aniversary']=='0000-00-00':
					TotalActivationDtls[i]['u_aniversary'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['u_aniversary'] = TotalActivationDtls[i]['u_aniversary'].isoformat()
					
				if TotalActivationDtls[i]['validity_start']=='0000-00-00':
					TotalActivationDtls[i]['validity_start'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['validity_start'] = TotalActivationDtls[i]['validity_start'].isoformat()
					
				if TotalActivationDtls[i]['validity_end']=='0000-00-00':
					TotalActivationDtls[i]['validity_end'] = '0000-00-00'
				else:
					TotalActivationDtls[i]['validity_end'] = TotalActivationDtls[i]['validity_end'].isoformat()
		
		conn.commit()
		cursor.close()
		return ({"attributes": {"status_desc": "Activation Details",
	                                "status": "success"
                                },
				"responseList": TotalActivationDtls
	                 }), status.HTTP_200_OK



@name_space.route("/MeeprotectProductsByChnnlId/<int:channel_id>")
class MeeprotectProductsByChnnlId(Resource):
	def get(self,channel_id):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()
		
		cur.execute("""SELECT `pack_id`,`pack_name`,`pack_code`,
			`pack_code`as 'pack_codename',`pack_type`,
			`pack_price` FROM `tbl_packs` INNER JOIN `channel_product_mapping` on 
			`tbl_packs`.`pack_id`=`channel_product_mapping`.`product_id` WHERE 
			`channel_product_mapping`.`channel_user_id`=%s""",(channel_id))
		MeeprotectProducts = cur.fetchall()
		if MeeprotectProducts:
			for i in range(len(MeeprotectProducts)):
				if MeeprotectProducts[i]['pack_codename'] =='YRLY':
					MeeprotectProducts[i]['pack_codename'] = 'Yearly'
				elif MeeprotectProducts[i]['pack_codename'] =='LFTM':
					MeeprotectProducts[i]['pack_codename'] = 'Lifetime'
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Meeprotect Products Details",
								"status": "success"
								},
				"responseList": MeeprotectProducts
	            }), status.HTTP_200_OK



@name_space.route("/ChannelWalletAmountByChnlId/<int:channel_id>")
class ChannelWalletAmountByChnlId(Resource):
	def get(self,channel_id):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()
		
		cur.execute("""SELECT `wallet_id`,`channel_user_id`,`wallet_balance` FROM 
			`wallet_balance` WHERE `channel_user_id`=%s""",(channel_id))
		walletdtls = cur.fetchone()
		if walletdtls:
			walletdtls = walletdtls
		else:
			walletdtls = []
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Wallet Details",
								"status": "success"
								},
				"responseList": walletdtls
	            }), status.HTTP_200_OK



@name_space.route("/MeeprotectChannelDtlsByChnnlId/<int:channel_id>")
class MeeprotectChannelDtlsByChnnlId(Resource):
	def get(self,channel_id):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()

		cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,`au_type`,
			`au_location`,`au_jdate`,`au_log_id`,`au_comp`,`au_address`,
			`au_parent`,`au_code`,`au_pass` FROM `tbl_channel_users` WHERE 
			`au_id`=%s""",(channel_id))
		ChannelDtls = cur.fetchone()
		if ChannelDtls:
			ChannelDtls['au_jdate'] = ChannelDtls['au_jdate'].isoformat()

		cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,`au_type`,
		   `au_location`,`au_jdate`,`au_log_id`,`au_comp`,`au_address`,
		   `au_parent`,`au_code`,`au_pass` FROM `tbl_channel_users` WHERE 
		    `au_parent`=%s""",(channel_id))
		ChannelChildDtls = cur.fetchall()

		if ChannelChildDtls:
			for i in range(len(ChannelChildDtls)):
				ChannelChildDtls[i]['au_jdate'] = ChannelChildDtls[i]['au_jdate'].isoformat()
				ChannelDtls['ChildDtls'] = ChannelChildDtls
				channelid = ChannelChildDtls[i]['au_id'] 
				parentid = ChannelChildDtls[i]['au_parent']
				if channelid != parentid:
					cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,`au_type`,
					   `au_location`,`au_jdate`,`au_log_id`,`au_comp`,`au_address`,
					   `au_parent`,`au_code`,`au_pass` FROM `tbl_channel_users` WHERE 
					    `au_parent`=%s""",(channelid))
					ChannlChildDtls = cur.fetchall()
					if ChannlChildDtls !=None:
						for j in range(len(ChannlChildDtls)):
							ChannlChildDtls[j]['au_jdate'] = ChannlChildDtls[j]['au_jdate'].isoformat()
							ChannelChildDtls[i]['Childitem'] = ChannlChildDtls
					# ChannlChildDtls = ChannelDtl(channelid)
					# ChannelChildDtls[i]['Childitem'] = ChannlChildDtls
		
		else:
			ChannelDtls['ChildDtls'] = []	
		return ({"attributes": {"status_desc": "Channel Details",
								"status": "success"
								},
				"responseList": ChannelDtls
	            }), status.HTTP_200_OK



@name_space.route("/SigninByContactNumber/<int:phone_no>")
class SigninByContactNumber(Resource):
	def get(self,phone_no):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()
		
		cur.execute("""SELECT `au_id`,`au_name`,`au_phone`,`au_username`,`au_pass`,
			`au_code` FROM `tbl_channel_users` WHERE `au_phone`=%s""",(phone_no))
		userdtls = cur.fetchone()
		
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Signin Details",
								"status": "success"
								},
				"responseList": userdtls
	            }), status.HTTP_200_OK



@name_space.route("/ParentWalletTransferChildListByChnnlId/<int:channel_id>")
class ParentWalletTransferChildListByChnnlId(Resource):
	def get(self,channel_id):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()

		cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,`au_type`,
			`au_location`,`au_jdate`,`au_log_id`,`au_comp`,`au_address`,
			`au_parent`,`au_code`,`au_pass` FROM `tbl_channel_users` WHERE 
			`au_id`=%s""",(channel_id))
		ChannelDtls = cur.fetchone()
		if ChannelDtls:
			ChannelDtls['au_jdate'] = ChannelDtls['au_jdate'].isoformat()

		cur.execute("""SELECT `au_id`,`au_username`,`au_name`,`au_email` FROM 
			`tbl_channel_users` WHERE `au_parent`=%s""",(channel_id))
		ChannelChildDtls = cur.fetchall()
			
		return ({"attributes": {"status_desc": "Child Details",
								"status": "success"
								},
				"responseList": ChannelChildDtls
	            }), status.HTTP_200_OK



@name_space.route("/WalletTransferToChild")
class WalletTransferToChild(Resource):
	@api.expect(WalletTransferToChild)
	def post(self):
		conn = meeprotect()
		cur = conn.cursor()
		details = request.get_json()
		
		form_au_id = details['form_au_id']
		to_au_id = details['to_au_id']
		transfer_balance = details['transfer_balance']
		
		cur.execute("""SELECT `wallet_id`, `channel_user_id`, `wallet_balance` 
			FROM `wallet_balance` WHERE `channel_user_id`=%s""",(form_au_id))
		walletDtls = cur.fetchone()

		if walletDtls:
			if walletDtls['wallet_balance']< transfer_balance:
				details = {"msg":"Insufficient balance"}
			else:
				cur.execute("""SELECT `transaction_id`, `form_au_id`, `to_au_id`, 
					`previous_balance`, `transfer_balance`, `updated_balance` FROM 
					`wallet_transaction` WHERE `form_au_id`=%s and `to_au_id`=%s ORDER BY 
					`transaction_id` DESC""",(form_au_id,to_au_id))
				transactionDtls = cur.fetchone()

				if transactionDtls == None:
					wallet_query = ("""INSERT INTO `wallet_transaction`(`form_au_id`, 
						`to_au_id`,`previous_balance`,`transfer_balance`,`updated_balance`) 
						VALUES(%s,%s,%s,%s,%s)""")
					insert_data = (form_au_id,to_au_id,0,transfer_balance,transfer_balance)
					walletdata = cur.execute(wallet_query,insert_data)

					wallet_balance = walletDtls['wallet_balance'] - transfer_balance
					
					update_wallet = ("""UPDATE `wallet_balance` SET `wallet_balance`=%s
					  WHERE `channel_user_id`=%s""")
					wallet_data = (wallet_balance,form_au_id)
					walletdata = cur.execute(update_wallet,wallet_data)

					cur.execute("""SELECT `wallet_id`, `channel_user_id`, `wallet_balance` 
						FROM `wallet_balance` WHERE `channel_user_id`=%s""",(to_au_id))
					childwalletDtls = cur.fetchone()
					if childwalletDtls == None:
						walletinsert_query = ("""INSERT INTO `wallet_balance`(`channel_user_id`, 
							`wallet_balance`) VALUES(%s,%s)""")
						walletinsert_data = (to_au_id,transfer_balance)
						walletinsertdata = cur.execute(walletinsert_query,walletinsert_data)
					else:
						updated_childbalance = childwalletDtls['wallet_balance'] + transfer_balance
					
						update_childwallet = ("""UPDATE `wallet_balance` SET 
							`wallet_balance`=%s WHERE `channel_user_id`=%s""")
						childwallet_data = (updated_childbalance,to_au_id)
						childwalletdata = cur.execute(update_childwallet,childwallet_data)
		
				else:
					updated_balance = transactionDtls['updated_balance'] + transfer_balance
					wallet_query = ("""INSERT INTO `wallet_transaction`(`form_au_id`, 
						`to_au_id`, `previous_balance`, `transfer_balance`, `updated_balance`) 
						VALUES(%s,%s,%s,%s,%s)""")
					insert_data = (form_au_id,to_au_id,transactionDtls['updated_balance'],
						transfer_balance,updated_balance)
					walletdata = cur.execute(wallet_query,insert_data)

					wallet_balance = walletDtls['wallet_balance'] - transfer_balance
					
					update_wallet = ("""UPDATE `wallet_balance` SET `wallet_balance`=%s
					  WHERE `channel_user_id`=%s""")
					wallet_data = (wallet_balance,form_au_id)
					walletdata = cur.execute(update_wallet,wallet_data)

					cur.execute("""SELECT `wallet_id`, `channel_user_id`, `wallet_balance` 
						FROM `wallet_balance` WHERE `channel_user_id`=%s""",(to_au_id))
					childwalletDtls = cur.fetchone()
					if childwalletDtls == None:
						walletinsert_query = ("""INSERT INTO `wallet_balance`(`channel_user_id`, 
							`wallet_balance`) VALUES(%s,%s)""")
						walletinsert_data = (to_au_id,transfer_balance)
						walletinsertdata = cur.execute(walletinsert_query,walletinsert_data)
					else:
						updated_childbalance = childwalletDtls['wallet_balance'] + transfer_balance
					
						update_childwallet = ("""UPDATE `wallet_balance` SET 
							`wallet_balance`=%s WHERE `channel_user_id`=%s""")
						childwallet_data = (updated_childbalance,to_au_id)
						childwalletdata = cur.execute(update_childwallet,childwallet_data)
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Child Wallet Transfer Details",
	                                "status": "success"
	                                },
				"responseList":details
	                 }), status.HTTP_200_OK




@name_space.route("/WalletTransferHistoryByParentId/<int:Parent_id>")
class WalletTransferHistoryByParentId(Resource):
	def get(self,Parent_id):

		conn = meeprotect()
		cur = conn.cursor()
		today = date.today()

		cur.execute("""SELECT `transaction_id`, `form_au_id`, `to_au_id`, 
			`au_name`, `previous_balance`, `transfer_balance`, 
			`updated_balance` FROM `wallet_transaction` INNER JOIN 
			`tbl_channel_users` ON `wallet_transaction`.`to_au_id`=
			`tbl_channel_users`.`au_id`WHERE `form_au_id`=%s""",(Parent_id))
		transferHistoryDtls = cur.fetchall()
			
		return ({"attributes": {"status_desc": "Transfer History Details",
								"status": "success"
								},
				"responseList": transferHistoryDtls
	            }), status.HTTP_200_OK



@name_space.route("/RetailerWalletBalance")
class RetailerWalletBalance(Resource):
	@api.expect()
	def post(self):
		conn = meeprotect()
		cur = conn.cursor()
		details = request.get_json()
		
		detail = []
		cur.execute("""SELECT distinct(`to_au_id`)as 'to_au_id' FROM 
			`wallet_transaction`""")
		retailerDtls = cur.fetchall()
		for i in range(len(retailerDtls)):
			
			cur.execute("""SELECT `au_id`,`au_name`,`au_email`,`au_phone`,
				`au_parent`,`au_code`,`au_pass` FROM `tbl_channel_users` WHERE 
			    `au_parent`=%s""",(retailerDtls[i]['to_au_id']))
			ChannelChildDtls = cur.fetchall()
			
			if ChannelChildDtls:
				response = "No Retailer Details"
			else:
				cur.execute("""SELECT `transaction_id`, `form_au_id`, `to_au_id`, 
					`previous_balance`, `transfer_balance`, `updated_balance` FROM 
					`wallet_transaction` WHERE `to_au_id`=%s ORDER BY 
					`transaction_id` DESC""",(retailerDtls[i]['to_au_id']))
				transactionDtls = cur.fetchone()

				updated_balance = transactionDtls['updated_balance'] - 1
				
				wallet_query = ("""INSERT INTO `wallet_transaction`(`form_au_id`, 
					`to_au_id`,`previous_balance`,`transfer_balance`,`updated_balance`) 
					VALUES(%s,%s,%s,%s,%s)""")
				insert_data = (transactionDtls['form_au_id'],
					transactionDtls['to_au_id'],transactionDtls['updated_balance'],
					0,updated_balance)
				walletdata = cur.execute(wallet_query,insert_data)

				update_childwallet = ("""UPDATE `wallet_balance` SET 
					`wallet_balance`=%s WHERE `channel_user_id`=%s""")
				childwallet_data = (updated_balance,retailerDtls[i]['to_au_id'])
				childwalletdata = cur.execute(update_childwallet,childwallet_data)

				response = {
							"form_au_id":transactionDtls['form_au_id'],			
							"to_au_id":transactionDtls['to_au_id'],
							"previous_balance":transactionDtls['updated_balance'],
							"transfer_balance":0,
							"updated_balance":updated_balance
							}
				detail.append(response)
	
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Retailer Wallet Details",
	                                "status": "success"
                                },
				"responseList": detail
	                 }), status.HTTP_200_OK



@name_space.route("/sendAppPushNotifications")
class sendAppPushNotifications(Resource):
	@api.expect(appmsgmodel)
	def post(self):
		connection = meeprotect()
		cursor = connection.cursor()
		details = request.get_json()

		appmsgmodel = details['appmsgmodel']
		appmsg = appmsgmodel

		for app in appmsg:
			user_id = app.get('user_id')
			title = app.get('title')
			msg = app.get('msg')

			cursor.execute("""SELECT * FROM `user_device` WHERE `user_id`=%s""",(user_id))
			deviceDtls = cursor.fetchone()
			if deviceDtls == None:
				msgResponse ={"Not found user device id"}
			else:
				device_id = deviceDtls['device_token']

				cursor.execute("""SELECT * FROM `tbl_user` WHERE `u_id`=%s""",(user_id))
				retDtls = cursor.fetchone()
				if retDtls == None:
					msgResponse ={"Not found retailer code"}
				else:
					ret_code = retDtls['u_ret_code']
					cursor.execute("""SELECT * FROM `retailer_firebase_mapping` where 
						`ret_code`=%s""",(ret_code))
					firebaseDtls = cursor.fetchone()
					if firebaseDtls == None:
						firebaseDtls ={"Not found firebase key"}
					else:
						api_key = firebaseDtls['firebase_key']
				data_message = {
								"title" : title,
								"message": msg
								}
				
				push_service = FCMNotification(api_key=api_key)
				msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
				sent = 'No'
				if msgResponse.get('success') == 1:
					sent = 'Yes'
					
					app_query = ("""INSERT INTO `app_massage`(`title`,`body`,
						`U_id`,`Device_ID`,`Sent`)  VALUES(%s,%s,%s,%s,%s)""")
					insert_data = (title,msg,user_id,device_id,sent)
					appdata = cursor.execute(app_query,insert_data)
			
		connection.commit()
		cursor.close()
		return ({"attributes": {
				    		"status_desc": "Push Notification",
				    		"status": "success"
				    		},
				    	}), status.HTTP_200_OK
#----------------------Send-Push-Notification---------------------#
@name_space.route("/RetailerWalletBalanceV2")
class RetailerWalletBalanceV2(Resource):
	@api.expect(walletdeduction)
	def post(self):
		conn = meeprotect()
		cur = conn.cursor()
		details = request.get_json()

		userid = details['user_id']
		appname = details['appname']

		cur.execute("""SELECT `u_ret_code` FROM `tbl_user` WHERE `u_id`=%s""",
			(userid))
		userDtls = cur.fetchone()
		
		cur.execute("""SELECT `au_id` FROM `tbl_channel_users` WHERE 
		    `au_code`=%s""",(userDtls['u_ret_code']))
		retailerDtls = cur.fetchone()
			
		if retailerDtls:
			
			cur.execute("""SELECT `transaction_id`, `form_au_id`, `to_au_id`, 
				`previous_balance`, `transfer_balance`, `updated_balance` FROM 
				`wallet_transaction` WHERE `to_au_id`=%s ORDER BY 
				`transaction_id` DESC""",(retailerDtls['au_id']))
			transactionDtls = cur.fetchone()
			# print(transactionDtls['updated_balance'])
			updated_balance = transactionDtls['updated_balance'] - 365

			if transactionDtls['updated_balance'] >365 :
				print("hi")
				wallet_query = ("""INSERT INTO `wallet_transaction`(`form_au_id`, 
					`to_au_id`,`previous_balance`,`transfer_balance`,`updated_balance`) 
					VALUES(%s,%s,%s,%s,%s)""")
				insert_data = (transactionDtls['form_au_id'],
					transactionDtls['to_au_id'],transactionDtls['updated_balance'],
					0,updated_balance)
				walletdata = cur.execute(wallet_query,insert_data)

				update_childwallet = ("""UPDATE `wallet_balance` SET 
					`wallet_balance`=%s WHERE `channel_user_id`=%s""")
				childwallet_data = (updated_balance,retailerDtls['au_id'])
				childwalletdata = cur.execute(update_childwallet,childwallet_data)

				msg = "Deducted"
			else:
				msg = 'Insufficient Balance'
				URL = BASE_URL + "meprotect_mail/CommunicationAPI/PushNotificationForRetailer"
				# print(URL)
				payload = {
							"user_id":userid,
							"appname":appname
						}
				# print(payload)
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				notifyResponse = requests.post(URL,data=json.dumps(payload), headers=headers)
				# status = notifyResponse[responseList]
				# print(notifyResponse)
				
		else:
			msg = 'No retailer details'
				
	
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Retailer Wallet Details",
                                "status": "success"
                                },
				"responseList": msg 
	                 }), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/PushNotificationForRetailer")
class PushNotificationForRetailer(Resource):
	@api.expect(retappmsg)
	def post(self):
		connection = meeprotect()
		cursor = connection.cursor()
		details = request.get_json()

		user_id = details['user_id']
		appname = details['appname']
		print(user_id)
		title = "Unable to register"
		msg = "Your wallet balance is insufficient due to which user is unable to register"
		# message = ""
		cursor.execute("""SELECT `u_ret_code` FROM `tbl_user` WHERE 
			`u_id`=%s""",(user_id))
		userDtls = cursor.fetchone()
		
		cursor.execute("""SELECT `au_id` FROM `tbl_channel_users` WHERE 
		    `au_code`=%s""",(userDtls['u_ret_code']))
		retailerDtls = cursor.fetchone()
		
		if retailerDtls:
			
			cursor.execute("""SELECT device_token FROM `retailer_device` WHERE 
				`ret_id`=%s""",(retailerDtls['au_id']))
			deviceDtls = cursor.fetchone()
			# print(deviceDtls)
			if deviceDtls == None:
				message = "Not found user device id"
			else:
				device_id = deviceDtls['device_token']

				cursor.execute("""SELECT * FROM `retailer_firebase_mapping` where 
					`ret_app_name`=%s""",(appname))
				firebaseDtls = cursor.fetchone()
				if firebaseDtls == None:
					message = "Not found firebase key"
				else:
					api_key = firebaseDtls['firebase_key']
					data_message = {
									"title" : title,
									"message": msg
									}
					
					push_service = FCMNotification(api_key=api_key)
					# print(api_key)
					msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
					sent = 'No'
					# print(msgResponse)
					message = "not success"
					if msgResponse.get('success') == 1:
						sent = 'Yes'
						
						app_query = ("""INSERT INTO `retapp_message`(`title`,`body`,
							`ret_id`,`Device_ID`,`Sent`)  VALUES(%s,%s,%s,%s,%s)""")
						insert_data = (title,msg,retailerDtls['au_id'],device_id,sent)
						appdata = cursor.execute(app_query,insert_data)
						message = "success"
		else:
			message ={"Not found retailer code"}	

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "push Notification",
	                                "status": "success"
	                            },
	            "responseList": message}), status.HTTP_200_OK


@name_space.route("/DeltaSecurityRetailerWalletBalance")
class DeltaSecurityRetailerWalletBalance(Resource):
	@api.expect(walletdeductionV2)
	def post(self):
		conn = meeprotect()
		cur = conn.cursor()
		details = request.get_json()

		retcode = details['retcode']
		appname = details['appname']

		cur.execute("""SELECT `au_id` FROM `tbl_channel_users` WHERE 
		    `au_code`=%s""",(retcode))
		retailerDtls = cur.fetchone()
			
		if retailerDtls:
			
			cur.execute("""SELECT `transaction_id`, `form_au_id`, `to_au_id`, 
				`previous_balance`, `transfer_balance`, `updated_balance` FROM 
				`wallet_transaction` WHERE `to_au_id`=%s ORDER BY 
				`transaction_id` DESC""",(retailerDtls['au_id']))
			transactionDtls = cur.fetchone()
			# print(transactionDtls['updated_balance'])
			updated_balance = transactionDtls['updated_balance'] - 365

			if transactionDtls['updated_balance'] >365 :
				
				wallet_query = ("""INSERT INTO `wallet_transaction`(`form_au_id`, 
					`to_au_id`,`previous_balance`,`transfer_balance`,`updated_balance`) 
					VALUES(%s,%s,%s,%s,%s)""")
				insert_data = (transactionDtls['form_au_id'],
					transactionDtls['to_au_id'],transactionDtls['updated_balance'],
					0,updated_balance)
				walletdata = cur.execute(wallet_query,insert_data)

				update_childwallet = ("""UPDATE `wallet_balance` SET 
					`wallet_balance`=%s WHERE `channel_user_id`=%s""")
				childwallet_data = (updated_balance,retailerDtls['au_id'])
				childwalletdata = cur.execute(update_childwallet,childwallet_data)

				msg = "Deducted"
			else:
				wallet_query = ("""INSERT INTO `wallet_transaction`(`form_au_id`, 
					`to_au_id`,`previous_balance`,`transfer_balance`,`updated_balance`) 
					VALUES(%s,%s,%s,%s,%s)""")
				insert_data = (transactionDtls['form_au_id'],
					transactionDtls['to_au_id'],transactionDtls['updated_balance'],
					0,updated_balance)
				walletdata = cur.execute(wallet_query,insert_data)

				update_childwallet = ("""UPDATE `wallet_balance` SET 
					`wallet_balance`=%s WHERE `channel_user_id`=%s""")
				childwallet_data = (updated_balance,retailerDtls['au_id'])
				childwalletdata = cur.execute(update_childwallet,childwallet_data)

				msg = 'Insufficient Balance'
				URL = BASE_URL + "meprotect_mail/CommunicationAPI/DeltaSecurityPushNotificationForRetailer"
				
				payload = {
							"retcode":retcode,
							"appname":appname
						}
				# print(payload)
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				notifyResponse = requests.post(URL,data=json.dumps(payload), headers=headers)
				# print(notifyResponse)
				
		else:
			msg = 'No retailer details'
				
	
		conn.commit()
		cur.close()
		return ({"attributes": {"status_desc": "Retailer Wallet Details",
                                "status": "success"
                                },
				"responseList": msg 
	                 }), status.HTTP_200_OK

#---------------------------------------------------------------#
@name_space.route("/DeltaSecurityPushNotificationForRetailer")
class DeltaSecurityPushNotificationForRetailer(Resource):
	@api.expect(retappmsgV2)
	def post(self):
		connection = meeprotect()
		cursor = connection.cursor()
		details = request.get_json()

		retcode = details['retcode']
		appname = details['appname']
		# print(retcode)
		title = "Unable to register"
		msg = "Your wallet balance is insufficient due to which user is unable to register"
		# message = ""
		
		cursor.execute("""SELECT `au_id` FROM `tbl_channel_users` WHERE 
		    `au_code`=%s""",(retcode))
		retailerDtls = cursor.fetchone()
		
		if retailerDtls:
			
			cursor.execute("""SELECT device_token FROM `retailer_device` WHERE 
				`ret_id`=%s""",(retailerDtls['au_id']))
			deviceDtls = cursor.fetchone()
			# print(deviceDtls)
			if deviceDtls == None:
				message = "Not found user device id"
			else:
				device_id = deviceDtls['device_token']

				cursor.execute("""SELECT * FROM `retailer_firebase_mapping` where 
					`ret_app_name`=%s""",(appname))
				firebaseDtls = cursor.fetchone()
				if firebaseDtls == None:
					message = "Not found firebase key"
				else:
					api_key = firebaseDtls['firebase_key']
					data_message = {
									"title" : title,
									"message": msg
									}
					
					push_service = FCMNotification(api_key=api_key)
					# print(api_key)
					msgResponse = push_service.notify_single_device(registration_id=device_id,data_message =data_message)
					sent = 'No'
					print(msgResponse)
					message = "not success"
					if msgResponse.get('success') == 1:
						sent = 'Yes'
						
						app_query = ("""INSERT INTO `retapp_message`(`title`,`body`,
							`ret_id`,`Device_ID`,`Sent`)  VALUES(%s,%s,%s,%s,%s)""")
						insert_data = (title,msg,retailerDtls['au_id'],device_id,sent)
						appdata = cursor.execute(app_query,insert_data)
						message = "success"
		else:
			message ={"Not found retailer code"}	

		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "push Notification",
	                                "status": "success"
	                            },
	            "responseList": message}), status.HTTP_200_OK

#---------------------------------------------------------------#

#--------------------------------Add-Protection-Plan-------------------------------#

@name_space.route("/AddProtecttionplan")
class AddProtecttionplan(Resource):
	@api.expect(protectionplan_model)
	def post(self):

		connection = mobileprotection()
		cursor = connection.cursor()		
		details = request.get_json()

		ret_code = details['ret_code']

		get_query = ("""SELECT *
			FROM `protection_plan` where `ret_code` = %s""")
		get_data = (ret_code)
		get_count = cursor.execute(get_query,get_data)

		if get_count > 0:
			print('hiii')
		else:			

			insert_query1 = ("""INSERT INTO `protection_plan`(`ret_code`,`validity_period`,`starting_amt`,`ending_amt`,`paid_amt`,`plan_type`) 
					VALUES(%s,6,0,15000,599,1)""")
			inser_data1 = (ret_code)
			cursor.execute(insert_query1,inser_data1)

			insert_query2 = ("""INSERT INTO `protection_plan`(`ret_code`,`validity_period`,`starting_amt`,`ending_amt`,`paid_amt`,`plan_type`) 
					VALUES(%s,6,15001,30000,799,1)""")
			cursor.execute(insert_query2,inser_data1)

			insert_query3 = ("""INSERT INTO `protection_plan`(`ret_code`,`validity_period`,`starting_amt`,`ending_amt`,`paid_amt`,`plan_type`) 
					VALUES(%s,12,0,15000,999,1)""")
			cursor.execute(insert_query3,inser_data1)

			insert_query4 = ("""INSERT INTO `protection_plan`(`ret_code`,`validity_period`,`starting_amt`,`ending_amt`,`paid_amt`,`plan_type`) 
					VALUES(%s,12,15001,30000,1299,1)""")
			cursor.execute(insert_query4,inser_data1)

			insert_query5 = ("""INSERT INTO `protection_plan`(`ret_code`,`validity_period`,`starting_amt`,`ending_amt`,`paid_amt`,`plan_type`) 
					VALUES(%s,24,0,15000,399,2)""")
			cursor.execute(insert_query5,inser_data1)

			insert_query6 = ("""INSERT INTO `protection_plan`(`ret_code`,`validity_period`,`starting_amt`,`ending_amt`,`paid_amt`,`plan_type`) 
					VALUES(%s,24,15001,30000,499,2)""")
			cursor.execute(insert_query6,inser_data1)

		connection.commit()
		cursor.close()

		return ({"attributes": {
				    "status_desc": "add_protection_plan",
				    "status": "success"
				},
				"responseList":details}), status.HTTP_200_OK

#--------------------------------Add-Protection-Plan-------------------------------#


