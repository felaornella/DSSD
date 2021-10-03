from flask import Response,jsonify, render_template
import requests

def nuevaPag():
    paises = requests.get("https://countriesnow.space/api/v0.1/countries/states").json()["data"]

    nomPaises=[]

    for each in paises:
        nomPaises.append(each["name"])

    nomPaises.sort()
   
    return render_template("form_sociedad_anonima.html",paises=nomPaises)

def nueva():
    dictToSend = {'username':'walter.bates', 'password':'bpm'}
    res = requests.post('http://host:port/bonita/loginservice', json=dictToSend,headers={"Content-Type" : "application/x-www-form-urlencoded"})
    print ('response from server:',res.text)
    dictFromServer = res.json()

    # crear un case
    data={"processDefinitionId":"5777042023671752656",
        "variables":[
            {
            "name":"stringVariable",
            "value":"aValue"
            },
            {
            "name":"dateVariable",
            "value":349246800000
            },
            {
            "name":"numericVariable",
            "value":5
            }
        ]
    }
    res = requests.post('http://host:port/API/bpm/case',data=data)

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