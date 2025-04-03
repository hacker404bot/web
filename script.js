// script.js
function uploadImage() {
    const input = document.getElementById('imageInput');
    const file = input.files[0];
    if (!file) {
        alert('Please select an image!');
        return;
    }

    const formData = new FormData();
    formData.append('image', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const textElement = document.getElementById('extractedText');
        const audioElement = document.getElementById('audioOutput');

        textElement.textContent = `Extracted Text: ${data.text}`;
        if (data.audio) {
            audioElement.src = data.audio + '?' + new Date().getTime(); // Prevent caching
            audioElement.style.display = 'block';
            audioElement.play();
        } else {
            audioElement.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('extractedText').textContent = 'Error processing image';
    });
}

document.getElementById('audioOutput').style.display = 'none';