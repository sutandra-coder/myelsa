from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
onboarding_teachers = Blueprint('onboarding_api', __name__)
api = Api(onboarding_teachers, version='1.0', title='myElsa Tutor Intelli Onboarding',
    description='myElsa Tutor Intelli Onboarding')
name_space = api.namespace('OnboardTeacher', description=':Onboard Teacher')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'

institution = api.model('Institution', {
	"institution_user_id":fields.Integer(required=True)
	})

@name_space.route("/createInstitute")
class createInstitute(Resource):
	@api.expect(institution)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		teacher_id = details.get('institution_user_id')
		cursor.execute("""SELECT `INSTITUTION_USER_NAME`, concat(`FIRST_NAME`, ' ',`LAST_NAME`) as 'FIRST_NAME',
			`INSTITUTION_NAME`,`Coupon_Name` FROM `institution_user_credential` ic,
			`institution_user_credential_master` icm, `coupon_dtls` cd WHERE 
			ic.`INSTITUTION_USER_ID` =icm.`INSTITUTION_USER_ID` 
			and ic.`INSTITUTION_USER_ID` = cd.`Last_update_Id`
			and ic.`INSTITUTION_USER_ID` = %s""",(details['institution_user_id']))
		institute_desc = cursor.description
		desc_names = [col[0] for col in institute_desc]
		institute_user_data = [dict(izip(desc_names, row)) for row in cursor.fetchall()]
		
		user_name = institute_user_data[0]['FIRST_NAME']
		if institute_user_data[0]['INSTITUTION_NAME']:
			institution_name = institute_user_data[0]['INSTITUTION_NAME']
		else:
			institution_name = institute_user_data[0]['FIRST_NAME']
		phone_no = institute_user_data[0]['INSTITUTION_USER_NAME']
		current_date = date.today()
		start_date = str(current_date)
		nextyear_date = current_date.replace(year=current_date.year + 1)
		end_date = str(nextyear_date)
		code = institute_user_data[0]['Coupon_Name']

		cursor.execute("""SELECT `INSTITUTION_ID` FROM `teacher_dtls` WHERE 
			`INSTITUTION_USER_ID_TEACHER` = %s and `INSTITUTION_ID` <> 1 
			ORDER BY `INSTITUTION_ID` DESC LIMIT 1""",(details['institution_user_id']))

		instiDtls = cursor.fetchone()
		print(instiDtls)
		if not instiDtls:

			insti_dtls_insert_query = ("""INSERT INTO `institution_dtls`(`INSTITUTION_NAME`,
				`INSTITUTION_START_DATE`,`INSTITUTION_END_DATE`,`INSTITUTION_PHONE_NUMBER`,`ADMIN_ID`) VALUES (%s,%s,%s,%s,%s)""")
			insti_dtls_data = (institution_name,start_date,end_date,phone_no,teacher_id)
			cursor.execute(insti_dtls_insert_query,insti_dtls_data)
			connection.commit()
			insti_id = cursor.lastrowid
			cursor.close()
			connection = mysql.connect()
			cursor = connection.cursor()
			details['institution_id'] = insti_id
			instiCode = code[0:4]+str(insti_id)
			details['institution_code'] = instiCode
			print(insti_id,instiCode)

			instiCodeInsertQuery = ("""INSERT INTO `institution_dtls_and_code_map`(`INSTITUTION_ID`, 
				`PHONE_NUMBER`, `CODE`) VALUES (%s,%s,%s)""")

			codeData = (insti_id,phone_no,instiCode)

			cursor.execute(instiCodeInsertQuery,codeData)

			credsMasterUpdate = ("""UPDATE `institution_user_credential_master` SET 
				`INSTITUTION_ID` = %s WHERE `INSTITUTION_USER_ID` = %s""")
			masterData = (insti_id,teacher_id)
			cursor.execute(credsMasterUpdate,masterData)
			print(insti_id)
			connection.commit()
			cursor.close()
			connection = mysql.connect()
			cursor = connection.cursor()

			tchrDtlsUpdate = ("""UPDATE `teacher_dtls` SET `INSTITUTION_ID` = %s
				WHERE `INSTITUTION_USER_ID_TEACHER` = %s""")
			tchrDtlsData = (insti_id,teacher_id)
			cursor.execute(tchrDtlsUpdate,tchrDtlsData)
			print(insti_id)
			connection.commit()
			cursor.close()
			connection = mysql.connect()
			cursor = connection.cursor()
			cursor.execute("""SELECT `Activity_Id` FROM `activity_institution`""")
			activity_id = cursor.fetchall()
			for act in activity_id:
				act_insti_map_insert_query = ("""INSERT INTO `activity_institution_mapping`(`Institution_Id`, 
					`Activity_ID`) VALUES(%s,%s)""")
				act_insti_map_data = (insti_id,act)
				cursor.execute(act_insti_map_insert_query,act_insti_map_data)
				print(act[0])
			connection.commit()
			cursor.close()
		else:
			cursor.execute("""SELECT `CODE` FROM `institution_dtls_and_code_map` 
				WHERE `INSTITUTION_ID` = %s""",(instiDtls[0]))

			codeDtls = cursor.fetchone()
			if codeDtls:
				instiCode = codeDtls[0][0:4]+str(instiDtls[0])
			else:
				instiCode = code[0:4]+str(instiDtls[0])
				instiCodeInsertQuery = ("""INSERT INTO `institution_dtls_and_code_map`(`INSTITUTION_ID`, 
				`PHONE_NUMBER`, `CODE`) VALUES (%s,%s,%s)""")

				codeData = (instiDtls[0],phone_no,instiCode)

				cursor.execute(instiCodeInsertQuery,codeData)
				
			details['institution_id'] = instiDtls[0]
			details['institution_code'] = instiCode
			connection.commit()
			cursor.close()
		return ({"attributes": {
	    				"status_desc": "Institution Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"InstitutionDtls":details}}), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0')