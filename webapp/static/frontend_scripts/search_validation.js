document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.querySelector('.search-bar');
    const urlInput = searchForm.querySelector('input[name="url"]');
    const sqlLevelRiskInput = searchForm.querySelector('#sql_level_risk'); // hidden input
    const sqlLabelInput = document.querySelector('#sql_label');
    const selectedDisplay = document.getElementById('selected'); // visible div in custom dropdown

    searchForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const url = urlInput.value.trim();
        const sqlLevelRisk = sqlLevelRiskInput.value;
        const selectedText = selectedDisplay.textContent;

        if (!url) {
            alert("Please enter a URL.");
            return;
        }

        // Extract label from custom dropdown display
        const label = selectedText.split(" - ")[0].trim();
        sqlLabelInput.value = label;

        try {
            // Step 1: Check if URL is registered
            const checkResponse = await fetch('/check-registered-url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const checkData = await checkResponse.json();
            if (!checkData.success) {
                alert(checkData.message);
                return;
            }

            if (!checkData.verified) {
                alert("This URL is not verified. Please complete the verification process first.");
                return;
            }

            // Step 2: Run the tests
            const formData = {
                url,
                sql_level_risk: sqlLevelRisk,
                sql_label: label
            };

            const testResponse = await fetch('/tests/run_tests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const testData = await testResponse.json();

            if (!testData.success) {
                alert("Error running tests: " + testData.error);
                return;
            }

            const taskId = testData.task_id;
            sessionStorage.setItem("task_id", taskId);
            window.location.href = `/tests/loading?task_id=${taskId}`;

        } catch (error) {
            console.error("🚨 Unexpected error:", error);
            alert("An unexpected error occurred. Please try again.");
        }
    });
});
