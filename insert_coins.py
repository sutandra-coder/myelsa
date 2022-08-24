from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
insert_coins = Blueprint('insert_coins_api', __name__)
api = Api(insert_coins, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('InsertCoins', description='Insert Coins')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'

mysql.init_app(app)


app.config['CORS_HEADERS'] = 'Content-Type'

insertcoin_post = api.model('insert_coins', {
	"user_id":fields.Integer(required=True),
	"coins":fields.Integer(required=True),
	"content_or_assessment_id":fields.Integer(required=True),
	"status":fields.String(required=True),})

updatecoin_put = api.model('update_coins', {
	"user_id":fields.Integer(required=True),
	"coins":fields.Integer(required=True),
	"total_earned_coins":fields.Integer(required=True),})

@name_space.route("/insert_coins")
class insertCoins(Resource):
	@api.expect(insertcoin_post)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		user_id = details['user_id']
		coins = details['coins']
		status_type = details['status']
		content_or_assessment_id = details['content_or_assessment_id']

		cursor.execute("""SELECT `Coins_transaction_Id` FROM `reward_transaction` 
			WHERE `INSTITUTION_USER_ID` = %s and `Transaction_Type` = %s 
			and `Remarks` = %s""",(user_id,status_type,content_or_assessment_id))

		trans_id = cursor.fetchone()
		if trans_id:
			trans_id = trans_id[0]

		if not trans_id:
			cursor.execute("""SELECT `ID`, `Coins`,`Total_earned_Coins` FROM `rewards_profile` 
				WHERE `INSTITUTION_USER_ID` = %s""",(user_id))

			previous_dtls = cursor.fetchall()
			print(previous_dtls)
			if previous_dtls:
				idx = previous_dtls[0][0]
				pre_coins = previous_dtls[0][1]
				total_coins = previous_dtls[0][2]
			else:
				profile_insert_query = ("""INSERT INTO `rewards_profile`(`INSTITUTION_USER_ID`, `Coins`, 
					`Star`,`Total_earned_Coins`,`Total_earned_Stars`, `Medel`,`Event_Coin`, `Last_ID`) 
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
				profile_data = (user_id,coins,0,coins,0,0,0,0)

				cursor.execute(profile_insert_query,profile_data)
				idx = cursor.lastrowid
				pre_coins = 0
				total_coins = 0
			coin = (idx,pre_coins,total_coins)

			trans_insert_query = ("""INSERT INTO `reward_transaction`(`INSTITUTION_USER_ID`, 
				`Transaction_Type`, `Redeem_ID`, `Previous_Coins`, `Coin_value`, `Updated_Coins`,
				`Previous_Star_Value`, `Star_Value`, `Reset_Star`, `Updated_Star_Value`, 
				`Event_Coin`, `Updated_Event_Coin`, `Previous_Event_Coin`, `Remarks`,`Last_ID`) 
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
			updated_coins = pre_coins+coins
			trans_data = (user_id,status_type,0,pre_coins,coins, updated_coins,0,0,0,0,0,0,0,content_or_assessment_id,0)
			cursor.execute(trans_insert_query,trans_data)

			total_earned_coins = total_coins + coins

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			update_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/insert_coins/InsertCoins/update_coins'
			update_data = {"user_id": user_id,
							"coins": updated_coins,
							"total_earned_coins": total_earned_coins
							}
			update_response = requests.put(update_url,data = json.dumps(update_data),headers = headers)
			r1 = update_response.json()
			print(r1,update_response.status_code)

			connection.commit()
			cursor.close()

			details['previous_coins'] = pre_coins
			details['updated_coins'] = updated_coins
			details['total_earned_coins'] = total_earned_coins

			return ({"attributes": {
			    				"status_desc": "Reward Coin Details.",
			    				"status": "success"
			    				},
			    				"responseList":details}), status.HTTP_200_OK
		else:
			return ({"attributes": {
			    				"status_desc": "Reward Coin Details.",
			    				"status": "success"
			    				},
			    				"responseList":{}}), status.HTTP_200_OK


@name_space.route("/update_coins")
class updateCoins(Resource):
	@api.expect(updatecoin_put)
	def put(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		user_id = details['user_id']
		coins = details['coins']
		total_earned_coins = details['total_earned_coins']

		profile_update_query = ("""UPDATE `rewards_profile` SET `Coins`= %s, 
			`Total_earned_Coins`= %s WHERE `INSTITUTION_USER_ID` = %s""")
		update_data = (coins,total_earned_coins,user_id)
		cursor.execute(profile_update_query,update_data)
		connection.commit()
		cursor.close()

		return ({"attributes": {
		    				"status_desc": "Reward Coin Details.",
		    				"status": "success"
		    				},
		    				"responseList":{"RewardCoinDtls":details}}), status.HTTP_200_OK	


if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)