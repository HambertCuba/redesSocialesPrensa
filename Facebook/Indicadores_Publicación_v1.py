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
import urllib.parse as urlparse
from urllib.parse import parse_qs
import urllib

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
PATH_LOG = '/home/ec2-pentaho/pentaho/unp/Facebook/publicacion/log/'
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
        JSON_FILE = '/home/ec2-pentaho/pentaho/unp/Facebook/publicacion/proceso/cmsproyecto-1610655853990-aa4048eb3551.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        CREDENCIALES = None
        CREDENCIALES = service_account.Credentials.from_service_account_file(
        JSON_FILE, scopes=SCOPES)
        # The ID and range of a sample spreadsheet.
        SPREADSHEET_ID = hoja #'1l8_KEVavN2Dz_aVC5CMEWAoWZJisgrfupHeAufkTrPI'
        RANGE_NAME = 'Indicadores_Publicación!A2'
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
        sendMail("[Facebook] I.Publicacion",f"Ocurrio un error en la carga de indicadores publicacion al sheet :" +name+ f" {err} ")
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


i=0
while i <= 10 :         
    time.sleep(2)
    token3 = resultadosprueba[i]['access_token']
    me3= resultadosprueba[i]['id']
    name=resultadosprueba[i]['name']
    item2=0
    listaReach=[]
    
    if i==0:
        while item2 <= len(owned_apps_p21):
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                responseprueba_4={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_p21[item2]['id']+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_p21[item2]['id']+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_p21[item2]['id']+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api4="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_p21[item2]['id']+'/attachments?access_token='+token3
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_4=requests.get(api4,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json() 
                responseprueba_4 = responseprueba_4.json() 
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
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                suma_reacciones= like+love+sorry+wow+anger+haha
                
                comments=responseprueba_3["summary"]["total_count"]
                try:
                    if responseprueba_4['data'][0]["target"] is None:
                        target=''
                        url_final=''
                    else:                       
                        target=responseprueba_4["data"][0]["target"]["url"]
                        parsed = urlparse.urlparse(target)
                        query_u=parse_qs(parsed.query)['u']
                        url = query_u[0]
                        r = requests.get(url, allow_redirects=True)
                        url_final=r.url
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_final=''
                  
                try:
                    if url_final=='':
                        directorio=''
                    else:                    
                      numero_1=url_final.find("pe/")+3
                      palabra_22=url_final[numero_1:]
                      numero_2=palabra_22.find("/")
                      directorio=palabra_22[0:numero_2]
                      directorio='/'+directorio+'/'
                except(ValueError,KeyError,ZeroDivisionError,NameError):  
                  directorio=''
                 
                try:
                    if url_final=='':
                        url_limpia=''
                    else:          
                        if url_final.find("noticia/")==-1:
                            numero_1=url_final.find("pe/")+2
                            numero_ref2=url_final.find("ecpm/")+5
                            url_limpia=url_final[numero_1:numero_ref2]
                        else:
                            numero_ref=url_final.find("noticia/")+8
                            numero_1=url_final.find("pe/")+2
                            url_limpia=url_final[numero_1:numero_ref]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_limpia=''
                  
            except Exception as err:
                sendMail("[Facebook] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=owned_apps_p21[item2]['id']
            try:
                  titulo22=owned_apps_p21[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     url_final,
                     url_limpia,
                     directorio,
                     id_22,
                     titulo22,
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
            if item2==len(owned_apps_p21):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='13RhYfyhCxN0dfGL_wPAkWO4fCrdQKycWEsKLV9azOPU'
        subir_drive(listapub, hoja, name)
        
        
    if i==1:
        while item2 <= len(owned_apps_correo):
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                responseprueba_4={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_correo[item2]['id']+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_correo[item2]['id']+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_correo[item2]['id']+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api4="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_correo[item2]['id']+'/attachments?access_token='+token3
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_4=requests.get(api4,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                responseprueba_4 = responseprueba_4.json()
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
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                    
                suma_reacciones= like+love+sorry+wow+anger+haha
                comments=responseprueba_3["summary"]["total_count"]
                
                try:
                    if responseprueba_4['data'][0]["target"] is None:
                        target=''
                        url_final=''
                    else:                       
                        target=responseprueba_4["data"][0]["target"]["url"]
                        parsed = urlparse.urlparse(target)
                        query_u=parse_qs(parsed.query)['u']
                        url = query_u[0]
                        r = requests.get(url, allow_redirects=True)
                        url_final=r.url
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_final=''
                
                try:
                    if url_final=='':
                        directorio=''
                    else:                    
                      numero_1=url_final.find("pe/")+3
                      palabra_22=url_final[numero_1:]
                      numero_2=palabra_22.find("/")
                      directorio=palabra_22[0:numero_2]
                      directorio='/'+directorio+'/'
                except(ValueError,KeyError,ZeroDivisionError,NameError):  
                  directorio=''
                 
                try:
                    if url_final=='':
                        url_limpia=''
                    else:          
                        if url_final.find("noticia/")==-1:
                            numero_1=url_final.find("pe/")+2
                            numero_ref2=url_final.find("ecpm/")+5
                            url_limpia=url_final[numero_1:numero_ref2]
                        else:
                            numero_ref=url_final.find("noticia/")+8
                            numero_1=url_final.find("pe/")+2
                            url_limpia=url_final[numero_1:numero_ref]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_limpia=''
                  
            except Exception as err:
                sendMail("[Facebook] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=owned_apps_correo[item2]['id']
            try:
                  titulo22=owned_apps_correo[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     url_final,
                     url_limpia,
                     directorio,
                     id_22,
                     titulo22,
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
            if item2==len(owned_apps_correo):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1QwMtFHD1i2Jlgx0opwrXOaaZw6imrKnyI0EPxa7Tkw8'
        subir_drive(listapub, hoja, name)
    
    if i==2:
        while item2 <= len(owned_apps_bocon):
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                responseprueba_4={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_bocon[item2]['id']+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_bocon[item2]['id']+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_bocon[item2]['id']+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api4="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_bocon[item2]['id']+'/attachments?access_token='+token3
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_4=requests.get(api4,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                responseprueba_4 = responseprueba_4.json()
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
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                suma_reacciones= like+love+sorry+wow+anger+haha    
                comments=responseprueba_3["summary"]["total_count"]
                try:
                    if responseprueba_4['data'][0]["target"] is None:
                        target=''
                        url_final=''
                    else:                       
                        target=responseprueba_4["data"][0]["target"]["url"]
                        parsed = urlparse.urlparse(target)
                        query_u=parse_qs(parsed.query)['u']
                        url = query_u[0]
                        r = requests.get(url, allow_redirects=True)
                        url_final=r.url
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_final=''
                
                try:
                    if url_final=='':
                        directorio=''
                    else:                    
                      numero_1=url_final.find("pe/")+3
                      palabra_22=url_final[numero_1:]
                      numero_2=palabra_22.find("/")
                      directorio=palabra_22[0:numero_2]
                      directorio='/'+directorio+'/'
                except(ValueError,KeyError,ZeroDivisionError,NameError):  
                  directorio=''
                 
                try:
                    if url_final=='':
                        url_limpia=''
                    else:          
                        if url_final.find("noticia/")==-1:
                            numero_1=url_final.find("pe/")+2
                            numero_ref2=url_final.find("ecpm/")+5
                            url_limpia=url_final[numero_1:numero_ref2]
                        else:
                            numero_ref=url_final.find("noticia/")+8
                            numero_1=url_final.find("pe/")+2
                            url_limpia=url_final[numero_1:numero_ref]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_limpia=''
            
            except Exception as err:
                sendMail("[Facebook] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=owned_apps_bocon[item2]['id']
            try:
                  titulo22=owned_apps_bocon[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     url_final,
                     url_limpia,
                     directorio,
                     id_22,
                     titulo22,
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
            if item2==len(owned_apps_bocon):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1HkVudTW_bTxNhYgDGtstoIokne6KGiDutrGUAlixEeU'
        subir_drive(listapub, hoja, name)
        
    if i==3:
        while item2 <= len(owned_apps_com):
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                responseprueba_4={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_com[item2]['id']+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_com[item2]['id']+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_com[item2]['id']+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api4="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_com[item2]['id']+'/attachments?access_token='+token3
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_4=requests.get(api4,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json() 
                responseprueba_4 = responseprueba_4.json()
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
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                suma_reacciones= like+love+sorry+wow+anger+haha    
                comments=responseprueba_3["summary"]["total_count"]
                
                try:
                    if responseprueba_4['data'][0]["target"] is None:
                        target=''
                        url_final=''
                    else:                       
                        target=responseprueba_4["data"][0]["target"]["url"]
                        parsed = urlparse.urlparse(target)
                        query_u=parse_qs(parsed.query)['u']
                        url = query_u[0]
                        r = requests.get(url, allow_redirects=True)
                        url_final=r.url
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_final=''
                
                try:
                    if url_final=='':
                        directorio=''
                    else:                    
                      numero_1=url_final.find("pe/")+3
                      palabra_22=url_final[numero_1:]
                      numero_2=palabra_22.find("/")
                      directorio=palabra_22[0:numero_2]
                      directorio='/'+directorio+'/'
                except(ValueError,KeyError,ZeroDivisionError,NameError):  
                  directorio=''
                 
                try:
                    if url_final=='':
                        url_limpia=''
                    else:          
                        if url_final.find("noticia/")==-1:
                            numero_1=url_final.find("pe/")+2
                            numero_ref2=url_final.find("ecpm/")+5
                            url_limpia=url_final[numero_1:numero_ref2]
                        else:
                            numero_ref=url_final.find("noticia/")+8
                            numero_1=url_final.find("pe/")+2
                            url_limpia=url_final[numero_1:numero_ref]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_limpia=''
            
            except Exception as err:
                sendMail("[Facebook] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=owned_apps_com[item2]['id']
            try:
                  titulo22=owned_apps_com[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     url_final,
                     url_limpia,
                     directorio,
                     id_22,
                     titulo22,
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
            if item2==len(owned_apps_com):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1PzBtLx0CsJdjrYJxt9kDhQgkteYPwFFdodTNuRlrVrY'
        subir_drive(listapub, hoja, name)
        
    if i==4:
        while item2 <= len(owned_apps_ojo):
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                responseprueba_4={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_ojo[item2]['id']+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_ojo[item2]['id']+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_ojo[item2]['id']+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api4="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_ojo[item2]['id']+'/attachments?access_token='+token3
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_4=requests.get(api4,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                responseprueba_4 = responseprueba_4.json() 
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
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                suma_reacciones= like+love+sorry+wow+anger+haha    
                comments=responseprueba_3["summary"]["total_count"]
                
                try:
                    if responseprueba_4['data'][0]["target"] is None:
                        target=''
                        url_final=''
                    else:                       
                        target=responseprueba_4["data"][0]["target"]["url"]
                        parsed = urlparse.urlparse(target)
                        query_u=parse_qs(parsed.query)['u']
                        url = query_u[0]
                        r = requests.get(url, allow_redirects=True)
                        url_final=r.url
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_final=''
                
                try:
                    if url_final=='':
                        directorio=''
                    else:                    
                      numero_1=url_final.find("pe/")+3
                      palabra_22=url_final[numero_1:]
                      numero_2=palabra_22.find("/")
                      directorio=palabra_22[0:numero_2]
                      directorio='/'+directorio+'/'
                except(ValueError,KeyError,ZeroDivisionError,NameError):  
                  directorio=''
                 
                try:
                    if url_final=='':
                        url_limpia=''
                    else:          
                        if url_final.find("noticia/")==-1:
                            numero_1=url_final.find("pe/")+2
                            numero_ref2=url_final.find("ecpm/")+5
                            url_limpia=url_final[numero_1:numero_ref2]
                        else:
                            numero_ref=url_final.find("noticia/")+8
                            numero_1=url_final.find("pe/")+2
                            url_limpia=url_final[numero_1:numero_ref]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_limpia=''
            
            except Exception as err:
                sendMail("[Facebook] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=owned_apps_ojo[item2]['id']
            try:
                  titulo22=owned_apps_ojo[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     url_final,
                     url_limpia,
                     directorio,
                     id_22,
                     titulo22,
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
            if item2==len(owned_apps_ojo):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1rwmermp9gUwICsQheOJIVmKqXZbOmkYA4XfHZ9vhEYs'
        subir_drive(listapub, hoja, name)
        
    if i==6:
        while item2 <= len(owned_apps_trome):
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                responseprueba_4={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_trome[item2]['id']+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_trome[item2]['id']+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_trome[item2]['id']+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api4="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_trome[item2]['id']+'/attachments?access_token='+token3
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_4=requests.get(api4,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                responseprueba_4 = responseprueba_4.json() 
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
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                suma_reacciones= like+love+sorry+wow+anger+haha    
                comments=responseprueba_3["summary"]["total_count"]
                
                try:
                    if responseprueba_4['data'][0]["target"] is None:
                        target=''
                        url_final=''
                    else:                       
                        target=responseprueba_4["data"][0]["target"]["url"]
                        parsed = urlparse.urlparse(target)
                        query_u=parse_qs(parsed.query)['u']
                        url = query_u[0]
                        r = requests.get(url, allow_redirects=True)
                        url_final=r.url
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_final=''
                
                try:
                    if url_final=='':
                        directorio=''
                    else:                    
                      numero_1=url_final.find("pe/")+3
                      palabra_22=url_final[numero_1:]
                      numero_2=palabra_22.find("/")
                      directorio=palabra_22[0:numero_2]
                      directorio='/'+directorio+'/'
                except(ValueError,KeyError,ZeroDivisionError,NameError):  
                  directorio=''
                 
                try:
                    if url_final=='':
                        url_limpia=''
                    else:          
                        if url_final.find("noticia/")==-1:
                            numero_1=url_final.find("pe/")+2
                            numero_ref2=url_final.find("ecpm/")+5
                            url_limpia=url_final[numero_1:numero_ref2]
                        else:
                            numero_ref=url_final.find("noticia/")+8
                            numero_1=url_final.find("pe/")+2
                            url_limpia=url_final[numero_1:numero_ref]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_limpia=''
            
            except Exception as err:
                sendMail("[Facebook] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=owned_apps_trome[item2]['id']
            try:
                  titulo22=owned_apps_trome[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     url_final,
                     url_limpia,
                     directorio,
                     id_22,
                     titulo22,
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
            if item2==len(owned_apps_trome):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='190W0NUSvRixX9pWyQjeJBBP9KBtCNLEciuC25Ifn7RE'
        subir_drive(listapub, hoja, name)
        
    if i==8:
        while item2 <= len(owned_apps_depor):
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                responseprueba_4={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_depor[item2]['id']+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_depor[item2]['id']+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_depor[item2]['id']+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api4="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_depor[item2]['id']+'/attachments?access_token='+token3
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_4=requests.get(api4,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json() 
                responseprueba_4 = responseprueba_4.json()
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
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                suma_reacciones= like+love+sorry+wow+anger+haha    
                comments=responseprueba_3["summary"]["total_count"]
                
                try:
                    if responseprueba_4['data'][0]["target"] is None:
                        target=''
                        url_final=''
                    else:                       
                        target=responseprueba_4["data"][0]["target"]["url"]
                        parsed = urlparse.urlparse(target)
                        query_u=parse_qs(parsed.query)['u']
                        url = query_u[0]
                        r = requests.get(url, allow_redirects=True)
                        url_final=r.url
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_final=''
                
                try:
                    if url_final=='':
                        directorio=''
                    else:                    
                      numero_1=url_final.find("pe/")+3
                      palabra_22=url_final[numero_1:]
                      numero_2=palabra_22.find("/")
                      directorio=palabra_22[0:numero_2]
                      directorio='/'+directorio+'/'
                except(ValueError,KeyError,ZeroDivisionError,NameError):  
                  directorio=''
                 
                try:
                    if url_final=='':
                        url_limpia=''
                    else:          
                        if url_final.find("noticia/")==-1:
                            numero_1=url_final.find("pe/")+2
                            numero_ref2=url_final.find("ecpm/")+5
                            url_limpia=url_final[numero_1:numero_ref2]
                        else:
                            numero_ref=url_final.find("noticia/")+8
                            numero_1=url_final.find("pe/")+2
                            url_limpia=url_final[numero_1:numero_ref]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_limpia=''
            
            except Exception as err:
                sendMail("[Facebook] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=owned_apps_depor[item2]['id']
            try:
                  titulo22=owned_apps_depor[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     url_final,
                     url_limpia,
                     directorio,
                     id_22,
                     titulo22,
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
            if item2==len(owned_apps_depor):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='15JTE1wDxosDL8HnO5kYJGzHhtTdG8uBYNiW4788-OyU'
        subir_drive(listapub, hoja, name)
        
    if i==9:
        while item2 <= len(owned_apps_gestion):
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                responseprueba_4={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_gestion[item2]['id']+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_gestion[item2]['id']+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_gestion[item2]['id']+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api4="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_gestion[item2]['id']+'/attachments?access_token='+token3
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_4=requests.get(api4,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json() 
                responseprueba_4 = responseprueba_4.json() 
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
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                suma_reacciones= like+love+sorry+wow+anger+haha    
                comments=responseprueba_3["summary"]["total_count"]
                
                try:
                    if responseprueba_4['data'][0]["target"] is None:
                        target=''
                        url_final=''
                    else:                       
                        target=responseprueba_4["data"][0]["target"]["url"]
                        parsed = urlparse.urlparse(target)
                        query_u=parse_qs(parsed.query)['u']
                        url = query_u[0]
                        r = requests.get(url, allow_redirects=True)
                        url_final=r.url
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_final=''
                
                try:
                    if url_final=='':
                        directorio=''
                    else:                    
                      numero_1=url_final.find("pe/")+3
                      palabra_22=url_final[numero_1:]
                      numero_2=palabra_22.find("/")
                      directorio=palabra_22[0:numero_2]
                      directorio='/'+directorio+'/'
                except(ValueError,KeyError,ZeroDivisionError,NameError):  
                  directorio=''
                 
                try:
                    if url_final=='':
                        url_limpia=''
                    else:          
                        if url_final.find("noticia/")==-1:
                            numero_1=url_final.find("pe/")+2
                            numero_ref2=url_final.find("ecpm/")+5
                            url_limpia=url_final[numero_1:numero_ref2]
                        else:
                            numero_ref=url_final.find("noticia/")+8
                            numero_1=url_final.find("pe/")+2
                            url_limpia=url_final[numero_1:numero_ref]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_limpia=''
            
            except Exception as err:
                sendMail("[Facebook] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=owned_apps_gestion[item2]['id']
            try:
                  titulo22=owned_apps_gestion[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     url_final,
                     url_limpia,
                     directorio,
                     id_22,
                     titulo22,
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
            if item2==len(owned_apps_gestion):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='10Oh63E69CGtcfYVFPb23UYN5o7Cg78YiGCIeZ-uEXVs'
        subir_drive(listapub, hoja, name)
        
    if i==10:
        while item2 <= len(owned_apps_mag):
            try:
                responseprueba_1={}
                responseprueba_2={}
                responseprueba_3={}
                responseprueba_4={}
                ##api3= "https://graph.facebook.com/"+'v10.0'+'/'+listatemp[item2]['id_pub']+'/insights/post_impressions_unique?access_token='+token3
                api=""
                api="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_mag[item2]['id']+'/insights?metric=post_impressions_unique,post_impressions_organic_unique,post_impressions_paid_unique,post_impressions,post_impressions_organic,post_impressions_paid,post_engaged_users,post_negative_feedback_unique,post_negative_feedback,post_reactions_by_type_total,post_clicks&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                #print(api)   
                api2="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_mag[item2]['id']+'?fields=permalink_url,shares&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api3="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_mag[item2]['id']+'/comments?summary=1&filter=stream&access_token='+token3+'&since='+fecha2+' 05:00:00&until='+fecha1+' 04:59:59'
                api4="https://graph.facebook.com/"+'v10.0'+'/'+owned_apps_mag[item2]['id']+'/attachments?access_token='+token3
                responseprueba_1=requests.get(api,
                                             stream=True,
                                             headers=headers3)
                responseprueba_2=requests.get(api2,
                                             stream=True,
                                             headers=headers3)
                responseprueba_3=requests.get(api3,
                                             stream=True,
                                             headers=headers3)
                responseprueba_4=requests.get(api4,
                                             stream=True,
                                             headers=headers3)
                responseprueba_1 = responseprueba_1.json()  
                responseprueba_2 = responseprueba_2.json() 
                responseprueba_3 = responseprueba_3.json()
                responseprueba_4 = responseprueba_4.json() 
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
                link_url=responseprueba_2["permalink_url"]
                
                try:
                  shares=responseprueba_2["shares"]["count"]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                    shares=0    
                suma_reacciones= like+love+sorry+wow+anger+haha    
                comments=responseprueba_3["summary"]["total_count"]
                
                try:
                    if responseprueba_4['data'][0]["target"] is None:
                        target=''
                        url_final=''
                    else:                       
                        target=responseprueba_4["data"][0]["target"]["url"]
                        parsed = urlparse.urlparse(target)
                        query_u=parse_qs(parsed.query)['u']
                        url = query_u[0]
                        r = requests.get(url, allow_redirects=True)
                        url_final=r.url
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_final=''
                
                try:
                    if url_final=='':
                        directorio=''
                    else:                    
                      numero_1=url_final.find("pe/")+3
                      palabra_22=url_final[numero_1:]
                      numero_2=palabra_22.find("/")
                      directorio=palabra_22[0:numero_2]
                      directorio='/'+directorio+'/'
                except(ValueError,KeyError,ZeroDivisionError,NameError):  
                  directorio=''
                 
                try:
                    if url_final=='':
                        url_limpia=''
                    else:          
                        if url_final.find("noticia/")==-1:
                            numero_1=url_final.find("pe/")+2
                            numero_ref2=url_final.find("ecpm/")+5
                            url_limpia=url_final[numero_1:numero_ref2]
                        else:
                            numero_ref=url_final.find("noticia/")+8
                            numero_1=url_final.find("pe/")+2
                            url_limpia=url_final[numero_1:numero_ref]
                except(ValueError,KeyError,ZeroDivisionError,NameError):
                  url_limpia=''
            
            except Exception as err:
                sendMail("[Facebook] I.Publicacion",f"Ocurrio un error en la obtencion de indicadores publicacion :"+name+ f" {err} ")
                logging.error(f"Ocurrio un error al consultar : {err}", exc_info=True)
                print(f'Other error occurred: {err}')  # Python 3.6
    
            # fechapub11=owned_apps_p21[item2]['created_time']
            # fechapub11=fechapub11.replace("T"," ")
            # fechapub11=fechapub11[0:19]
            id_22=owned_apps_mag[item2]['id']
            try:
                  titulo22=owned_apps_mag[item2]['message']
            except(ValueError,KeyError,ZeroDivisionError,NameError):
                    #print('falla anger')  
                  titulo22=''
            listaReach.append( ##formato para agregar a una lista de forma manual
                [
                     fecha2,
                     link_url,
                     url_final,
                     url_limpia,
                     directorio,
                     id_22,
                     titulo22,
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
            if item2==len(owned_apps_mag):
                print(item2)
                break
        listapub=[]
        listapub=[listaReach]
        hoja='1sNN8VJ57VLUmbmQ4eocaCxuWEATp_jWjgGtoPER9D0c'
        subir_drive(listapub, hoja, name)
    
    i+=1 
            

    






