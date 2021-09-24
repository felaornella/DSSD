from flask import render_template,redirect, url_for


def not_found_error(e):
    kwargs = {
        "error_name": "404 Not Found Error",
        "error_description": "La url a la que quiere acceder no existe",
    }
    return render_template("error.html", **kwargs), 404
    #return redirect(url_for("usuario_login"))


def unauthorized_error(e):
    kwargs = {
        "error_name": "401 Unauthorized Error",
        "error_description": "No está autorizado para acceder a la url",
    }
    return render_template("error.html", **kwargs), 401
    #return redirect(url_for("alumno_login"))



