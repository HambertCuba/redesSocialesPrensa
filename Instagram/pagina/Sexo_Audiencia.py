import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

import webbrowser
import time
import pandas as pd
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
PATH_LOG = '/home/ec2-pentaho/pentaho/unp/Instagram/pagina/sexo/log/'
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
 	    server.sendmail(SENDER_SMTP, RECEIVERS_SMTP, msg.as_string())
 	    server.close()
 	# Display an error message if something goes wrong.
 	except Exception as e:
 		 logging.error(f"Exception occurred: {e}", exc_info=True)
 	else:
 	    logging.info("Carga de Indicadores Pagina Sexo")
 	return


def subir_drive(listasubir,hoja,name):
    try:        
        #JSON_FILE = 'cmsproyecto-1610655853990-aa4048eb3551.json'
        JSON_FILE = '/home/ec2-pentaho/pentaho/unp/Instagram/pagina/sexo/cmsproyecto-1610655853990-aa4048eb3551.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        CREDENCIALES = None
        CREDENCIALES = service_account.Credentials.from_service_account_file(
        JSON_FILE, scopes=SCOPES)
        # The ID and range of a sample spreadsheet.
        SPREADSHEET_ID = hoja #'1l8_KEVavN2Dz_aVC5CMEWAoWZJisgrfupHeAufkTrPI'
        RANGE_NAME = 'Audiencia_Sexo!A2'
        service = build('sheets', 'v4', credentials=CREDENCIALES)
        
        # ------ Agregamos el nuevo contenido ----------------
        carga_datos = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="USER_ENTERED",
        body={"values":listasubir})
        if carga_datos:
            print(f'inserta datos')
        else:
            sys.exit() #si hay un error corta el script
        carga_datos.execute()

    except Exception as err:
        sendMail("[Instagram] I.Pagina",f"Ocurrio un error en la carga de indicadores pagina sexo al sheet :"+name+" {err} ")
        logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
        print(f'Other error occurred: {err}')  # Python 3.6


headers1 = {
    'Content-Type': 'application/json'
                }

#id y token de cuentas
#comercio,p21,correo,bocon,ojo,trome,depor
a = [['17841401810950570', 'EAAfj47wzha8BAPidlKbUwl0OXdYvEGNTcaVzfBUiG4dPOZAHEZCzBgVwsaZBbsB9rdpvEUiDzS9eZCGRCnexrrod6AN2jb75ZCwfyZAhjgpclZAWJfwvhkZAyKRVkrSZBmoKHfhMyXbul4aYSZABBXqjisqtSZB3fA6t5PHFZB86g8Uh4nNZCqXtZBtyUJZAOnkSgDZBWZCgZD'], 
     ['17841400118433671', 'EAAfj47wzha8BAKvnyTEJQfgmH0YYfJ6cqyYwZBFEmnTZAKRW8oit69DclYAOFolv61ZAUAxOsRLnhwO4Dh0PhlLpdYg61Sq7wYZAcWXR713ZCwZCQtDo25PyMrEvuR6QbGJTXbhszSEcBtZBSwwPgczxJZBzEguZCpOAHJBTEbVXpd0mLQFFhbemRugE8qV2cfKQZD'],
     ['17841402209037198', 'EAAfj47wzha8BAMWXbZAdjiRY8Lv3zkzF05Hf1cYUaTcFXXam1ZCZCmMCKAJY7QvqCJ0tUwcwTvEqeTPnBxWcmQZBE4kxKsb3qAQaZBFusFi4lRBGqMyZBqZAGa8jr4U0RA5c3NCzeHHVmxUHkwcerw1oKuPPQfFc8kcjBO2664TpfILTKWSQzj5MFscJXy5PLoZD'],
     ['17841402218427177', 'EAAfj47wzha8BAPlzphOVryEurORT7YFn2swhZBN7fd0zms711PGDSLHVgKCof5F0C0kQxet0FUzi2RX7TtNCX4Hzy0Wgyo9zG9JzzwamBZCdzBmnW7vYUZCt3vVlVKBNgTZBfD9OOxViILzndZByTxWCtQOss2GJGZBF6gh40Qp9jcH0TicI2t6cFttYrTGmwZD'],
     ['17841402262227176', 'EAAfj47wzha8BAPGyeAeEiGKdt81cL6qIsHgG4TCj3HpxMJ9H0xbB8kNDS7xiwbcXwn7hwqb9quo487OEH8amBlcYTlXn74LWNHxbOQLzcLjsz8V78fFlgSZCv6fdP0RQCZAFCs3ujEZAMRMZAN8BAM1z1TbLs2pzI7RI4HsxmCsytWv3b8qOPM5gor9rZCzkZD'],
     ['17841403402984824', 'EAAfj47wzha8BAHIpMf4MKaudIEyox4fxQ5q6DWMMUDtZCeYDAynihvPfZAInJ9N5yvswqUzgaSkGzFHOwSA4lMaaCIjUNrG11aBxd81tgZCFC022Q3axx3p5jAQhur1JaetanCy919aXxxMG0nKZCx8YPcI8cWPn6KeX1rr8ZBn3f1XA59SF8DrxbaBEZAmgoZD'],
     ['17841401572678380', 'EAAfj47wzha8BAG2t6wklpL8hH6x6lqp0t1IQuanttmK8EeZCJ09LFvSg5k7aGd9r3CWFhiXA3GUjBB2NlfLMckZAvQeQ87Lkg6wjZCenXa7nXO2LZBN7ZAvFjFgh0eMmu88zWtdZBi9SlPh015pmABVZAcQ50L0tB2QUlgqCYNYR6V9kdKHFQcBkuyT2kCMGlsZD']]

owned_apps_p21=[]
owned_apps_correo=[]
owned_apps_bocon=[]
owned_apps_com=[]
owned_apps_ojo=[]
owned_apps_trome=[]
owned_apps_depor=[]

i=0
while i<= 6:
    try:
        api= 'https://graph.facebook.com/'+a[i][0]+'/insights?metric=audience_gender_age&period=lifetime&access_token='+a[i][1]
        responseprueba=requests.get(api,stream=True,headers=headers1)
        responseprueba = responseprueba.json()
        resultadosprueba=responseprueba["data"]
        resultadosprueba_1=resultadosprueba[0]["values"][0]["value"]
    except Exception as err:
         sendMail("[Instagram] I.Pagina",f"Ocurrio un error en la obtencion de indicadores pagina sexo : " + f"{err} ")
         logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
         print(f'Other error occurred: {err}')  # Python 3.6

    if i==0:
        item2=0
        listaReach=[]
        owned_apps_com=resultadosprueba_1
        owned_apps_com=[owned_apps_com]
        resultados2=[]
        resultados2=owned_apps_com[0]
        df1=pd.DataFrame(resultados2.items(),columns=['Key','Value'])
        audiencia_list = df1.values.tolist()
        item2=0
        listaReach=[]
        while item2 <= len(audiencia_list):
            region=audiencia_list[item2][0]
            value=audiencia_list[item2][1]
            listaReach.append( ##formato para agregar a una lista de forma manual
            [
            region,
            value,
            ]
            )
            item2+=1
            if item2==len(audiencia_list):
                print(item2)
                break        
        name='Comercio'
        hoja='1--sqHgzuaaahfZWk9beWQqsoFScruyCI_qr_aQF5r74'
        subir_drive(listaReach,hoja,name)
        
    if i==1:
        item2=0
        listaReach=[]
        owned_apps_p21=resultadosprueba_1
        owned_apps_p21=[owned_apps_p21]
        resultados2=[]
        resultados2=owned_apps_p21[0]
        df1=pd.DataFrame(resultados2.items(),columns=['Key','Value'])
        audiencia_list = df1.values.tolist()
        item2=0
        listaReach=[]
        while item2 <= len(audiencia_list):
            region=audiencia_list[item2][0]
            value=audiencia_list[item2][1]
            listaReach.append( ##formato para agregar a una lista de forma manual
            [
            region,
            value,
            ]
            )
            item2+=1
            if item2==len(audiencia_list):
                print(item2)
                break        
        name='Peru21'
        hoja='1eRO8Qdva2u9_7O43PZ64eTkUqlHHv8kV3ErT0QXGNBE'
        subir_drive(listaReach,hoja,name)
    
    if i==2:
        item2=0
        listaReach=[]
        owned_apps_correo=resultadosprueba_1
        owned_apps_correo=[owned_apps_correo]
        resultados2=[]
        resultados2=owned_apps_correo[0]
        df1=pd.DataFrame(resultados2.items(),columns=['Key','Value'])
        audiencia_list = df1.values.tolist()
        item2=0
        listaReach=[]
        while item2 <= len(audiencia_list):
            region=audiencia_list[item2][0]
            value=audiencia_list[item2][1]
            listaReach.append( ##formato para agregar a una lista de forma manual
            [
            region,
            value,
            ]
            )
            item2+=1
            if item2==len(audiencia_list):
                print(item2)
                break        
        name='Correo'
        hoja='1GffkrykC1EIMu5QZRgtivNJAri6P9mX-M4yBA5bN_TU'
        subir_drive(listaReach,hoja,name)
    
    if i==3:
        item2=0
        listaReach=[]
        owned_apps_bocon=resultadosprueba_1
        owned_apps_bocon=[owned_apps_bocon]
        resultados2=[]
        resultados2=owned_apps_bocon[0]
        df1=pd.DataFrame(resultados2.items(),columns=['Key','Value'])
        audiencia_list = df1.values.tolist()
        item2=0
        listaReach=[]
        while item2 <= len(audiencia_list):
            region=audiencia_list[item2][0]
            value=audiencia_list[item2][1]
            listaReach.append( ##formato para agregar a una lista de forma manual
            [
            region,
            value,
            ]
            )
            item2+=1
            if item2==len(audiencia_list):
                print(item2)
                break        
        name='Bocon'
        hoja='1n8Fqm7QyrRlUN72-sjsQy6UJNvkqCYr2NfyNzhRfK1s'
        subir_drive(listaReach,hoja,name)
        
    if i==4:
        item2=0
        listaReach=[]
        owned_apps_ojo=resultadosprueba_1
        owned_apps_ojo=[owned_apps_ojo]
        resultados2=[]
        resultados2=owned_apps_ojo[0]
        df1=pd.DataFrame(resultados2.items(),columns=['Key','Value'])
        audiencia_list = df1.values.tolist()
        item2=0
        listaReach=[]
        while item2 <= len(audiencia_list):
            region=audiencia_list[item2][0]
            value=audiencia_list[item2][1]
            listaReach.append( ##formato para agregar a una lista de forma manual
            [
            region,
            value,
            ]
            )
            item2+=1
            if item2==len(audiencia_list):
                print(item2)
                break        
        name='Ojo'
        hoja='1G4dC6y2mqeJ0BvIZu73ldCzxXgFAAXDuGfYOF5L7NE0'
        subir_drive(listaReach,hoja,name)
        
    if i==5:
        item2=0
        listaReach=[]
        owned_apps_trome=resultadosprueba_1
        owned_apps_trome=[owned_apps_trome]
        resultados2=[]
        resultados2=owned_apps_trome[0]
        df1=pd.DataFrame(resultados2.items(),columns=['Key','Value'])
        audiencia_list = df1.values.tolist()
        item2=0
        listaReach=[]
        while item2 <= len(audiencia_list):
            region=audiencia_list[item2][0]
            value=audiencia_list[item2][1]
            listaReach.append( ##formato para agregar a una lista de forma manual
            [
            region,
            value,
            ]
            )
            item2+=1
            if item2==len(audiencia_list):
                print(item2)
                break        
        name='Trome'
        hoja='1qkYvIEgoPSyyCBSYVZ7AJ7eHlGvGuBjQHrfwwKHJBSY'
        subir_drive(listaReach,hoja,name)
        
    if i==6:
        item2=0
        listaReach=[]
        owned_apps_depor=resultadosprueba_1
        owned_apps_depor=[owned_apps_depor]
        resultados2=[]
        resultados2=owned_apps_depor[0]
        df1=pd.DataFrame(resultados2.items(),columns=['Key','Value'])
        audiencia_list = df1.values.tolist()
        item2=0
        listaReach=[]
        while item2 <= len(audiencia_list):
            region=audiencia_list[item2][0]
            value=audiencia_list[item2][1]
            listaReach.append( ##formato para agregar a una lista de forma manual
            [
            region,
            value,
            ]
            )
            item2+=1
            if item2==len(audiencia_list):
                print(item2)
                break        
        name='Depor'
        hoja='1CbsBI_00ncCBblrXW8ug3bUQR5-GfnPTjGCAAoff-04'
        subir_drive(listaReach,hoja,name)
        
    i+=1
    
