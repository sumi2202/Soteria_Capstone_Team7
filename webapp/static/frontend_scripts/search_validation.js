document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.querySelector('.search-bar');
    const urlInput = searchForm.querySelector('input[name="url"]');
    const levelRiskSelect = searchForm.querySelector('#sql_level_risk');

    searchForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submit

        const url = urlInput.value.trim();
        const sqlLevelRisk = levelRiskSelect.value;

        if (!url) {
            alert("Please enter a URL.");
            return;
        }

        try {
            // Step 1: Check if URL is registered
            const response = await fetch('/check-registered-url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();
            if (!data.success) {
                alert(data.message);  // Show message if registration fails
                return;
            }

            // Step 2: Run security tests with URL and SQLi level/risk
            const testResponse = await fetch('/tests/run_tests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url,
                    sql_level_risk: sqlLevelRisk
                })
            });

            const testData = await testResponse.json();
            console.log("✅ Test Response Data:", testData);

            if (!testData.success) {
                alert("Error running tests: " + testData.error);
                return;
            }

            const taskId = testData.task_id;

            // Optional: Store task ID
            sessionStorage.setItem("task_id", taskId);

            // Redirect to loading screen
            window.location.href = `/tests/loading?task_id=${taskId}`;

        } catch (error) {
            console.error("🚨 Unexpected error:", error);
            alert("An unexpected error occurred. Please try again.");
        }
    });
});
