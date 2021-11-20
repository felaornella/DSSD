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

def nuevaPag():
    paises= getPaises()["data"]
    #paises = requests.get("https://countriesnow.space/api/v0.1/countries/states").json()["data"]
    
    return render_template("form_sociedad_anonima.html",paises=paises)

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
        filename = "estatuto_"+str(sociedad.id)+".pdf"# +"."+ file.filename.split(".")[-1]
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        
        UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static','temp','estatutos')
        file.save(os.path.join(UPLOAD_FOLDER.replace("\\resources",""), filename))
        GD.subir_archivo("app/static/temp/estatutos/estatuto_"+str(sociedad.id)+".pdf",GD.folder_estatuto)
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

def login_general_page():
    if ("email_user" in session):
        return redirect(url_for("nueva_sa"))
    return render_template("login_apoderado.html")

def login_general():
    data = request.form
    if Usuario.autenticar(data["email"],data["pass"]):
        session["email_user"]=data["email"]
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
        temp=[]
        for each in session:
            temp.append(each)
        for each in temp:
            if each != "_permanent":
                del session[each]
    return redirect(url_for("login_apoderado"))
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
def vista_sociedad(hash):
    ## BUSCAR POR SOCIEDAD TODO
    soc= Sociedad.buscarSociedadPorId(hash)
    if soc is None:
        flash("Sociedad no encontrada",category="error")
        return redirect(url_for("home"))

    return render_template("sociedad.html",sociedad=soc)
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
    

    # Generar carpeta virtual (Subir a drive)
    GD.subir_archivo("app/static/temp/sociedades/sociedad_"+str(soc.id)+".pdf",GD.folder_sociedades)
    # Version 2
    #pdf= None
    #GD.subir_archivo2("sociedad_"+soc.hash+".pdf",pdf,GD.folder_sociedades)
    # El pdf de la sociedad ya esta arriba en la nube 
    return jsonify({'msg':'Carpeta virtual creada'}),200,{'ContentType':"application/json"}


