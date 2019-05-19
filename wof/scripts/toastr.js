function enviarMensagem(msg,type,title) {
    
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": false,
        "progressBar": true,
        "positionClass": "toast-bottom-right",
        "preventDuplicates": false,
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "55000",
        "extendedTimeOut": "15000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
      }

    toastr[type](msg,title)
}

function troca_campos(val){
  var condicao1 = document.getElementById("condicao1"+val);
  var condicao2 = document.getElementById("condicao2"+val);
  var condicao3 = document.getElementById("condicao3"+val);
  var condicao4 = document.getElementById("condicao4"+val);

  condicao1.style.display = "none";
  condicao2.style.display = "block";
  condicao3.style.display = "none";
  condicao4.style.display = "block";
}