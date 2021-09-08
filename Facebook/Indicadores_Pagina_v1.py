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
PATH_LOG = '/home/ec2-pentaho/pentaho/unp/Facebook/pagina/log/'
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
 	    logging.info("Carga de Indicadores Pagina")
 	return


#sacar las fechas de filtro
formato1="%Y-%m-%d"
formato2="%y-%m-%d"
fecha_atras = now - timedelta(days=1)
#print(fecha_atras)
fecha1=now.strftime(formato1)
fecha2=fecha_atras.strftime(formato1)
#print(fecha2)

def subir_ipagina(listasubir,hoja,name):
    try:        
        #JSON_FILE = 'cmsproyecto-1610655853990-aa4048eb3551.json'
        JSON_FILE = '/home/ec2-pentaho/pentaho/unp/Facebook/pagina/proceso/cmsproyecto-1610655853990-aa4048eb3551.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        CREDENCIALES = None
        CREDENCIALES = service_account.Credentials.from_service_account_file(
        JSON_FILE, scopes=SCOPES)
        # The ID and range of a sample spreadsheet.
        SPREADSHEET_ID = hoja #'1l8_KEVavN2Dz_aVC5CMEWAoWZJisgrfupHeAufkTrPI'
        RANGE_NAME = 'Indicadores_Página!A2'
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
        sendMail("[Facebook] I.Pagina",f"Ocurrio un error en la carga de indicadores pagina al sheet :"+name+" {err} ")
        logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
        print(f'Other error occurred: {err}')  # Python 3.6


#sacar la cuenta de facebook:id y token
token = "EAAfj47wzha8BAAZBBwcWMXs6hVpIGuh7Sx1P0RxEWDbKtYDZA1ezpm3bYlOAeoS5jxmaq4HRqiUXWgudZCaQziGLG0l2XEvzfOQ87PiBVpMKSDbewqBuLdajKbvgr9hNScLlb00VcZB3RLnhpyJfmW3SouC15K50RIe0kWWlSHOps8ozzVfjDsXh14ZB538H0RZAXzyUVNBgZDZD"
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
lista1=[]

#####sacar las publicaciones por cada objeto de la lista - cantidad e id del objeto
owned_apps_p21=[]
owned_apps_correo=[]
owned_apps_bocon=[]
owned_apps_com=[]
owned_apps_ojo=[]
owned_apps_trome=[]
owned_apps_depor=[]
owned_apps_gestion=[]
owned_apps_mag=[]
i=0
while i<= 10:
     
    token1 = resultadosprueba[i]['access_token']
    me2= resultadosprueba[i]['id']
    api2= "https://graph.facebook.com/"+'v10.0'+'/'+me2+'/'+'published_posts?access_token='+token1+'&period=day&since='+fecha2+'05:00:00 &until='+fecha1+' 04:59:59&limit=100'
    print(api2)
    headers2 = {
        'Content-Type': 'application/json'
                    }
    owned_apps = []
    responseprueba2=requests.get(api2,stream=True,headers=headers2)
    #print(response.url)
    responseprueba2 = responseprueba2.json()
    resultadosprueba2=responseprueba2["data"]
    owned_apps.extend(responseprueba2['data'])
    after = responseprueba2.get('paging',{}).get('cursors',{}).get('after',None)
    #print(responseprueba2["paging"]['next'])
    
    while after:            
        api_paginated = api2  + "&after=" + after
        responseprueba_2 = requests.get(url=api_paginated, stream=True, headers = headers2)
        #pprint(responseprueba2.url) 
        responseprueba_2 = responseprueba_2.json()
        owned_apps.extend(responseprueba_2['data'])
        after = responseprueba_2.get('paging',{}).get('cursors',{}).get('after',None)
     
        if not after or after == '':
            #print(after)
            break
    if i==0:
        owned_apps_p21=owned_apps
        cantidad_p21=len(owned_apps_p21)
    if i==1:
        owned_apps_correo=owned_apps
        cantidad_correo=len(owned_apps_correo)
    if i==2:
        owned_apps_bocon=owned_apps
        cantidad_bocon=len(owned_apps_bocon)
    if i==3:
        owned_apps_com=owned_apps
        cantidad_com=len(owned_apps_com)
    if i==4:
        owned_apps_ojo=owned_apps
        cantidad_ojo=len(owned_apps_ojo)
    if i==6:
        owned_apps_trome=owned_apps
        cantidad_trome=len(owned_apps_trome)
    if i==8:
        owned_apps_depor=owned_apps
        cantidad_depor=len(owned_apps_depor)
    if i==9:
        owned_apps_gestion=owned_apps
        cantidad_gestion=len(owned_apps_gestion)
    if i==10:
        owned_apps_mag=owned_apps
        cantidad_mag=len(owned_apps_mag)    
    
    i+=1

#######################parametros para la pagina
i=0
while i <= 10 :    
    try:
        time.sleep(2)
        token3 = resultadosprueba[i]['access_token']
        me3= resultadosprueba[i]['id']
        name=resultadosprueba[i]['name']
        api3= "https://graph.facebook.com/"+'v10.0'+'/'+me3+'/insights?metric=page_impressions_unique,page_impressions_organic_unique,page_impressions_paid_unique,page_impressions,page_impressions_organic,page_impressions_paid,page_engaged_users,page_negative_feedback_unique,page_negative_feedback,page_fans,page_consumptions,page_video_views,page_video_complete_views_30s,page_daily_video_ad_break_earnings_by_crosspost_status&access_token='+token3+'&period=day&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
        api4= "https://graph.facebook.com/"+'v11.0'+'/'+me3+'?fields=followers_count&access_token='+token3
        #print(api3)
        headers3 = {
            'Content-Type': 'application/json'
                        }
        responseprueba3=requests.get(api3,stream=True,headers=headers3)
        responseprueba4=requests.get(api4,stream=True,headers=headers3)
        #print(response.url)
        responseprueba3 = responseprueba3.json()
        responseprueba4 = responseprueba4.json()
        
        page_impressions_unique=responseprueba3["data"][0]["values"][0]["value"]
        page_impressions_organic_unique=responseprueba3["data"][1]["values"][0]["value"]
        page_impressions_paid_unique=responseprueba3["data"][2]["values"][0]["value"]
        page_impressions=responseprueba3["data"][3]["values"][0]["value"]
        page_impressions_organic=responseprueba3["data"][4]["values"][0]["value"]
        page_impressions_paid=responseprueba3["data"][5]["values"][0]["value"]
        page_engaged_users=responseprueba3["data"][6]["values"][0]["value"]
        page_negative_feedback_unique=responseprueba3["data"][7]["values"][0]["value"]
        page_negative_feedback=responseprueba3["data"][8]["values"][0]["value"]
        page_actions_post_reactions_like_total=responseprueba3["data"][9]["values"][0]["value"]
        page_consumptions=responseprueba3["data"][10]["values"][0]["value"]
        page_video_views=responseprueba3["data"][11]["values"][0]["value"]
        page_video_complete_views_30s=responseprueba3["data"][12]["values"][0]["value"]
        likes=responseprueba4["followers_count"]
        
        try:
            page_daily_video_ad_break_earnings_by_crosspost_status=responseprueba3["data"][13]["values"][0]["value"]["owned"]
        except:
            page_daily_video_ad_break_earnings_by_crosspost_status=0
    except Exception as err:
         sendMail("[Facebook] I.Pagina",f"Ocurrio un error en la obtencion de indicadores pagina : " +name+ f"{err} ")
         logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
         print(f'Other error occurred: {err}')  # Python 3.6

    listafinal2=[]
    if i==0:
        listafinal2=[[fecha2,cantidad_p21,page_impressions_unique,page_impressions_organic_unique,page_impressions_paid_unique,
                  page_impressions,page_impressions_organic,page_impressions_paid,page_engaged_users,
                  page_negative_feedback_unique,page_negative_feedback,page_actions_post_reactions_like_total,
                  page_consumptions,page_video_views,page_video_complete_views_30s,page_daily_video_ad_break_earnings_by_crosspost_status,likes
                  ]]
        hoja= '13RhYfyhCxN0dfGL_wPAkWO4fCrdQKycWEsKLV9azOPU'
        subir_ipagina(listafinal2,hoja,name)
        
    if i==1:
        listafinal2=[[fecha2,cantidad_correo,page_impressions_unique,page_impressions_organic_unique,page_impressions_paid_unique,
                  page_impressions,page_impressions_organic,page_impressions_paid,page_engaged_users,
                  page_negative_feedback_unique,page_negative_feedback,page_actions_post_reactions_like_total,
                  page_consumptions,page_video_views,page_video_complete_views_30s,page_daily_video_ad_break_earnings_by_crosspost_status,likes
                  ]]
        hoja='1QwMtFHD1i2Jlgx0opwrXOaaZw6imrKnyI0EPxa7Tkw8'
        subir_ipagina(listafinal2,hoja,name)
        
    if i==2:
        listafinal2=[[fecha2,cantidad_bocon,page_impressions_unique,page_impressions_organic_unique,page_impressions_paid_unique,
                  page_impressions,page_impressions_organic,page_impressions_paid,page_engaged_users,
                  page_negative_feedback_unique,page_negative_feedback,page_actions_post_reactions_like_total,
                  page_consumptions,page_video_views,page_video_complete_views_30s,page_daily_video_ad_break_earnings_by_crosspost_status,likes
                  ]]
        hoja='1HkVudTW_bTxNhYgDGtstoIokne6KGiDutrGUAlixEeU'
        subir_ipagina(listafinal2,hoja,name)
        
    if i==3:
        listafinal2=[[fecha2,cantidad_com,page_impressions_unique,page_impressions_organic_unique,page_impressions_paid_unique,
                  page_impressions,page_impressions_organic,page_impressions_paid,page_engaged_users,
                  page_negative_feedback_unique,page_negative_feedback,page_actions_post_reactions_like_total,
                  page_consumptions,page_video_views,page_video_complete_views_30s,page_daily_video_ad_break_earnings_by_crosspost_status,likes
                  ]]
        hoja='1PzBtLx0CsJdjrYJxt9kDhQgkteYPwFFdodTNuRlrVrY'
        subir_ipagina(listafinal2,hoja,name)
        
    if i==4:
        listafinal2=[[fecha2,cantidad_ojo,page_impressions_unique,page_impressions_organic_unique,page_impressions_paid_unique,
                  page_impressions,page_impressions_organic,page_impressions_paid,page_engaged_users,
                  page_negative_feedback_unique,page_negative_feedback,page_actions_post_reactions_like_total,
                  page_consumptions,page_video_views,page_video_complete_views_30s,page_daily_video_ad_break_earnings_by_crosspost_status,likes
                  ]]
        hoja='1rwmermp9gUwICsQheOJIVmKqXZbOmkYA4XfHZ9vhEYs'
        subir_ipagina(listafinal2,hoja,name)
    
    if i==6:
        listafinal2=[[fecha2,cantidad_trome,page_impressions_unique,page_impressions_organic_unique,page_impressions_paid_unique,
                  page_impressions,page_impressions_organic,page_impressions_paid,page_engaged_users,
                  page_negative_feedback_unique,page_negative_feedback,page_actions_post_reactions_like_total,
                  page_consumptions,page_video_views,page_video_complete_views_30s,page_daily_video_ad_break_earnings_by_crosspost_status,likes
                  ]]
        hoja='190W0NUSvRixX9pWyQjeJBBP9KBtCNLEciuC25Ifn7RE'
        subir_ipagina(listafinal2,hoja,name)
        
    if i==8:
        listafinal2=[[fecha2,cantidad_depor,page_impressions_unique,page_impressions_organic_unique,page_impressions_paid_unique,
                  page_impressions,page_impressions_organic,page_impressions_paid,page_engaged_users,
                  page_negative_feedback_unique,page_negative_feedback,page_actions_post_reactions_like_total,
                  page_consumptions,page_video_views,page_video_complete_views_30s,page_daily_video_ad_break_earnings_by_crosspost_status,likes
                  ]]
        hoja='15JTE1wDxosDL8HnO5kYJGzHhtTdG8uBYNiW4788-OyU'
        subir_ipagina(listafinal2,hoja,name)
        
    if i==9:
        listafinal2=[[fecha2,cantidad_gestion,page_impressions_unique,page_impressions_organic_unique,page_impressions_paid_unique,
                  page_impressions,page_impressions_organic,page_impressions_paid,page_engaged_users,
                  page_negative_feedback_unique,page_negative_feedback,page_actions_post_reactions_like_total,
                  page_consumptions,page_video_views,page_video_complete_views_30s,page_daily_video_ad_break_earnings_by_crosspost_status,likes
                  ]]
        hoja='10Oh63E69CGtcfYVFPb23UYN5o7Cg78YiGCIeZ-uEXVs'
        subir_ipagina(listafinal2,hoja,name)
        
    if i==10:
        listafinal2=[[fecha2,cantidad_mag,page_impressions_unique,page_impressions_organic_unique,page_impressions_paid_unique,
                  page_impressions,page_impressions_organic,page_impressions_paid,page_engaged_users,
                  page_negative_feedback_unique,page_negative_feedback,page_actions_post_reactions_like_total,
                  page_consumptions,page_video_views,page_video_complete_views_30s,page_daily_video_ad_break_earnings_by_crosspost_status,likes
                  ]]
        hoja='1sNN8VJ57VLUmbmQ4eocaCxuWEATp_jWjgGtoPER9D0c'
        subir_ipagina(listafinal2,hoja,name)
        
    i+=1                   
                                     
                             


