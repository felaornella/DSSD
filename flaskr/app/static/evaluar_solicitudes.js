var count_soc= document.getElementById("sociedadesDiv").children.length

for (let i=1; i<=count_soc;i++){
    $("#buttonRechazar"+i).on("click",pedirRazon)
}

function pedirRazon(){
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
              alert(motivoRechazo)
            }
          }
        }
      })
}