import qrcode
from pathlib import Path
from flask import jsonify, send_file
import app.drive.GoogleDriveFlask as GD
from app.models.sociedad import Sociedad

def generar_qr(id):
    soc= Sociedad.buscarSociedadPorId(id)
    if soc is None or soc.hash is None:
        return jsonify({'msg':'Sociedad no encontrada'}),404,{'ContentType':"application/json"}
    
    # Get qr from the api 
    url = "localhost:5000/sociedad?hash="+str(soc.hash)  # Url de la sociedad que se va a mostrar
    # Find if the qr exists in app/static/qr/ 
    qr_path = Path("app/static/temp/qr/qr_"+str(soc.id)+'.png')
    if not qr_path.exists():
        print("no existe se crea y se guarda en drive")
        img = qrcode.make(url)
        img.save('app/static/temp/qr/qr_'+str(soc.id)+'.png')
        GD.subir_archivo("app/static/temp/qr/qr_"+str(soc.id)+".png",GD.folder_qr)
    else:
        print("existe") 
        
    # Return 200 OK
    return jsonify({'msg':'Creado'}),200,{'ContentType':"application/json"}

def obtener_qr(id):
    
    qr_path = Path("app/static/temp/qr/qr_"+str(id)+'.png')
    if not qr_path.exists():
        print("no existe - lo busca en drive")
        GD.bajar_acrchivo_por_nombre("qr_"+str(id)+'.png',"app/static/temp/qr/")
        # Return error "file not found" 
        if not qr_path.exists():
            print("no existe ni en drive")
            return jsonify({'msg':'File not found'}),404,{'ContentType':"application/json"}
    
    return send_file('static\\temp\\qr\\qr_'+str(id)+'.png', mimetype='image/png')
