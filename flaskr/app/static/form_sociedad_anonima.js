var listadoSocios = $("#bloqueListado")

$("#buttonAddSocioNuevo").on("click",agregarSocio)


function agregarSocio() {
    var nombre = $("#apellidoSocioNuevo").val().trim() + ", " + $("#nombreSocioNuevo").val().trim()
    var porcentaje = $("#porcentaje").val()

    var socio = document.createElement("p")
    socio.innerText= nombre + " - " + porcentaje + "%"
    socio.setAttribute("margin-top","auto")
    socio.setAttribute("margin-bottom","auto")
    socio.setAttribute("font-size","1.25rem")


    var colSocio= document.createElement("div")
    colSocio.setAttribute("class","col-8")
    colSocio.setAttribute("style","text-align:center")
    
    var colButton= document.createElement("div")
    colButton.setAttribute("class","col-4")
    
    var button= document.createElement("button")
    button.innerText="X"
    button.setAttribute("class","btn btn-outline-danger")
    
    colButton.appendChild(button)
    colSocio.appendChild(socio)
    
    var socioEntero = document.createElement("div")
    socioEntero.appendChild(colSocio)
    socioEntero.appendChild(colButton)

    listadoSocios.prepend(socioEntero)
}

function setPaises() {
    $.get({
        url: "https://api.first.org/data/v1/countries",
        success: function (response) {

            for (var [key, valueC] of response["data"]) {
                if (key == "AR") {
                    $("#paisesExportacion").append($('<option>', {
                        value: key,
                        text: valueC["country"],
                        selected: true
                    }));
                } else {
                    $("#paisesExportacion").append($('<option>', {
                        value: key,
                        text: valueC["country"]
                    }));

                    alert(key + " = " + value["country"]);
                }
            }
        },
        error: function (response) {
            Toast.fire({
                icon: 'error',
                title: response.responseJSON.msg
            })
        }
    })
}