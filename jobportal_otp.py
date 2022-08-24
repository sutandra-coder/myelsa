from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import pymysql
import random
import math
app = Flask(__name__)
cors = CORS(app)
otp_jobportal = Blueprint('otp_jobportal_api', __name__)
api = Api(otp_jobportal, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('JobPortalOTP', description='Job Portal OTP')

def mysql_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_job_portal',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

app.config['CORS_HEADERS'] = 'Content-Type'


otp_model = api.model('OTP', {
    "otp":fields.Integer(),
    "user_role":fields.String(),
    "firstname":fields.String(required=True),
    "lastname":fields.String(required=True),
    # "generatedby":fields.String(required=True,default='System'),
    "mailid":fields.String(),
    "address":fields.String(),
    "phoneno":fields.String(),
    "user_id":fields.String()
    })
GUPSHUP_USERID = '2000188641'
GUPSHUP_PASSWORD = 'UDLMDQEUP'

def generateotp():
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        print(math.floor(random.random() * 10))
        OTP += digits[int(math.floor(random.random() * 10))]
    return OTP

@name_space.route("/generateOTP")
class generateOTP(Resource):
    @api.expect(otp_model)
    def post(self):
        connection = mysql_connection()
        cursor = connection.cursor()
        details = request.get_json()
        otp = generateotp()
        user_role = details['user_role']
        firstname = details['firstname']
        lastname = details['lastname']
        generatedby = 'SYSTEM' #details['generatedby']
        mailid = details['mailid']
        address = details['address']
        phoneno = details['phoneno']
        user_id = details['user_id'] or None
        opt_insert_query = ("""INSERT INTO `jobportal_user_otp`(`OTP`, `USER_ROLE`, `FIRST_NAME`,
            `LAST_NAME`, `GENERATED_BY`, `MAIL_ID`, `Address`, `PHONE_NUMBER`, `User_ID`) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
        otp_data = (otp,user_role,firstname,lastname,generatedby,mailid,address,phoneno,user_id)

        cursor.execute(opt_insert_query,otp_data)

        url = "http://enterprise.smsgupshup.com/GatewayAPI/rest"
        method = 'sendMessage'
        send_to = 'send_to'
        msg_type = 'TEXT'
        auth_scheme = 'PLAIN'
        smsformat = 'JSON'
        sms_response = []

        sms_body = 'Hi {} The OTP for the Online Transaction is {}. \
        This OTP is valid only for one time use. Do not share OTP for security reasons.'.format(firstname,otp)
        user_mobile_no = phoneno
        
        payload ="method={}&send_to={}&msg={}&msg_type={}&userid={}&auth_scheme={}&password={}&format={}".format(method,
            user_mobile_no,sms_body,msg_type,GUPSHUP_USERID,auth_scheme,GUPSHUP_PASSWORD,smsformat)
        postUrl = url+'?'+payload
        response = requests.request("POST", postUrl)

        response = json.loads(response.text)['response']['status']
        
        if response == 'success':
            sms_status = 'success'
        else:
            sms_status = 'failure'

        connection.commit()
        cursor.close()

        return ({"attributes": { 
                            "status_desc": "User OTP Details",
                            "status": sms_status,
                            "otp":otp}}), status.HTTP_200_OK