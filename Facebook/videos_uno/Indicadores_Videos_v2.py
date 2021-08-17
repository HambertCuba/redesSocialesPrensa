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
PATH_LOG = '/home/ec2-pentaho/pentaho/unp/Facebook/videos_uno/log/'
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
 	    logging.info("Carga de Indicadores Publicacion")
 	return

def subir_drive(listasubir,hoja,name):
    try:
        #JSON_FILE = 'cmsproyecto-1610655853990-aa4048eb3551.json'
        JSON_FILE = '/home/ec2-pentaho/pentaho/unp/Facebook/videos_uno/proceso/cmsproyecto-1610655853990-aa4048eb3551.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        CREDENCIALES = None
        CREDENCIALES = service_account.Credentials.from_service_account_file(
        JSON_FILE, scopes=SCOPES)
        # The ID and range of a sample spreadsheet.
        SPREADSHEET_ID = hoja #'1l8_KEVavN2Dz_aVC5CMEWAoWZJisgrfupHeAufkTrPI'
        RANGE_NAME = 'Indicadores_por_Video!A2'
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
        sendMail("[Facebook] I.Video c/uno",f"Ocurrio un error en la carga de indicadores videos al sheet :" +name+ f" {err} ")
        logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
        print(f'Other error occurred: {err}')  # Python 3.6
    

#sacar las fechas de filtro
formato1="%Y-%m-%d"
formato2="%y-%m-%d"
now = datetime.today()
fecha_atras = now - timedelta(days=1)
#print(fecha_atras)
fecha1=now.strftime(formato1)
fecha2=fecha_atras.strftime(formato1)
#print(fecha2)

#sacar la cuenta de facebook:id y token
token = "EAAfj47wzha8BAMAacVES9jcb2UJZAFwdJsAokZBCNZAzEVpCPSOHfodvgxqmUJEwtcvMdDKek9EiiPteLMVYIfkPrdLXZCP3f6CT9aQFq7onNCbDaKdvlYKxKKrvTJvAEHwTHvodpUMkhmxRZCMrxZBGZCHGMkcipPR4BZCXN0Qi1FZAKHgZA7dZBA5"
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
headers3 = {
    'Content-Type': 'application/json'
                }  

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
    #api2= "https://graph.facebook.com/"+'v10.0'+'/'+me2+'/'+'published_posts?access_token='+token1+'&period=day&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59&limit=100'
    api2= "https://graph.facebook.com/"+'v10.0'+'/'+me2+'/'+'published_posts?access_token='+token1+'&period=day&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59&limit=100'
    #print(api2)
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
        token3 = resultadosprueba[i]['access_token']
        owned_apps_p21=owned_apps
        cantidad_p21=len(owned_apps_p21)
        item2=0
        listap21=[]
        while item2 <= len(owned_apps_p21):
            responseprueba_p21={}
            api=""
            api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_p21[item2]['id']+'/attachments?access_token='+token3
            responseprueba_p21=requests.get(api,stream=True,headers=headers3)
            responseprueba_p21 = responseprueba_p21.json()
            id22=owned_apps_p21[item2]['id']
            try:
                  desc=responseprueba_p21["data"][0]["title"]
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  desc=''
                  
            try:
                  copy=owned_apps_p21[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  copy=''
                  
            tipo=responseprueba_p21["data"][0]["type"]            
            # listap21_new
            if tipo=='video_inline':
                listap21.append([id22,copy,desc,tipo])
                         
            item2+=1
            if item2==len(owned_apps_p21):
                print(item2)
                break
   
    if i==1:
        token3 = resultadosprueba[i]['access_token']
        owned_apps_correo=owned_apps
        cantidad_correo=len(owned_apps_correo)
        item2=0
        listacorr=[]
        while item2 <= len(owned_apps_correo):
            responseprueba_corr={}
            api=""
            api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_correo[item2]['id']+'/attachments?access_token='+token3
            responseprueba_corr=requests.get(api,stream=True,headers=headers3)
            responseprueba_corr = responseprueba_corr.json()
            id22=owned_apps_correo[item2]['id']
            try:
                  desc=responseprueba_corr["data"][0]["title"]
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  desc='' 
            try:
                  copy=owned_apps_correo[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  copy=''        
            tipo=responseprueba_corr["data"][0]["type"]    
            if tipo=='video_inline':
                listacorr.append([id22,copy,desc,tipo])
                         
            item2+=1
            if item2==len(owned_apps_correo):
                print(item2)
                break
            
    if i==2:
        token3 = resultadosprueba[i]['access_token']
        owned_apps_bocon=owned_apps
        cantidad_bocon=len(owned_apps_bocon)
        item2=0
        listaboco=[]
        while item2 <= len(owned_apps_bocon):
            responseprueba_boco={}
            api=""
            api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_bocon[item2]['id']+'/attachments?access_token='+token3
            responseprueba_boco=requests.get(api,stream=True,headers=headers3)
            responseprueba_boco = responseprueba_boco.json()
            id22=owned_apps_bocon[item2]['id']
            try:
                  desc=responseprueba_boco["data"][0]["title"]
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  desc=''    
            try:
                  copy=owned_apps_bocon[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  copy=''      
            tipo=responseprueba_boco["data"][0]["type"]    
            if tipo=='video_inline':
                listaboco.append([id22,copy,desc,tipo])
                         
            item2+=1
            if item2==len(owned_apps_bocon):
                print(item2)
                break
    if i==3:
        token3 = resultadosprueba[i]['access_token']
        owned_apps_com=owned_apps
        cantidad_com=len(owned_apps_com)
        item2=0
        listacomer=[]
        while item2 <= len(owned_apps_com):
            responseprueba_comer={}
            api=""
            api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_com[item2]['id']+'/attachments?access_token='+token3
            responseprueba_comer=requests.get(api,stream=True,headers=headers3)
            responseprueba_comer = responseprueba_comer.json()
            id22=owned_apps_com[item2]['id']
            try:
                  desc=responseprueba_comer["data"][0]["title"]
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  desc=''     
            try:
                  copy=owned_apps_com[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  copy=''     
            tipo=responseprueba_comer["data"][0]["type"]    
            if tipo=='video_inline':
                listacomer.append([id22,copy,desc,tipo])
                         
            item2+=1
            if item2==len(owned_apps_com):
                print(item2)
                break
        
    if i==4:
        token3 = resultadosprueba[i]['access_token']
        owned_apps_ojo=owned_apps
        cantidad_ojo=len(owned_apps_ojo)
        item2=0
        listaojo=[]
        while item2 <= len(owned_apps_ojo):
            responseprueba_ojo={}
            api=""
            api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_ojo[item2]['id']+'/attachments?access_token='+token3
            responseprueba_ojo=requests.get(api,stream=True,headers=headers3)
            responseprueba_ojo = responseprueba_ojo.json()
            id22=owned_apps_ojo[item2]['id']
            try:
                  desc=responseprueba_ojo["data"][0]["title"]
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  desc=''
            try:
                  copy=owned_apps_ojo[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  copy=''           
            tipo=responseprueba_ojo["data"][0]["type"]    
            if tipo=='video_inline':
                listaojo.append([id22,copy,desc,tipo])
                         
            item2+=1
            if item2==len(owned_apps_ojo):
                print(item2)
                break
        
    if i==6:
        token3 = resultadosprueba[i]['access_token']
        owned_apps_trome=owned_apps
        cantidad_trome=len(owned_apps_trome)
        item2=0
        listatrom=[]
        while item2 <= len(owned_apps_trome):
            responseprueba_tro={}
            api=""
            api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_trome[item2]['id']+'/attachments?access_token='+token3
            responseprueba_tro=requests.get(api,stream=True,headers=headers3)
            responseprueba_tro = responseprueba_tro.json()
            id22=owned_apps_trome[item2]['id']
            try:
                  desc=responseprueba_tro["data"][0]["title"]
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  desc=''   
            try:
                  copy=owned_apps_trome[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  copy=''        
            tipo=responseprueba_tro["data"][0]["type"]    
            if tipo=='video_inline':
                listatrom.append([id22,copy,desc,tipo])
                         
            item2+=1
            if item2==len(owned_apps_trome):
                print(item2)
                break
    if i==8:
        token3 = resultadosprueba[i]['access_token']
        owned_apps_depor=owned_apps
        cantidad_depor=len(owned_apps_depor)
        item2=0
        listadepo=[]
        while item2 <= len(owned_apps_depor):
            responseprueba_depo={}
            api=""
            api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_depor[item2]['id']+'/attachments?access_token='+token3
            responseprueba_depo=requests.get(api,stream=True,headers=headers3)
            responseprueba_depo = responseprueba_depo.json()
            id22=owned_apps_depor[item2]['id']
            try:
                  desc=responseprueba_depo["data"][0]["title"]
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  desc=''  
            try:
                  copy=owned_apps_depor[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  copy=''        
            tipo=responseprueba_depo["data"][0]["type"]    
            if tipo=='video_inline':
                listadepo.append([id22,copy,desc,tipo])
                         
            item2+=1
            if item2==len(owned_apps_depor):
                print(item2)
                break
    if i==9:
        token3 = resultadosprueba[i]['access_token']
        owned_apps_gestion=owned_apps
        cantidad_gestion=len(owned_apps_gestion)
        item2=0
        listagest=[]
        while item2 <= len(owned_apps_gestion):
            responseprueba_gest={}
            api=""
            api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_gestion[item2]['id']+'/attachments?access_token='+token3
            responseprueba_gest=requests.get(api,stream=True,headers=headers3)
            responseprueba_gest = responseprueba_gest.json()
            id22=owned_apps_gestion[item2]['id']
            try:
                  desc=responseprueba_gest["data"][0]["title"]
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  desc=''  
            try:
                  copy=owned_apps_gestion[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  copy=''         
            tipo=responseprueba_gest["data"][0]["type"]    
            if tipo=='video_inline':
                listagest.append([id22,copy,desc,tipo])
                         
            item2+=1
            if item2==len(owned_apps_gestion):
                print(item2)
                break
    if i==10:
        token3 = resultadosprueba[i]['access_token']
        owned_apps_mag=owned_apps
        cantidad_mag=len(owned_apps_mag)
        item2=0
        listamag=[]
        while item2 <= len(owned_apps_mag):
            responseprueba_mag={}
            api=""
            api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_mag[item2]['id']+'/attachments?access_token='+token3
            responseprueba_mag=requests.get(api,stream=True,headers=headers3)
            responseprueba_mag = responseprueba_mag.json()
            id22=owned_apps_mag[item2]['id']
            try:
                  desc=responseprueba_mag["data"][0]["title"]
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  desc=''    
                  
            try:
                  copy=owned_apps_mag[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  copy='' 
            tipo=responseprueba_mag["data"][0]["type"]    
            if tipo=='video_inline':
                listamag.append([id22,copy,desc,tipo])
                         
            item2+=1
            if item2==len(owned_apps_mag):
                print(item2)
                break
    i+=1

i=0
while i <= 10 :         
    time.sleep(2)
    token3 = resultadosprueba[i]['access_token']
    me3= resultadosprueba[i]['id']
    name=resultadosprueba[i]['name']
    item2=0
    listaReach=[]
    
    if i==0:
        while item2 <= len(listap21):
            if len(listap21)==0:
                listaReach=[]
                break
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+listap21[item2][0]+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks,post_video_views&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+listap21[item2][0]+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+listap21[item2][0]+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                post_impressions_unique=responseprueba_1["data"][0]["values"][0]["value"]
                post_impressions_organic_unique=responseprueba_1["data"][1]["values"][0]["value"]
                post_impressions_paid_unique=responseprueba_1["data"][2]["values"][0]["value"]
                post_impressions=responseprueba_1["data"][3]["values"][0]["value"]
                post_impressions_organic=responseprueba_1["data"][4]["values"][0]["value"]
                post_impressions_paid=responseprueba_1["data"][5]["values"][0]["value"]
                post_engaged_users=responseprueba_1["data"][6]["values"][0]["value"]
                post_negative_feedback_unique=responseprueba_1["data"][7]["values"][0]["value"]
                post_negative_feedback=responseprueba_1["data"][8]["values"][0]["value"]
                try:
                  anger=responseprueba_1["data"][9]["values"][0]["value"]["anger"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    anger=0
                
                try:
                  haha=responseprueba_1["data"][9]["values"][0]["value"]["haha"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla haha')  
                    haha=0
                    
                try:
                  like=responseprueba_1["data"][9]["values"][0]["value"]["like"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla like')  
                    like=0
                    
                try:
                  love=responseprueba_1["data"][9]["values"][0]["value"]["love"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla love')  
                    love=0
                 
                try:
                  sorry=responseprueba_1["data"][9]["values"][0]["value"]["sorry"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    sorry=0
                
                try:
                  wow=responseprueba_1["data"][9]["values"][0]["value"]["wow"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    wow=0
            
                post_clicks=responseprueba_1["data"][10]["values"][0]["value"] 
                video_3s=responseprueba_1["data"][11]["values"][0]["value"] 
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                    
                suma_reacciones= like+love+sorry+wow+anger+haha
                comments=responseprueba_3["summary"]["total_count"]
                
                                  
            except Exception as err:
                sendMail("[Facebook] I.Video c/uno",f"Ocurrio un error en la obtencion de indicadores por cada video :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=listap21[item2][0]
            copy_22=listap21[item2][1]
            try:
                  titulo22=listap21[item2][2]
            except(ValueError,KeyError,ZeroDivisionError,NameError): 
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     id_22,
                     copy_22,
                     titulo22,
                     video_3s,
                     post_impressions_unique,
                     post_impressions_organic_unique,
                     post_impressions_paid_unique,
                     post_impressions,
                     post_impressions_organic,
                     post_impressions_paid,
                     post_engaged_users,
                     post_negative_feedback_unique,
                     post_negative_feedback,
                     like,
                     love,
                     sorry,
                     wow,
                     anger,
                     haha,           
                     post_clicks,
                     shares,
                     comments,
                     suma_reacciones,
                ]
            )
            item2+=1
            if item2==len(listap21):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='142sKZmLAFEFp44_s22y-p9wBu0nfuIZxWo29d_b2Fs0'
        subir_drive(listapub, hoja, name)
        
      
    if i==1:
        while item2 <= len(listacorr):
            if len(listacorr)==0:
                listaReach=[]
                break
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+listacorr[item2][0]+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks,post_video_views&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+listacorr[item2][0]+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+listacorr[item2][0]+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                post_impressions_unique=responseprueba_1["data"][0]["values"][0]["value"]
                post_impressions_organic_unique=responseprueba_1["data"][1]["values"][0]["value"]
                post_impressions_paid_unique=responseprueba_1["data"][2]["values"][0]["value"]
                post_impressions=responseprueba_1["data"][3]["values"][0]["value"]
                post_impressions_organic=responseprueba_1["data"][4]["values"][0]["value"]
                post_impressions_paid=responseprueba_1["data"][5]["values"][0]["value"]
                post_engaged_users=responseprueba_1["data"][6]["values"][0]["value"]
                post_negative_feedback_unique=responseprueba_1["data"][7]["values"][0]["value"]
                post_negative_feedback=responseprueba_1["data"][8]["values"][0]["value"]
                try:
                  anger=responseprueba_1["data"][9]["values"][0]["value"]["anger"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    anger=0
                
                try:
                  haha=responseprueba_1["data"][9]["values"][0]["value"]["haha"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla haha')  
                    haha=0
                    
                try:
                  like=responseprueba_1["data"][9]["values"][0]["value"]["like"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla like')  
                    like=0
                    
                try:
                  love=responseprueba_1["data"][9]["values"][0]["value"]["love"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla love')  
                    love=0
                 
                try:
                  sorry=responseprueba_1["data"][9]["values"][0]["value"]["sorry"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    sorry=0
                
                try:
                  wow=responseprueba_1["data"][9]["values"][0]["value"]["wow"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    wow=0
            
                post_clicks=responseprueba_1["data"][10]["values"][0]["value"] 
                video_3s=responseprueba_1["data"][11]["values"][0]["value"]
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                    
                suma_reacciones= like+love+sorry+wow+anger+haha
                comments=responseprueba_3["summary"]["total_count"]
                
                                  
            except Exception as err:
                sendMail("[Facebook] I.Video c/uno",f"Ocurrio un error en la obtencion de indicadores por cada video :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=listacorr[item2][0]
            copy_22=listacorr[item2][1]
            try:
                  titulo22=listacorr[item2][2]
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     id_22,
                     copy_22,
                     titulo22,
                     video_3s,
                     post_impressions_unique,
                     post_impressions_organic_unique,
                     post_impressions_paid_unique,
                     post_impressions,
                     post_impressions_organic,
                     post_impressions_paid,
                     post_engaged_users,
                     post_negative_feedback_unique,
                     post_negative_feedback,
                     like,
                     love,
                     sorry,
                     wow,
                     anger,
                     haha,           
                     post_clicks,
                     shares,
                     comments,
                     suma_reacciones,
                ]
            )
            item2+=1
            if item2==len(listacorr):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1AJ5vjVa6D8PxiZULUZ2Ny_Bi4qH4682d1s901dCw0Fk'
        subir_drive(listapub, hoja, name)
    
    if i==2:
        while item2 <= len(listaboco):
            if len(listaboco)==0:
                listaReach=[]
                break
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+listaboco[item2][0]+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks,post_video_views&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+listaboco[item2][0]+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+listaboco[item2][0]+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                post_impressions_unique=responseprueba_1["data"][0]["values"][0]["value"]
                post_impressions_organic_unique=responseprueba_1["data"][1]["values"][0]["value"]
                post_impressions_paid_unique=responseprueba_1["data"][2]["values"][0]["value"]
                post_impressions=responseprueba_1["data"][3]["values"][0]["value"]
                post_impressions_organic=responseprueba_1["data"][4]["values"][0]["value"]
                post_impressions_paid=responseprueba_1["data"][5]["values"][0]["value"]
                post_engaged_users=responseprueba_1["data"][6]["values"][0]["value"]
                post_negative_feedback_unique=responseprueba_1["data"][7]["values"][0]["value"]
                post_negative_feedback=responseprueba_1["data"][8]["values"][0]["value"]
                try:
                  anger=responseprueba_1["data"][9]["values"][0]["value"]["anger"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    anger=0
                
                try:
                  haha=responseprueba_1["data"][9]["values"][0]["value"]["haha"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla haha')  
                    haha=0
                    
                try:
                  like=responseprueba_1["data"][9]["values"][0]["value"]["like"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla like')  
                    like=0
                    
                try:
                  love=responseprueba_1["data"][9]["values"][0]["value"]["love"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla love')  
                    love=0
                 
                try:
                  sorry=responseprueba_1["data"][9]["values"][0]["value"]["sorry"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    sorry=0
                
                try:
                  wow=responseprueba_1["data"][9]["values"][0]["value"]["wow"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    wow=0
            
                post_clicks=responseprueba_1["data"][10]["values"][0]["value"]
                video_3s=responseprueba_1["data"][11]["values"][0]["value"]
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                    
                suma_reacciones= like+love+sorry+wow+anger+haha
                comments=responseprueba_3["summary"]["total_count"]
                
                                  
            except Exception as err:
                sendMail("[Facebook] I.Video c/uno",f"Ocurrio un error en la obtencion de indicadores por cada video :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=listaboco[item2][0]
            copy_22=listaboco[item2][1]
            try:
                  titulo22=listaboco[item2][2]
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     id_22,
                     copy_22,
                     titulo22,
                     video_3s,
                     post_impressions_unique,
                     post_impressions_organic_unique,
                     post_impressions_paid_unique,
                     post_impressions,
                     post_impressions_organic,
                     post_impressions_paid,
                     post_engaged_users,
                     post_negative_feedback_unique,
                     post_negative_feedback,
                     like,
                     love,
                     sorry,
                     wow,
                     anger,
                     haha,           
                     post_clicks,
                     shares,
                     comments,
                     suma_reacciones,
                ]
            )
            item2+=1
            if item2==len(listaboco):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='14wVlKHFI_S3PvC6I_SZO_VlRPnGiq_iShLsD5rTYhuM'
        subir_drive(listapub, hoja, name)
        
    if i==3:
        while item2 <= len(listacomer):
            if len(listacomer)==0:
                listaReach=[]
                break
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+listacomer[item2][0]+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks,post_video_views&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+listacomer[item2][0]+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+listacomer[item2][0]+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                post_impressions_unique=responseprueba_1["data"][0]["values"][0]["value"]
                post_impressions_organic_unique=responseprueba_1["data"][1]["values"][0]["value"]
                post_impressions_paid_unique=responseprueba_1["data"][2]["values"][0]["value"]
                post_impressions=responseprueba_1["data"][3]["values"][0]["value"]
                post_impressions_organic=responseprueba_1["data"][4]["values"][0]["value"]
                post_impressions_paid=responseprueba_1["data"][5]["values"][0]["value"]
                post_engaged_users=responseprueba_1["data"][6]["values"][0]["value"]
                post_negative_feedback_unique=responseprueba_1["data"][7]["values"][0]["value"]
                post_negative_feedback=responseprueba_1["data"][8]["values"][0]["value"]
                try:
                  anger=responseprueba_1["data"][9]["values"][0]["value"]["anger"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    anger=0
                
                try:
                  haha=responseprueba_1["data"][9]["values"][0]["value"]["haha"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla haha')  
                    haha=0
                    
                try:
                  like=responseprueba_1["data"][9]["values"][0]["value"]["like"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla like')  
                    like=0
                    
                try:
                  love=responseprueba_1["data"][9]["values"][0]["value"]["love"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla love')  
                    love=0
                 
                try:
                  sorry=responseprueba_1["data"][9]["values"][0]["value"]["sorry"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    sorry=0
                
                try:
                  wow=responseprueba_1["data"][9]["values"][0]["value"]["wow"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    wow=0
            
                post_clicks=responseprueba_1["data"][10]["values"][0]["value"]
                video_3s=responseprueba_1["data"][11]["values"][0]["value"]
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                    
                suma_reacciones= like+love+sorry+wow+anger+haha
                comments=responseprueba_3["summary"]["total_count"]
                
                                  
            except Exception as err:
                sendMail("[Facebook] I.Video c/uno",f"Ocurrio un error en la obtencion de indicadores por cada video :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=listacomer[item2][0]            
            copy_22=listacomer[item2][1]
            try:
                  titulo22=listacomer[item2][2]
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     id_22,
                     copy_22,
                     titulo22,
                     video_3s,
                     post_impressions_unique,
                     post_impressions_organic_unique,
                     post_impressions_paid_unique,
                     post_impressions,
                     post_impressions_organic,
                     post_impressions_paid,
                     post_engaged_users,
                     post_negative_feedback_unique,
                     post_negative_feedback,
                     like,
                     love,
                     sorry,
                     wow,
                     anger,
                     haha,           
                     post_clicks,
                     shares,
                     comments,
                     suma_reacciones,
                ]
            )
            item2+=1
            if item2==len(listacomer):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1EZf6n_ZBAd3dAh2x5vIGDovUynO38AUQ2Do60H667rE'
        subir_drive(listapub, hoja, name)
        
    if i==4:
        while item2 <= len(listaojo):
            if len(listaojo)==0:
                listaReach=[]
                break
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+listaojo[item2][0]+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks,post_video_views&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+listaojo[item2][0]+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+listaojo[item2][0]+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                post_impressions_unique=responseprueba_1["data"][0]["values"][0]["value"]
                post_impressions_organic_unique=responseprueba_1["data"][1]["values"][0]["value"]
                post_impressions_paid_unique=responseprueba_1["data"][2]["values"][0]["value"]
                post_impressions=responseprueba_1["data"][3]["values"][0]["value"]
                post_impressions_organic=responseprueba_1["data"][4]["values"][0]["value"]
                post_impressions_paid=responseprueba_1["data"][5]["values"][0]["value"]
                post_engaged_users=responseprueba_1["data"][6]["values"][0]["value"]
                post_negative_feedback_unique=responseprueba_1["data"][7]["values"][0]["value"]
                post_negative_feedback=responseprueba_1["data"][8]["values"][0]["value"]
                try:
                  anger=responseprueba_1["data"][9]["values"][0]["value"]["anger"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    anger=0
                
                try:
                  haha=responseprueba_1["data"][9]["values"][0]["value"]["haha"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla haha')  
                    haha=0
                    
                try:
                  like=responseprueba_1["data"][9]["values"][0]["value"]["like"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla like')  
                    like=0
                    
                try:
                  love=responseprueba_1["data"][9]["values"][0]["value"]["love"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla love')  
                    love=0
                 
                try:
                  sorry=responseprueba_1["data"][9]["values"][0]["value"]["sorry"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    sorry=0
                
                try:
                  wow=responseprueba_1["data"][9]["values"][0]["value"]["wow"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    wow=0
            
                post_clicks=responseprueba_1["data"][10]["values"][0]["value"]
                video_3s=responseprueba_1["data"][11]["values"][0]["value"]
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                    
                suma_reacciones= like+love+sorry+wow+anger+haha
                comments=responseprueba_3["summary"]["total_count"]
                
                                  
            except Exception as err:
                sendMail("[Facebook] I.Video c/uno",f"Ocurrio un error en la obtencion de indicadores por cada video :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=listaojo[item2][0]
            copy_22=listaojo[item2][1]
            try:
                  titulo22=listaojo[item2][2]
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     id_22,
                     copy_22,
                     titulo22,
                     video_3s,
                     post_impressions_unique,
                     post_impressions_organic_unique,
                     post_impressions_paid_unique,
                     post_impressions,
                     post_impressions_organic,
                     post_impressions_paid,
                     post_engaged_users,
                     post_negative_feedback_unique,
                     post_negative_feedback,
                     like,
                     love,
                     sorry,
                     wow,
                     anger,
                     haha,           
                     post_clicks,
                     shares,
                     comments,
                     suma_reacciones,
                ]
            )
            item2+=1
            if item2==len(listaojo):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1Y3Pzhf2MmMGq1HevPsJ1i_SIrubV0UOtOS32LfzPX3I'
        subir_drive(listapub, hoja, name)
        
    if i==6:
        while item2 <= len(listatrom):
            if len(listatrom)==0:
                listaReach=[]
                break
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+listatrom[item2][0]+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks,post_video_views&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+listatrom[item2][0]+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+listatrom[item2][0]+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                post_impressions_unique=responseprueba_1["data"][0]["values"][0]["value"]
                post_impressions_organic_unique=responseprueba_1["data"][1]["values"][0]["value"]
                post_impressions_paid_unique=responseprueba_1["data"][2]["values"][0]["value"]
                post_impressions=responseprueba_1["data"][3]["values"][0]["value"]
                post_impressions_organic=responseprueba_1["data"][4]["values"][0]["value"]
                post_impressions_paid=responseprueba_1["data"][5]["values"][0]["value"]
                post_engaged_users=responseprueba_1["data"][6]["values"][0]["value"]
                post_negative_feedback_unique=responseprueba_1["data"][7]["values"][0]["value"]
                post_negative_feedback=responseprueba_1["data"][8]["values"][0]["value"]
                try:
                  anger=responseprueba_1["data"][9]["values"][0]["value"]["anger"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    anger=0
                
                try:
                  haha=responseprueba_1["data"][9]["values"][0]["value"]["haha"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla haha')  
                    haha=0
                    
                try:
                  like=responseprueba_1["data"][9]["values"][0]["value"]["like"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla like')  
                    like=0
                    
                try:
                  love=responseprueba_1["data"][9]["values"][0]["value"]["love"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla love')  
                    love=0
                 
                try:
                  sorry=responseprueba_1["data"][9]["values"][0]["value"]["sorry"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    sorry=0
                
                try:
                  wow=responseprueba_1["data"][9]["values"][0]["value"]["wow"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    wow=0
            
                post_clicks=responseprueba_1["data"][10]["values"][0]["value"]
                video_3s=responseprueba_1["data"][11]["values"][0]["value"]
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                    
                suma_reacciones= like+love+sorry+wow+anger+haha
                comments=responseprueba_3["summary"]["total_count"]
                
                                  
            except Exception as err:
                sendMail("[Facebook] I.Video c/uno",f"Ocurrio un error en la obtencion de indicadores por cada video :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=listatrom[item2][0]
            copy_22=listatrom[item2][1]
            try:
                  titulo22=listatrom[item2][2]
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     id_22,
                     copy_22,
                     titulo22,
                     video_3s,
                     post_impressions_unique,
                     post_impressions_organic_unique,
                     post_impressions_paid_unique,
                     post_impressions,
                     post_impressions_organic,
                     post_impressions_paid,
                     post_engaged_users,
                     post_negative_feedback_unique,
                     post_negative_feedback,
                     like,
                     love,
                     sorry,
                     wow,
                     anger,
                     haha,           
                     post_clicks,
                     shares,
                     comments,
                     suma_reacciones,
                ]
            )
            item2+=1
            if item2==len(listatrom):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1HryQJuTJGjknueQJBoPlLOPD06nYXsurcYbwrh13CyI'
        subir_drive(listapub, hoja, name)
        
    if i==8:
        while item2 <= len(listadepo):
            if len(listadepo)==0:
                listaReach=[]
                break
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                responseprueba_4={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+listadepo[item2][0]+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks,post_video_views&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+listadepo[item2][0]+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+listadepo[item2][0]+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                post_impressions_unique=responseprueba_1["data"][0]["values"][0]["value"]
                post_impressions_organic_unique=responseprueba_1["data"][1]["values"][0]["value"]
                post_impressions_paid_unique=responseprueba_1["data"][2]["values"][0]["value"]
                post_impressions=responseprueba_1["data"][3]["values"][0]["value"]
                post_impressions_organic=responseprueba_1["data"][4]["values"][0]["value"]
                post_impressions_paid=responseprueba_1["data"][5]["values"][0]["value"]
                post_engaged_users=responseprueba_1["data"][6]["values"][0]["value"]
                post_negative_feedback_unique=responseprueba_1["data"][7]["values"][0]["value"]
                post_negative_feedback=responseprueba_1["data"][8]["values"][0]["value"]
                try:
                  anger=responseprueba_1["data"][9]["values"][0]["value"]["anger"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    anger=0
                
                try:
                  haha=responseprueba_1["data"][9]["values"][0]["value"]["haha"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla haha')  
                    haha=0
                    
                try:
                  like=responseprueba_1["data"][9]["values"][0]["value"]["like"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla like')  
                    like=0
                    
                try:
                  love=responseprueba_1["data"][9]["values"][0]["value"]["love"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla love')  
                    love=0
                 
                try:
                  sorry=responseprueba_1["data"][9]["values"][0]["value"]["sorry"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    sorry=0
                
                try:
                  wow=responseprueba_1["data"][9]["values"][0]["value"]["wow"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    wow=0
            
                post_clicks=responseprueba_1["data"][10]["values"][0]["value"]
                video_3s=responseprueba_1["data"][11]["values"][0]["value"]
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                    
                suma_reacciones= like+love+sorry+wow+anger+haha
                comments=responseprueba_3["summary"]["total_count"]
                
                                  
            except Exception as err:
                sendMail("[Facebook] I.Video c/uno",f"Ocurrio un error en la obtencion de indicadores por cada video :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=listadepo[item2][0]
            copy_22=listadepo[item2][1]
            try:
                  titulo22=listadepo[item2][2]
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     id_22,
                     copy_22,
                     titulo22,
                     video_3s,
                     post_impressions_unique,
                     post_impressions_organic_unique,
                     post_impressions_paid_unique,
                     post_impressions,
                     post_impressions_organic,
                     post_impressions_paid,
                     post_engaged_users,
                     post_negative_feedback_unique,
                     post_negative_feedback,
                     like,
                     love,
                     sorry,
                     wow,
                     anger,
                     haha,           
                     post_clicks,
                     shares,
                     comments,
                     suma_reacciones,
                ]
            )
            item2+=1
            if item2==len(listadepo):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='15uPwjFRKItO27vUEUvFEyxnEnkvhgnXAyW4umrloorg'
        subir_drive(listapub, hoja, name)
        
    if i==9:
        while item2 <= len(listagest):
            if len(listagest)==0:
                listaReach=[]
                break
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+listagest[item2][0]+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks,post_video_views&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+listagest[item2][0]+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+listagest[item2][0]+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                post_impressions_unique=responseprueba_1["data"][0]["values"][0]["value"]
                post_impressions_organic_unique=responseprueba_1["data"][1]["values"][0]["value"]
                post_impressions_paid_unique=responseprueba_1["data"][2]["values"][0]["value"]
                post_impressions=responseprueba_1["data"][3]["values"][0]["value"]
                post_impressions_organic=responseprueba_1["data"][4]["values"][0]["value"]
                post_impressions_paid=responseprueba_1["data"][5]["values"][0]["value"]
                post_engaged_users=responseprueba_1["data"][6]["values"][0]["value"]
                post_negative_feedback_unique=responseprueba_1["data"][7]["values"][0]["value"]
                post_negative_feedback=responseprueba_1["data"][8]["values"][0]["value"]
                try:
                  anger=responseprueba_1["data"][9]["values"][0]["value"]["anger"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    anger=0
                
                try:
                  haha=responseprueba_1["data"][9]["values"][0]["value"]["haha"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla haha')  
                    haha=0
                    
                try:
                  like=responseprueba_1["data"][9]["values"][0]["value"]["like"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla like')  
                    like=0
                    
                try:
                  love=responseprueba_1["data"][9]["values"][0]["value"]["love"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla love')  
                    love=0
                 
                try:
                  sorry=responseprueba_1["data"][9]["values"][0]["value"]["sorry"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    sorry=0
                
                try:
                  wow=responseprueba_1["data"][9]["values"][0]["value"]["wow"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    wow=0
            
                post_clicks=responseprueba_1["data"][10]["values"][0]["value"]
                video_3s=responseprueba_1["data"][11]["values"][0]["value"]
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                    
                suma_reacciones= like+love+sorry+wow+anger+haha
                comments=responseprueba_3["summary"]["total_count"]
                
                                  
            except Exception as err:
                sendMail("[Facebook] I.Video c/uno",f"Ocurrio un error en la obtencion de indicadores por cada video :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=listagest[item2][0]
            copy_22=listagest[item2][1]
            
            try:
                  titulo22=listagest[item2][2]
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     id_22,
                     copy_22,
                     titulo22,
                     video_3s,
                     post_impressions_unique,
                     post_impressions_organic_unique,
                     post_impressions_paid_unique,
                     post_impressions,
                     post_impressions_organic,
                     post_impressions_paid,
                     post_engaged_users,
                     post_negative_feedback_unique,
                     post_negative_feedback,
                     like,
                     love,
                     sorry,
                     wow,
                     anger,
                     haha,           
                     post_clicks,
                     shares,
                     comments,
                     suma_reacciones,
                ]
            )
            item2+=1
            if item2==len(listagest):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1BL7f39mOBtlAL_cO52OgQtqAPfN3BcOtCWuHIiXfyV4'
        subir_drive(listapub, hoja, name)
        
    if i==10:
        while item2 <= len(listamag):
            if len(listamag)==0:
                listaReach=[]
                break
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+listamag[item2][0]+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks,post_video_views&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+listamag[item2][0]+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+listamag[item2][0]+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                post_impressions_unique=responseprueba_1["data"][0]["values"][0]["value"]
                post_impressions_organic_unique=responseprueba_1["data"][1]["values"][0]["value"]
                post_impressions_paid_unique=responseprueba_1["data"][2]["values"][0]["value"]
                post_impressions=responseprueba_1["data"][3]["values"][0]["value"]
                post_impressions_organic=responseprueba_1["data"][4]["values"][0]["value"]
                post_impressions_paid=responseprueba_1["data"][5]["values"][0]["value"]
                post_engaged_users=responseprueba_1["data"][6]["values"][0]["value"]
                post_negative_feedback_unique=responseprueba_1["data"][7]["values"][0]["value"]
                post_negative_feedback=responseprueba_1["data"][8]["values"][0]["value"]
                try:
                  anger=responseprueba_1["data"][9]["values"][0]["value"]["anger"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    anger=0
                
                try:
                  haha=responseprueba_1["data"][9]["values"][0]["value"]["haha"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla haha')  
                    haha=0
                    
                try:
                  like=responseprueba_1["data"][9]["values"][0]["value"]["like"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla like')  
                    like=0
                    
                try:
                  love=responseprueba_1["data"][9]["values"][0]["value"]["love"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla love')  
                    love=0
                 
                try:
                  sorry=responseprueba_1["data"][9]["values"][0]["value"]["sorry"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    sorry=0
                
                try:
                  wow=responseprueba_1["data"][9]["values"][0]["value"]["wow"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla sorry')  
                    wow=0
            
                post_clicks=responseprueba_1["data"][10]["values"][0]["value"]
                video_3s=responseprueba_1["data"][11]["values"][0]["value"]
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                    
                suma_reacciones= like+love+sorry+wow+anger+haha
                comments=responseprueba_3["summary"]["total_count"]
                
                                  
            except Exception as err:
                sendMail("[Facebook] I.Video c/uno",f"Ocurrio un error en la obtencion de indicadores por cada video :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=listamag[item2][0]
            copy_22=listamag[item2][1]
            try:
                  titulo22=listamag[item2][2]
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     id_22,
                     copy_22,
                     titulo22,
                     video_3s,
                     post_impressions_unique,
                     post_impressions_organic_unique,
                     post_impressions_paid_unique,
                     post_impressions,
                     post_impressions_organic,
                     post_impressions_paid,
                     post_engaged_users,
                     post_negative_feedback_unique,
                     post_negative_feedback,
                     like,
                     love,
                     sorry,
                     wow,
                     anger,
                     haha,           
                     post_clicks,
                     shares,
                     comments,
                     suma_reacciones,
                ]
            )
            item2+=1
            if item2==len(listamag):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1puOs2q2Gjs6I7IR7vfFsnvkY_Jo0Pr5Bi1fH0r9Tg_A'
        subir_drive(listapub, hoja, name)
    
    i+=1 
            

    






