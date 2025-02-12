async function validateURL(){
    const email = document.getElementById('email').value;
    const url = document.getElementById('url').value;

    const response = await fetch('/validate', {
        method: 'POST',
        headers: {'Content-Type' : 'application/json'},
        body: JSON.stringify({email,url})
    });

    const result = await response.json();
    let message = '';

    if (result.validURL === 1){
        message = "Invalid or unreachable URL.";
    } else if (result.alreadyRegistered === 1){
        message = "already registered";
    } else {
        message = "URL available";
    }
}