var count_soc= document.getElementById("sociedadesDiv").children.length

for (let i=1; i<=count_soc;i++){
   
    $("#buttonRechazar"+i).on("click",pedirRazon)
    $("#buttonAceptar"+i).on("click",aceptarSolicitud)
}

function pedirRazon(){
    solicitudId= $(this).data('idsol')
    
    Swal.fire({
        input: 'textarea',
        inputLabel: 'Motivo de Rechazo',
        inputPlaceholder: 'Ingrese el motivo del rechazo...',
        inputAttributes: {
          'aria-label': 'Ingrese el motivo del rechazo'
        },
        showCancelButton: true,
        confirmButtonText: 'Confirmar',
        cancelButtonText: "Cancelar",
        reverseButtons:true,
        preConfirm:(motivoRechazo) =>{
          if (motivoRechazo==""){
            Swal.showValidationMessage(
              "Por favor ingrese el motivo del rechazo"
            )
          }else{
            if (motivoRechazo.length>250){
              Swal.showValidationMessage(
                "El tamaño máximo permitido es de 250 caracteres"
              ) 
            }else{
              data2={"comentario":motivoRechazo}
              data2["solicitudId"]=solicitudId
              
              $.post({
                url: "/rechazar_solicitud",
                processData: false,
                contentType: false,
                datatType: "json",
                data: JSON.stringify(data2),
                success: function(response){
                    Swal.fire({
                      icon: 'success',
                      title:'Comentario enviado con exito',
                      timer: 2000,
                    })
                    borrarSolicitud(solicitudId)
                },
                error: function(response) {
                  Swal.fire({
                    icon: 'error',
                    title: response.responseJSON,
                    showConfirmButton: true,
                    timerProgressBar: true,
                    timer: 2500
                  })
                }
              })
            }
          }
        }
      })
}


function aceptarSolicitud(){
  solicitudId= $(this).data('idsol')
  Swal.fire({
    title: 'Estas seguro?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Si'
  }).then((result) => {
    if (result.isConfirmed) {
      data2={}
      data2["solicitudId"]=solicitudId
      $.post({
        url: "/aceptar_solicitud",
        processData: false,
        contentType: false,
        datatType: "json",
        data: JSON.stringify(data2),
        success: function(response){
            Swal.fire({
              icon: 'success',
              title:'Solicitud Aprobada!',
              timer: 2000,
            })
            borrarSolicitud(solicitudId)
        },
        error: function(response) {
          Swal.fire({
            icon: 'error',
            title: response.responseJSON,
            showConfirmButton: true,
            timerProgressBar: true,
            timer: 2500
          })
        }
      })

    }
  })
}

function borrarSolicitud(id){
  document.getElementById("sociedadesDiv").removeChild(document.getElementById("solicitudDiv"+id))
}
