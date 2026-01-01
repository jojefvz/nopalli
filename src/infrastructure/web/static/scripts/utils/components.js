
// handling modal setup
export function setupModals() {
  let openModalBtns = document.querySelectorAll('.js-modal-open');
  let closeModalBtns = document.querySelectorAll('.js-modal-close');

  openModalBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modal = document.querySelector(e.target.dataset.modalTarget);
      modal.classList.remove('hidden');
    });
  });

  closeModalBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modal = document.querySelector(e.target.dataset.modalTarget);
      modal.classList.add('hidden');
    });
  });
}

// toast notification
export function showToast(data) {
    let toastType = '';
    let toastMessage = '';
    let toastClass = '';
    if (Object.hasOwn(data, 'code')) {
      toastType += 'ERROR';
      toastMessage += `${data.message}`;
      toastClass = 'error';
    } else {
      toastType += 'SUCCESS'
      toastMessage += `Location Created: ${data.name}`;
      toastClass = 'success'
    }

    let toastHTML = `
    <div class="toast-container ${toastClass}">
      <div class="toast-type">${toastType}:</div>
      <div class="toast-message">${toastMessage}</div>
    </div>
    `;

    setTimeout(() => {
      document.body.insertAdjacentHTML('beforeend', toastHTML);
    }, 100);

    setTimeout(() => {
      document.querySelector('.toast-container').remove();
    }, 5000);
}