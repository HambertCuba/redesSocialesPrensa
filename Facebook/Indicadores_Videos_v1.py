import json
import pandas as pd
import csv
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
#from googledrive import subir_archivo
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
#from googledrive import subir_archivo

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
PATH_LOG = '/home/ec2-pentaho/pentaho/unp/Facebook/videos/log/'
name_log =PATH_LOG+'log_video_'+now.strftime("%Y_%m_%d")+'.log'
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
 	    logging.info("Carga de Indicadores Video")
 	return

#sacar las fechas de filtro
formato1="%Y-%m-%d"
formato2="%y-%m-%d"
now = datetime.today()
fecha_atras = now - timedelta(days=1)
#print(fecha_atras)
fecha1=now.strftime(formato1)
fecha2=fecha_atras.strftime(formato1)
#fecha2='2021-05-10'
#print(fecha2)

#sacar la cuenta de facebook:id y token
token = "EAAfj47wzha8BAM5270sDihowaSZCEEZBBPDqMDKZA8aoIKHpjGsmgcksN6rTWVYF72C3NnMavw3Jx99IjGoUogVPyfIbPqOj5JKfbJ4HZArr9WNIm3DNYxZANnCsWUW6wNzUag7sosfcPc44e32UjJksvn2BVJeDe5x1Eofn0Kyq59AsQOgBN3zaaF8yzEZBdWkGBnf9egoYCVZCTL6V5GpoSbPiBqpGlhn0WWulRyzn4BSqGQCQ9yE"
me= "122990462555483"
api= "https://graph.facebook.com/"+'v10.0'+'/'+me+'/'+'accounts?fields=name,access_token&access_token='+token
print(api)
headers1 = {
    'Content-Type': 'application/json'
                }
responseprueba=requests.get(api,stream=True,headers=headers1)
#print(response.url)
responseprueba = responseprueba.json()
resultadosprueba=responseprueba["data"]

def subir_archivo(listasubir,hoja,name):
    try: 
        #JSON_FILE = 'cmsproyecto-1610655853990-aa4048eb3551.json'
        JSON_FILE = '/home/ec2-pentaho/pentaho/unp/Facebook/videos/proceso/cmsproyecto-1610655853990-aa4048eb3551.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        CREDENCIALES = None
        CREDENCIALES = service_account.Credentials.from_service_account_file(
        JSON_FILE, scopes=SCOPES)
        # The ID and range of a sample spreadsheet.
        SPREADSHEET_ID = hoja#'1l8_KEVavN2Dz_aVC5CMEWAoWZJisgrfupHeAufkTrPI'
        RANGE_NAME = 'Indicadores_Video!A2'
        service = build('sheets', 'v4', credentials=CREDENCIALES)
        
        # ------ Agregamos el nuevo contenido ----------------
        carga_datos = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="USER_ENTERED",
        body={"values":listasubir})
        if carga_datos:
            print(f'inserta datos')
        else:
            sys.exit() #si hay un error corta el script
        carga_datos.execute()
    except Exception as err:
        sendMail("[Facebook] I.Videos",f"Ocurrio un error en la carga de indicadores video al sheet " +name+ f": {err} ")
        logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
        print(f'Other error occurred: {err}')  # Python 3.6
        
        
        
#######################parametros para videos
#METRICAS
i=0
while i <=10: 
    try:
        time.sleep(5)
        token3 = resultadosprueba[i]['access_token']
        me3= resultadosprueba[i]['id']
        name=resultadosprueba[i]['name']
        api3= "https://graph.facebook.com/"+'v10.0'+'/'+me3+'/insights?metric=page_video_views,page_video_views_10s,page_video_complete_views_30s&access_token='+token3+'&period=day&since='+fecha2+ ' 05:00:00&until='+fecha1+' 04:59:59'
        print(api3)
        headers3 = {
            'Content-Type': 'application/json'
                        }
        responseprueba3=requests.get(api3,stream=True,headers=headers3)
        #print(response.url)
        responseprueba3 = responseprueba3.json()        
        
        page_video_views=responseprueba3["data"][0]["values"][0]["value"]
        page_video_views_10s=responseprueba3["data"][1]["values"][0]["value"]
        page_video_complete_views_30s=responseprueba3["data"][2]["values"][0]["value"]
        
    except Exception as err:
         sendMail("[Facebook] I.Videos",f"Ocurrio un error en la obtencion de indicadores video: " +name+ f": {err} ")
         logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
         print(f'Other error occurred: {err}')  # Python 3.6  
        
    if i==0:                   
        listafinal_p21=[[fecha2,page_video_views,page_video_views_10s,page_video_complete_views_30s]]   
        hoja= '13RhYfyhCxN0dfGL_wPAkWO4fCrdQKycWEsKLV9azOPU'
        subir_archivo(listafinal_p21,hoja,name)
                        
    if i==1:                   
        listafinal_dco=[[fecha2,page_video_views,page_video_views_10s,page_video_complete_views_30s]]
        hoja='1QwMtFHD1i2Jlgx0opwrXOaaZw6imrKnyI0EPxa7Tkw8'
        subir_archivo(listafinal_dco,hoja,name)
            
    if i==2:                   
        listafinal_elboc=[[fecha2,page_video_views,page_video_views_10s,page_video_complete_views_30s]]
        hoja='1HkVudTW_bTxNhYgDGtstoIokne6KGiDutrGUAlixEeU'
        subir_archivo(listafinal_elboc,hoja,name)
            
    if i==3:                   
        listafinal_com=[[fecha2,page_video_views,page_video_views_10s,page_video_complete_views_30s]]
        hoja='1PzBtLx0CsJdjrYJxt9kDhQgkteYPwFFdodTNuRlrVrY'
        subir_archivo(listafinal_com,hoja,name)
            
    if i==4:                   
        listafinal_ojo=[[fecha2,page_video_views,page_video_views_10s,page_video_complete_views_30s]]
        hoja='1rwmermp9gUwICsQheOJIVmKqXZbOmkYA4XfHZ9vhEYs'
        subir_archivo(listafinal_ojo,hoja,name)
                     
            
    if i==6:                   
        listafinal_tro=[[fecha2,page_video_views,page_video_views_10s,page_video_complete_views_30s]]
        hoja='190W0NUSvRixX9pWyQjeJBBP9KBtCNLEciuC25Ifn7RE'
        subir_archivo(listafinal_tro,hoja,name)
      
    if i==8:                   
        listafinal_dep=[[fecha2,page_video_views,page_video_views_10s,page_video_complete_views_30s]]
        hoja='15JTE1wDxosDL8HnO5kYJGzHhtTdG8uBYNiW4788-OyU'
        subir_archivo(listafinal_dep,hoja,name)
            
    if i==9:                   
        listafinal_ges=[[fecha2,page_video_views,page_video_views_10s,page_video_complete_views_30s]]
        hoja='10Oh63E69CGtcfYVFPb23UYN5o7Cg78YiGCIeZ-uEXVs'
        subir_archivo(listafinal_ges,hoja,name)
            
    if i==10:                   
        listafinal_mag=[[fecha2,page_video_views,page_video_views_10s,page_video_complete_views_30s]]
        hoja='1sNN8VJ57VLUmbmQ4eocaCxuWEATp_jWjgGtoPER9D0c'
        subir_archivo(listafinal_mag,hoja,name)
            
            
    i+=1
        # if i==2:
        #     print(i)
        #     break
                                  
    # except Exception as err:
    #     #sendMail("[Facebook] I.Videos",f"Ocurrio un error en la obtencion de indicadores video : {err} ")
    #     #logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
    #     print(f'Other error occurred: {err}')  # Python 3.6                            

