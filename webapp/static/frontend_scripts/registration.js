const modal = document.getElementById('uploadModal');
const uploadButton = document.getElementById('openUploadModal');
const closeButton = document.querySelector('.close-button');

// Open modal on upload button click
uploadButton.addEventListener('click', () => {
    modal.style.display = 'block';
});

// Close modal on X button click
closeButton.addEventListener('click', () => {
    modal.style.display = 'none';
});

// Close modal when clicking outside the content box
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
document.addEventListener('DOMContentLoaded', () => {
    const proofIdInput = document.getElementById('proofIdInput');
    const ownershipDocInput = document.getElementById('ownershipDocInput');

    const idPreview = document.getElementById('id-preview');
    const ownershipPreview = document.getElementById('ownership-preview');

    proofIdInput.addEventListener('change', () => {
        const file = proofIdInput.files[0];
        if (file) {
            idPreview.innerText = `Selected File: ${file.name}`;
        } else {
            idPreview.innerText = '';
        }
    });

    ownershipDocInput.addEventListener('change', () => {
        const file = ownershipDocInput.files[0];
        if (file) {
            ownershipPreview.innerText = `Selected File: ${file.name}`;
        } else {
            ownershipPreview.innerText = '';
        }
    });
});
