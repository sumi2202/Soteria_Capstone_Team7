document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.querySelector('.search-bar');
    const urlInput = searchForm.querySelector('input[name="q"]');

    searchForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const url = urlInput.value.trim();
        if (!url) {
            alert("Please enter a URL.");
            return;
        }

        // Send the URL to the server to check if it's registered
        const response = await fetch('/check-registered-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (!data.success) {
            alert(data.message);  // Show the warning if the URL is not registered
        } else {
            // Proceed with the tests if URL is registered
            alert("URL is registered. You can now perform tests!");
            // Add logic to enable test functionality
        }
    });
});

