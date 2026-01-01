import {setupModals, showToast} from './utils/components.js'

// Handling modal open and close
setupModals();


// Intercepting new location submission

document.getElementById('new-location-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  document.querySelector(".js-modal-submit").disabled = true;
  
  const formData = new FormData(this);

  const plainObject = Object.fromEntries(formData.entries());
  console.log("IN GOING JSON:", plainObject);
  const jsonPayload = JSON.stringify(plainObject);

  fetch('/locations/create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    body: jsonPayload,
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(errorData => {
        throw new Error(`Server Error: ${response.status} - ${errorData.message || 'Unknown Error'}`);
      });
    }
    return response.json();
  })
  .then(result => {
    showToast(result);
    console.log("OUTGOING JSON", result);
    this.reset();
  })
  .catch(error => {
    console.error('Fetch error:', error);
    alert(error.message || 'A network error occurred. Please try again.');
  })
  .finally(() => {
    document.querySelector(".js-modal-submit").disabled = false;
  });
});
