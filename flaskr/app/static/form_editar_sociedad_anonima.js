var listadoSocios = $("#bloqueListado")
var selectSocios = document.getElementById("apoderado")

var sociosCount=0
var porcentajeTot=0

var sociosEnSelect=0

var maxPerc = 0

$("#buttonAddSocioNuevo").on("click",agregarSocio)
$("#buttonEnviarForm").on("click",enviar)

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
    socioEntero.setAttribute("style","margin-bottom:1rem; border-bottom: 1.5px solid rgba(0,0,0,0.25); padding-bottom:.5rem")
    socioEntero.setAttribute("id","socio"+sociosCount)
    socioEntero.setAttribute("perc",porcentaje)
    socioEntero.setAttribute("nombre", $("#nombreSocioNuevo").val().trim())
    socioEntero.setAttribute("apellido",$("#apellidoSocioNuevo").val().trim())
    socioEntero.appendChild(colSocio)
    socioEntero.appendChild(colButton)

    listadoSocios.prepend(socioEntero)
    
    agregarASelect(nombre, porcentaje,socioEntero.getAttribute("id"),null)

    $("#buttonSocio"+sociosCount).on("click",()=>{quitar(socioEntero.getAttribute("id"))})

    $("#nombreSocioNuevo").val("")
    $("#apellidoSocioNuevo").val("")
    $("#porcentaje").val("")

    bloqueoCampos()
}
function agregarSocioParams(porcentaje, apellidoSocioNuevo,nombreSocioNuevo) {
    porcentajeTot = porcentajeTot + porcentaje
    sociosCount=sociosCount+1

    var nombre = apellidoSocioNuevo + ", " + nombreSocioNuevo
    var porciento = porcentaje

    var socio = document.createElement("p")
    socio.innerText= nombre + " - " + porciento + "%"
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
    socioEntero.setAttribute("style","margin-bottom:1rem; border-bottom: 1.5px solid rgba(0,0,0,0.25); padding-bottom:.5rem")
    socioEntero.setAttribute("id","socio"+sociosCount)
    socioEntero.setAttribute("perc",porciento)
    socioEntero.setAttribute("nombre", nombreSocioNuevo)
    socioEntero.setAttribute("apellido",apellidoSocioNuevo)
    socioEntero.appendChild(colSocio)
    socioEntero.appendChild(colButton)

    listadoSocios.prepend(socioEntero)
    
    agregarASelect(nombre, porciento,socioEntero.getAttribute("id"),null)

    $("#buttonSocio"+sociosCount).on("click",()=>{quitar(socioEntero.getAttribute("id"))})

    $("#nombreSocioNuevo").val("")
    $("#apellidoSocioNuevo").val("")
    $("#porcentaje").val("")

    bloqueoCampos()
}

function agregarASelect(name, perc, id, apoderado=false){
    if (sociosEnSelect == 0){
        $("#optionNoData").hide()
        $("#apoderado").removeAttr("disabled")
    }
    sociosEnSelect +=1 

    var op = document.createElement("option")
    op.setAttribute("value",id)
    op.innerText= name + " - " + perc
    op.setAttribute("id", "select"+id)
    op.setAttribute("perc",perc)
    
    if (apoderado == true || (apoderado == null && sociosEnSelect == 1 || parseInt(perc) > maxPerc) ){
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


function enviar(){
    var data2={}
  	

	
    paisesStr=""
    paises = $("#paisesExportacion").val()
    for (let i=0; i<paises.length; i++){
        if (i!=0){
            paisesStr = paisesStr + "," + paises[i]
        }else{
            paisesStr = paises[i]
        }
    }
    data2["paisesExportacion"]=paisesStr

    socios = document.getElementById("bloqueListado").children
    sociosDic= {}
    for (let i=0; i<socios.length; i++){
        sociosDic["socio"+i]={
            "nombre": socios[i].getAttribute("nombre"),
            "apellido": socios[i].getAttribute("apellido"),
            "porcentaje": socios[i].getAttribute("perc"),
            "apoderado": $("#apoderado").val()==socios[i].getAttribute("id")
        }
    }


	datos= new FormData(document.getElementById("formulario"))

	var myFile = $('#estatuto').prop('files')
	datos.append('estatuto',myFile)
	console.log(myFile)
	datos.append("paisesExpo",paisesStr)
	datos.append("socios",JSON.stringify(sociosDic))
	showLoadingSing()
    $.post({
        url: "/editar/"+String(sociedad_id),
        processData: false,
        contentType: false,
		processData: false,
        data: datos,
        success: function(response){
            Swal.close()
            Swal.fire({
              icon: 'success',
              title:'Sociedad editada con exito',
              timer: 2000,
              willClose: ()=>{window.location.assign("/menu_apoderado")}
            })
            
        },
        error: function(response) {
            Swal.close()
            Swal.fire({
                icon: 'error',
                title: response.responseJSON["msg"],
                showConfirmButton: true,
                timerProgressBar: true,
                timer: 2500
            })
        }
    })
}

function limpiarForm(){
    $("#nombreSociedad").val("")
    $("#fechaCreacion").val("")
    //$("#estatuto").val("")   ver como hacer con tipo file
    $("#domicilioLegal").val("")
    $("#domicilioReal").val("")
    $("#email").val("")
    $("#paisesExportacion").val("")
    $('.selectpicker').selectpicker('refresh');

    for (let i=document.getElementById("bloqueListado").children.length -1;i>=0;i--){
        quitar(document.getElementById("bloqueListado").children[i].getAttribute("id"))
    }
}

function bloqueoCampos(){
    document.getElementById("apoderado").disabled=true
}

function showLoadingSing(){
    Swal.fire({
        title: 'Procesando...',
        showConfirmButton: false,
        allowOutsideClick: false,
        html: 'Estamos procesando su pedido, por favor aguarde',
        didOpen: () => {
          Swal.showLoading()
        }
      })
}