function formatChatMessage(text) {
    // メッセージを整形する処理
    let formattedText = text
        // 文末の。で改行を入れる
        .replace(/。/g, '。\n')
        // 箇条書きの前に空行を入れる
        .replace(/\n- /g, '\n\n- ')
        // 箇条書きの後に空行を入れる
        .replace(/\n(?!-|$)/g, '\n\n');

    // HTMLに変換（安全な形で）
    formattedText = formattedText
        .split('\n')
        .map(line => {
            // 箇条書きの処理
            if (line.trim().startsWith('- ')) {
                return `<li class="chat-list-item">${line.substring(2)}</li>`;
            }
            // 通常の段落の処理
            return line.trim() ? `<p class="chat-paragraph">${line}</p>` : '';
        })
        .join('');

    // 箇条書きをulタグで囲む
    formattedText = formattedText
        .replace(/<li class="chat-list-item">/g, '<ul class="chat-list"><li class="chat-list-item">')
        .replace(/<\/li><p/g, '</li></ul><p')
        .replace(/<\/li>(?!<\/ul>)/g, '</li></ul>');

    return formattedText;
}

// スタイルを追加
const style = document.createElement('style');
style.textContent = `
    .chat-paragraph {
        margin-bottom: 1em;
        line-height: 1.6;
    }

    .chat-list {
        margin: 1em 0;
        padding-left: 2em;
    }

    .chat-list-item {
        margin-bottom: 0.8em;
        line-height: 1.4;
        color: #ffffff;
    }

    .message {
        margin: 10px 0;
        padding: 15px;
        border-radius: 10px;
        max-width: 80%;
    }

    .ai-message {
        background: #444444;
        border-left: 4px solid #dc3545;
        color: #ffffff;
    }

    .user-message {
        background: #dc3545;
        margin-left: auto;
        text-align: left;
        color: #ffffff;
    }

    .chat-paragraph {
        color: #ffffff;
        margin: 0.5em 0;
    }
`;
document.head.appendChild(style);

// メッセージ表示関数を修正
function displayMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = isUser ? 'user-message' : 'assistant-message';
    
    // アシスタントのメッセージの場合、フォーマットを適用
    if (!isUser) {
        content = formatChatMessage(content);
    }
    
    messageDiv.innerHTML = content;
    document.getElementById('chat-messages').appendChild(messageDiv);
    messageDiv.scrollIntoView({ behavior: 'smooth' });
}