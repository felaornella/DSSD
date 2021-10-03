var listadoSocios = $("#bloqueListado")
var selectSocios = document.getElementById("apoderado")

var sociosCount=0
var porcentajeTot=0

var sociosEnSelect=0

var maxPerc = 0

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
    if ($("#porcentaje").val().trim()==""|| ($("#apellidoSocioNuevo").val().trim()=="" || $("#nombreSocioNuevo").val().trim()=="")){
        Toast.fire({
            icon: 'warning',
            title: "Datos incorrectos o faltantes"
        })
        return false
    }
    if (parseInt($("#porcentaje").val())<=0 || parseInt($("#porcentaje").val())>100){
        Toast.fire({
            icon: 'error',
            title: "El porcentaje del socio debe estar entre 0% y 100%"
        })
        return false
    }
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
    var porcentaje = parseInt($("#porcentaje").val())

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
    
    agregarASelect(nombre, porcentaje,socioEntero.getAttribute("id"))

    $("#buttonSocio"+sociosCount).on("click",()=>{quitar(socioEntero.getAttribute("id"))})

    $("#nombreSocioNuevo").val("")
    $("#apellidoSocioNuevo").val("")
    $("#porcentaje").val("")

    bloqueoCampos()
}

function agregarASelect(name, perc, id){
    if (sociosEnSelect == 0){
        $("#optionNoData").hide()
        $("#apoderado").removeAttr("disabled")
    }
    sociosEnSelect +=1 

    var op = document.createElement("option")
    op.setAttribute("value",name)
    op.innerText= name + " - " + perc
    op.setAttribute("id", "select"+id)
    op.setAttribute("perc",perc)

    if (sociosEnSelect == 1 || parseInt(perc) > maxPerc){
        op.setAttribute("selected",true)
        maxPerc= parseInt(perc)
    }

    selectSocios.appendChild(op)
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
    quitarDeSelect("select"+id)
    sociosCount-=1
    console.log(id)
    bloqueoCampos()
}

function quitarDeSelect(id){
    console.log(id)
    percTemp=parseInt($("#"+id).attr("perc"))
    document.getElementById("apoderado").removeChild(document.getElementById(id))
    sociosEnSelect-=1
    if (maxPerc == percTemp && sociosEnSelect>0){
        maxPerc=0
        idSelected=0
        for (let i=1; i<document.getElementById("apoderado").children.length; i++){
            if (parseInt(document.getElementById("apoderado").children[i].getAttribute("perc"))>maxPerc){
                
                console.log("entre")
                maxPerc=parseInt(document.getElementById("apoderado").children[i].getAttribute("perc"))
                idSelected=document.getElementById("apoderado").children[i].getAttribute("id")
            }
        }
        //document.getElementById(idSelected).setAttribute("selected", true)
        $("#apoderado").val($("#"+idSelected).val())
    }

    
    
    if (sociosEnSelect == 0){
        $("#optionNoData").show()
        $("#apoderado").attr("disabled",true)
        $("#apoderado").val($("#optionNoData").val())
    }

}