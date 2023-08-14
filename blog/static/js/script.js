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

window.onload = () => {
    const swiperConfig = {
        direction: 'horizontal',
        mousewheel: {
            invert: true,
            forceToAxis : true,
        },
        mousewheelControl: true,
        releaseOnEdges: true,
        slidesPerView: 2,
        spaceBetween: 30,
        centeredSlides: true,
        loop: true,
        parallax: true,
        speed: 1000,
        keyboard: {
            enabled: true,
            onlyInViewport: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
            dynamicBullets: true,
        },
        autoplay: {
            delay: 2000,
        },
        fadeEffect: {
            crossFade: true
        },
    };

  const divswipe = new Swiper('.swiper-container', swiperConfig);
};

function shareOnFacebook(pk) {
    const link = 'http://127.0.0.1:8000/article/' + pk;
    const url = "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(link);
    window.open(url, "_blank");
}
function shareOnTwitter(pk) {
    const url = 'http://127.0.0.1:8000/article/' + pk;
    const encodedUrl = encodeURIComponent(url);
    const encodedMessage = encodeURIComponent("Check out this link!");
    window.open("https://twitter.com/intent/tweet?url=" + encodedUrl + "&text=" + encodedMessage);
}
function shareOnPinterest(pk) {
    const url = 'http://127.0.0.1:8000/article/' + pk;
    const encodedUrl = encodeURIComponent(url);
    const encodedMessage = encodeURIComponent("Check out this link!");
    window.open("https://www.pinterest.com/pin/create/button/?url=" + encodedUrl + "&description=" + encodedMessage);
}
function shareOnLinkedIn(pk) {
    const url = 'http://127.0.0.1:8000/article/' + pk;
    const encodedUrl = encodeURIComponent(url);
    const encodedMessage = encodeURIComponent("Check out this link!");
    window.open("https://www.linkedin.com/shareArticle?mini=true&url=" + encodedUrl + "&title=" + encodedMessage);
}
