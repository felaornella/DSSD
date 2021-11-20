from flask import Response,jsonify, render_template, request, session, url_for, flash ,send_file , make_response
import requests
from werkzeug.utils import redirect
import app.helpers.bonita as bonita
from app.models.sociedad import Sociedad
import json

def getContinentes():
    #With GraphQL
    url = "https://countries.trevorblades.com/"

    payload = json.dumps({
    "query": "{ continents  {  	code,  	name }}"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload).json()
    
    return response

def get_estadisticas_paises():
    # Get estadisticas de paises de la sociedades
    sociedades = Sociedad.all()
    paises_estadisticas = {}
    continentes_estadisticas = {}
    for sociedad in sociedades:
        #Parse sociedad.pais ,split by ,
        paises = sociedad.paises.split(',')
        for pais in paises:
            continente = pais.split('(')[1].split(')')[0]
            if continente in continentes_estadisticas:
                continentes_estadisticas[continente] += 1
            else:
                continentes_estadisticas[continente] = 1
            
            if pais in paises_estadisticas:
                paises_estadisticas[pais] += 1
            else:
                paises_estadisticas[pais] = 1
    
    # Order by value paises_estadisticas
    paises_estadisticas = sorted(paises_estadisticas.items(), key=lambda x: x[1], reverse=True)
    # Order by value continentes_estadisticas
    
    continentes = getContinentes()['data']
    
    continentes_estadisticas2={}
    # Remplace code from continentes_estadisticas with name from continentes
    for code,cant in continentes_estadisticas.items():
        for cont in continentes['continents']:
            if code == cont['code']:
                continentes_estadisticas2[cont['name']] = cant
   
    continentes_estadisticas = sorted(continentes_estadisticas2.items(), key=lambda x: x[1], reverse=True)
    return render_template('estadisticas.html', paises_estadisticas=paises_estadisticas, continentes_estadisticas=continentes_estadisticas)
    # Get estadisticas de paises de la sociedades

def get_metricas():
    cant_fallidos=0
    cant_activos=0
    activitys= bonita.getAllActivity()
    # count cant in array json from getAllCasesFinalizados
    cant_finalizados= len(bonita.getAllCasesFinalizados())

    # Analyze activitys and get metrics.
    # Count how much activitys have each type (from value displayName)
    metrics={}
    for activity in activitys:
        if activity['state'] == 'failed':
            cant_fallidos += 1
        else:
            cant_activos += 1

        if activity['displayName'] in metrics:
            metrics[activity['displayName']] += 1
        else:
            metrics[activity['displayName']] = 1
    
    return render_template('metricas.html',cantidad_procesos_activos=cant_activos,cantidad_procesos_fallidos=cant_fallidos, cantidad_procesos_finalizados=cant_finalizados,metrics=metrics.items())