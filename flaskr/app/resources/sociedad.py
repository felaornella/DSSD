from flask import Response,jsonify, render_template, request, session, url_for, flash ,send_file , make_response
import requests
from werkzeug.utils import redirect
import app.helpers.bonita as bonita
from app.models.sociedad import Sociedad
from app.models.socio import Socio
from app.models.usuario import Usuario
import os
import json
import app.drive.GoogleDriveFlask as GD
import base64
from pathlib import Path
import datetime
from cryptography.fernet import Fernet
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
    if (bonita.searchActivityByCase(soc.caseId) == None):
        flash("Paso el limite de tiempo para editar. Debe iniciar el proceo devuelta",category="error")
        return redirect(url_for("home"))
    
    socios= soc.socios
    aux=[]
    for soci in socios:
        aux.append({"porcentaje":soci.porcentaje, "nombreSocioNuevo":soci.nombre,"apellidoSocioNuevo":soci.apellido,'apoderado':soci.apoderado})
    #paises = requests.get("https://countriesnow.space/api/v0.1/countries/states").json()["data"]
    print(soc.estado)
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
    if (json.loads(data["socios"]).values().__len__()==0):
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
            print("cambio de archivo")
            #borrar file vieja
            file = request.files['estatuto']
            if file:
                filename = "estatuto_"+str(sociedad.id)+".pdf"# +"."+ file.filename.split(".")[-1]
                APP_ROOT = os.path.dirname(os.path.abspath(__file__))
                
                UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static','temp','estatutos')
                file.save(os.path.join(UPLOAD_FOLDER.replace("\\resources",""), filename))
                GD.subir_archivo("app/static/temp/estatutos/estatuto_"+str(sociedad.id)+".pdf",GD.folder_estatuto)
                # UPLOAD_FOLDER = url_for("static",filename= "")
                # file.save((UPLOAD_FOLDER+filename))
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
    paises= getPaises()["data"]
    #paises = requests.get("https://countriesnow.space/api/v0.1/countries/states").json()["data"]
    
    return render_template("form_sociedad_anonima.html",paises=paises)

def nueva():
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

def estampillar(): #soc_id
    token = heroku_log()
    token= json.loads(token.content.decode())["token"]
    
    #buscar socciedad
    soc_id= request.args.get("id_soc")
    soc= Sociedad.buscarSociedadPorId(soc_id)
    
    # buscar expendiente
    filename = "estatuto_"+str(soc_id)+".pdf"# +"."+ file.filename.split(".")[-1]
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static','temp', 'estatutos')
    path= (os.path.join(UPLOAD_FOLDER.replace("\\resources",""), filename))
    path2 = Path(path)
    if not path2.exists():
        GD.bajar_acrchivo_por_nombre("estatuto_"+id+'.pdf',"app/static/temp/estatutos/")
        if not path2.exists():
            print("no existe ni en drive")
            return jsonify({'msg':'Estatuto not found'}),404,{'ContentType':"application/json"}
    
    with open(path, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
        
    #print(encoded_string)
    # cargar datos de sociedad y expediente
    datos= {
        "numeroExpediente": str(soc.id),
        "file": encoded_string,
    }
    res =requests.post("https://dssd-estatuto.herokuapp.com/api/upload/file", data=datos, headers={"Authorization": "Bearer "+token})
    hash = res.json()["hash"]


    soc.hash = hash
    soc.save()
    
    return str(hash) #Response(status=200)
    

    
    

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

def login_general_page():
    if ("email_user" in session):
        return redirect(url_for("nueva_sa"))
    return render_template("login_apoderado.html")

def login_general():
    data = request.form
    if Usuario.autenticar(data["email"],data["pass"]):
        session["email_user"]=data["email"]
        if "edit" in session:
            dir = session["edit"]
            return redirect("/editar/"+dir)
        return redirect(url_for("nueva_sa"))
    else:
        flash("Usuario o contraseña incorrectos.",category="error")
        return redirect(url_for("login_apoderado"))


def register_general_page():
    if ("email_user" in session):
        return redirect(url_for("nueva_sa"))
    return render_template("register_apoderado.html")

def register_general():
    data = request.form
    if Usuario.crearNuevo(data["email"],data["pass"], data["nombre"], data["apellido"], data["dni"]) is not None:
        session["email_user"]=data["email"]
        return redirect(url_for("nueva_sa"))
    else:
        flash("Datos incorrectos.",category="error")
        return redirect(url_for("register_apoderado"))

hashnum= 968532556
def hashear(num): 
    return num
def deshashear(num):
    return num
    
def loginPage():
    if ("tipo_user" in session):
        if session["tipo_user"]==1:
            return redirect(url_for("menu_mesa_de_entrada"))
        elif session["tipo_user"]==2:
            return redirect(url_for("menu_area_de_legales"))
        else:
            logout()
    return render_template("login.html")


def logout_general():
    if session.get("email_user"):
        del session["email_user"]
    return redirect(url_for("login_apoderado"))

def logout():
    if session.get("id_usuario"):
        del session["tipo_user"]
        del session["id_usuario"]
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
        
        try:
            r= requests.get("http://localhost:8080/bonita/API/identity/role?f=name=gerencia",headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
            idGerencia=r.json()[0]["id"]
        except:
            print("no pude levantar el id de gerencia")    

        r = requests.get("http://localhost:8080/bonita/API/identity/user?f=userName=" + data["username"],headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
        idUser= r.json()[0]["id"]
        session["id_usuario"]=idUser
        r2 = requests.get("http://localhost:8080/bonita/API/identity/membership?f=user_id=" + idUser, headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
  
        mesaEntrada=False
        areaLegales=False
        gerencia=False
        for each in r2.json():
            if not mesaEntrada and each["role_id"]==idMesa:                
                mesaEntrada=True
            if not areaLegales and each["role_id"]==idLegales:
                areaLegales=True
            if not gerencia and each["role_id"]==idGerencia:
                gerencia=True
       
        if (mesaEntrada):
            session["tipo_user"]=1
            return redirect(url_for("menu_mesa_de_entrada"))
        elif areaLegales:
            session["tipo_user"]=2
            return redirect(url_for("menu_area_de_legales"))
        elif gerencia:
            session["tipo_user"]=3
            return redirect(url_for("menu_gerencia"))
        else:
            return redirect(url_for("login_page"))
    else:
        flash("Usuario desactivado.",category="error")
        return redirect(url_for("login_page"))

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
def vista_sociedad():
    # get hash from query param "hash"
    #print(request.full_path)
    # parse request.full_path to get hash
    hash = request.full_path.split("hash=")[-1]
    
    ## BUSCAR POR SOCIEDAD TODO
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

    filename = "estatuto_"+str(soc.id)+".pdf"# +"."+ file.filename.split(".")[-1]
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

    filename = "sociedad_"+str(soc.id)+".pdf"# +"."+ file.filename.split(".")[-1]
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
    
    # Si necesitas el estatuto usa el metodo obtener_estatuto, que te devuelve el file .
    # Aunque el estatuto es un pdf para mi tenes como que poner un link que te deje obtener el estatuto. Con la ruta 

    # Si necesitas el qr usa el metodo obtener_qr, que te devuelve el file de la imagen.
    
    
    # obtener_qr(soc.id)   HAY QUE VER QUE TE DEVUELVE Y SI TE SIRVE
   
    # Generar PDF con el estatuo y guardarlo esn static/temp/sociedades/sociedad_{hash}.pdf
    from io import BytesIO, StringIO
    from xhtml2pdf import pisa
    
    
    # Generate PDF from render template hola.html
     
    html = render_template('sociedad.html',sociedad=soc)
    
    result = open("app/static/temp/sociedades/sociedad_"+str(soc.id)+".pdf","w+b")

    pisa_status = pisa.CreatePDF(
            html,                # the HTML to convert
            dest=result)
    
    result.close()
    soc.estado= 5
    soc.save()
    # Generar carpeta virtual (Subir a drive)

# COMENTARIO TEMPORAL==============================
#    GD.subir_archivo("app/static/temp/sociedades/sociedad_"+str(soc.id)+".pdf",GD.folder_sociedades)
    # Version 2
    #pdf= None
    #GD.subir_archivo2("sociedad_"+soc.hash+".pdf",pdf,GD.folder_sociedades)
    # El pdf de la sociedad ya esta arriba en la nube 
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
