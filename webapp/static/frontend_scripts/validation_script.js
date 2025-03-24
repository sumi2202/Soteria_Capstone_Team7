async function validateURL() {
    const url = document.getElementById('url').value;

    const response = await fetch('/validation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
    });

    const result = await response.json();
    let existMessage = '';
    let availMessage = '';
    const allowRegister = document.getElementById('allowRegister');

    // positive svg
    const checkSVG = `
      <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2" width="50" height="50">
        <circle class="path circle" fill="#2CBE9B" stroke="#ffffff" stroke-width="6" stroke-miterlimit="10" cx="65.1" cy="65.1" r="62.1"/>
        <polyline class="path check" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" points="100.2,40.2 51.5,88.8 29.8,67.5"/>
      </svg>
      <p class="success" style="font-size: 14px;">URL EXISTS</p>
    `;

    const availSVG = `
      <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2" width="50" height="50">
        <circle class="path circle" fill="#2CBE9B" stroke="#ffffff" stroke-width="6" stroke-miterlimit="10" cx="65.1" cy="65.1" r="62.1"/>
        <polyline class="path check" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" points="100.2,40.2 51.5,88.8 29.8,67.5"/>
      </svg>
      <p class="success" style="font-size: 14px;">URL IS AVAILABLE</p>
    `;


    // negative svg
    const errorSVG = `
      <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2" width="50" height="50">
        <circle class="path circle" fill="#DB5461" stroke="#ffffff" stroke-width="6" stroke-miterlimit="10" cx="65.1" cy="65.1" r="62.1"/>
        <line class="path line" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" x1="34.4" y1="37.9" x2="95.8" y2="92.3"/>
        <line class="path line" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" x1="95.8" y1="38" x2="34.4" y2="92.2"/>
      </svg>
      <p class="error" style="font-size: 14px;">ERROR</p>
    `;

    const invalidSVG = `
      <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2" width="50" height="50">
        <circle class="path circle" fill="#DB5461" stroke="#ffffff" stroke-width="6" stroke-miterlimit="10" cx="65.1" cy="65.1" r="62.1"/>
        <line class="path line" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" x1="34.4" y1="37.9" x2="95.8" y2="92.3"/>
        <line class="path line" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" x1="95.8" y1="38" x2="34.4" y2="92.2"/>
      </svg>
      <p class="error" style="font-size: 14px;">URL IS INVALID</p>
    `;

    const alrRegSVG = `
      <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2" width="50" height="50">
        <circle class="path circle" fill="#DB5461" stroke="#ffffff" stroke-width="6" stroke-miterlimit="10" cx="65.1" cy="65.1" r="62.1"/>
        <line class="path line" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" x1="34.4" y1="37.9" x2="95.8" y2="92.3"/>
        <line class="path line" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" x1="95.8" y1="38" x2="34.4" y2="92.2"/>
      </svg>
      <p class="error" style="font-size: 14px;">URL IS ALREADY REGISTERED</p>
    `;
    const nonexistSVG = `
      <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2" width="50" height="50">
        <circle class="path circle" fill="#DB5461" stroke="#ffffff" stroke-width="6" stroke-miterlimit="10" cx="65.1" cy="65.1" r="62.1"/>
        <line class="path line" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" x1="34.4" y1="37.9" x2="95.8" y2="92.3"/>
        <line class="path line" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" x1="95.8" y1="38" x2="34.4" y2="92.2"/>
      </svg>
      <p class="error" style="font-size: 14px;">URL DOES NOT EXIST</p>
    `;


    const cannotSVG = `
      <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2" width="50" height="50">
        <circle class="path circle" fill="#DB5461" stroke="#ffffff" stroke-width="6" stroke-miterlimit="10" cx="65.1" cy="65.1" r="62.1"/>
        <line class="path line" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" x1="34.4" y1="37.9" x2="95.8" y2="92.3"/>
        <line class="path line" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-miterlimit="10" x1="95.8" y1="38" x2="34.4" y2="92.2"/>
      </svg>
      <p class="error" style="font-size: 14px;">URL CANNOT BE REGISTERED</p>
    `;


    // Handle validation results
    if (result.error) {
        existMessage = errorSVG;
        availMessage = cannotSVG;
        allowRegister.disabled = true;
    } else if (result.invalidURL === 1) {
        existMessage = invalidSVG;
        availMessage = cannotSVG;
        allowRegister.disabled = true;
    } else if (result.validURL === 1) {
        existMessage = nonexistSVG;
        availMessage = cannotSVG;
        allowRegister.disabled = true;
    } else {
        existMessage = checkSVG;
        if (result.alreadyRegistered === 1) {
            availMessage = alrRegSVG;
            allowRegister.disabled = true;
        } else {
            availMessage = availSVG;
            allowRegister.disabled = false;
        }
    }

    // Insert the SVG and messages into the respective elements
    document.getElementById('existResult').innerHTML = existMessage;
    document.getElementById('availResult').innerHTML = availMessage; // <-- fixed here
}
function registerURL() {
    console.log("📌 Redirecting to /register-link...");
    window.location.href = "/register-link";
}