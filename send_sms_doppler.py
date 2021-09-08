from __future__ import print_function
import pickle
import os.path
import sys
import os.path

import datetime
from datetime import timedelta  

from apiclient import errors
from apiclient import http
import io
#from io import StringIO
import pandas as pd
import numpy as np
import csv

import logging
import psycopg2
import psycopg2.extras
import configparser


import smtplib  
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


#import itertools
#from random import randint
#from statistics import mean

import boto3
import requests 
from requests.exceptions import HTTPError

print("Ejecutando ")
config = configparser.ConfigParser()
config.read('/home/ec2-pentaho/pentaho/dynamo/credential/config.ini')
#config.read('D:/jhonn/PROYECTOS/UND/APP/DYNAMO/credential/config.ini')

PRODUCTION = config['CONFIG']['PRODUCTION']

if PRODUCTION == '1':
	print("Entorno de produccion")
	config_param = 'CREDENTIAL_PG_INTERNO'
	path='/home/ec2-pentaho/pentaho/lumingo/Automatizado_Supermercado_1'
	PATH_LOG = '/home/ec2-pentaho/pentaho/lumingo/Automatizado_Supermercado_1/log/'#config['CONFIG']['PATH_LOG_INFOBIP_GET_DATA']
else:
	print("Entorno de desarrollo")
	config_param = 'CREDENTIAL_PG_EXTERNO'
	PATH_LOG = '../log/'
	path='D:/jhonn/PROYECTOS/UND/Automatizados/Automatizados UND/Automatizados UND/PAGO_EFECTIVO/RECORDATORIO'



print(PRODUCTION)
USER = config[config_param]['USER']
PASSWORD = config[config_param]['PASSWORD']
HOST = config[config_param]['HOST']
PORT = config[config_param]['PORT']


config_mail = 'CONFIG_MAIL'

SENDER_NAME_SMTP = config[config_mail]['SENDER_NAME']
SENDER_SMTP = config[config_mail]['SENDER']
RECEIVERS_SMTP = config[config_mail]['RECEIVERS']
HOST_SMTP = config[config_mail]['HOST']
PORT_SMTP = config[config_mail]['PORT']
USERNAME_SMTP = config[config_mail]['USERNAME']
PASSWORD_SMTP = config[config_mail]['PASSWSORD']


ACCESS_KEY = config['default']['aws_access_key_id']
SECRET_KEY = config['default']['aws_secret_access_key']
#SESSION_TOKEN = config['default']['PASSWSORD']

now = datetime.datetime.now()
yesterday = datetime.datetime.now() - timedelta(days=30) 
print(yesterday.strftime("%Y-%m"))

name_log =PATH_LOG+'log_sms_doppler_'+now.strftime("%Y_%m_%d")+'.log'
logging.basicConfig(filename=name_log,  filemode='a',format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


mail_titulo="[Doppler] Recordatorio SMS Doppler"

def sendMail(subject,message):
	print("Enviando mensaje")
	print(subject)
	print(message)
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = email.utils.formataddr((SENDER_NAME_SMTP, SENDER_SMTP))
	msg['To'] = RECEIVERS_SMTP
	part1 = MIMEText(message, 'plain')
	#part2 = MIMEText(BODY_HTML, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	msg.attach(part1)
	#msg.attach(part2)

	# Try to send the message.
	try:  
	    server = smtplib.SMTP(HOST_SMTP, PORT_SMTP)
	    server.ehlo()
	    server.starttls()
	    #stmplib docs recommend calling ehlo() before & after starttls()
	    server.ehlo()
	    server.login(USERNAME_SMTP, PASSWORD_SMTP)
	    server.sendmail(SENDER_SMTP, RECEIVERS_SMTP.split(','), msg.as_string())
	    server.close()
	# Display an error message if something goes wrong.
	except Exception as e:
		logging.error(f"Exception occurred: {e}", exc_info=True)
	else:
	    logging.info("Mail enviado")
	return

def leerDatos():
	connectionPy=None
	try:

		connection = psycopg2.connect(user = USER,
										password = PASSWORD,
										host = HOST,
										port = PORT,
										database = 'Pago Efectivo')
		cursor = connection.cursor()

		postgreSQL_select_Query = """ select
	a.*,
	case 
						when to_char(fecha_expiracion,'D')='1' then 'Dom '
						when to_char(fecha_expiracion,'D')='2' then 'Lun '
						when to_char(fecha_expiracion,'D')='3' then 'Mar '
						when to_char(fecha_expiracion,'D')='4' then 'Mie '
						when to_char(fecha_expiracion,'D')='5' then 'Jue '
						when to_char(fecha_expiracion,'D')='6' then 'Vie '
						when to_char(fecha_expiracion,'D')='7' then 'Sáb '
						else ''
					end || to_char(fecha_expiracion,'DD/MM/YY HH12:MIAM') as fecha_expiracion_t
					
from recordatorio.envio_celular_servicio_temp a 
inner join recordatorio.servicio_evento b on b.idservicio = a.id_servicio and b.plataforma_envio_celular=2
where envio_emblue_celular = false
order by a.evento_celular; """
		cursor.execute(postgreSQL_select_Query)
		datos = cursor.fetchall()
		#print(datos)
		cols = list(map(lambda x: x[0], cursor.description))
		df = pd.DataFrame(datos, columns=cols)
		cursor.close()
		#for index, dato in df.iterrows():
		groups = list()
		groups_data = list()
		#print(df)
		param = []
		datos_doppler = []
		ultimo = True
		contador = 0
		contador_enviados = 0
		contador_final = 0
		for g, data in df.groupby('evento_celular'):

			ultimo = True
			param = []
			datos_doppler = []
			contador = 0

			for index, dato in data.iterrows():
				contador = contador + 1
				contador_final = contador_final + 1
				datos_doppler.append({
						'email':(dato['mail_cip'].split('@')[0])+'@dopplersms.com' ##dato['mail_cip']
						,'fields':[
							{
								'name':'NroCIP'
								,'value':dato['cip']
							},
							{
								'name':'IdServicio'
								,'value':dato['id_servicio']
							},
							{
								'name':'EstadoCIP'
								,'value':dato['estado_cip']
							},
							{
								'name':'FechaGeneracion'
								,'value':str(dato['fecha_generacion'])
							},
							{
								'name':'FechaExpiracion'
								,'value':dato['fecha_expiracion_t']
							},
							{
								'name':'Tienda'
								,'value':dato['tienda']
							},
							{
								'name':'Monto'
								,'value':dato['monto']
							},
							{
								'name':'Moneda'
								,'value':dato['moneda']
							},
							{
								'name':'IdMoneda'
								,'value':('S/' if dato['moneda'].upper() =='SOLES' else 'USD')
							},
							{
								'name':'telefono'
								,'value':dato['celular']
							}
						]
					}
				)
				param.append([
					dato['mail_cip']
					]
				)
				if contador > 100:		
					estado = sendDoppler(g,datos_doppler,param)		
					if estado == 1:
						contador_enviados = contador_enviados + contador	
					param = []
					datos_doppler = []
					contador = 0
					ultimo = True

			if ultimo == True and contador > 0:
				estado = sendDoppler(g,datos_doppler,param)	
				if estado == 1:
					contador_enviados = contador_enviados + contador
				param = []
				datos_doppler = []
				contador = 0
				ultimo = True

		if ultimo == True and contador > 0:
			estado = sendDoppler(g,datos_doppler,param)	
			if estado == 1:
				contador_enviados = contador_enviados + contador

		sendMail(mail_titulo,f"{contador_enviados} SMS enviados de {contador_final} al api de Doppler para sus envíos correspondientes")

	except ( psycopg2.Error) as error :		
		logging.error(f"Ocurrio un error al listar : {error}", exc_info=True)
		print(error)
		raise error
	except (Exception) as error :		
		logging.error(f"Ocurrio un error al insertar : {error}", exc_info=True)
		print(error)
		raise error
	finally:
		if(connection):
			cursor.close()
			connection.close()

def sendDoppler(list_id,datos_doppler,param):
	url = 'https://restapi.fromdoppler.com/accounts/daniel.hualpa@orbis.com.pe/lists/'+str(list_id)+'/subscribers/import'
	estado = 0
	token = 'token 60DB215E1C773FAB0E7F2DA1B9792169'
	headers = {'Content-type': 'application/json', 'Authorization': token}
	#r = requests.get(url, data=json.dumps(data), headers=headers)
	

	data =  {
			    "items": datos_doppler,
				"fields":[
				    "NroCIP",
				    "EstadoCIP",
				    "FechaGeneracion",
				    "FechaExpiracion",
				    "IdServicio",
				    "Tienda",
				    "Monto",
				    "Moneda",
				    "IdMoneda",
				    "icono",
				    "HoraTienda",
				    "WaTienda",
				    "TipoCompra",
				    "telefono"
				]
			}	
	print(data)
	try:    	
		r = requests.post(url, headers=headers, json=data)
	except HTTPError as http_err:
		sendMail(mail_titulo,f"Ocurrio un error al enviar {url}: {http_err}")
		logging.error(f"Ocurrio un error al consultar {url}: {http_err}", exc_info=True)
		print(f'HTTP error occurred: {http_err}')  # Python 3.6
		estado = 0
	except Exception as err:
		sendMail(mail_titulo,f"Ocurrio un error al enviar {url}: {err}")
		logging.error(f"Ocurrio un error al consultar {url}: {err}", exc_info=True)
		print(f'Other error occurred: {err}')  # Python 3.6
		estado = 0
	else:
		#print(r.raise_for_status())
		if r.status_code == 200 or r.status_code == 202:
			try:
				connection = psycopg2.connect(user = USER,
												password = PASSWORD,
												host = HOST,
												port = PORT,
												database = 'Pago Efectivo')
				cursor = connection.cursor()
				
				postgres_insert_query = """
				update recordatorio.envio_celular_servicio_temp aa
				set envio_emblue_celular=true,
					fecha_envio_emblue_celular = now()
				where  %s=aa.mail_cip;

					  """

				psycopg2.extras.execute_batch(cursor,postgres_insert_query,param)
				connection.commit()
				estado = 1
			except ( psycopg2.Error) as error :
				sendMail(mail_titulo,f"Ocurrio un error al listar: {error}")
				logging.error(f"Ocurrio un error al listar : {error}", exc_info=True)
				print(error)
				estado = 0
			except (Exception) as error :
				sendMail(mail_titulo,f"Ocurrio un error al listar {url}: {error}")
				logging.error(f"Ocurrio un error al insertar : {error}", exc_info=True)
				print(error)
				estado = 0
			finally:
				if(connection):
					cursor.close()
					connection.close()
		else:
			sendMail(mail_titulo,f"Ocurrio un error al enviar {url}: {r.content}")
			logging.error(f"Ocurrio un error al consultar {url}: {r.content}", exc_info=True)
			print(f'Other error occurred: {r.content}')  # Python 3.6
			estado = 0
	return estado
def main():
	try:	
		leerDatos()		
	except Exception as err:
		sendMail(mail_titulo,f"Ocurrio un error al enviar : {err}")
		logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
		print(f'Other error occurred: {err}')  # Python 3.6

if __name__ == '__main__':
	main()