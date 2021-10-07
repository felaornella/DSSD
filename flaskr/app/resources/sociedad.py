from flask import Response,jsonify, render_template, request
import requests
from werkzeug.utils import redirect
import app.helpers.bonita as bonita
from app.models.sociedad import Sociedad
from app.models.socio import Socio

def nuevaPag():
    paises = requests.get("https://countriesnow.space/api/v0.1/countries/states").json()["data"]

    nomPaises=[]

    for each in paises:
        nomPaises.append(each["name"])

    nomPaises.sort()
   
    return render_template("form_sociedad_anonima.html",paises=nomPaises)

def nueva():
    data= request.get_json(force=True)
    
    sociedad = Sociedad(data["nombreSociedad"],data["fechaCreacion"],data["domicilioLegal"],data["domicilioReal"],data["emailApoderado"],data["paisesExportacion"])

    print(data["socios"])

    for each in data["socios"]:
        soc = Socio(data["socios"][each]["nombre"],data["socios"][each]["apellido"],data["socios"][each]["porcentaje"],data["socios"][each]["apoderado"])
        sociedad.socios.append(soc)

    sociedad.save()
    print(sociedad.id)
    guardarEnBonita(sociedad.id,sociedad.correoApoderado)
    return Response(status=200)

def guardarEnBonita(id,emailApoderado):
    
    bonita.autenticion('walter.bates','bpm')
    idProc= bonita.getProcessId("DSSD - Proceso de Registro de SA")
    caseId= bonita.initiateProcess(idProc)

    bonita.setVariable(caseId,"emailApoderado",emailApoderado,"java.lang.String")
    bonita.setVariable(caseId,"idSolicitud",id,"java.lang.String")

    activityId= bonita.searchActivityByCase(caseId)
    
    bonita.assignTask(activityId,"4")
    #bonita.completeActivity(activityId)
    return jsonify({'msg':'Creado'}),200,{'ContentType':"application/json"}


def loginPage():
    return render_template("login.html")

def login():
    data = request.form
    if bonita.autenticion(data["username"],data["password"]):
        #ver tipo de usuario y redireccionar
        return Response(status=200)
    else:
        return jsonify({'msg':'Los datos ingresados son incorrectos'}),400,{'ContentType':'application-json'}

# Authenticate to Bonita
# To log in, use the following request:
# Request URL
# http://host:port/bonita/loginservice
# Request Method
# POST
# Content-Type
# application/x-www-form-urlencoded
# Form Data
# username: a username
# password: a password
# redirect: true or false. false is the default value if the redirect parameter is not specified. It indicates that the service should not redirect to Bonita Applications (after a successful login) or to the login page (after a login failure).
# redirectUrl: the URL of the page to be displayed after a succesful login. If it is specified, then the a redirection after the login will be performed even if the "redirect" parameter is not present in the request.
# tenant: the tenant to log in to (optional for Enterprise and Performance editions, not supported for Community, Teamwork and Efficiency editions)