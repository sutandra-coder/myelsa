from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
import datetime
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)


def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='meeprotect',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def techdrive_meprotect():
	connection = pymysql.connect(host='techdrive.xyz',
	                             user='techdrive_meprote',
	                             password='Webs_$#@!56',
	                             db='techdrive_meprotect',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection



sms_backup = Blueprint('smsbackup_api', __name__)
api = Api(sms_backup,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('smsBackup',description='Sms Backup')

smsbackup=api.model('smsbackup', {
	"u_emailid":fields.String(),
	"address":fields.String(),
	"read":fields.String(),
	"body":fields.String(),
	"date":fields.String(),
	"type":fields.String()
	})

smsbackupDtls=api.model('smsbackupDtls', {
	"smsbackup":fields.List(fields.Nested(smsbackup))
	})


@name_space.route("/smsbackup")
class smsbackup(Resource):
	@api.expect(smsbackupDtls)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		
		# u_emailid = details['u_emailid']
		# address = details['address']
		# read = details['read']
		# body = details['body']
		# date = details['date']
		# types = details['type']
		smsbackup = details['smsbackup']
		sms = smsbackup

		for sm in sms:
			u_emailid = sm['u_emailid']
			address = sm['address']
			read = sm['read']
			body = sm['body']
			date = sm['date']
			types = sm['type']

			emailid_insert_query = ("""INSERT INTO `sms_bckup`(`u_emailid`,`address`,`read`,`body`,`date`,`type`) VALUES 
				(%s,%s,%s,%s,%s,%s)""")
			insert_data = (u_emailid,address,read,body,date,types)
			smsbackdata = cursor.execute(emailid_insert_query,insert_data)
			# print(smsbackdata)

		connection.commit()
		if smsbackdata:
			return ({"attributes": {"status_desc": "Sms Backup Details",
	                                "status": "success"
	                                }
	                 }), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Sms Backup Details",
	                                "status": "Not success"
	                                }
	                 }), status.HTTP_403_OK


#---------------------------------------------------------------------------#

@name_space.route("/meprotectSmsbackup")
class meprotectSmsbackup(Resource):
	@api.expect(smsbackupDtls)
	def post(self):
		connection = techdrive_meprotect()
		cursor = connection.cursor()
		details = request.get_json()
		today = date.today() 
		
		smsbackup = details['smsbackup']
		sms = smsbackup

		for sm in sms:
			u_emailid = sm['u_emailid']
			address = sm['address']
			read = sm['read']
			body = sm['body']
			datee = sm['date']
			types = sm['type']

			emailid_insert_query = ("""INSERT INTO `sms_bckup`(`u_emailid`,`address`,`read`,`body`,`date`,`type`) VALUES 
				(%s,%s,%s,%s,%s,%s)""")
			insert_data = (u_emailid,address,read,body,today,types)
			smsbackdata = cursor.execute(emailid_insert_query,insert_data)
			# print(smsbackdata)

		connection.commit()
		if smsbackdata:
			return ({"attributes": {"status_desc": "Sms Backup Details",
	                                "status": "success"
	                                }
	                 }), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Sms Backup Details",
	                                "status": "Not success"
	                                }
	                 }), status.HTTP_403_OK
#---------------------------------------------------------------------------#		