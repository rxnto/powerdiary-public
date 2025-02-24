document.addEventListener('DOMContentLoaded', function () {
    const muscleNames = {
        'soubou': '僧帽筋',
        'chest': '胸筋',
        'kouhaikin': '広背筋',
        'trapsmiddle': '背中中部',
        'shoulders': '肩',
        'biceps': '上腕二頭筋',
        'triceps': '上腕三頭筋',
        'zenwan': '前腕',
        'abs': '腹筋',
        'hukushakin': '腹斜筋',
        'quads': '大腿四頭筋',
        'hamstrings': 'ハムストリングス',
        'calves': 'ふくらはぎ',
        'lowerback': '腰部',
        'glutes': '臀筋'
    };

    function updateMuscleCounts(data) {
        const container = document.getElementById('muscle-counts');
        container.innerHTML = '';

        Object.entries(muscleNames).forEach(([key, name]) => {
            const count = data[key] || 0;
            const div = document.createElement('div');
            div.className = 'muscle-count-item';
            div.innerHTML = `
                <strong>${name}:</strong> ${count}回
            `;
            container.appendChild(div);
        });
    }

    // 履歴アイテムのクリックイベント
    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', function () {
            const year = this.dataset.year;
            const month = this.dataset.month;

            // アクティブ状態の更新
            document.querySelectorAll('.history-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            // データの取得
            fetch(`/api/monthly-muscle-counts/${year}/${month}/`)
                .then(response => response.json())
                .then(data => {
                    updateMuscleCounts(data);
                })
                .catch(error => console.error('Error:', error));
        });
    });

    // 日付の変更を監視
    function checkDateChange() {
        const currentDate = new Date();
        const lastCheckedDate = localStorage.getItem('lastCheckedDate');

        if (lastCheckedDate) {
            const lastDate = new Date(lastCheckedDate);
            if (lastDate.getMonth() !== currentDate.getMonth() ||
                lastDate.getFullYear() !== currentDate.getFullYear()) {
                // 月が変わった場合、自動的に月次更新を実行
                fetch('/api/advance-month/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        }
                    });
            }
        }

        localStorage.setItem('lastCheckedDate', currentDate.toISOString());
    }

    // 1時間ごとに日付チェック
    checkDateChange();
    setInterval(checkDateChange, 3600000);


    // 日付変更ボタンのクリックイベント
    document.getElementById('nextMonthBtn').addEventListener('click', function () {
        console.log('Next month button clicked'); // デバッグ出力

        fetch('/api/advance-month/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({}) // 空のJSONオブジェクトを送信
        })
            .then(response => {
                console.log('Response received:', response); // デバッグ出力
                return response.json();
            })
            .then(data => {
                console.log('Data received:', data); // デバッグ出力
                if (data.success) {
                    location.reload();
                } else {
                    console.error('Error:', data.error);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
            });
    });

    // CSRFトークン取得
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

    // 最初の履歴アイテムをクリック
    const firstItem = document.querySelector('.history-item');
    if (firstItem) {
        firstItem.click();
    }
});