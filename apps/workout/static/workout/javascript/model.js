// static/workout/javascript/model.js

document.addEventListener('DOMContentLoaded', function() {
    function getColor(count) {
        // 10回で最大の濃さに
        const intensity = Math.min(count / 10, 1);
        const r = Math.round(231 + (254 - 231) * intensity);
        const g = Math.round(236 + (91 - 236) * intensity);
        const b = Math.round(239 + (127 - 239) * intensity);
        return `rgb(${r}, ${g}, ${b})`;
    }

    function updateMuscleColors(muscleCounts) {
        // 全ての部位リスト
        const muscleGroups = [
            'soubou',       // 僧帽筋
            'chest',         // 胸筋
            'kouhaikin',    // 広背筋
            'trapsmiddle',  // 背中中部
            'shoulders',    // 肩
            'biceps',       // 上腕二頭筋
            'triceps',      // 上腕三頭筋
            'zenwan',       // 前腕
            'abs',          // 腹筋
            'hukushakin',   // 腹斜筋
            'quads',        // 大腿四頭筋
            'hamstrings',   // ハムストリングス
            'calves',        // ふくらはぎ
            'lowerback',    // 腰部
            'glutes',       // 臀筋
            // 'jouwan',       // 上腕
        ];
        
        muscleGroups.forEach(muscle => {
            const count = muscleCounts[muscle] || 0;
            const elements = document.querySelectorAll(`[data-muscle="${muscle}"]`);
            elements.forEach(element => {
                const paths = element.querySelectorAll('path');
                paths.forEach(path => {
                    path.style.fill = getColor(count);
                });
            });
        });

        console.log('Updated muscle colors:', muscleCounts); // デバッグ用
    }

    function fetchMuscleData() {
        fetch('/api/muscle-counts/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Received muscle data:', data); // デバッグ用
                updateMuscleColors(data);
            })
            .catch(error => {
                console.error('Error fetching muscle data:', error);
            });
    }

    // 初期データの取得
    fetchMuscleData();

    // 30秒ごとに更新
    setInterval(fetchMuscleData, 30000);
});