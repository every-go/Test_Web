document.addEventListener("scroll", function() {
    var header = document.querySelector("header");
    var logo = document.querySelector("#header-logo");
    if(window.scrollY > 100) {
        header.classList.add("scrolled");
        logo.classList.add("scrolled-logo");
    } else {
        header.classList.remove("scrolled");
        logo.classList.remove("scrolled-logo");
    }
});