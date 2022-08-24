from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields

app = Flask(__name__)
app1 = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
mysql1 = MySQL()
grammar_content_details = Blueprint('grammar_content_api', __name__)
api = Api(grammar_content_details, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('GrammarContent', description=':Grammar Content Details')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_lab_lang1'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app1.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app1.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app1.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app1.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql1.init_app(app1)

app.config['CORS_HEADERS'] = 'Content-Type'


@name_space.route("/getGrammarContentDetails/<string:dashboard_desc>/<string:activity_desc>")
class getGrammarContentDetails(Resource):
	def get(self,dashboard_desc,activity_desc):
		connection = mysql.connect()
		cursor = connection.cursor()
		cursor.execute("""SELECT cm.`Content_Master_ID` as content_id, cm.`content_master_name` as content_name, 
			cm.`Content_Image_Path` as content_image_url FROM content_master cm WHERE cm.`Content_Master_ID` in 
			(SELECT `Content_Master_ID` FROM `content_rule` WHERE `Activity_Mapping_ID` in 
			(SELECT `Activity_Mapping_ID` FROM `activity_mapping` WHERE `Activity_ID` in 
			(SELECT `Activity_ID` FROM `activity` WHERE `Activity_Desc` like %s)) 
			and level = %s)""",(dashboard_desc,activity_desc.split()[-1]))
		details = cursor.fetchall()
		if details:
			desc = cursor.description
			column_names = [col[0] for col in desc]
			content_details = [dict(izip(column_names, row)) for row in details]
			print(content_details)
		else:
			content_details = []
		cursor.close()
		return ({"attributes": {
	    				"status_desc": "Content Details.",
	    				"status": "success"
	    				},
	    				"responseList":content_details}), status.HTTP_200_OK

@name_space.route("/getMysyllabusContentDetails/<activity_id>/<user_class>/<board>")
class getMysyllabusContentDetails(Resource):
	def get(self,activity_id,user_class,board):
		connection = mysql.connect()
		cursor = connection.cursor()
		cursor.execute("""SELECT cm.`Content_Master_ID` as content_id, cm.`content_master_name` as 
			content_name, cm.`Content_Image_Path` as content_image_url FROM content_master cm 
			WHERE cm.`Content_Master_ID` in 
			(SELECT `Content_Master_ID` FROM `content_rule` WHERE `Activity_Mapping_ID` in 
			(SELECT `Activity_Mapping_ID` FROM `activity_mapping` WHERE `Activity_ID` = %s) 
			and board_id = (SELECT `Board_ID`FROM `board` WHERE `Board_Desc` = %s) AND class = %s)""",(activity_id,board,user_class))
		details = cursor.fetchall()
		if details:
			desc = cursor.description
			column_names = [col[0] for col in desc]
			content_details = [dict(izip(column_names, row)) for row in details]
			print(content_details)
		
			for i in range(len(content_details)):
				content_details[i]['Board_Desc'] = board
		else:
			content_details = []
		cursor.close()
		return ({"attributes": {
	    				"status_desc": "Content Details.",
	    				"status": "success"
	    				},
	    				"responseList":content_details}), status.HTTP_200_OK


@name_space.route("/getWorksheetDetails/<int:activity_id>/<int:user_class>/<string:board_desc>")
class getWorksheet(Resource):
	def get(self,activity_id,user_class,board_desc):
		connection = mysql.connect()
		cursor = connection.cursor()

		conn = mysql1.connect()
		cur = conn.cursor()
		worksheet_data = []
		# if role.lower() == 'student':

		cursor.execute("""SELECT `Content_Master_ID`,`Content_Type`,`Content_Master_Name`, 
			`Content_Image_Path` FROM `content_master` WHERE `Content_Master_ID` in 
			(SELECT `Content_Master_ID` FROM `content_rule` WHERE `Class` = %s and `Board_ID` in 
			(SELECT `Board_ID` FROM `board` WHERE `Board_Desc` = %s) and `Activity_Mapping_ID` in
			(SELECT `Activity_Mapping_ID` FROM `activity_mapping` WHERE `Activity_ID` = %s and 
			`Activity_Category_ID` = 0 AND `Activity_Category_Type_ID` = 0 
			AND `Activity_Category_Sub_Type_ID` = 0))""",(user_class,board_desc,activity_id))

		worksheet_dtls = cursor.fetchall()
		if worksheet_dtls:
			desc = cursor.description
			col_names = [col[0] for col in desc]
			worksheet_data = [dict(izip(col_names, row)) for row in worksheet_dtls]

		for idx in worksheet_data:
			content_id = idx['Content_Master_ID']
			cur.execute("""SELECT `product_id` FROM `product_content_master` 
				WHERE `content_master_id` = %s""",(content_id))
			product_id = cur.fetchone()
			if product_id:
				product_id = product_id[0]
				cur.execute("""SELECT `Dashboard_ID`,`Activity_ID`,`Activity_Type`, 
					`Product_CODE`,`Product_Desc`,`Product_Image_Path`,`Product_Price`,
					`GST_Value`,`SGST_Value`,`CGST_Value`,`Delivery_Charges`,
					`Delivery_Charges_Waived_Flag`,`Start_Date`,`End_Date`,`Period_Type`,
					`Period_Duration`, `Discount` FROM `product` WHERE `Product_ID` = %s""",(product_id))

				product_dtls = cur.fetchall()
				if product_dtls:
					desc = cur.description
					col_names = [col[0] for col in desc]
					product_data = [dict(izip(col_names, row)) for row in product_dtls]
					for i in range(len(product_data)):
						product_data[i]['Delivery_Charges'] = float(product_data[i]['Delivery_Charges'])
						product_data[i]['Start_Date'] = (product_data[i]['Start_Date']).isoformat()
						product_data[i]['End_Date'] = (product_data[i]['End_Date']).isoformat()
					idx['product_data'] = product_data
		# else:
		# 	cursor.execute("""SELECT `Content_Master_ID`,`Content_Type`,`Content_Master_Name`, 
		# 		`Content_Image_Path` FROM `content_master` WHERE `Content_Master_ID` in 
		# 		(SELECT `Content_Master_ID` FROM `content_rule` WHERE `Activity_Mapping_ID` in
		# 		(SELECT `Activity_Mapping_ID` FROM `activity_mapping` WHERE `Activity_ID` = %s and 
		# 		`Activity_Category_ID` = 0 AND `Activity_Category_Type_ID` = 0 
		# 		AND `Activity_Category_Sub_Type_ID` = 0))""",(activity_id))

		# 	worksheet_dtls = cursor.fetchall()
		# 	if worksheet_dtls:
		# 		desc = cursor.description
		# 		col_names = [col[0] for col in desc]
		# 		worksheet_data = [dict(izip(col_names, row)) for row in worksheet_dtls]

		# 	for idx in worksheet_data:
		# 		content_id = idx['Content_Master_ID']
		# 		cur.execute("""SELECT `product_id` FROM `product_content_master` 
		# 			WHERE `content_master_id` = %s""",(content_id))
		# 		product_id = cur.fetchone()
		# 		if product_id:
		# 			product_id = product_id[0]
		# 			cur.execute("""SELECT `Dashboard_ID`,`Activity_ID`,`Activity_Type`, 
		# 				`Product_CODE`,`Product_Desc`,`Product_Image_Path`,`Product_Price`,
		# 				`GST_Value`,`SGST_Value`,`CGST_Value`,`Delivery_Charges`,
		# 				`Delivery_Charges_Waived_Flag`,`Start_Date`,`End_Date`,`Period_Type`,
		# 				`Period_Duration` FROM `product` WHERE `Product_ID` = %s""",(product_id))

		# 			product_dtls = cur.fetchall()
		# 			if product_dtls:
		# 				desc = cur.description
		# 				col_names = [col[0] for col in desc]
		# 				product_data = [dict(izip(col_names, row)) for row in product_dtls]
		# 				for i in range(len(product_data)):
		# 					product_data[i]['Delivery_Charges'] = float(product_data[i]['Delivery_Charges'])
		# 					product_data[i]['Start_Date'] = (product_data[i]['Start_Date']).isoformat()
		# 					product_data[i]['End_Date'] = (product_data[i]['End_Date']).isoformat()
		# 				idx['product_data'] = product_data
		cursor.close()
		cur.close()
		return ({"attributes": {
		    				"status_desc": "Worksheet Details.",
		    				"status": "success"
		    				},
		    				"responseList":worksheet_data}), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0')