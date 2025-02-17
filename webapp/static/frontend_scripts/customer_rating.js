document.addEventListener("DOMContentLoaded", function () {
    const stars = document.querySelectorAll(".stars img"); //getting all the star images into a list

    for (let i = 0; i < stars.length; i++){
        const current_star = stars[i];

        // onclick function for each star
        current_star.addEventListener("click", function () {
            for (let j = 0; j < stars.length; j++){
                if (j <= i ) { // filling in clicked star and all stars before it
                    stars[j].src = "static/assets/rating_filled.png";
                } else {
                    stars[j].src = "static/assets/rating_unfilled.png";
                }
            }
        });
    }


});
