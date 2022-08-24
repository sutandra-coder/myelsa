from flask import Flask, request, jsonify, json, render_template
from flask_api import status
from jinja2._compat import izip
import datetime
# from datetime import datetime
import pymysql
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests, os
from PIL import Image
import imgkit
import wget
app = Flask(__name__)
app_next = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
mysql_next = MySQL()
yrb_admin_portal = Blueprint('yrb_admin_portal_api', __name__)
api = Api(yrb_admin_portal,  title='MyElsa API',
          description='MyElsa API')
name_space = api.namespace('YRBAdminPortal',
                           description='YRB Admin Portal')
name_space_next = api.namespace('YRBCAdmin',
                               description='YRBC Admin')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_yrbc'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)
connection = mysql.connect()

app_next.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app_next.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app_next.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app_next.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql_next.init_app(app_next)
connection_next = mysql_next.connect()

def mysql_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                user='creamson_langlab',
                                password='Langlab@123',
                                db='creamson_logindb',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection

def mysql_next_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                user='creamson_langlab',
                                password='Langlab@123',
                                db='creamson_yrbc',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection


UPLOAD_FOLDER = '/home/ubuntu/tally/uploadfolder'
SERVER_PATH = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/tally/uploadfolder/'

post_feedback_model = api.model('postfeedback', {
    "Participant_ID": fields.Integer(),
    "Institution_user_id": fields.Integer(),
    "Length_Word_Limit": fields.String(),
    "Character": fields.String(),
    "Plot_of_the_story": fields.String(),
    "Vocabulary_Grammar": fields.String(),
    "Comment": fields.String(),
    "Last_Update_Id": fields.Integer()})

addUser = api.model('addUserDto', {
    "city": fields.String(),
    "dateOfBirth": fields.String(),
    "emailId": fields.String(),
    "firstName": fields.String(),
    "gender": fields.String(),
    "institutionUserName": fields.String(),
    "institutionUserPassword": fields.String(),
    "institutionUserRole": fields.String(),
    "institutionUserStatus": fields.String(),
    "lastName": fields.String(),
    "middleName": fields.String(),
    "pincode": fields.String(),
    "primaryContactNumber": fields.String(),
    "secondaryContactNumber": fields.String(),
    "state": fields.String(),
    "streetAddress": fields.String(),
    "userEndDate": fields.String(),
    "userEnrollDate": fields.String(),
    "userTaxId": fields.String(),
    "userUniqueId": fields.String(),
    "board": fields.String(),
    "studentname": fields.String(),
    "class": fields.String(),
    "institutionName": fields.String(),
    "institutionId": fields.Integer(),
    "licenseKey": fields.String()
    })

cert_model = api.model('cert_model', {
    "schoolname": fields.String(),
    "imagepath": fields.String(),
    "class": fields.String(),
    "phoneno": fields.String(),
    "username": fields.String(),
    "userid": fields.String()})

user_profile_update = api.model('User Profile Update', {
    "firstname":fields.String(),
    "lastname":fields.String(),
    "middlename":fields.String(),
    "parentsname":fields.String(),
    "city":fields.String(),
    "user_class":fields.String(),
    "mobileno":fields.String(),
    "emailid":fields.String(),
    "institutionname":fields.String(),
    "update_status":fields.String(required=True),
    "certificate_status":fields.String(required=True)
    })

user_download_update = api.model('User download Update', {
    "is_download":fields.String(required=True)
    })



@name_space.route("/getfilepath")
class getfilepath(Resource):
    def get(self):
        connection = mysql.connect()
        cursor = connection.cursor()

        cursor.execute("""SELECT `Participant_Id`,`participant_institution_user_id`,`name`,`Class`,
            `Primary_Contact_No`,`School_Name`,`Content_File_Path`
            FROM `yrb_participant`""")

        get_file = cursor.fetchall()

        if get_file:
            desc = cursor.description
            print(desc)
            col_names = [col[0] for col in desc]
            yrb_details = [dict(izip(col_names, row)) for row in get_file]
            # print(yrb_details)
            # file_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/tally/uploadfolder/8729980130.png'
            # file_name = requests.get(file_url,allow_redirects=True)
            # # print(os.path.abspath(file_name))
            # open('c:/users/hello.pdf', 'wb').write(file_name.content)
            # filepath = os.path.abspath(file_name)
            # yrb_details['Last_Update_TS'] = yrb_details['Last_Update_TS'].isoformat()

        else:
            yrb_details = []
        cursor.close()
        return ({"attributes": {"status_desc": "YRB Details.",
                                "status": "success"
                                },
                 "responseList": yrb_details}), status.HTTP_200_OK


@name_space.route("/feedbackdetailsPost")
class feedbackdetailsPost(Resource):
    @api.expect(post_feedback_model)
    def post(self):
        connection = mysql.connect()
        cursor = connection.cursor()
        details = request.get_json()

        Participant_ID = details['Participant_ID']
        Institution_user_id = details['Institution_user_id']
        Length_Word_Limit = details['Length_Word_Limit']
        Character = details['Character']
        Plot_of_the_story = details['Plot_of_the_story']
        Vocabulary_Grammar = details['Vocabulary_Grammar']
        Comment = details['Comment']
        Last_Update_Id = details['Last_Update_Id']
        feedback_insert_query = ("""INSERT INTO feedback(`Participant_ID`, `Institution_user_id`, `Length_Word_Limit`, 
         `Character`, `Plot_of_the_story`, `Vocabulary_Grammar`, `Comment`, `Last_Update_Id`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
        feedback_data = (Participant_ID, Institution_user_id, Length_Word_Limit, Character, 
            Plot_of_the_story, Vocabulary_Grammar, Comment, Last_Update_Id)
        cursor.execute(feedback_insert_query, feedback_data)
        connection.commit()

        
        return ({"attributes": {"status_desc": "YRB Details",
                                "status": "success"
                                }
                 }), status.HTTP_200_OK


@name_space.route("/yrb_leaderboard/<int:user_id>")
class yrb_leaderboard(Resource):
    def get(self,user_id):
        connection = mysql.connect()
        cursor = connection.cursor()

        cursor.execute("""SELECT `Participant_Id`,`participant_institution_user_id`,`name`,`Class`,
            `Primary_Contact_No`,`School_Name`,`certificate_path`
            FROM `yrb_participant`""")

        get_file = cursor.fetchall()

        if get_file:
            desc = cursor.description
            col_names = [col[0] for col in desc]
            yrb_details = [dict(izip(col_names, row)) for row in get_file]
            for i,j in enumerate(yrb_details):
                j['image_url'] = None
        else:
            yrb_details = []

        cursor.execute("""SELECT `certificate_path` FROM `yrb_participant` 
            where `participant_institution_user_id` = %s""",(user_id))

        cert_path = cursor.fetchone()
        if cert_path:
            cert_path = cert_path[0]
        else:
            cert_path = None
        cursor.close()

        return ({"attributes": {"status_desc": "YRB Details.",
                                "status": "success"
                                },
                 "responseList": {"user_certificate_path":cert_path,
                                    "all_users":yrb_details}}), status.HTTP_200_OK


@name_space.route("/yrb_register")
class yrb_register(Resource):
    @api.expect(addUser)
    def put(self):
        payload = request.get_json()
        connection = mysql.connect()
        cursor = connection.cursor()
        phone_no = payload['institutionUserName']
        post_url = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/myelsa_registration/myELSARegistration/registration'
        payload = json.dumps(payload)
        headers = {'Content-type':'application/json', 'Accept':'application/json'}
        post_response = requests.post(post_url, data=payload, headers=headers)
        r = post_response.json()
        res_status = r['responseList']['STATUS']
        res_user_id = r['responseList']['user_id']
        print(r,res_status,res_user_id)
        # print(r)
        update_query = ("""UPDATE `yrb_participant` SET `participant_institution_user_id` = %s 
            WHERE `Primary_Contact_No` = %s""")
        update_data = (res_user_id,phone_no)
        cursor.execute(update_query,update_data)

        return r



@name_space.route("/yrb_certificate")
class yrb_certificate(Resource):
    @api.expect(cert_model)
    def put(self):
        details = request.get_json()
        connection = mysql.connect()
        cursor = connection.cursor()
        template_name = 'yrb_cert.html'
        # filename = 'templates/hetal.html'
        outputFilename = "{}.png".format(details['username'].replace(' ','_')+details['userid'])
        d1 = {'name':details['username'],'school':details['schoolname']}
        sourceHtml = render_template(template_name, details=d1)
        filename = os.path.join(UPLOAD_FOLDER,outputFilename)
        open(filename,'w').write(sourceHtml)
        config = imgkit.config(wkhtmltoimage='/usr/bin/wkhtmltoimage')
        imgkit.from_string(sourceHtml,filename,config=config)
        original = Image.open(filename)
        width, height = original.size   # Get dimensions
        print(width, height)
        left = 0
        top = 0
        right = 720
        bottom = 546
        cropped_example = original.crop((left, top, right, bottom))
        # cropped_example.show()
        # open('yrbtest.png','w').write(cropped_example)
        cropped_example.save(filename)
        # update_query = ("""""")
        abs_html_path = SERVER_PATH+outputFilename
        # os.remove(filename)
        return abs_html_path


@name_space.route("/update_yrb_profile/<int:user_id>")
class update_yrb_profile(Resource):
    @api.expect(user_profile_update)
    def put(self,user_id):
        details = request.get_json()
        connection = mysql.connect()
        cursor = connection.cursor()
        name = details['firstname'] + ' ' + details['lastname']
        user_class = details['user_class']
        institutionname = details['institutionname']
        update_status = details['update_status']
        mobileno = details['mobileno']
        city = details['city']
        certificate_status = details['certificate_status']
        update_query = ("""UPDATE `yrb_participant` SET `name` = %s,`Class` = %s, 
            `School_Name` = %s, `update_status` = %s,`secondary_phoneno`= %s, 
            `location` = %s, `certificate_status` = %s where participant_institution_user_id = %s""")

        update_data = (name,user_class,institutionname,update_status,mobileno,city,certificate_status,user_id)

        cursor.execute(update_query,update_data)

        connection.commit()
        cursor.close()

        response = 'Profile Updated'
        return ({"attributes": {"status_desc": "YRB Profile Details.",
                                "status": "success"
                                },
                 "responseList": response}), status.HTTP_200_OK

@name_space.route("/update_yrb_download/<int:user_id>/<string:is_download>")
class update_yrb_download(Resource):
    def put(self,user_id,is_download):
        details = request.get_json()
        connection = mysql.connect()
        cursor = connection.cursor()
        update_query = ("""UPDATE `yrb_participant` SET `is_download` = %s 
            where participant_institution_user_id = %s""")

        update_data = (is_download,user_id)

        cursor.execute(update_query,update_data)

        connection.commit()
        cursor.close()
        response = 'Profile Updated'
        return ({"attributes": {"status_desc": "YRB Profile Details.",
                                "status": "success"
                                },
                 "responseList": response}), status.HTTP_200_OK


@name_space.route("/getYRBProfileStatus/<int:user_id>")
class getYRBProfileStatus(Resource):
    def get(self,user_id):
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("""SELECT `update_status`,`is_download`,`certificate_status` 
            FROM `yrb_participant` WHERE `participant_institution_user_id` = %s""",(user_id))

        user_status = cursor.fetchone()
        if user_status:
            update_status = user_status[0]
            is_download = user_status[1]
            certificate_status = user_status[2]
        response = {"update_status":update_status,
                    "is_download":is_download,
                    "certificate_status":certificate_status} 

        cursor.close()

        return ({"attributes": {"status_desc": "YRB Profile Details.",
                                "status": "success"
                                },
                 "responseList": response}), status.HTTP_200_OK

@name_space_next.route("/user_tracking_details/<string:Tracking_StartDate>/<string:Tracking_EndDate>/<int:Count>")
class user_tracking_details(Resource):
    def get(self, Tracking_StartDate, Tracking_EndDate, Count):
        connection = mysql.connect()
        cursor = connection.cursor()

        connection_next = mysql_next.connect()
        cursor_next = connection_next.cursor()
        details = []
        cursor.execute("""SELECT `participant_institution_user_id`,'' as Track_day,'' as 
        Count_of_days,name FROM `yrb_participant`""")

        get_details = cursor.fetchall()

        if get_details:
            desc = cursor.description
            col_names = [col[0] for col in desc]
            get_user_tracking_details = [dict(izip(col_names, row)) for row in get_details]

            for i in range(len(get_user_tracking_details)):
                details.append(
                    get_user_tracking_details[i]['participant_institution_user_id'])
            details = tuple(details)
            
            cursor_next.execute("""SELECT *, LENGTH(Track_day) - LENGTH(REPLACE(Track_day, ',', '')) +1 
                AS COUNT_OF_days FROM (SELECT `institution_user_id`,
                GROUP_CONCAT(DISTINCT(date(`last_update_ts`))) AS Track_day 
                FROM `institution_user_tracking` WHERE `institution_user_id` 
                in %s and date(`start_time`) between %s and %s GROUP BY
                  `institution_user_id` ORDER BY (DAY(`last_update_ts`)) ASC) AS cnt2
                  HAVING COUNT_OF_days > %s""",(details,Tracking_StartDate,Tracking_EndDate,Count))
        track_details = cursor_next.fetchall()
        if track_details:
            desc = cursor.description
            col_names = [col[0] for col in desc]
            get_tracking_details = [dict(izip(col_names, row)) for row in track_details]
            for i in range(len(get_tracking_details)):
                cursor.execute("""SELECT `name`,Primary_Contact_No
                    FROM `yrb_participant` where participant_institution_user_id=%s""",(get_tracking_details[i]['participant_institution_user_id']))

                get_name = cursor.fetchone()
                get_tracking_details[i]['name']=get_name[0]
                get_tracking_details[i]['phone_no']=get_name[1]
        else:
            get_tracking_details = []
        cursor.close()
        return ({"attributes": {"status_desc": "YRB User Tracking Details.",
                                "status": "success"
                                },
                "responseList": get_tracking_details}), status.HTTP_200_OK

@name_space_next.route("/totalparticipant")
class getfilepath(Resource):
    def get(self):
        connection = mysql.connect()
        cursor = connection.cursor()

        cursor.execute("""SELECT COUNT(`participant_institution_user_id`) as Total
            FROM `yrb_participant`""")

        total = cursor.fetchall()

        if total:
            desc = cursor.description
            col_names = [col[0] for col in desc]
            total_count = [dict(izip(col_names, row)) for row in total]

        else:
            total_count = []
        cursor.close()
        return ({"attributes": {"status_desc": "YRB Details.",
                                "status": "success"
                                },
                "responseList": total_count}), status.HTTP_200_OK

@name_space.route("/yrbc_feedback_dtls/<int:institution_user_id>")
class yrbc_feedback_dtls(Resource):
    def get(self,institution_user_id):
        next_connection = mysql_next_connection()
        next_cursor = next_connection.cursor()

        connection = mysql_connection()
        cursor = connection.cursor()
        details=[]

        next_cursor.execute("""SELECT `Plot_of_the_story` as 'Plot of the story',
        `Length_Word_Limit`as 'Word limit and length', `Vocabulary_Grammar` as 
        'Vocabulary and grammar',`Character`,`Our_assessment` as 'Our assessment',
        `Rating` FROM `yrb_participant` INNER join `feedback` on yrb_participant.
        `participant_institution_user_id`=feedback. `Institution_user_id` where 
        `participant_institution_user_id`=%s""",(institution_user_id))
            
        feebback_dtls = next_cursor.fetchone()
        if feebback_dtls:
            for i,j in feebback_dtls.items():
                details.append({
                        "label":i,
                        "comment":j
                        })
            # feebback_dtls['Length_Word_Limit']=IMAGE_URL['IMAGE_URL']
            # feebback_dtls['IMAGE_URL']=IMAGE_URL['IMAGE_URL']
            Rating=feebback_dtls['Rating']
        else:
            return ({"attributes": {"status_desc": "Report Details fetched.",
                                "status": "success",
                                "Rating": 0
                                },
                 "responseList": []}), status.HTTP_200_OK

        cursor.close()
        return ({"attributes": {"status_desc": "Report Details fetched.",
                                "status": "success",
                                "Rating": Rating
                                },
                 "responseList": details}), status.HTTP_200_OK

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
