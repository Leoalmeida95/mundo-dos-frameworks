
function troca_campos(val1,val2){
    var condicao1 = document.getElementById("condicao1-"+val1+"-"+val2);
    var condicao2 = document.getElementById("condicao2-"+val1+"-"+val2);
    var condicao3 = document.getElementById("condicao3-"+val1+"-"+val2);
    var condicao4 = document.getElementById("condicao4-"+val1+"-"+val2);
  
    condicao1.style.display = "none";
    condicao2.style.display = "block";
    condicao3.style.display = "none";
    condicao4.style.display = "block";
  }