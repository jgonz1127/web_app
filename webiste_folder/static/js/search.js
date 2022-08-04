window.addEventListener('load', () => {
    //cache the graph ids
    const main_graph = document.getElementById("main_image");
    const side_graph1 = document.getElementById("side_image1");
    const side_graph2 = document.getElementById("side_image2");
    let current_graph = 0;
    const nav_toggle = document.getElementsByClassName("navbar_toggle")[0];
    const nav_links = document.getElementsByClassName("link");
    const inner_nav_toggle = document.getElementById("inner_navigate_toggle");
    const inner_nav_items = document.getElementById("inner_navigate_links");

    inner_nav_toggle.addEventListener("click", ()=> {
        if (inner_nav_items.style.display === "block") {
            inner_nav_toggle.style.opacity = "100%";
            inner_nav_items.style.display = "none"
        }
        else {
            inner_nav_toggle.style.opacity = "45%";
            inner_nav_items.style.display = "block"
        }
    });

    nav_toggle.addEventListener('click', () => {
        for (let i = 0; i < nav_links.length; i++){
            nav_links[i].classList.toggle('active');
        } 
    });
      
    arrow_click = (arrow_clicked) => {
        
        if (arrow_clicked === 'right') {
            if (current_graph === 0) {
                current_graph++;
                main_graph.style.display = "none";
                side_graph1.style.display = "inline";
            } else if (current_graph === 1) {
                current_graph++;
                side_graph2.style.display = "inline";
                side_graph1.style.display = "none";

            } else {
                current_graph = 0;
                side_graph2.style.display = "none";
                main_graph.style.display = "inline";
            }
        } else {
            if (current_graph === 0) {
                current_graph = 2;
                main_graph.style.display = "none";
                side_graph2.style.display = "inline";
            } else if (current_graph === 2) {
                current_graph--;
                side_graph2.style.display = "none";
                side_graph1.style.display = "inline";
            } else {
                current_graph--;
                main_graph.style.display = "inline";
                side_graph1.style.display = "none";
            }
        }
    }


    read_more_button = (dots_id, more_id, button_id ) => {
        const dots = document.getElementById(dots_id);
        const moreText = document.getElementById(more_id);
        const btnText = document.getElementById(button_id);

        if (dots.style.display === "none") {
            dots.style.display = "inline";
            btnText.innerHTML = "Read more";
            moreText.style.display = "none";
        } else {
            dots.style.display = "none";
            btnText.innerHTML = "Read less";
            moreText.style.display = "inline";
        }
    }
});