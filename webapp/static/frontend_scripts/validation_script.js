async function validateURL(){
    const url = document.getElementById('url').value;
    const allowRegister = document.getElementByID('allowRegister')

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
        allowRegister.disabled = true;

    }else if (result.invalidURL === 1) {
        existMessage = "❌ URL IS INVALID.";
        availMessage = "❌ URL CANNOT BE REGISTERED.";
        allowRegister.disabled = true;

    }
    else if (result.validURL === 1) {
        existMessage = "❌ URL DOES NOT EXIST OR IS UNREACHABLE";
        availMessage = "❌ URL CANNOT BE REGISTERED";
        allowRegister.disabled = true;
    }
    else {
        existMessage = "✅ URL EXISTS";

        if(result.alreadyRegistered === 1){
            availMessage = "⚠️ URL IS ALREADY REGISTERED";
            allowRegister.disabled = true;
        } else {
            availMessage = "✅ URL IS AVAILABLE FOR REGISTRATION";
            allowRegister.disabled = false;
        }

    }

    document.getElementById('existResult').innerText = existMessage;
    document.getElementById('availResult').innerText = availMessage;

}