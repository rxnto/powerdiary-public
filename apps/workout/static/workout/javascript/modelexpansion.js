document.querySelectorAll('.front-view, .back-view').forEach(element => {
    element.addEventListener('click', function() {
      const modal = document.createElement('div');
      modal.className = 'modal-overlay';
      modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
      `;
  
      const zoomedContent = this.cloneNode(true);
      zoomedContent.style.cssText = `
        transform: scale(0.8);
        background: #999999;
        padding: 20px;
      `;
  
      modal.appendChild(zoomedContent);
      document.body.appendChild(modal);
  
      modal.addEventListener('click', function(e) {
        if (e.target === modal) {
          modal.remove();
        }
      });
    });
  });