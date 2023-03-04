window.addEventListener('scroll',(e)=>{
        const nav = document.querySelector('.nav');
        if(window.pageYOffset>0){
          nav.classList.add("add-shadow");
        }else{
          nav.classList.remove("add-shadow");
        }
      });

function toggle(){
    if(document.getElementById("btn-bars").className == "fa-solid fa-bars fa-lg btn-nav")
       document.getElementById("btn-bars").className = "fa-solid fa-xl fa-xmark btn-nav";
    else
       document.getElementById("btn-bars").className = "fa-solid fa-bars fa-lg btn-nav";
}

