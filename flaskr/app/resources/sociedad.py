from flask import Response,jsonify, render_template, request, session, url_for, flash ,send_file , make_response
import requests
from werkzeug.utils import redirect
import app.helpers.bonita as bonita
from app.models.sociedad import Sociedad
from app.models.socio import Socio
import os
import json
import app.drive.GoogleDriveFlask as GD
from pathlib import Path
from xhtml2pdf import pisa
import re

def home():
    return render_template("home.html")

def getPaises():
    #With GraphQL
    url = "https://countries.trevorblades.com/"

    payload = json.dumps({
    "query": "{ continents  {  	code,  	name,  countries{  name,    code  } }}"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload).json()
    
    return response


def editarPag(hash):

    if (not "email_user" in session):
        session["edit"]=hash
        return redirect(url_for("login_apoderado"))
    id= deshashear(int(hash))
    print(id)
    paises= getPaises()["data"]
    soc= Sociedad.buscarSociedadPorId(id)
    if not soc:
        return redirect(url_for("home"))
    if (session["email_user"] != soc.correoApoderado):
        flash("No tiene acceso para editar esto.",category="error")
        return redirect(url_for("home"))
    if (soc.estado!=1 and soc.estado!=3):
        flash("La sociedad esta en estado de evaluacion.",category="error")
        return redirect(url_for("home"))
    bonita.autenticion('solicitante.general','solicitante')
    if (bonita.searchActivityByCase(soc.caseId) == None):
        flash("Paso el limite de tiempo para editar. Debe iniciar el proceo devuelta",category="error")
        return redirect(url_for("home"))
    
    socios= soc.socios
    aux=[]
    for soci in socios:
        aux.append({"porcentaje":soci.porcentaje, "nombreSocioNuevo":soci.nombre,"apellidoSocioNuevo":soci.apellido,'apoderado':soci.apoderado})
    
    return render_template("form_edit_sociedad_anonima.html",estado=soc.estado,soc_id=hash,socios=aux,paises=paises,nombre=soc.nombre, fecha= soc.fechaCreacion,seleccionados=soc.paises.split(","),email= soc.correoApoderado, real=soc.domicilioReal, legal=soc.domicilioLegal)


def guardarEdicion(hash):
    
    if (not "email_user" in session):
        return redirect(url_for("login"))
    id= deshashear(int(hash))
    data= request.form.to_dict()
    if ("estatuto" in request.files):
        file= request.files['estatuto']
    else :
        file= None
    sociedad= Sociedad.buscarSociedadPorId(id)
    print(sociedad.estado)
    print(sociedad.estado!=1)
    print(sociedad.estado!=3)
    if (sociedad.estado!=1 and sociedad.estado!=3):
        return jsonify({'msg':'La sociedad esta en estado de evaluacion'}),400,{'ContentType':"application/json"}
    if (session["email_user"] != sociedad.correoApoderado):
        return jsonify({'msg':'No tenes acceso para editar esto'}),400,{'ContentType':"application/json"}
    #Buscar sociedad vieja y editarla
    print(json.loads(data["socios"]).values())
    # Check all fields are filled in data and return especific error if not
    if ("nombreSociedad" in data and data["nombreSociedad"] == ""):
        return jsonify({'msg':'El nombre de la sociedad es requerido'}),400,{'ContentType':"application/json"}
    if ("fechaCreacion" in data and  data["fechaCreacion"] == ""):
        return jsonify({'msg':'La fecha de creacion es requerida'}),400,{'ContentType':"application/json"}
    if ("domicilioLegal" in data and data["domicilioLegal"] == ""):
        return jsonify({'msg':'El domicilio legal es requerido'}),400,{'ContentType':"application/json"}
    if ("domicilioReal" in data and data["domicilioReal"] == ""):
        return jsonify({'msg':'El domicilio real es requerido'}),400,{'ContentType':"application/json"}
    # Check if email is valid with regex
    if ("email" in data and data["email"] == "" and  not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"])):
        return jsonify({'msg':'El email es requerido'}),400,{'ContentType':"application/json"}
    if ("socios" in data and json.loads(data["socios"]).values().__len__()==0):
        return jsonify({'msg':'No se puede guardar una sociedad sin socios'}),400,{'ContentType':"application/json"}
    if (sociedad.estado==1):
        sociedad.nombre =data["nombreSociedad"]
        sociedad.fechaCreacion =data["fechaCreacion"]
        sociedad.domicilioLegal =data["domicilioLegal"]
        sociedad.domicilioReal =data["domicilioReal"]
        sociedad.correoApoderado =data["email"]
        sociedad.paises =data["paisesExpo"]
        
        
        #eliminar socios
        for socio in sociedad.socios:
            socio.delete()
        for each in json.loads(data["socios"]).values():
            soc = Socio(each["nombre"],each["apellido"],each["porcentaje"],each["apoderado"])
            sociedad.socios.append(soc)
        
   

    if "edit" in session:
        del session["edit"]
    
    if (sociedad.estado==3):
        if file:
            #print("cambio de archivo")
            
            file = request.files['estatuto']
            if file:
                filename = "estatuto_"+str(sociedad.id)+".pdf"
                APP_ROOT = os.path.dirname(os.path.abspath(__file__))
                
                UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static','temp','estatutos')
                file.save(os.path.join(UPLOAD_FOLDER.replace("\\resources",""), filename))
                GD.subir_archivo("app/static/temp/estatutos/estatuto_"+str(sociedad.id)+".pdf",GD.folder_estatuto)
        else:
            return jsonify({'msg':'El estatuto es requerido'}),400,{'ContentType':"application/json"}  

      
    bonita.autenticion('solicitante.general','solicitante')
    r= requests.get("http://localhost:8080/bonita/API/identity/role?f=name=Solicitante",headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
    idSolic=r.json()[0]["id"]

    activityId= bonita.searchActivityByCase(sociedad.caseId)
    bonita.assignTask(activityId,idSolic)
    bonita.completeActivity(activityId)
    sociedad.estado = sociedad.estado - 1
    sociedad.save()
    return Response(status=200)


def nuevaPag():
    if (not "email_user" in session):
        return redirect(url_for("login"))
    paises= getPaises()["data"]
    
    return render_template("form_sociedad_anonima.html",paises=paises)

def nueva():
    if (not "email_user" in session):
        return redirect(url_for("login"))
    data= request.form.to_dict()

    
    if ("estatuto" in request.files and request.files['estatuto']):
        file= request.files['estatuto']
    else :
        return jsonify({'msg':'El estatuto es requerido'}),400,{'ContentType':"application/json"}
    # Check all fields are filled in data and return especific error if not
    if (data["nombreSociedad"] == ""):
        return jsonify({'msg':'El nombre de la sociedad es requerido'}),400,{'ContentType':"application/json"}
    if (data["fechaCreacion"] == ""):
        return jsonify({'msg':'La fecha de creacion es requerida'}),400,{'ContentType':"application/json"}
    if (data["domicilioLegal"] == ""):
        return jsonify({'msg':'El domicilio legal es requerido'}),400,{'ContentType':"application/json"}
    if (data["domicilioReal"] == ""):
        return jsonify({'msg':'El domicilio real es requerido'}),400,{'ContentType':"application/json"}
    # Check if email is valid with regex
    if (data["email"] == "" and  not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"])):
        return jsonify({'msg':'El email es requerido'}),400,{'ContentType':"application/json"}
    if (json.loads(data["socios"]).values().__len__()==0):
        return jsonify({'msg':'No se puede guardar una sociedad sin socios'}),400,{'ContentType':"application/json"}


    
    sociedad = Sociedad(data["nombreSociedad"],data["fechaCreacion"],data["domicilioLegal"],data["domicilioReal"],data["email"],data["paisesExpo"],0)
    if sociedad.paises == "":
        sociedad.paises = "Argentina(SA)" 
    
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
    
    if file:
        filename = "estatuto_"+str(sociedad.id)+".pdf"# +"."+ file.filename.split(".")[-1]
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        
        UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static','temp','estatutos')
        file.save(os.path.join(UPLOAD_FOLDER.replace("\\resources",""), filename))
        GD.subir_archivo("app/static/temp/estatutos/estatuto_"+str(sociedad.id)+".pdf",GD.folder_estatuto)

        
    bonita.setVariable(caseId,"emailApoderado",sociedad.correoApoderado,"java.lang.String")
    bonita.setVariable(caseId,"idSolicitud",sociedad.id,"java.lang.String")
    
    return Response(status=200)


hashnum= 968532556
def hashear(num): 
    return num
def deshashear(num):
    return num
    

def menu_apoderado():
    if (not "email_user" in session):
        return redirect(url_for("login_apoderado"))
    return render_template("menu_apoderado.html")

def menu_mesaEntrada():
    if (not "tipo_user" in session or not "id_usuario" in session or session["tipo_user"]!=1):
        return redirect(url_for("login_page"))
    
    sociedades= Sociedad.all()
    cant_listos=0
    cant_pendientes=0
    for each in sociedades:
        if each.estado==5:
            cant_listos+=1
        elif each.estado==0:
            cant_pendientes+=1
    return render_template("menu_mesa_de_entrada.html", cant_listos=cant_listos, cant_pendientes=cant_pendientes)

def menu_legales():
    if (not "tipo_user" in session or not "id_usuario" in session or session["tipo_user"]!=2):
        return redirect(url_for("login_page"))
    sociedades= Sociedad.all()
    cant_pendientes=0
    for each in sociedades:
        if each.estado==2:
            cant_pendientes+=1
    return render_template("menu_area_de_legales.html", cant_pendientes=cant_pendientes)


def menu_gerencia():
    if (not "tipo_user" in session or not "id_usuario" in session or session["tipo_user"]!=3):
        return redirect(url_for("login_page"))
    return render_template("menu_gerencia.html")


def evaluar_solicitudes():
    if (not "tipo_user" in session or not "id_usuario" in session or session["tipo_user"]!=1):
        return redirect(url_for("login_page"))
    socis= Sociedad.all()
    sociedades=[]
    for each in socis:
        if(each.estado==0):
            soci={}
            soci["sociedad"]=each
            soci["paises"]=each.paises.split(",")
            sociedades.append(soci)
    return render_template("evaluar_solicitudes.html",sociedades=sociedades)

def evaluar_estatutos():
    if (not "tipo_user" in session or not "id_usuario" in session or session["tipo_user"]!=2):
        return redirect(url_for("login_page"))
    socis= Sociedad.all()
    sociedades=[]
    for each in socis:
        if(each.estado==2):
            soci={}
            soci["sociedad"]=each
            soci["paises"]=each.paises.split(",")
            sociedades.append(soci)
    return render_template("evaluar_estatutos.html",sociedades=sociedades)

def rechazar_solicitud():
    data= request.get_json(force=True)


    socis= Sociedad.buscarSociedadPorId(data["solicitudId"])
    socis.estado=1
    socis.save()
    activityId= bonita.searchActivityByCase(socis.caseId)
    print("ActivityId : "+ str(activityId))
    bonita.setVariable(socis.caseId,"solicitudValido","false","java.lang.Boolean")
    bonita.setVariable(socis.caseId,"comentarios",data["comentario"],"java.lang.String")

    bonita.assignTask(activityId,session["id_usuario"])
    bonita.completeActivity(activityId)
    return jsonify({'msg':'Creado'}),200,{'ContentType':"application/json"}


def aceptar_solicitud():
    data= request.get_json(force=True)
    socis= Sociedad.buscarSociedadPorId(data["solicitudId"])
    socis.estado=2
    socis.save()
    activityId= bonita.searchActivityByCase(socis.caseId)
    bonita.setVariable(socis.caseId,"solicitudValido","true","java.lang.Boolean")
    bonita.assignTask(activityId,session["id_usuario"])
    bonita.completeActivity(activityId)
    return jsonify({'msg':'Creado'}),200,{'ContentType':"application/json"}

def rechazar_estatuto():
    data= request.get_json(force=True)

    socis= Sociedad.buscarSociedadPorId(data["solicitudId"])
    socis.estado=3
    socis.save()
    activityId= bonita.searchActivityByCase(socis.caseId)

    bonita.setVariable(socis.caseId,"estatutoValido","false","java.lang.Boolean")
    bonita.setVariable(socis.caseId,"comentarios",data["comentario"],"java.lang.String")

    bonita.assignTask(activityId,session["id_usuario"])
    bonita.completeActivity(activityId)
    return jsonify({'msg':'Creado'}),200,{'ContentType':"application/json"}


def aceptar_estatuto():
    data= request.get_json(force=True)
    socis= Sociedad.buscarSociedadPorId(data["solicitudId"])
    socis.estado=4
    socis.save()
    activityId= bonita.searchActivityByCase(socis.caseId)
    bonita.setVariable(socis.caseId,"estatutoValido","true","java.lang.Boolean")
    bonita.assignTask(activityId,session["id_usuario"])
    bonita.completeActivity(activityId)
    return jsonify({'msg':'Creado'}),200,{'ContentType':"application/json"}


def vista_sociedad():
    # parse request.full_path to get hash
    hash = request.full_path.split("hash=")[-1]
    
    soc= Sociedad.buscarSociedadPorHash(hash)
    if soc is None:
        flash("Sociedad no encontrada",category="error")
        return redirect(url_for("home"))

    return render_template("sociedad_vista.html",sociedad=soc)


def obtener_estatuo(id):
    soc= Sociedad.buscarSociedadPorId(id)
    if soc is None:
        flash("Sociedad no encontrada",category="error")
        return redirect(url_for("home"))

    filename = "estatuto_"+str(soc.id)+".pdf"
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static','temp', 'estatutos')
    path= os.path.join(UPLOAD_FOLDER.replace("\\resources",""), filename)
    print(path)
    qr_path = Path(path)
    if not qr_path.exists():
        GD.bajar_acrchivo_por_nombre("estatuto_"+str(soc.id)+'.pdf',"app/static/temp/estatutos/")
        if not qr_path.exists():
            print("no existe ni en drive")
            return jsonify({'msg':'Estatuto not found'}),404,{'ContentType':"application/json"}

    return send_file('static\\temp\\estatutos\\estatuto_'+str(soc.id)+'.pdf', mimetype='application/pdf')

def obtener_pdf_sociedad(id):
    soc= Sociedad.buscarSociedadPorId(id)
    if soc is None:
        flash("Sociedad no encontrada",category="error")
        return redirect(url_for("home"))

    filename = "sociedad_"+str(soc.id)+".pdf"
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static','temp', 'sociedades')
    path= os.path.join(UPLOAD_FOLDER.replace("\\resources",""), filename)
    qr_path = Path(path)
    if not qr_path.exists():
        GD.bajar_acrchivo_por_nombre("sociedad_"+str(soc.id)+'.pdf',"app/static/temp/sociedades/")
        if not qr_path.exists():
            print("no existe ni en drive")
            return jsonify({'msg':'Sociedad not found'}),404,{'ContentType':"application/json"}

    return send_file('static\\temp\\sociedades\\sociedad_'+str(soc.id)+'.pdf', mimetype='application/pdf')


def generar_carpeta_virtual(id):
    soc= Sociedad.buscarSociedadPorId(id)
    if soc is None:
        flash("Sociedad no encontrada",category="error")
        return redirect(url_for("home"))
    
   
    # Generar PDF con el estatuo y guardarlo esn static/temp/sociedades/sociedad_{id}.pdf
     
    html = render_template('sociedad.html',sociedad=soc)
    
    result = open("app/static/temp/sociedades/sociedad_"+str(soc.id)+".pdf","w+b")

    pisa_status = pisa.CreatePDF(
            html,                # the HTML to convert
            dest=result)
    
    result.close()
    soc.estado= 5
    soc.save()
    
    return jsonify({'msg':'Carpeta virtual creada'}),200,{'ContentType':"application/json"}

def generar_carpetas_fisicas():
    if (not "tipo_user" in session or not "id_usuario" in session or session["tipo_user"]!=1):
        return redirect(url_for("login_page"))
    socis= Sociedad.all()
    sociedades=[]
    for each in socis:
        if(each.estado==5):
            soci={}
            soci["sociedad"]=each
            soci["paises"]=each.paises.split(",")
            sociedades.append(soci)
    return render_template("generar_carpetas_fisica.html",sociedades=sociedades)

def generar_carpeta_fisica():
    if (not "tipo_user" in session or not "id_usuario" in session or session["tipo_user"]!=1):
        return redirect(url_for("login_page"))
    data= request.get_json(force=True)
    socis= Sociedad.buscarSociedadPorId(data["solicitudId"])
    socis.estado=10
    socis.save()
    activityId= bonita.searchActivityByCase(socis.caseId)
    bonita.assignTask(activityId,session["id_usuario"])
    bonita.completeActivity(activityId)
    return jsonify({'msg':'Creado'}),200,{'ContentType':"application/json"}
