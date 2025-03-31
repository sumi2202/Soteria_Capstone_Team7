document.addEventListener("DOMContentLoaded", function () {
    const stars = document.querySelectorAll(".stars img"); //getting all the star images into a list
    const btn = document.querySelector(".submit"); //submit button
    let rating_value = 0;

    for (let i = 0; i < stars.length; i++){
        const current_star = stars[i];

        // onclick function for each star
        current_star.addEventListener("click", function () {
            for (let j = 0; j < stars.length; j++){
                if (j <= i ) { // filling in clicked star and all stars before it
                    stars[j].src = "static/assets/rating_filled_edit.png";
                } else {
                    stars[j].src = "static/assets/rating_unfilled_edit.png";
                }
            }

            rating_value = i + 1 //stores rating value depending on how many stars are filled
        });
    }



    //getting selected rating
    btn.addEventListener("click", async function() {
        //no selected value
        if (rating_value === 0){
            alert("Please select a rating.");
            return;
        }

        //sending value to views.py for db insertion
        const reply = await fetch("/submit_rating", {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ rating: rating_value})
        });
        const value = await reply.json();
        alert(value.output_msg); //getting output message after trying to insert in db
    });
});
