from flask import Response,jsonify, render_template, request, session, url_for, flash 
import requests
from werkzeug.utils import redirect
import app.helpers.bonita as bonita
from app.models.sociedad import Sociedad
from app.models.socio import Socio
import os
import json


def nuevaPag():
    paises = requests.get("https://countriesnow.space/api/v0.1/countries/states").json()["data"]

    nomPaises=[]

    for each in paises:
        nomPaises.append(each["name"])

    nomPaises.sort()
   
    return render_template("form_sociedad_anonima.html",paises=nomPaises)

def nueva():
    data= request.form.to_dict()
    file= request.files['estatuto']

    
    sociedad = Sociedad(data["nombreSociedad"],data["fechaCreacion"],data["domicilioLegal"],data["domicilioReal"],data["email"],data["paisesExpo"],"Esperando Confirmacion")

    
    # print(dict(data["socios"]))

    for each in json.loads(data["socios"]).values():
        print(each)
        soc = Socio(each["nombre"],each["apellido"],each["porcentaje"],each["apoderado"])
        sociedad.socios.append(soc)


    bonita.autenticion('solicitante.general','solicitante')
    idProc= bonita.getProcessId("DSSD - Proceso de Registro de SA")
    caseId= bonita.initiateProcess(idProc)
    sociedad.caseId=caseId
    
    sociedad.save()
    #print(sociedad.id)
    file = request.files['estatuto']
    if file:
        filename = "estatuto"+str(sociedad.id)# +"."+ file.filename.split(".")[-1]
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        
        UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static')
        file.save(os.path.join(UPLOAD_FOLDER.replace("\\resources",""), filename))
        # UPLOAD_FOLDER = url_for("static",filename= "")
        # file.save((UPLOAD_FOLDER+filename))
        
    bonita.setVariable(caseId,"emailApoderado",sociedad.correoApoderado,"java.lang.String")
    bonita.setVariable(caseId,"idSolicitud",sociedad.id,"java.lang.String")
    
    return Response(status=200)

def estampillar(): #soc_id
    token = heroku_log()
    token= json.loads(token.content.decode())["token"]
    
    #buscar socciedad
    soc_id= request.args.get("id_soc")
    soc= Sociedad.buscarSociedadPorId(soc_id)
    
    # buscar expendiente
    filename = "estatuto"+str(soc_id)+".pdf"# +"."+ file.filename.split(".")[-1]
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static')
    path= (os.path.join(UPLOAD_FOLDER.replace("\\resources",""), filename))
    import base64
    with open(path, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
        
    print(encoded_string)
    # cargar datos de sociedad y expediente
    datos= {
    "numeroExpediente": str(soc.id),
    "file": encoded_string,
    }
    res =requests.post("https://dssd-estatuto.herokuapp.com/api/upload/file", data=datos, headers={"Authorization": "Bearer "+token})
    hash = res.json()["hash"]


    soc.hash = hash
    soc.save()
    
    return jsonify({'hash':hash}),200,{'ContentType':"application/json"} #Response(status=200)
    

    
    

def heroku_log():
    datos={"email":"nahuel_bigu@gmail.com","password":"asd123"}
    token=requests.post("https://dssd-estatuto.herokuapp.com/api/users/signin",data= datos)
    return token
    
def guardarEnBonita(id,emailApoderado):
    
    bonita.autenticion('solicitante.general','solicitante')
    idProc= bonita.getProcessId("DSSD - Proceso de Registro de SA")
    caseId= bonita.initiateProcess(idProc)
   
    bonita.setVariable(caseId,"emailApoderado",emailApoderado,"java.lang.String")
    bonita.setVariable(caseId,"idSolicitud",id,"java.lang.String")

    
    return caseId
    #activityId= bonita.searchActivityByCase(caseId)
    
    #bonita.assignTask(activityId,"4")
    #bonita.completeActivity(activityId)
    #return jsonify({'msg':'Creado'}),200,{'ContentType':"application/json"}


def loginPage():
    if ("tipo_user" in session):
        if session["tipo_user"]==1:
            return redirect(url_for("menu_mesa_de_entrada"))
        elif session["tipo_user"]==2:
            return redirect(url_for("menu_area_de_legales"))
        else:
            logout()
    return render_template("login.html")

def logout():
    if session.get("id_usuario"):
        temp=[]
        for each in session:
            temp.append(each)
        for each in temp:
            if each != "_permanent":
                del session[each]
    return redirect(url_for("login_page"))

def login():
    data = request.form
    if bonita.autenticion(data["username"],data["password"]):
        try:
            r= requests.get("http://localhost:8080/bonita/API/identity/role?f=name=MesaDeEntrada",headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
            idMesa=r.json()[0]["id"]
        except:
            print("no pude levantar el id de mesa de entrada")

        try:
            r= requests.get("http://localhost:8080/bonita/API/identity/role?f=name=AreaDeLegales",headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
            idLegales=r.json()[0]["id"]
        except:
            print("no pude levantar el id de area legales")

        r = requests.get("http://localhost:8080/bonita/API/identity/user?f=userName=" + data["username"],headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
        idUser= r.json()[0]["id"]
        session["id_usuario"]=idUser
        r2 = requests.get("http://localhost:8080/bonita/API/identity/membership?f=user_id=" + idUser, headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
  
        mesaEntrada=False
        areaLegales=False
        for each in r2.json():
            if not mesaEntrada and each["role_id"]==idMesa:                
                mesaEntrada=True
            if not areaLegales and each["role_id"]==idLegales:
                areaLegales=True
       
        if (mesaEntrada):
            session["tipo_user"]=1
            return redirect(url_for("menu_mesa_de_entrada"))
        elif areaLegales:
            session["tipo_user"]=2
            return redirect(url_for("menu_area_de_legales"))
        else:
            return redirect(url_for("login_page"))
    else:
        flash("Usuario desactivado.",category="error")
        return redirect(url_for("login_page"))

def menu_mesaEntrada():
    if (not "tipo_user" in session or not "id_usuario" in session or session["tipo_user"]!=1):
        return redirect(url_for("login_page"))
    return render_template("menu_mesa_de_entrada.html")

def menu_legales():
    if (not "tipo_user" in session or not "id_usuario" in session or session["tipo_user"]!=2):
        return redirect(url_for("login_page"))
    return render_template("menu_area_de_legales.html")

def evaluar_solicitudes():
    if (not "tipo_user" in session or not "id_usuario" in session or session["tipo_user"]!=1):
        return redirect(url_for("login_page"))

    

    socis= Sociedad.all()
    sociedades=[]
    for each in socis:
        if(each.estado=="Esperando Confirmacion"):
            soci={}
            soci["sociedad"]=each
            soci["paises"]=each.paises.split(",")
            sociedades.append(soci)
    return render_template("evaluar_solicitudes.html",sociedades=sociedades)


def rechazar_solicitud():
    data= request.get_json(force=True)


    socis= Sociedad.buscarSociedadPorId(data["solicitudId"])
    socis.estado="Esperando Correccion"
    socis.save()
    activityId= bonita.searchActivityByCase(socis.caseId)

    bonita.setVariable(socis.caseId,"solicitudValido","false","java.lang.Boolean")
    bonita.setVariable(socis.caseId,"comentarios",data["comentario"],"java.lang.String")

    bonita.assignTask(activityId,session["id_usuario"])
    bonita.completeActivity(activityId)
    return jsonify({'msg':'Creado'}),200,{'ContentType':"application/json"}


def aceptar_solicitud():
    data= request.get_json(force=True)
    socis= Sociedad.buscarSociedadPorId(data["solicitudId"])
    socis.estado="Esperando Evaluacion Estatuto"
    socis.save()
    activityId= bonita.searchActivityByCase(socis.caseId)
    bonita.setVariable(socis.caseId,"solicitudValido","true","java.lang.Boolean")
    bonita.assignTask(activityId,session["id_usuario"])
    bonita.completeActivity(activityId)
    return jsonify({'msg':'Creado'}),200,{'ContentType':"application/json"}
    
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




    