document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.querySelector('.search-bar');
    const urlInput = searchForm.querySelector('input[name="url"]');

    searchForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const url = urlInput.value.trim();
        if (!url) {
            alert("Please enter a URL.");
            return;
        }

        try {
            // Check if the URL is registered
            const response = await fetch('/check-registered-url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();
            if (!data.success) {
                alert(data.message);  // Only alert if registration fails
                return;
            }

            // Start security tests
            const testResponse = await fetch('/run_tests/run_tests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const testData = await testResponse.json();
            console.log("Test Response Data:", testData);  // Log response for debugging

            if (!testData.success) {
                alert("Error running tests: " + testData.error);
                return;
            }

            const taskId = testData.task_id;

            // Save taskId to sessionStorage for later use (optional)
            sessionStorage.setItem("task_id", taskId);

            // Redirect the user to the loading page with task_id
            window.location.href = `/run_tests/loading?task_id=${taskId}`;

        } catch (error) {
            console.error("Error:", error);
            alert("An unexpected error occurred. Please try again.");
        }
    });
});
