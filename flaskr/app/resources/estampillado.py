from flask import jsonify, request
import requests
from app.models.sociedad import Sociedad
import os
import json
import app.drive.GoogleDriveFlask as GD
import base64
from pathlib import Path


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