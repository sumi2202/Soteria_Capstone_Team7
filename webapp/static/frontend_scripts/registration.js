document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('uploadModal');
    const uploadButton = document.getElementById('openUploadModal');
    const closeButton = document.querySelector('.close-button');
    const registerBtn = document.getElementById('registerBtn');
    const submitBtn = document.querySelector('.submit-btn');

    const proofIdInput = document.getElementById('proofIdInput');
    const ownershipDocInput = document.getElementById('ownershipDocInput');

    const idPreview = document.getElementById('id-preview');
    const ownershipPreview = document.getElementById('ownership-preview');

    let proofIdFiles = []; // Store all Proof of ID files
    let ownershipFiles = []; // Store all Ownership Documents

    uploadButton.addEventListener('click', () => {
        modal.classList.add('show');
    });

    closeButton.addEventListener('click', () => {
        modal.classList.remove('show');
    });


    // Close modal when clicking outside the content box
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Append files to preview and files array
    function appendFiles(inputElement, previewElement, fileList) {
        Array.from(inputElement.files).forEach((file) => {
            if (!fileList.some(f => f.name === file.name)) {
                fileList.push(file);
                updatePreview(previewElement, fileList);
            }
        });
        inputElement.value = ""; // Reset input to allow same file selection
    }

    // Update preview of files
    function updatePreview(previewElement, fileList) {
    previewElement.innerHTML = "";
    const ul = document.createElement('ul');
    fileList.forEach((file, index) => {
        const li = document.createElement('li');

        // Trimmed display name
        const maxLength = 15;
        const fileName = file.name.length > maxLength
            ? file.name.slice(0, maxLength) + '...'
            : file.name;

        li.textContent = fileName;

        const removeBtn = document.createElement('button');
        removeBtn.textContent = '❌';
        removeBtn.style.marginLeft = '10px';
        removeBtn.style.cursor = 'pointer';

        removeBtn.addEventListener('click', () => {
            fileList.splice(index, 1);
            updatePreview(previewElement, fileList);
        });

        li.appendChild(removeBtn);
        ul.appendChild(li);
    });
    previewElement.appendChild(ul);
}


    // File input change event listeners
    proofIdInput.addEventListener('change', () => {
        appendFiles(proofIdInput, idPreview, proofIdFiles);
    });

    ownershipDocInput.addEventListener('change', () => {
        appendFiles(ownershipDocInput, ownershipPreview, ownershipFiles);
    });

    // Submit button logic (attach files to form)
    submitBtn.addEventListener('click', () => {
        const formData = new FormData();

        // Collect user details
        formData.append('firstName', document.getElementById('FirstName').value);
        formData.append('lastName', document.getElementById('LastName').value);
        formData.append('email', document.getElementById('Email').value);

        // Attach selected files to formData
        proofIdFiles.forEach(file => formData.append('proofIdFiles', file));
        ownershipFiles.forEach(file => formData.append('ownershipFiles', file));

        // Store formData in a variable for later use (register button)
        window.tempFormData = formData;
        alert('Files attached to the form. You can now proceed to register.');
    });

    // Register button logic (send data to backend)
    registerBtn.addEventListener('click', () => {
        if (window.tempFormData) {
            fetch('/register-link', {
                method: 'POST',
                body: window.tempFormData
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if (data.success) {
                    window.location.href = '/dashboard';
                }
            })
            .catch(error => console.error('Error:', error));
        } else {
            alert('Please attach the required files before registering.');
        }
    });
});

