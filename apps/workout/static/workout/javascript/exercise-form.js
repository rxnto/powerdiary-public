// static/workout/javascript/exercise-form.js

document.addEventListener('DOMContentLoaded', function () {
    // 部位ごとの代表的な種目のプリセット
    const exercisePresets = {
        soubou: [
            'シュラッグ',
            'ベントオーバーロー',
            'ダンベルシュラッグ',
            'アップライトロウ',
            'ケーブルフェイスプル',
            'デッドリフト',
            'マシンシュラッグ'
        ],
        chest: [
            'ベンチプレス',
            'ダンベルフライ',
            'ディップス',
            'プッシュアップ',
            'インクラインベンチプレス',
            'ケーブルクロスオーバー'
        ],
        kouhaikin: [
            'ラットプルダウン',
            'チンニング',
            'ベントオーバーロー',
            'シーテッドロー',
            'デッドリフト'
        ],
        trapsmiddle: [
            'ラットプルダウン',
            'ベントオーバーロー',
            'シーテッドロー',
            'ダンベルローイング',
            'Tバーロー',
            'ケーブルロー',
            'プルアップ'
        ],
        shoulders: [
            'ミリタリープレス',
            'サイドレイズ',
            'フロントレイズ',
            'リアレイズ',
            'アップライトロー'
        ],
        biceps: [
            'ダンベルカール',
            'バーベルカール',
            'ハンマーカール',
            'プリーチャーカール',
            'インクラインカール'
        ],
        triceps: [
            'トライセプスプレスダウン',
            'スカルクラッシャー',
            'フレンチプレス',
            'ケーブルプッシュダウン'
        ],
        zenwan: [
            'リストカール',
            'リバースリストカール',
            'ハンマーカール',
            'リバースカール',
            'ファーマーズウォーク',
            'デッドハング'
        ],
        abs: [
            'クランチ',
            'プランク',
            'レッグレイズ',
            'シットアップ',
            'ロシアンツイスト',
            'デッドバグ'
        ],
        hukushakin: [  
            'サイドクランチ',  
            'ツイストクランチ',  
            'ロシアンツイスト',  
            'サイドプランク',  
            'ウィンドミル',  
            'ハンギングレッグツイスト',  
            'ケーブルウッドチョッパー'  
        ]  
        ,
        quads: [
            'スクワット',
            'レッグプレス',
            'レッグエクステンション',
            'ブルガリアンスクワット',
            'ハックスクワット'
        ],
        hamstrings: [
            'レッグカール',
            'ルーマニアンデッドリフト',
            'グッドモーニング',
            'シングルレッグデッドリフト'
        ],
        calves: [
            'カーフレイズ',
            'シーテッドカーフレイズ',
            'ドンキーカーフレイズ',
            'レッグプレスカーフレイズ'
        ],
        lowerback: [  
            'バックエクステンション',
            'デッドリフト',
            'ルーマニアンデッドリフト'
        ],
        glutes: [  
            'ヒップスラスト',
            'ブルガリアンスクワット',
            'ルーマニアンデッドリフト',
            'ケーブルキックバック',
            'グルートブリッジ'
        ]
    };

    const form = document.getElementById('exercise-form');
    const targetMuscleSelect = document.getElementById('target_muscle');
    const presetNameSelect = document.getElementById('preset_name');
    const customNameInput = document.getElementById('custom_name');
    const isCustomCheckbox = document.getElementById('isCustomExercise');
    const persistValuesCheckbox = document.getElementById('persistValues');
    const presetExerciseDiv = document.getElementById('preset-exercise-div');
    const customExerciseDiv = document.getElementById('custom-exercise-div');
    const finalNameInput = document.getElementById('final_name');
    const weightInput = document.getElementById('weight');
    const repsInput = document.getElementById('repetitions');

    // チェックボックスの状態を復元
    isCustomCheckbox.checked = localStorage.getItem('isCustom') === 'true';
    persistValuesCheckbox.checked = localStorage.getItem('persistValues') === 'true';

    // 値を保存する関数
    function saveValues() {
        if (persistValuesCheckbox.checked) {
            localStorage.setItem('target_muscle', targetMuscleSelect.value);
            localStorage.setItem('isCustom', isCustomCheckbox.checked);
            localStorage.setItem('persistValues', persistValuesCheckbox.checked);
            localStorage.setItem('weight', weightInput.value);
            localStorage.setItem('repetitions', repsInput.value);

            if (isCustomCheckbox.checked) {
                localStorage.setItem('custom_name', customNameInput.value);
            } else {
                localStorage.setItem(`preset_${targetMuscleSelect.value}`, presetNameSelect.value);
            }
        }
    }

    // フォームをリセットする関数
    function resetForm() {
        targetMuscleSelect.value = '';
        presetNameSelect.value = '';
        customNameInput.value = '';
        weightInput.value = '';
        repsInput.value = '';
        localStorage.clear();
    }

    // ターゲット部位が変更されたときの処理
    targetMuscleSelect.addEventListener('change', function () {
        const muscle = this.value;
        const exercises = exercisePresets[muscle] || [];

        // プリセット種目の選択肢を更新
        presetNameSelect.innerHTML = '<option value="">種目を選択</option>';
        exercises.forEach(exercise => {
            const option = document.createElement('option');
            option.value = exercise;
            option.textContent = exercise;
            presetNameSelect.appendChild(option);
        });

        // 値を保持する場合は以前の選択を復元
        if (persistValuesCheckbox.checked && !isCustomCheckbox.checked) {
            const savedPresetName = localStorage.getItem(`preset_${muscle}`);
            if (savedPresetName) {
                presetNameSelect.value = savedPresetName;
            }
        }

        saveValues();
    });

    // フォーム送信時の処理
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        if (isCustomCheckbox.checked) {
            finalNameInput.value = customNameInput.value;
        } else {
            finalNameInput.value = presetNameSelect.value;
        }

        if (persistValuesCheckbox.checked) {
            saveValues();
        } else {
            localStorage.clear();
        }

        this.submit();
    });

    // カスタム種目チェックボックスの切り替え
    isCustomCheckbox.addEventListener('change', function () {
        if (this.checked) {
            presetExerciseDiv.style.display = 'none';
            customExerciseDiv.style.display = 'block';
            const savedCustomName = localStorage.getItem('custom_name');
            if (savedCustomName && persistValuesCheckbox.checked) {
                customNameInput.value = savedCustomName;
            }
        } else {
            presetExerciseDiv.style.display = 'block';
            customExerciseDiv.style.display = 'none';
            if (persistValuesCheckbox.checked) {
                const muscle = targetMuscleSelect.value;
                const savedPresetName = localStorage.getItem(`preset_${muscle}`);
                if (savedPresetName) {
                    presetNameSelect.value = savedPresetName;
                }
            }
        }
        saveValues();
    });

    // 値の保持チェックボックスの切り替え
    persistValuesCheckbox.addEventListener('change', function () {
        if (this.checked) {
            saveValues();
        } else {
            resetForm();
        }
        localStorage.setItem('persistValues', this.checked);
    });

    // ページ読み込み時の処理
    if (persistValuesCheckbox.checked) {
        const savedMuscle = localStorage.getItem('target_muscle');
        if (savedMuscle) {
            targetMuscleSelect.value = savedMuscle;
            targetMuscleSelect.dispatchEvent(new Event('change'));
        }

        isCustomCheckbox.dispatchEvent(new Event('change'));

        const savedWeight = localStorage.getItem('weight');
        if (savedWeight) weightInput.value = savedWeight;

        const savedReps = localStorage.getItem('repetitions');
        if (savedReps) repsInput.value = savedReps;
    }
});