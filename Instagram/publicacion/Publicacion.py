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
PATH_LOG = '/home/ec2-pentaho/pentaho/unp/Instagram/publicacion/log/'
name_log =PATH_LOG+'log_pagina_'+now.strftime("%Y_%m_%d")+'.log'
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
 	    logging.info("Carga de Indicadores Publicacion")
 	return


#sacar las fechas de filtro
formato1="%Y-%m-%d"
formato2="%y-%m-%d"
fecha_atras = now - timedelta(days=1)
#print(fecha_atras)
fecha1=now.strftime(formato1)
fecha2=fecha_atras.strftime(formato1)
fecha2_1=dateutil.parser.parse(fecha2).date()
#print(fecha2)

fecha_ayer=now - timedelta(hours=5)
fecha_ayer_1=fecha_ayer.strftime(formato1)
fecha_ayer_2=dateutil.parser.parse(fecha_ayer_1).date()


def subir_drive(listasubir,hoja,name):
    try:        
        #JSON_FILE = 'cmsproyecto-1610655853990-aa4048eb3551.json'
        JSON_FILE = '/home/ec2-pentaho/pentaho/unp/Instagram/publicacion/proceso/cmsproyecto-1610655853990-aa4048eb3551.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        CREDENCIALES = None
        CREDENCIALES = service_account.Credentials.from_service_account_file(
        JSON_FILE, scopes=SCOPES)
        # The ID and range of a sample spreadsheet.
        SPREADSHEET_ID = hoja #'1l8_KEVavN2Dz_aVC5CMEWAoWZJisgrfupHeAufkTrPI'
        RANGE_NAME = 'Indicadores_Publicaci??n!A2'
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
        sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la carga de indicadores publicacion al sheet :"+name+" {err} ")
        logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
        print(f'Other error occurred: {err}')  # Python 3.6


#id y token de cuentas
#comercio,p21,correo,bocon,ojo,trome,depor
a = [['17841401810950570', 'EAAfj47wzha8BADZCAuYLkqj2RxqPXslfYVpQshtZBQvDV3Sb27ZAUd7s15WzqXasbWci7ZAZBilATZBCtgqjPrRidCZA04lOrOza6A0vCuceJccVWdrMy4O7Gb89mYvZA8KsOCpujW19U4vhe33Ly7euZCj9iFdodbV7nCAS9ytBxDexjZBN98yLNTi2Q9T9H3rs6wrLTL9NRD0QZDZD'], 
     ['17841400118433671', 'EAAfj47wzha8BACYb7lQZBkgazpDPWIKKe2eg3gh27jTTlqSzbt4TVMlBRFn5pyPnIbHpc7sSJjEaYO0dmQ1ZBvTypRn6buqEMElbl8D6lHEQBG0tppV5xr8uH4ch0C03Cc9ZBumhKWRAYZASh03I1mMWp81muwqBzpRkq7KT2nlE5xYy9xCK9OKJJCC8ZBZCcC7Navx2GYCAZDZD'],
     ['17841402209037198', 'EAAfj47wzha8BAEnQ2aQGmNNZBodUCGm6WgNVIaUCp35YJSWL8ivOJaQC4bWbap0Ky408RanahBURqkOrFy4FGjRZCwzHpMZBZCQpzvNllD7QMthr87ZATiTZCwj6PZAXf3Xog08nRmTSVpt9HB2rMLJMSOfUkoO8vWgvCZBio10FHxzb6l9oEfMzkCs7WUDWqlD49vHQxmNpJQZDZD'],
     ['17841402218427177', 'EAAfj47wzha8BAOJiIOZAykwkXBvkvFdsomGGhPsxZAeQvoOvGVj28AhL1128c2LpFvRj5NYq989av2OGZCdllDaww0ZBuuIE2ZCPNr7MDIDAoMDFAbZCiaPIwPmrjZCZAS3JTIZBg65R6CTm7hyyAccUPDoTFts2pCZADPZAnv5UD4IPvLshY6zFxbB9Jna10dZAtXg7CVByb7f91gZDZD'],
     ['17841402262227176', 'EAAfj47wzha8BAOJiIOZAykwkXBvkvFdsomGGhPsxZAeQvoOvGVj28AhL1128c2LpFvRj5NYq989av2OGZCdllDaww0ZBuuIE2ZCPNr7MDIDAoMDFAbZCiaPIwPmrjZCZAS3JTIZBg65R6CTm7hyyAccUPDoTFts2pCZADPZAnv5UD4IPvLshY6zFxbB9Jna10dZAtXg7CVByb7f91gZDZD'],
     ['17841403402984824', 'EAAfj47wzha8BABEy0ZBvtHQKl82tfi648MO4KEXau9E2orJIDBoCBzi3Hk0aysvSZCRSolpwjQ9LlToxl5nF4VXsgln77SiWV4YfMiTPv05FU6eAZB1r35Bl0awAglyVnlKPlRwgvegTYe3ZCPVqKzWev6F1ZAVH9kpTZAUXgynpNx2LMCu0awNe5z0eLIcXr15OdR7yZCiywZDZD'],
     ['17841401572678380', 'EAAfj47wzha8BAFOkocul9e1cZBaDeDxSJGRIDDveZCnDzHyZAbF0vZBd5twKhZC7QGvKu7bnbSYpWWGCZAFzivzvOlfzUXfXQ6DOJQjgIWdGUZCxrgZBsKAgbD5Kcy5XFRvwbnNN3DRJy7D7Ku5FwVMpfgECodlqp8D9wlqXbjLYQquMKZA2j9JBzLLBwbcEebGUESJxHMum8FQZDZD']]
# id_com=""
# token_com=""
# id_p21=""
# token_p21=""
# id_corr=""
# token_corr=""
# id_boc=""
# token_boc=""
# id_ojo=""
# token_ojo=""
# id_tro=""
# token_tro=""
# id_dep=""
# token_dep=""

#sacar la cuenta de facebook:id y token
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

owned_apps_p21_2=[]
owned_apps_correo_2=[]
owned_apps_bocon_2=[]
owned_apps_com_2=[]
owned_apps_ojo_2=[]
owned_apps_trome_2=[]
owned_apps_depor_2=[]
i=0
while i<= 6:
    owned_apps = []
    api= 'https://graph.facebook.com/v10.0/'+a[i][0]+'/media?access_token='+a[i][1]+'&limit=50'
    responseprueba=requests.get(api,stream=True,headers=headers1)
    responseprueba = responseprueba.json()
    resultadosprueba=responseprueba["data"]
    owned_apps=resultadosprueba
    
    if i==0:
        owned_apps_com=owned_apps
        cantidad_com=len(owned_apps_com)
    if i==1:
        owned_apps_p21=owned_apps
        cantidad_p21=len(owned_apps_p21)
    if i==2:
        owned_apps_correo=owned_apps
        cantidad_correo=len(owned_apps_correo)
    if i==3:
        owned_apps_bocon=owned_apps
        cantidad_bocon=len(owned_apps_bocon)
    if i==4:
        owned_apps_ojo=owned_apps
        cantidad_ojo=len(owned_apps_ojo)
    if i==5:
        owned_apps_trome=owned_apps
        cantidad_trome=len(owned_apps_trome)
    if i==6:
        owned_apps_depor=owned_apps
        cantidad_depor=len(owned_apps_depor)
   
    i+=1

i=0

while i<= 6:     
    token=''
    item2=0
    listaReach=[]
    id22=''
    titulo=''
    link=''
    tipo=''
        
    if i==0:
        while item2 <= len(owned_apps_com):
            name='Diario El Comercio'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_com[item2]['id']+'?fields=timestamp,caption,permalink,thumbnail_url,media_type,media_url&access_token='+a[i][1]
                #print(api1)
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                id22=owned_apps_com[item2]['id']
                fecha=responseprueba_1["timestamp"]
                try:
                    titulo=responseprueba_1["caption"]
                except:
                    titulo=''
                link=responseprueba_1["permalink"]
                tipo=responseprueba_1["media_type"]
                
                fechapub11=fecha.replace("T"," ")
                fechapub12=fechapub11[0:19]
                old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
                fecha_atras = old - timedelta(hours=5)
                fecha_atras_1=fecha_atras.strftime(formato1)
                fecha2=dateutil.parser.parse(fecha_atras_1).date()
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores principales de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            if fecha2==fecha2_1 :
                    fecha22=fecha2.strftime(formato1)
                    owned_apps_com_2.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
					]
                )
            item2+=1
            if item2==len(owned_apps_com):
                print(item2)
                break
    
    if i==1:
        while item2 <= len(owned_apps_p21):
            name='Diario Peru21'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_p21[item2]['id']+'?fields=timestamp,caption,permalink,thumbnail_url,media_type,media_url&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                id22=owned_apps_p21[item2]['id']
                fecha=responseprueba_1["timestamp"]
                try:
                    titulo=responseprueba_1["caption"]
                except:
                    titulo=''
                link=responseprueba_1["permalink"]
                tipo=responseprueba_1["media_type"]
                
                fechapub11=fecha.replace("T"," ")
                fechapub12=fechapub11[0:19]
                old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
                fecha_atras = old - timedelta(hours=5)
                fecha_atras_1=fecha_atras.strftime(formato1)
                fecha2=dateutil.parser.parse(fecha_atras_1).date()
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores principales de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            if fecha2==fecha2_1 :
                    fecha22=fecha2.strftime(formato1)
                    owned_apps_p21_2.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
					]
                )
            item2+=1
            if item2==len(owned_apps_p21):
                print(item2)
                break    
    
    if i==2:
        while item2 <= len(owned_apps_correo):
            name='Diario Correo'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_correo[item2]['id']+'?fields=timestamp,caption,permalink,thumbnail_url,media_type,media_url&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                id22=owned_apps_correo[item2]["id"]
                fecha=responseprueba_1["timestamp"]
                try:
                    titulo=responseprueba_1["caption"]
                except:
                    titulo=''
                link=responseprueba_1["permalink"]
                tipo=responseprueba_1["media_type"]
                
                fechapub11=fecha.replace("T"," ")
                fechapub12=fechapub11[0:19]
                old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
                fecha_atras = old - timedelta(hours=5)
                fecha_atras_1=fecha_atras.strftime(formato1)
                fecha2=dateutil.parser.parse(fecha_atras_1).date()
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores principales de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            if fecha2==fecha2_1 :
                    fecha22=fecha2.strftime(formato1)
                    owned_apps_correo_2.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
					]
                )
            item2+=1
            if item2==len(owned_apps_correo):
                print(item2)
                break
    
    if i==3:
        while item2 <= len(owned_apps_bocon):
            name='Diario Bocon'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_bocon[item2]['id']+'?fields=timestamp,caption,permalink,thumbnail_url,media_type,media_url&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                id22=owned_apps_bocon[item2]["id"]
                fecha=responseprueba_1["timestamp"]
                try:
                    titulo=responseprueba_1["caption"]
                except:
                    titulo=''
                link=responseprueba_1["permalink"]
                tipo=responseprueba_1["media_type"]
                
                fechapub11=fecha.replace("T"," ")
                fechapub12=fechapub11[0:19]
                old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
                fecha_atras = old - timedelta(hours=5)
                fecha_atras_1=fecha_atras.strftime(formato1)
                fecha2=dateutil.parser.parse(fecha_atras_1).date()
            
            except Exception as err:
                #sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores principales de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            if fecha2==fecha2_1 :
                    fecha22=fecha2.strftime(formato1)
                    owned_apps_bocon_2.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
					]
                )
            item2+=1
            if item2==len(owned_apps_bocon):
                print(item2)
                break
    
    if i==4:
        while item2 <= len(owned_apps_ojo):
            name='Diario Ojo'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_ojo[item2]['id']+'?fields=timestamp,caption,permalink,thumbnail_url,media_type,media_url&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                id22=owned_apps_ojo[item2]["id"]
                fecha=responseprueba_1["timestamp"]
                try:
                    titulo=responseprueba_1["caption"]
                except:
                    titulo=''
                link=responseprueba_1["permalink"]
                tipo=responseprueba_1["media_type"]
                
                fechapub11=fecha.replace("T"," ")
                fechapub12=fechapub11[0:19]
                old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
                fecha_atras = old - timedelta(hours=5)
                fecha_atras_1=fecha_atras.strftime(formato1)
                fecha2=dateutil.parser.parse(fecha_atras_1).date()
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores principales de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            if fecha2==fecha2_1 :
                    fecha22=fecha2.strftime(formato1)
                    owned_apps_ojo_2.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
					]
                )
            item2+=1
            if item2==len(owned_apps_ojo):
                print(item2)
                break
    
    if i==5:
        while item2 <= len(owned_apps_trome):
            name='Diario Trome'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_trome[item2]['id']+'?fields=timestamp,caption,permalink,thumbnail_url,media_type,media_url&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                id22=owned_apps_trome[item2]["id"]
                fecha=responseprueba_1["timestamp"]
                try:
                    titulo=responseprueba_1["caption"]
                except:
                    titulo=''
                link=responseprueba_1["permalink"]
                tipo=responseprueba_1["media_type"]
                
                fechapub11=fecha.replace("T"," ")
                fechapub12=fechapub11[0:19]
                old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
                fecha_atras = old - timedelta(hours=5)
                fecha_atras_1=fecha_atras.strftime(formato1)
                fecha2=dateutil.parser.parse(fecha_atras_1).date()
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores principales de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            if fecha2==fecha2_1 :
                    fecha22=fecha2.strftime(formato1)
                    owned_apps_trome_2.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
					]
                )
            item2+=1
            if item2==len(owned_apps_trome):
                print(item2)
                break
    
    if i==6:
        while item2 <= len(owned_apps_depor):
            name='Diario Depor'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_depor[item2]['id']+'?fields=timestamp,caption,permalink,thumbnail_url,media_type,media_url&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                id22=owned_apps_depor[item2]["id"]
                fecha=responseprueba_1["timestamp"]
                try:
                    titulo=responseprueba_1["caption"]
                except:
                    titulo=''
                link=responseprueba_1["permalink"]
                tipo=responseprueba_1["media_type"]
                
                fechapub11=fecha.replace("T"," ")
                fechapub12=fechapub11[0:19]
                old=datetime.strptime(fechapub12, '%Y-%m-%d %H:%M:%S')
                fecha_atras = old - timedelta(hours=5)
                fecha_atras_1=fecha_atras.strftime(formato1)
                fecha2=dateutil.parser.parse(fecha_atras_1).date()
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores principales de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            if fecha2==fecha2_1 :
                    fecha22=fecha2.strftime(formato1)
                    owned_apps_depor_2.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
					]
                )
            item2+=1
            if item2==len(owned_apps_depor):
                print(item2)
                break
    i+=1

#######################parametros para la pagina
i=0
while i <= 6 :
    token=''
    #token=a[i][1]
    item2=0
    listaReach=[]

    if i==0:
        while item2 <= len(owned_apps_com_2):
            name='Diario Comercio'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_com_2[item2][1]+'/insights?metric=engagement,impressions,reach,saved&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                likes=responseprueba_1["data"][0]["values"][0]["value"]
                impresions=responseprueba_1["data"][1]["values"][0]["value"]
                reach=responseprueba_1["data"][2]["values"][0]["value"]
                saved=responseprueba_1["data"][3]["values"][0]["value"]
                
                fecha22=owned_apps_com_2[item2][0]
                id22=owned_apps_com_2[item2][1]
                titulo=owned_apps_com_2[item2][2]
                link=owned_apps_com_2[item2][3]
                tipo=owned_apps_com_2[item2][4]
                
                if tipo=='VIDEO':
                    responseprueba_2={}
                    api2="https://graph.facebook.com/v10.0/"+id22+'/insights?metric=video_views&access_token='+a[i][1]
                    responseprueba_2=requests.get(api2,stream=True,headers=headers1)
                    responseprueba_2 = responseprueba_2.json()
                    views=responseprueba_2["data"][0]["values"][0]["value"]
                else:
                    views=0
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores secundarios de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
                    likes,
                    impresions,
                    reach,
                    saved,
                    views,
					]
                )
            item2+=1
            if item2==len(owned_apps_com_2):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1p-GZQzMCw35GshsbECCw9MOK_iUb70e0-519u4hYgHA'
        subir_drive(listapub, hoja, name)
                
    
    if i==1:
        while item2 <= len(owned_apps_p21_2):
            name='Diario Peru21'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_p21_2[item2][1]+'/insights?metric=engagement,impressions,reach,saved&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                likes=responseprueba_1["data"][0]["values"][0]["value"]
                impresions=responseprueba_1["data"][1]["values"][0]["value"]
                reach=responseprueba_1["data"][2]["values"][0]["value"]
                saved=responseprueba_1["data"][3]["values"][0]["value"]
                
                fecha22=owned_apps_p21_2[item2][0]
                id22=owned_apps_p21_2[item2][1]
                titulo=owned_apps_p21_2[item2][2]
                link=owned_apps_p21_2[item2][3]
                tipo=owned_apps_p21_2[item2][4]
                
                if tipo=='VIDEO':
                    responseprueba_2={}
                    api2="https://graph.facebook.com/v10.0/"+id22+'/insights?metric=video_views&access_token='+a[i][1]
                    responseprueba_2=requests.get(api2,stream=True,headers=headers1)
                    responseprueba_2 = responseprueba_2.json()
                    views=responseprueba_2["data"][0]["values"][0]["value"]
                else:
                    views=0                
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores secundarios de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
                    likes,
                    impresions,
                    reach,
                    saved,
                    views,
					]
                )
            item2+=1
            if item2==len(owned_apps_p21_2):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='14j_GGSotF_JZh7ZDKDAo3jrq7FXQOaX5bFF-qVIzCt0'
        subir_drive(listapub, hoja, name)
        
    if i==2:
        while item2 <= len(owned_apps_correo_2):
            name='Diario Correo'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_correo_2[item2][1]+'/insights?metric=engagement,impressions,reach,saved&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                likes=responseprueba_1["data"][0]["values"][0]["value"]
                impresions=responseprueba_1["data"][1]["values"][0]["value"]
                reach=responseprueba_1["data"][2]["values"][0]["value"]
                saved=responseprueba_1["data"][3]["values"][0]["value"]
                
                fecha22=owned_apps_correo_2[item2][0]
                id22=owned_apps_correo_2[item2][1]
                titulo=owned_apps_correo_2[item2][2]
                link=owned_apps_correo_2[item2][3]
                tipo=owned_apps_correo_2[item2][4]
                
                if tipo=='VIDEO':
                    responseprueba_2={}
                    api2="https://graph.facebook.com/v10.0/"+id22+'/insights?metric=video_views&access_token='+a[i][1]
                    responseprueba_2=requests.get(api2,stream=True,headers=headers1)
                    responseprueba_2 = responseprueba_2.json()
                    views=responseprueba_2["data"][0]["values"][0]["value"]
                else:
                    views=0                
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores secundarios de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
                    likes,
                    impresions,
                    reach,
                    saved,
                    views,
					]
                )
            item2+=1
            if item2==len(owned_apps_correo_2):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1_gtBu5qcJf3DFE6RVI02K0-J-hmfELIujtVjxKWnexg'
        subir_drive(listapub, hoja, name)
    
    if i==3:
        while item2 <= len(owned_apps_bocon_2):
            name='Diario Bocon'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_bocon_2[item2][1]+'/insights?metric=engagement,impressions,reach,saved&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                likes=responseprueba_1["data"][0]["values"][0]["value"]
                impresions=responseprueba_1["data"][1]["values"][0]["value"]
                reach=responseprueba_1["data"][2]["values"][0]["value"]
                saved=responseprueba_1["data"][3]["values"][0]["value"]
                
                fecha22=owned_apps_bocon_2[item2][0]
                id22=owned_apps_bocon_2[item2][1]
                titulo=owned_apps_bocon_2[item2][2]
                link=owned_apps_bocon_2[item2][3]
                tipo=owned_apps_bocon_2[item2][4]
                
                if tipo=='VIDEO':
                    responseprueba_2={}
                    api2="https://graph.facebook.com/v10.0/"+id22+'/insights?metric=video_views&access_token='+a[i][1]
                    responseprueba_2=requests.get(api2,stream=True,headers=headers1)
                    responseprueba_2 = responseprueba_2.json()
                    views=responseprueba_2["data"][0]["values"][0]["value"]
                else:
                    views=0
                
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores secundarios de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
                    likes,
                    impresions,
                    reach,
                    saved,
                    views,
					]
                )
            item2+=1
            if item2==len(owned_apps_bocon_2):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='13YgjNaNAA-vXgd3_VQvOmPmZSROyjWFbcjNU3GpwH1Y'
        subir_drive(listapub, hoja, name)
    
    if i==4:
        while item2 <= len(owned_apps_ojo_2):
            name='Diario Ojo'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_ojo_2[item2][1]+'/insights?metric=engagement,impressions,reach,saved&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                likes=responseprueba_1["data"][0]["values"][0]["value"]
                impresions=responseprueba_1["data"][1]["values"][0]["value"]
                reach=responseprueba_1["data"][2]["values"][0]["value"]
                saved=responseprueba_1["data"][3]["values"][0]["value"]
                
                fecha22=owned_apps_ojo_2[item2][0]
                id22=owned_apps_ojo_2[item2][1]
                titulo=owned_apps_ojo_2[item2][2]
                link=owned_apps_ojo_2[item2][3]
                tipo=owned_apps_ojo_2[item2][4]
                
                if tipo=='VIDEO':
                    responseprueba_2={}
                    api2="https://graph.facebook.com/v10.0/"+id22+'/insights?metric=video_views&access_token='+a[i][1]
                    responseprueba_2=requests.get(api2,stream=True,headers=headers1)
                    responseprueba_2 = responseprueba_2.json()
                    views=responseprueba_2["data"][0]["values"][0]["value"]
                else:
                    views=0                
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores secundarios de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
                    likes,
                    impresions,
                    reach,
                    saved,
                    views,
					]
                )
            item2+=1
            if item2==len(owned_apps_ojo_2):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1vI2bqcIrYs0dgIQWPpvu90H1rdrrlQa8cjViziSEH50'
        subir_drive(listapub, hoja, name)
    
    if i==5:
        while item2 <= len(owned_apps_trome_2):
            name='Diario Trome'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_trome_2[item2][1]+'/insights?metric=engagement,impressions,reach,saved&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                likes=responseprueba_1["data"][0]["values"][0]["value"]
                impresions=responseprueba_1["data"][1]["values"][0]["value"]
                reach=responseprueba_1["data"][2]["values"][0]["value"]
                saved=responseprueba_1["data"][3]["values"][0]["value"]
                
                fecha22=owned_apps_trome_2[item2][0]
                id22=owned_apps_trome_2[item2][1]
                titulo=owned_apps_trome_2[item2][2]
                link=owned_apps_trome_2[item2][3]
                tipo=owned_apps_trome_2[item2][4]
                
                if tipo=='VIDEO':
                    responseprueba_2={}
                    api2="https://graph.facebook.com/v10.0/"+id22+'/insights?metric=video_views&access_token='+a[i][1]
                    responseprueba_2=requests.get(api2,stream=True,headers=headers1)
                    responseprueba_2 = responseprueba_2.json()
                    views=responseprueba_2["data"][0]["values"][0]["value"]
                else:
                    views=0                
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores secundarios de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
                    likes,
                    impresions,
                    reach,
                    saved,
                    views,
					]
                )
            item2+=1
            if item2==len(owned_apps_trome_2):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1GOvsevHz1fXYmDAssQQOKuNPpGYnEAk0v0OBwtLxXhA'
        subir_drive(listapub, hoja, name)
    
    if i==6:
        while item2 <= len(owned_apps_depor_2):
            name='Diario Depor'
            try:    
                responseprueba_1={}
                api1="https://graph.facebook.com/v10.0/"+owned_apps_depor_2[item2][1]+'/insights?metric=engagement,impressions,reach,saved&access_token='+a[i][1]
                responseprueba_1=requests.get(api1,stream=True,headers=headers1)
                responseprueba_1 = responseprueba_1.json()
                likes=responseprueba_1["data"][0]["values"][0]["value"]
                impresions=responseprueba_1["data"][1]["values"][0]["value"]
                reach=responseprueba_1["data"][2]["values"][0]["value"]
                saved=responseprueba_1["data"][3]["values"][0]["value"]
                
                fecha22=owned_apps_depor_2[item2][0]
                id22=owned_apps_depor_2[item2][1]
                titulo=owned_apps_depor_2[item2][2]
                link=owned_apps_depor_2[item2][3]
                tipo=owned_apps_depor_2[item2][4]
                
                if tipo=='VIDEO':
                    responseprueba_2={}
                    api2="https://graph.facebook.com/v10.0/"+id22+'/insights?metric=video_views&access_token='+a[i][1]
                    responseprueba_2=requests.get(api2,stream=True,headers=headers1)
                    responseprueba_2 = responseprueba_2.json()
                    views=responseprueba_2["data"][0]["values"][0]["value"]
                else:
                    views=0
                
            
            except Exception as err:
                sendMail("[Instagram] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores secundarios de publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
                
            listaReach.append( ##formato para agregar a una lista de forma manual
					[
					fecha22,
					id22,
					titulo,
					link,
					tipo,
                    likes,
                    impresions,
                    reach,
                    saved,
                    views
					]
                )
            item2+=1
            if item2==len(owned_apps_depor_2):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1NRm55tJa6hm4mke9BSVlCR4wAZrR3F0EA8C0HjMPpM0'
        subir_drive(listapub, hoja, name)
    i+=1                   
                                     
                             


