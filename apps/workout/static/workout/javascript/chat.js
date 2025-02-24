document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const endButton = document.getElementById('end-button');
    const historiesList = document.getElementById('chat-histories');

    let currentMessages = []; // メッセージ履歴を保持する配列
    let isViewingHistory = false; // 履歴閲覧モードかどうか

    // メッセージを追加する関数
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
        // messageDiv.textContent = content;
        messageDiv.innerHTML = isUser ? content : formatChatMessage(content);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // メッセージを配列に追加（履歴閲覧モードでない場合のみ）
        if (!isViewingHistory) {
            currentMessages.push({
                is_user: isUser,
                content: content
            });
        }
    }

    // メッセージを送信する関数
    function sendMessage() {
        const message = userInput.value.trim();
        if (message && !isViewingHistory) {
            addMessage(message, true);
            userInput.value = '';
            adjustTextareaHeight();

            fetch('/chat_response/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            })
                .then(response => {
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let aiMessage = '';
                    let aiMessageElement = null;

                    function readStream() {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                if (aiMessage && !isViewingHistory) {
                                    currentMessages.push({
                                        is_user: false,
                                        content: aiMessage
                                    });
                                }
                                return;
                            }

                            const chunk = decoder.decode(value);
                            const lines = chunk.split('\n');

                            lines.forEach(line => {
                                if (line.startsWith('data: ')) {
                                    const content = line.slice(6);
                                    if (content === '[DONE]') {
                                        // Do nothing, we've already added the message
                                    } else {
                                        aiMessage += content;
                                        if (!aiMessageElement) {
                                            aiMessageElement = document.createElement('div');
                                            aiMessageElement.classList.add('message', 'ai-message');
                                            chatMessages.appendChild(aiMessageElement);
                                        }
                                        aiMessageElement.innerHTML = formatChatMessage(aiMessage);
                                        chatMessages.scrollTop = chatMessages.scrollHeight;
                                    }
                                }
                            });

                            readStream();
                        });
                    }

                    readStream();
                })
                .catch(error => console.error('Error:', error));
        }
    }

    // チャット履歴を保存する関数
    async function saveChatHistory() {
        if (currentMessages.length === 0) return false;

        console.log('Saving chat history...', currentMessages); // デバッグ用

        try {
            const response = await fetch('/chat/save-history/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ messages: currentMessages })
            });

            const data = await response.json();
            console.log('Save response:', data); // デバッグ用

            if (data.success) {
                currentMessages = []; // メッセージ履歴をクリア
                loadChatHistories(); // 履歴一覧を更新
                return true;
            } else {
                console.error('Error saving chat history:', data.error);
                return false;
            }
        } catch (error) {
            console.error('Error:', error);
            return false;
        }
    }

    // チャット履歴一覧を読み込む関数
    async function loadChatHistories() {
        try {
            const response = await fetch('/chat/histories/');
            const data = await response.json();
            if (data.success) {
                historiesList.innerHTML = ''; // 一覧をクリア
                data.histories.forEach(history => {
                    const historyItem = document.createElement('div');
                    historyItem.classList.add('history-item');

                    // フレックスコンテナを作成
                    const flexContainer = document.createElement('div');
                    flexContainer.classList.add('history-item-content');

                    // タイトルを表示
                    const titleSpan = document.createElement('span');
                    titleSpan.textContent = history.title;
                    titleSpan.classList.add('history-title');
                    flexContainer.appendChild(titleSpan);

                    // 削除ボタンを作成
                    const deleteButton = document.createElement('button');
                    deleteButton.innerHTML = '<i class="fa fa-times"></i>';
                    deleteButton.classList.add('delete-history-button');
                    deleteButton.onclick = (e) => {
                        e.stopPropagation(); // クリックイベントの伝播を停止
                        confirmDeleteHistory(history.id);
                    };
                    flexContainer.appendChild(deleteButton);

                    historyItem.appendChild(flexContainer);

                    // 履歴クリック時の処理
                    historyItem.addEventListener('click', (e) => {
                        if (!e.target.classList.contains('delete-history-button')) {
                            loadChatHistory(history.id);
                        }
                    });

                    historiesList.appendChild(historyItem);
                });
            }
        } catch (error) {
            console.error('Error loading chat histories:', error);
        }
    }

    // 履歴を削除する確認モーダルを表示する関数
    function confirmDeleteHistory(historyId) {
        const modal = document.createElement('div');
        modal.classList.add('modal-background');
        modal.innerHTML = `
            <div class="modal-content">
                <h3>チャット履歴の削除</h3>
                <p>このチャット履歴を削除してもよろしいですか？</p>
                <div class="modal-buttons">
                    <button class="modal-button cancel">キャンセル</button>
                    <button class="modal-button delete">削除</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const cancelButton = modal.querySelector('.cancel');
        const deleteButton = modal.querySelector('.delete');

        cancelButton.onclick = () => {
            document.body.removeChild(modal);
        };

        deleteButton.onclick = async () => {
            try {
                const response = await fetch(`/chat/history/${historyId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                const data = await response.json();
                if (data.success) {
                    document.body.removeChild(modal);
                    loadChatHistories(); // 履歴一覧を更新

                    // 現在表示中の履歴が削除された場合は新規チャットを開始
                    if (isViewingHistory) {
                        startNewChat(false);
                    }
                } else {
                    console.error('Error deleting chat history:', data.error);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        };
    }

    // 新規チャット確認モーダルを表示する関数
    async function handleNewChat() {
        // 現在のチャットがあり、履歴閲覧モードでない場合
        if (currentMessages.length > 0 && !isViewingHistory) {
            return new Promise((resolve) => {
                const modal = document.createElement('div');
                modal.classList.add('modal-background');
                modal.innerHTML = `
                    <div class="modal-content">
                        <h3>チャットの保存</h3>
                        <p>現在のチャットを保存してから新しいチャットを開始しますか？</p>
                        <div class="modal-buttons">
                            <button class="modal-button cancel">保存せずに新規チャット</button>
                            <button class="modal-button delete">保存して新規チャット</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                modal.querySelector('.cancel').onclick = () => {
                    document.body.removeChild(modal);
                    resolve(false);
                };

                modal.querySelector('.delete').onclick = () => {
                    document.body.removeChild(modal);
                    resolve(true);
                };
            });
        }
        return false;
    }

    // 特定のチャット履歴を読み込む関数
    async function loadChatHistory(historyId) {
        // 現在のチャットがあり、履歴閲覧モードでない場合は保存
        if (currentMessages.length > 0 && !isViewingHistory) {
            await saveChatHistory();
        }

        try {
            const response = await fetch(`/chat/history/${historyId}/`);
            const data = await response.json();
            if (data.success) {
                isViewingHistory = true;
                chatMessages.innerHTML = '';
                data.messages.forEach(msg => {
                    addMessage(msg.content, msg.is_user);
                });

                // 入力欄と全てのボタンを無効化
                userInput.disabled = true;
                sendButton.disabled = true;
                endButton.disabled = true;

                // スタイルも変更して無効化を視覚的に表示
                userInput.style.opacity = '0.5';
                sendButton.style.opacity = '0.5';
                endButton.style.opacity = '0.5';

                // 現在のメッセージをクリア（履歴表示中は新しいメッセージを保存しない）
                currentMessages = [];
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    // 新規チャットを開始する関数
    async function startNewChat(shouldSave = false) {
        try {
            // 保存が必要な場合
            if (shouldSave && currentMessages.length > 0 && !isViewingHistory) {
                const saved = await saveChatHistory();
                if (!saved) {
                    console.error('Failed to save chat history');
                    return;
                }
            }

            // チャットをリセット
            isViewingHistory = false;
            chatMessages.innerHTML = '';
            currentMessages = [];

            // UIを有効化
            userInput.disabled = false;
            sendButton.disabled = false;
            endButton.disabled = false;

            userInput.style.opacity = '1';
            sendButton.style.opacity = '1';
            endButton.style.opacity = '1';

            // 履歴一覧を更新
            await loadChatHistories();
        } catch (error) {
            console.error('Error starting new chat:', error);
        }
    }

    // テキストエリアの高さを調整する関数
    function adjustTextareaHeight() {
        userInput.style.height = 'auto';
        userInput.style.height = (userInput.scrollHeight) + 'px';
    }

    // イベントリスナーの設定
    sendButton.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    userInput.addEventListener('input', adjustTextareaHeight);

    endButton.addEventListener('click', async () => {
        await saveChatHistory();
        startNewChat(false);
    });

    // 新規チャットボタンのイベントリスナーを設定
    const newChatButton = document.getElementById('new-chat-button');
    if (newChatButton) {
        newChatButton.addEventListener('click', async () => {
            console.log('New chat button clicked'); // デバッグ用
            const shouldSave = await handleNewChat();
            console.log('Should save:', shouldSave); // デバッグ用

            if (shouldSave) {
                console.log('Attempting to save chat history...'); // デバッグ用
                try {
                    const saved = await saveChatHistory();
                    console.log('Save result:', saved); // デバッグ用
                    if (!saved) {
                        console.error('Failed to save chat history');
                        return;
                    }
                } catch (error) {
                    console.error('Error saving chat history:', error);
                    return;
                }
            }

            // チャットをリセット
            isViewingHistory = false;
            chatMessages.innerHTML = '';
            currentMessages = [];

            // UIを有効化
            userInput.disabled = false;
            sendButton.disabled = false;
            endButton.disabled = false;

            userInput.style.opacity = '1';
            sendButton.style.opacity = '1';
            endButton.style.opacity = '1';

            // 履歴一覧を更新
            await loadChatHistories();
        });
    }

    // ページを離れる前にチャット履歴を保存
    window.addEventListener('beforeunload', () => {
        if (currentMessages.length > 0 && !isViewingHistory) {
            saveChatHistory();
        }
    });

    // CSRFトークンを取得する関数
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // 初期読み込み時にチャット履歴一覧を表示
    loadChatHistories();
});