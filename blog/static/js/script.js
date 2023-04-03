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

document.addEventListener("DOMContentLoaded", function(){
	        /////// Prevent closing from click inside dropdown
	        document.querySelectorAll('.dropdown-menu').forEach(function(element){
	        	element.addEventListener('click', function (e) {
	        		e.stopPropagation();
	        	});
	        })
	    });

document.addEventListener('DOMContentLoaded', function () {
    let footerheight = document.querySelector("footer").offsetHeight;
    document.querySelector("body").style.paddingBottom = footerheight;
});




const swiper = new Swiper('.swiper', {
  direction: 'horizontal',
  loop: true,

   navigation: {
    nextEl: '.next',
    prevEl: '.prev',
  },

})