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
from xhtml2pdf import pisa
import re

def login_general_page():
    if ("email_user" in session):
        return redirect(url_for("menu_apoderado"))
    return render_template("login_apoderado.html")

def login_general():
    data = request.form
    if Usuario.autenticar(data["email"],data["pass"]):
        session["email_user"]=data["email"]
        if "edit" in session:
            dir = session["edit"]
            return redirect("/editar/"+dir)
        return redirect(url_for("menu_apoderado"))
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
