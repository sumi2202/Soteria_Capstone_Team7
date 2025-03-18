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
                alert(data.message);
                return;
            }

            alert("URL is registered. Running security tests...");

            // Start tests
            const testResponse = await fetch('/run_tests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const testData = await testResponse.json();
            if (!testData.success) {
                alert("Error running tests: " + testData.error);
                return;
            }

            const taskId = testData.task_id;
             sessionStorage.setItem("task_id", taskId);

                // Redirect to the loading page
                window.location.href = "/loading";  // Redirect to loading page
            } catch (error) {
                console.error("Error:", error);
                alert("An unexpected error occurred. Please try again.");
            }

            // Show loading message
            document.getElementById("loadingScreen").style.display = "block";

            // Poll the test status every 2 seconds
            const checkTestStatus = async () => {
                const statusResponse = await fetch(`/test_status/${taskId}`);
                const statusData = await statusResponse.json();

                if (statusData.status === "completed") {
                    window.location.href = "/test_results";
                } else {
                    setTimeout(checkTestStatus, 2000);  // Keep checking
                }
            };

            checkTestStatus();
        } catch (error) {
            console.error("Error:", error);
            alert("An unexpected error occurred. Please try again.");
        }
    });
});


