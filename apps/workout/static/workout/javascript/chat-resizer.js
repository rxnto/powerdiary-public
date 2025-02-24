document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const resizer = document.createElement('div');
    resizer.className = 'resizer';
    
    // リサイザーを入力欄の上に挿入
    const inputContainer = document.getElementById('input-container');
    chatContainer.insertBefore(resizer, inputContainer);

    let isResizing = false;
    let startHeight;
    let startY;

    resizer.addEventListener('mousedown', function(e) {
        isResizing = true;
        startHeight = chatContainer.offsetHeight;
        startY = e.clientY;
        
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', stopResizing);
    });

    function handleMouseMove(e) {
        if (!isResizing) return;

        const diffY = e.clientY - startY;
        const newHeight = startHeight + diffY;
        
        // 最小値と最大値を設定
        const minHeight = 300;
        const maxHeight = window.innerHeight * 0.9;
        
        if (newHeight >= minHeight && newHeight <= maxHeight) {
            chatContainer.style.height = newHeight + 'px';
        }
    }

    function stopResizing() {
        isResizing = false;
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', stopResizing);
    }
});