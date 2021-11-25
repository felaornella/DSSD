import requests
from flask import session
def autenticion(usuario,contraseña):
    body = {'username':usuario, 'password':contraseña, 'redirect':'false'}
  
    res = requests.post('http://localhost:8080/bonita/loginservice', data=body,headers={"Content-Type" : "application/x-www-form-urlencoded"})
    if res.status_code==200:
        session["X-Bonita-API-Token"] = res.cookies.get('X-Bonita-API-Token')
        session["Cookies-bonita"] = "JSESSIONID="+res.cookies.get('JSESSIONID')+";X-Bonita-API-Token="+res.cookies.get('X-Bonita-API-Token')
        return True
    else:
        print("El codigo de error fue: " + str(res.status_code))
        return False

    #print(session["X-Bonita-API-Token"])
    
def getProcessId(nombreProceso):

    res = requests.get("http://localhost:8080/bonita/API/bpm/process", params={"s":nombreProceso} ,headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
    #print(res.json()[0]["id"])
   
    session["id-process"]=res.json()[0]["id"]
    return session["id-process"]


def setVariable(caseId,variable,valor,tipo):
    body= {"value":str(valor),"type":str(tipo)}
    res = requests.put("http://localhost:8080/bonita/API/bpm/caseVariable/"+str(caseId)+"/"+str(variable),json=body,headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
    print("Estado de set variable " + str(res.status_code))

def initiateProcess(idProc):
    res = requests.post("http://localhost:8080/bonita/API/bpm/process/"+idProc+"/instantiation", headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
    return res.json()["caseId"]


def searchActivityByCase(caseId):
    res= requests.get("http://localhost:8080/bonita/API/bpm/task", params={"f":"caseId="+str(caseId)} ,headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
    return res.json()[0]["id"]

def assignTask(activityId,idUser):
    body={"assigned_id": str(idUser) }
    res = requests.put("http://localhost:8080/bonita/API/bpm/userTask/"+str(activityId),json=body , headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
    # Print the status code of the response.
    print("Estado de asignacion " + str(res.status_code))

def completeActivity(activityId):
    res = requests.post("http://localhost:8080/bonita/API/bpm/userTask/"+str(activityId)+"/execution", headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
    print("Estado de ejecucion " + str(res.status_code))

def checkRole(role,idUser):
    r = requests.get("http://localhost:8080/bonita/API/identity/membership?f=user_id=" + idUser, headers={"X-Bonita-API-Token":session["X-Bonita-API-Token"],"Cookie":session["Cookies-bonita"]})
    tipo_user= r.json()
    for x in tipo_user:
        if (x["role_id"]==role):
            return True
    return False
    

def getAllActivity():
    body = {'username':"gerencia", 'password':"gerencia", 'redirect':'false'}
  
    res = requests.post('http://localhost:8080/bonita/loginservice', data=body,headers={"Content-Type" : "application/x-www-form-urlencoded"})
    if res.status_code==200:
        tokenbonita= res.cookies.get('X-Bonita-API-Token')
        cookiesbonita = "JSESSIONID="+res.cookies.get('JSESSIONID')+";X-Bonita-API-Token="+res.cookies.get('X-Bonita-API-Token')
        
        url = "http://localhost:8080/bonita/API/bpm/activity"

    
        res= requests.get(url, params={"o":"last_update_date"} ,headers={"X-Bonita-API-Token":tokenbonita,"Cookie":cookiesbonita})
    
        return res.json()
    return []

def getAllCasesFinalizados():
    body = {'username':"gerencia", 'password':"gerencia", 'redirect':'false'}
  
    res = requests.post('http://localhost:8080/bonita/loginservice', data=body,headers={"Content-Type" : "application/x-www-form-urlencoded"})
    if res.status_code==200:
        tokenbonita= res.cookies.get('X-Bonita-API-Token')
        cookiesbonita = "JSESSIONID="+res.cookies.get('JSESSIONID')+";X-Bonita-API-Token="+res.cookies.get('X-Bonita-API-Token')
        
        url = "http://localhost:8080/bonita/API/bpm/archivedCase?o"

    
        res= requests.get(url ,headers={"X-Bonita-API-Token":tokenbonita,"Cookie":cookiesbonita})
    
        return res.json()
    return []
    
def getAllActivityFinalizados():
    body = {'username':"gerencia", 'password':"gerencia", 'redirect':'false'}
  
    res = requests.post('http://localhost:8080/bonita/loginservice', data=body,headers={"Content-Type" : "application/x-www-form-urlencoded"})
    if res.status_code==200:
        tokenbonita= res.cookies.get('X-Bonita-API-Token')
        cookiesbonita = "JSESSIONID="+res.cookies.get('JSESSIONID')+";X-Bonita-API-Token="+res.cookies.get('X-Bonita-API-Token')
        
        url = "http://localhost:8080/bonita/API/bpm/archivedActivity?o=reached_state_date desc"

    
        res= requests.get(url ,headers={"X-Bonita-API-Token":tokenbonita,"Cookie":cookiesbonita})
        
        return res.json()
    return []
