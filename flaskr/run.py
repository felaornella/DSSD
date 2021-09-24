from app import create_app

if __name__ == "__main__":
    app = create_app()
    
    #lanzar para toda la red wifi
    #app.run(host='192.168.0.14', port=5000)

    #lanzar local
    app.run()