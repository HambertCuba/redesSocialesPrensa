import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

import webbrowser
import time
import pandas
import pprint
from datetime import datetime, date, timedelta
import calendar
import facebook_business
import requests, urllib3
import pandas.io.formats.excel
from openpyxl import load_workbook
from openpyxl import Workbook
import xlsxwriter
import pydrive2
from openpyxl import load_workbook
from openpyxl.workbook import Workbook
from googleapiclient.discovery import build
from google.oauth2 import service_account
import sys
import logging
import smtplib  
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
import dateutil.parser

config = configparser.ConfigParser()
config.read('/home/ec2-pentaho/pentaho/dynamo/credential/config2.ini')

config_param = 'CREDENTIAL_PG_INTERNO'

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


now = datetime.today()
#sacar las fechas de filtro
formato1="%Y-%m-%d"
formato2="%y-%m-%d"
now = datetime.today()
fecha_7=now - timedelta(days=7)
fecha_7_1=fecha_7.strftime(formato1)
fecha_7_2=dateutil.parser.parse(fecha_7_1).date()

fecha_ayer=now - timedelta(hours=5)
fecha_ayer_1=fecha_ayer.strftime(formato1)
fecha_ayer_2=dateutil.parser.parse(fecha_ayer_1).date()


# fecha_atras = now - timedelta(days=1)
# fecha_adelante=now + timedelta(days=1)
# #print(fecha_atras)
# fecha_adelante1=fecha_adelante.strftime(formato1)
# fecha_adelante1=dateutil.parser.parse(fecha_adelante1).date()
# fecha_hoy=now.strftime(formato1)
# fecha_hoy_1=dateutil.parser.parse(fecha_hoy).date()
# fecha_atras=fecha_atras.strftime(formato1)
# fecha_atras_1=datetime.strptime(fecha_atras, '%Y-%m-%d')
# fecha_atras_2=fecha_atras_1.strftime(formato1)
# fecha_atras_22=dateutil.parser.parse(fecha_atras_2).date()


PATH_LOG = '/home/ec2-pentaho/pentaho/unp/Youtube/log/'
name_log =PATH_LOG+'log_pubicacion_'+now.strftime("%Y_%m_%d")+'.log'
logging.basicConfig(filename=name_log,  filemode='a',format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
 	    logging.info("Carga de Indicadores videos_2")
 	return

def subir_drive(listasubir,hoja,name):
    try:
        #JSON_FILE = 'cmsproyecto-1610655853990-aa4048eb3551.json'
        JSON_FILE = '/home/ec2-pentaho/pentaho/unp/Youtube/proceso/cmsproyecto-1610655853990-aa4048eb3551.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        CREDENCIALES = None
        CREDENCIALES = service_account.Credentials.from_service_account_file(
        JSON_FILE, scopes=SCOPES)
        # The ID and range of a sample spreadsheet.
        SPREADSHEET_ID = hoja #'1l8_KEVavN2Dz_aVC5CMEWAoWZJisgrfupHeAufkTrPI'
        RANGE_NAME = 'Indicadores_Video!A2'
        service = build('sheets', 'v4', credentials=CREDENCIALES)
        
        # ------ Agregamos el nuevo contenido ----------------
        carga_datos = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="USER_ENTERED",
        body={"values":listasubir[0]})
        if carga_datos:
            print(f'inserta datos')
        else:
            sys.exit() #si hay un error corta el script
        carga_datos.execute()

    except Exception as err:
        sendMail("[Youtube] I.Videos_2",f"Ocurrio un error en la carga de indicadores videos_2 al sheet :" +name+ f" {err} ")
        logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
        print(f'Other error occurred: {err}')  # Python 3.6



#comercio,gestion,p21,correo,ojo,bocon,depor,trome
canales=["UCLtGUPjKLqa3zgdmhKCZONg","UC1FZF46zaC26_CynNc786_g","UCNd09h2GugrdeT_80LxOFMw","UC_r8BVAjEb2cTfTPowQKAjg",
         "UCAyu1eK7EmjlS4WIao2VcAg","UC_Zf04jfJGHEE8g4YLU5YYg","UCaUt56hZx77Uc1podeWwW2g","UChzS9L4GwAe0lRFallqbaGg"]
canal_com= "UCLtGUPjKLqa3zgdmhKCZONg"
api_key= "AIzaSyBFTQ6Co8paqw0PBh-vupCKjvfgU5OcwJk"
headers1 = {
    'Content-Type': 'application/json'
                }
owned_apps_p21=[]
owned_apps_correo=[]
owned_apps_bocon=[]
owned_apps_com=[]
owned_apps_ojo=[]
owned_apps_trome=[]
owned_apps_depor=[]
owned_apps_gestion=[]
i=0
while i<= 7:
    channel=canales[i]
    owned_apps = []
    api= 'https://www.googleapis.com/youtube/v3/search?key='+api_key+'&channelId='+channel+'&part=snippet,id&order=date&maxResults=80'
    #print(api)
    responseprueba=requests.get(api,stream=True,headers=headers1)
#print(response.url)
    responseprueba = responseprueba.json()
    resultadosprueba=responseprueba["items"]
    owned_apps=resultadosprueba
    
    if i==0:
        owned_apps_com=owned_apps
        cantidad_com=len(owned_apps_com)
    if i==1:
        owned_apps_gestion=owned_apps
        cantidad_gestion=len(owned_apps_gestion)
    if i==2:
        owned_apps_p21=owned_apps
        cantidad_p21=len(owned_apps_p21)
    if i==3:
        owned_apps_correo=owned_apps
        cantidad_correo=len(owned_apps_correo)
    if i==4:
        owned_apps_ojo=owned_apps
        cantidad_ojo=len(owned_apps_ojo)
    if i==5:
        owned_apps_bocon=owned_apps
        cantidad_bocon=len(owned_apps_bocon)
    if i==6:
        owned_apps_depor=owned_apps
        cantidad_depor=len(owned_apps_depor)
    if i==7:
        owned_apps_trome=owned_apps
        cantidad_trome=len(owned_apps_trome) 
    
    i+=1

i=0
while i <= 7:
	time.sleep(1)
	item2=0
	listaReach=[]
	if i==0:
		while item2 <= len(owned_apps_com):
			name=""
			name=owned_apps_com[0]["snippet"]["channelTitle"]
			try:
				responseprueba_1={}
				api="https://www.googleapis.com/youtube/v3/videos?part=statistics&id="+owned_apps_com[item2]["id"]["videoId"]+'&key='+api_key
				responseprueba_1=requests.get(api,stream=True,headers=headers1)
				responseprueba_1 = responseprueba_1.json()
				try:
					views=responseprueba_1["items"][0]["statistics"]["viewCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					  views=0
				try:
					like=responseprueba_1["items"][0]["statistics"]["likeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					like=0
				try:
					dislikes=responseprueba_1["items"][0]["statistics"]["dislikeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					dislikes=0
				try:
					comments=responseprueba_1["items"][0]["statistics"]["commentCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					comments=0
          
			except Exception as err:
				sendMail("[Youtube] I.Videos_2",f"Ocurrio un error en la obtencion de indicadores videos :"+name+ f" {err} ")
				logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
				print(f'Other error occurred: {err}')  # Python 3.6
                
                
			id_22=owned_apps_com[item2]['snippet']['title']
			desc_22=owned_apps_com[item2]['snippet']['description']
			fecha=owned_apps_com[item2]['snippet']['publishedAt']
			fechapub11=fecha.replace("T"," ")
			fechapub12=fechapub11[0:19]
			old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
			fecha_atras = old - timedelta(hours=5)
			fecha_atras_1=fecha_atras.strftime(formato1)
			fecha2=dateutil.parser.parse(fecha_atras_1).date()
			if fecha2>=fecha_7_2 and fecha2<fecha_ayer_2 :
				fecha22=fecha2.strftime(formato1)
				listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id_22,
					desc_22,
					views,
					like,
					dislikes,
					comments,
					]
                )
			item2+=1
			if item2==len(owned_apps_com):
				print(item2)
				break
		listapub=[]
		listapub=[listaReach]
		hoja='13p18umTJjadj6Jmc9dKSXqragxcYcA0F_5LT31DMKKw'
		subir_drive(listapub, hoja, name)
	
	if i==1:
		while item2 <= len(owned_apps_gestion):
			name=""
			name=owned_apps_gestion[0]["snippet"]["channelTitle"]
			try:
				responseprueba_1={}
				api="https://www.googleapis.com/youtube/v3/videos?part=statistics&id="+owned_apps_gestion[item2]["id"]["videoId"]+'&key='+api_key
				responseprueba_1=requests.get(api,stream=True,headers=headers1)
				responseprueba_1 = responseprueba_1.json()
				try:
					views=responseprueba_1["items"][0]["statistics"]["viewCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					  views=0
				try:
					like=responseprueba_1["items"][0]["statistics"]["likeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					like=0
				try:
					dislikes=responseprueba_1["items"][0]["statistics"]["dislikeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					dislikes=0

				try:
					comments=responseprueba_1["items"][0]["statistics"]["commentCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					comments=0
          
			except Exception as err:
				sendMail("[Youtube] I.Videos_2",f"Ocurrio un error en la obtencion de indicadores videos :"+name+ f" {err} ")
				logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
				print(f'Other error occurred: {err}')  # Python 3.6
                
                
			id_22=owned_apps_gestion[item2]['snippet']['title']
			desc_22=owned_apps_gestion[item2]['snippet']['description']
			fecha=owned_apps_gestion[item2]['snippet']['publishedAt']
			fechapub11=fecha.replace("T"," ")
			fechapub12=fechapub11[0:19]
			old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
			fecha_atras = old - timedelta(hours=5)
			fecha_atras_1=fecha_atras.strftime(formato1)
			fecha2=dateutil.parser.parse(fecha_atras_1).date()
			if fecha2>=fecha_7_2 and fecha2<fecha_ayer_2 :
				fecha22=fecha2.strftime(formato1)
				listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id_22,
					desc_22,
					views,
					like,
					dislikes,
					comments,
					]
                )
			item2+=1
			if item2==len(owned_apps_gestion):
				print(item2)
				break
		listapub=[]
		listapub=[listaReach]
		hoja='1GqAly6pOxecUPaAPaNfzzTt_8oHZdgEIWUdh4ltbEl0'
		subir_drive(listapub, hoja, name)
	if i==2:
		while item2 <= len(owned_apps_p21):
			name=""
			name=owned_apps_p21[0]["snippet"]["channelTitle"]
			try:
				responseprueba_1={}
				api="https://www.googleapis.com/youtube/v3/videos?part=statistics&id="+owned_apps_p21[item2]["id"]["videoId"]+'&key='+api_key
				responseprueba_1=requests.get(api,stream=True,headers=headers1)
				responseprueba_1 = responseprueba_1.json()
				try:
					views=responseprueba_1["items"][0]["statistics"]["viewCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					  views=0
				try:
					like=responseprueba_1["items"][0]["statistics"]["likeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					like=0
				try:
					dislikes=responseprueba_1["items"][0]["statistics"]["dislikeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					dislikes=0
				try:
					comments=responseprueba_1["items"][0]["statistics"]["commentCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					comments=0
          
			except Exception as err:
				sendMail("[Youtube] I.Videos_2",f"Ocurrio un error en la obtencion de indicadores videos :"+name+ f" {err} ")
				logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
				print(f'Other error occurred: {err}')  # Python 3.6
                
                
			id_22=owned_apps_p21[item2]['snippet']['title']
			desc_22=owned_apps_p21[item2]['snippet']['description']
			fecha=owned_apps_p21[item2]['snippet']['publishedAt']
			fechapub11=fecha.replace("T"," ")
			fechapub12=fechapub11[0:19]
			old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
			fecha_atras = old - timedelta(hours=5)
			fecha_atras_1=fecha_atras.strftime(formato1)
			fecha2=dateutil.parser.parse(fecha_atras_1).date()
			if fecha2>=fecha_7_2 and fecha2<fecha_ayer_2 :
				fecha22=fecha2.strftime(formato1)
				listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id_22,
					desc_22,
					views,
					like,
					dislikes,
					comments,
					]
                )
			item2+=1
			if item2==len(owned_apps_p21):
				print(item2)
				break
		listapub=[]
		listapub=[listaReach]
		hoja='1xz_fj7GKYT0ju8bR3HnJw2p1iCKnNvwHPerMahT8Qbo'
		subir_drive(listapub, hoja, name)
	if i==3:
		while item2 <= len(owned_apps_correo):
			name=""
			name=owned_apps_correo[0]["snippet"]["channelTitle"]
			try:
				responseprueba_1={}
				api="https://www.googleapis.com/youtube/v3/videos?part=statistics&id="+owned_apps_correo[item2]["id"]["videoId"]+'&key='+api_key
				responseprueba_1=requests.get(api,stream=True,headers=headers1)
				responseprueba_1 = responseprueba_1.json()
				try:
					views=responseprueba_1["items"][0]["statistics"]["viewCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					  views=0
				try:
					like=responseprueba_1["items"][0]["statistics"]["likeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					like=0
				try:
					dislikes=responseprueba_1["items"][0]["statistics"]["dislikeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					dislikes=0
				try:
					comments=responseprueba_1["items"][0]["statistics"]["commentCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					comments=0
          
			except Exception as err:
				sendMail("[Youtube] I.Videos_2",f"Ocurrio un error en la obtencion de indicadores videos :"+name+ f" {err} ")
				logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
				print(f'Other error occurred: {err}')  # Python 3.6
                
                
			id_22=owned_apps_correo[item2]['snippet']['title']
			desc_22=owned_apps_correo[item2]['snippet']['description']
			fecha=owned_apps_correo[item2]['snippet']['publishedAt']
			fechapub11=fecha.replace("T"," ")
			fechapub12=fechapub11[0:19]
			old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
			fecha_atras = old - timedelta(hours=5)
			fecha_atras_1=fecha_atras.strftime(formato1)
			fecha2=dateutil.parser.parse(fecha_atras_1).date()
			if fecha2>=fecha_7_2 and fecha2<fecha_ayer_2 :
				fecha22=fecha2.strftime(formato1)
				listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id_22,
					desc_22,
					views,
					like,
					dislikes,
					comments,
					]
                )
			item2+=1
			if item2==len(owned_apps_correo):
				print(item2)
				break
		listapub=[]
		listapub=[listaReach]
		hoja='1SBxuC_oaAcbpEsufEyh5F0BCotQFZUgJ87EVHmT8Xtc'
		subir_drive(listapub, hoja, name)
	if i==4:
		while item2 <= len(owned_apps_ojo):
			name=""
			name=owned_apps_ojo[0]["snippet"]["channelTitle"]
			try:
				responseprueba_1={}
				api="https://www.googleapis.com/youtube/v3/videos?part=statistics&id="+owned_apps_ojo[item2]["id"]["videoId"]+'&key='+api_key
				responseprueba_1=requests.get(api,stream=True,headers=headers1)
				responseprueba_1 = responseprueba_1.json()
				try:
					views=responseprueba_1["items"][0]["statistics"]["viewCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					  views=0
				try:
					like=responseprueba_1["items"][0]["statistics"]["likeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					like=0
				try:
					dislikes=responseprueba_1["items"][0]["statistics"]["dislikeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					dislikes=0
				try:
					comments=responseprueba_1["items"][0]["statistics"]["commentCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					comments=0
          
			except Exception as err:
				sendMail("[Youtube] I.Videos_2",f"Ocurrio un error en la obtencion de indicadores videos :"+name+ f" {err} ")
				logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
				print(f'Other error occurred: {err}')  # Python 3.6
                
                
			id_22=owned_apps_ojo[item2]['snippet']['title']
			desc_22=owned_apps_ojo[item2]['snippet']['description']
			fecha=owned_apps_ojo[item2]['snippet']['publishedAt']
			fechapub11=fecha.replace("T"," ")
			fechapub12=fechapub11[0:19]
			old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
			fecha_atras = old - timedelta(hours=5)
			fecha_atras_1=fecha_atras.strftime(formato1)
			fecha2=dateutil.parser.parse(fecha_atras_1).date()
			if fecha2>=fecha_7_2 and fecha2<fecha_ayer_2 :
				fecha22=fecha2.strftime(formato1)
				listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id_22,
					desc_22,
					views,
					like,
					dislikes,
					comments,
					]
                )
			item2+=1
			if item2==len(owned_apps_ojo):
				print(item2)
				break
		listapub=[]
		listapub=[listaReach]
		hoja='1XB78QXwDXsqg4-nCN9S5une25ApGkzoQt6fyIBQOXcU'
		subir_drive(listapub, hoja, name)
	if i==5:
		while item2 <= len(owned_apps_bocon):
			name=""
			name=owned_apps_bocon[0]["snippet"]["channelTitle"]
			try:
				responseprueba_1={}
				api="https://www.googleapis.com/youtube/v3/videos?part=statistics&id="+owned_apps_bocon[item2]["id"]["videoId"]+'&key='+api_key
				responseprueba_1=requests.get(api,stream=True,headers=headers1)
				responseprueba_1 = responseprueba_1.json()
				try:
					views=responseprueba_1["items"][0]["statistics"]["viewCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					  views=0
				try:
					like=responseprueba_1["items"][0]["statistics"]["likeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					like=0
				try:
					dislikes=responseprueba_1["items"][0]["statistics"]["dislikeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					dislikes=0

				try:
					comments=responseprueba_1["items"][0]["statistics"]["commentCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					comments=0
          
			except Exception as err:
				sendMail("[Youtube] I.Videos_2",f"Ocurrio un error en la obtencion de indicadores videos :"+name+ f" {err} ")
				logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
				print(f'Other error occurred: {err}')  # Python 3.6
                
                
			id_22=owned_apps_bocon[item2]['snippet']['title']
			desc_22=owned_apps_bocon[item2]['snippet']['description']
			fecha=owned_apps_bocon[item2]['snippet']['publishedAt']
			fechapub11=fecha.replace("T"," ")
			fechapub12=fechapub11[0:19]
			old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
			fecha_atras = old - timedelta(hours=5)
			fecha_atras_1=fecha_atras.strftime(formato1)
			fecha2=dateutil.parser.parse(fecha_atras_1).date()
			if fecha2>=fecha_7_2 and fecha2<fecha_ayer_2 :
				fecha22=fecha2.strftime(formato1)
				listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id_22,
					desc_22,
					views,
					like,
					dislikes,
					comments,
					]
                )
			item2+=1
			if item2==len(owned_apps_bocon):
				print(item2)
				break
		listapub=[]
		listapub=[listaReach]
		hoja='1pKyx4K7ug79LfXekqX0GEHY8OnW5wUvlxCugmjt8Neg'
		subir_drive(listapub, hoja, name)
	if i==6:
		while item2 <= len(owned_apps_depor):
			name=""
			name=owned_apps_depor[0]["snippet"]["channelTitle"]
			try:
				responseprueba_1={}
				api="https://www.googleapis.com/youtube/v3/videos?part=statistics&id="+owned_apps_depor[item2]["id"]["videoId"]+'&key='+api_key
				responseprueba_1=requests.get(api,stream=True,headers=headers1)
				responseprueba_1 = responseprueba_1.json()
				try:
					views=responseprueba_1["items"][0]["statistics"]["viewCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					  views=0
				try:
					like=responseprueba_1["items"][0]["statistics"]["likeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					like=0
				try:
					dislikes=responseprueba_1["items"][0]["statistics"]["dislikeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					dislikes=0

				try:
					comments=responseprueba_1["items"][0]["statistics"]["commentCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					comments=0
          
			except Exception as err:
				sendMail("[Youtube] I.Videos_2",f"Ocurrio un error en la obtencion de indicadores videos :"+name+ f" {err} ")
				logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
				print(f'Other error occurred: {err}')  # Python 3.6
                
                
			id_22=owned_apps_depor[item2]['snippet']['title']
			desc_22=owned_apps_depor[item2]['snippet']['description']
			fecha=owned_apps_depor[item2]['snippet']['publishedAt']
			fechapub11=fecha.replace("T"," ")
			fechapub12=fechapub11[0:19]
			old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
			fecha_atras = old - timedelta(hours=5)
			fecha_atras_1=fecha_atras.strftime(formato1)
			fecha2=dateutil.parser.parse(fecha_atras_1).date()
			if fecha2>=fecha_7_2 and fecha2<fecha_ayer_2 :
				fecha22=fecha2.strftime(formato1)
				listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id_22,
					desc_22,
					views,
					like,
					dislikes,
					comments,
					]
                )
			item2+=1
			if item2==len(owned_apps_depor):
				print(item2)
				break
		listapub=[]
		listapub=[listaReach]
		hoja='1BV-nZuUUyqjZAxgCJPPc_z-KaxG8mnzCe2dBs8W5klw'
		subir_drive(listapub, hoja, name)
	if i==7:
		while item2 <= len(owned_apps_trome):
			name=""
			name=owned_apps_trome[0]["snippet"]["channelTitle"]
			try:
				responseprueba_1={}
				api="https://www.googleapis.com/youtube/v3/videos?part=statistics&id="+owned_apps_trome[item2]["id"]["videoId"]+'&key='+api_key
				responseprueba_1=requests.get(api,stream=True,headers=headers1)
				responseprueba_1 = responseprueba_1.json()
				try:
					views=responseprueba_1["items"][0]["statistics"]["viewCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					  views=0
				try:
					like=responseprueba_1["items"][0]["statistics"]["likeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					like=0
				try:
					dislikes=responseprueba_1["items"][0]["statistics"]["dislikeCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					dislikes=0
				try:
					comments=responseprueba_1["items"][0]["statistics"]["commentCount"]
				except(ValueError,KeyError,ZeroDivisionError,NameError):
					comments=0
          
			except Exception as err:
				sendMail("[Youtube] I.Videos_2",f"Ocurrio un error en la obtencion de indicadores videos :"+name+ f" {err} ")
				logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
				print(f'Other error occurred: {err}')  # Python 3.6
                
                
			id_22=owned_apps_trome[item2]['snippet']['title']
			desc_22=owned_apps_trome[item2]['snippet']['description']
			fecha=owned_apps_trome[item2]['snippet']['publishedAt']
			fechapub11=fecha.replace("T"," ")
			fechapub12=fechapub11[0:19]
			old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
			fecha_atras = old - timedelta(hours=5)
			fecha_atras_1=fecha_atras.strftime(formato1)
			fecha2=dateutil.parser.parse(fecha_atras_1).date()
			if fecha2>=fecha_7_2 and fecha2<fecha_ayer_2 :
				fecha22=fecha2.strftime(formato1)
				listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id_22,
					desc_22,
					views,
					like,
					dislikes,
					comments,
					]
                )
			item2+=1
			if item2==len(owned_apps_trome):
				print(item2)
				break
		listapub=[]
		listapub=[listaReach]
		hoja='1268SnnboJ1IbF4L5KaWVwcROJypwSIfXejw9CYXoWi4'
		subir_drive(listapub, hoja, name)
	i+=1
    
    
    
    