async function validateURL(){
    const url = document.getElementById('url').value;

    const response = await fetch('/validation', {
        method: 'POST',
        headers: {'Content-Type' : 'application/json'},
        body: JSON.stringify({url})
    });

    const result = await response.json();
    let existMessage = '';
    let availMessage = '';

    if(result.error){
        existMessage = "❌ ERROR: " + result.error;

    }else if (result.invalidURL === 1) {
        existMessage = "❌ URL IS INVALID.";
        availMessage = "❌ URL CANNOT BE REGISTERED.";
    }
    else if (result.validURL === 1) {
        existMessage = "❌ URL DOES NOT EXIST OR IS UNREACHABLE";
        availMessage = "❌ URL CANNOT BE REGISTERED";
    }
    else {
        existMessage = "✅ URL EXISTS";

        availMessage = result.alreadyRegistered === 1
            ? "⚠️ URL IS ALREADY REGISTERED"
            : "✅ URL IS AVAILABLE FOR REGISTRATION";
    }

    document.getElementById('existResult').innerText = existMessage;
    document.getElementById('availResult').innerText = availMessage;

}