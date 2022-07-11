
window.addEventListener('load', () => {
    const nav_toggle = document.getElementsByClassName("navbar_toggle")[0];
    const nav_links = document.getElementsByClassName("link");
    nav_toggle.addEventListener('click', () => {
        for (let i = 0; i < nav_links.length; i++){
            nav_links[i].classList.toggle('active');
        } 
    });
});


