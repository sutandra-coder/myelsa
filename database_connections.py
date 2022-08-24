import pymysql

def creamson_academy_connection():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_academy',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

def connect_gif():
    connection = pymysql.connect(host='gif-project.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
                                 user='admin',
                                 password='mldtFSH8GKgRSOViqshD',
                                 db='gif_user_credentials',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


'''def connect_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def connect_logindb():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='cbdHoRPQPRfTdC0uSPLt',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection


def connect_lab_lang1():
	connection = pymysql.connect(host='creamsonservices.com',
                                user='creamson_langlab',
                                password='Langlab@123',
                                db='creamson_lab_lang1',
                                charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection


'''def connect_userLibrary():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_user_library',
									charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def connect_userLibrary():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_user_library',
									charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)

def connect_elsalibrary():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='myelsa_user_library',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection