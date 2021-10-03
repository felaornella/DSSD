var listadoSocios = $("#bloqueListado")
var sociosCount=0
var porcentajeTot=0

$("#buttonAddSocioNuevo").on("click",agregarSocio)

const Toast = Swal.mixin({
  toast: true,
  position: 'top',
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  didOpen: (toast) => {
    toast.addEventListener('mouseenter', Swal.stopTimer)
    toast.addEventListener('mouseleave', Swal.resumeTimer)
  }
})


function agregarSocio() {
    if (parseInt($("#porcentaje").val()) + porcentajeTot > 100){
        Toast.fire({
            icon: 'error',
            title: "El porcentaje total no puede ser mayor al 100%"
        })
        return false
    }
    porcentajeTot = porcentajeTot + parseInt($("#porcentaje").val())
    sociosCount=sociosCount+1

    var nombre = $("#apellidoSocioNuevo").val().trim() + ", " + $("#nombreSocioNuevo").val().trim()
    var porcentaje = $("#porcentaje").val()

    var socio = document.createElement("p")
    socio.innerText= nombre + " - " + porcentaje + "%"
    socio.setAttribute("style","margin-bottom: 0; font-size:1.25rem")


    var colSocio= document.createElement("div")
    colSocio.setAttribute("class","col-8")
    colSocio.setAttribute("style","text-align:left")
    
    var colButton= document.createElement("div")
    colButton.setAttribute("class","col-3")
    
    var button= document.createElement("button")
    button.innerText="X"
    button.setAttribute("class","btn btn-outline-danger")
    button.setAttribute("id","buttonSocio"+ sociosCount)
    
    colButton.appendChild(button)
    colSocio.appendChild(socio)
    
    var socioEntero = document.createElement("div")
    socioEntero.setAttribute("class","row  align-items-center")
    socioEntero.setAttribute("style","margin-bottom:1rem")
    socioEntero.setAttribute("id","socio"+sociosCount)
    socioEntero.setAttribute("perc",porcentaje)
    socioEntero.setAttribute("name",nombre)
    socioEntero.appendChild(colSocio)
    socioEntero.appendChild(colButton)

    listadoSocios.prepend(socioEntero)
    
    $("#buttonSocio"+sociosCount).on("click",()=>{quitar(socioEntero.getAttribute("id"))})

    $("#nombreSocioNuevo").val("")
    $("#apellidoSocioNuevo").val("")
    $("#porcentaje").val("")

    bloqueoCampos()
}

function bloqueoCampos(){
    if (porcentajeTot==100){
        $("#nombreSocioNuevo").attr("disabled",true)
        $("#apellidoSocioNuevo").attr("disabled",true)
        $("#porcentaje").attr("disabled",true)
        $("#buttonAddSocioNuevo").attr("disabled",true)
        Toast.fire({
            icon: 'success',
            title: "Se alcanzo el 100% de participacion"
        })
    }else{
        $("#nombreSocioNuevo").removeAttr("disabled")
        $("#apellidoSocioNuevo").removeAttr("disabled")
        $("#porcentaje").removeAttr("disabled")
        $("#buttonAddSocioNuevo").removeAttr("disabled")
    }
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
                title: response.msg
            })
        }
    })
}

function quitar(id){
    porcentajeTot = porcentajeTot - parseInt($("#"+id).attr("perc"))
    document.getElementById("bloqueListado").removeChild(document.getElementById(id))
    bloqueoCampos()
}