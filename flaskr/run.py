from app import create_app
from app.drive.GoogleDriveFlask import login 
if __name__ == "__main__":
    app = create_app()
    
    #lanzar para toda la red wifi
    #app.run(host='192.168.0.14', port=5000)
    #
    # =============================NO FUNCIONA =============================
    #    login()
    #lanzar local
    app.run()