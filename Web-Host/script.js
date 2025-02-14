let xhr;  // Declare a global variable to store the XMLHttpRequest object

//upload form
document.getElementById('uploadForm').onsubmit = function(event) {
  event.preventDefault();

  const fileInput = document.querySelector('input[type="file"]');
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);

  xhr = new XMLHttpRequest();  // Create a new XMLHttpRequest object
  xhr.open('POST', '/upload', true);

  xhr.upload.onprogress = function(event) {
    if (event.lengthComputable) {
      const percentComplete = (event.loaded / event.total) * 100;
      const progressBar = document.getElementById('progress-bar');
      progressBar.style.width = percentComplete + '%';
      progressBar.textContent = Math.round(percentComplete) + '%';
    }
  };

  xhr.onloadstart = function() {
    document.getElementById('progress-container').style.display = 'block';
    document.getElementById('stopButton').style.display = 'inline'; // Show the stop button
  };

  xhr.onloadend = function() {
    if (xhr.status == 200) {
        alert('File uploaded successfully');
        // Trigger a page reload after upload is complete
        window.location.href = '/';  // Redirect to the home page after upload
    } else {
        alert('Failed to upload file');
    }
    document.getElementById('progress-container').style.display = 'none';
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-bar').textContent = '0%';
    document.getElementById('stopButton').style.display = 'none';  // Hide the stop button when upload ends
  };

  xhr.send(formData);
};

//download form
document.getElementById('downloadForm').onsubmit = function(event) {
  event.preventDefault();

  const selectElement = document.getElementById('file-select');
  const selectedOptions = Array.from(selectElement.selectedOptions);
  const formData = new FormData();

  selectedOptions.forEach(option => {
    formData.append('files', option.value);
  });

  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/download', true);
  xhr.responseType = 'blob';  // Expecting a binary file

  xhr.onload = function() {
    console.log('onload called');
    if (xhr.status == 200) {
      console.log('Status 200: File download initiated');
      const blob = new Blob([xhr.response], { type: 'application/octet-stream' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = selectedOptions[0].value;  // Assuming single file selection
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else {
      console.error('Failed to download file, status: ' + xhr.status);
      alert('Failed to download file, status: ' + xhr.status);
    }
  };

  xhr.onerror = function() {
    console.error('Request failed');
    alert('Failed to send file request');
  };

  xhr.send(formData);
};


// Stop upload functionality
document.getElementById('stopButton').onclick = function() {
  if (xhr) {
    xhr.abort();  // Abort the upload
    document.getElementById('progress-container').style.display = 'none';
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-bar').textContent = '0%';
    document.getElementById('stopButton').style.display = 'none';  // Hide the stop button
    alert('Upload stopped');
  }
};
