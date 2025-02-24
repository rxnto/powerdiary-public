// $( document ).ready(function() {

//   $( '#end-workout' ).click(function() {
//     return confirm("ワークアウトを終了してもよろしいですか？");
//   });

//   $( '#delete-exercise' ).click(function() {
//     return confirm("このエクササイズを削除してもよろしいですか？");
//   });

//   $( '#delete-workout' ).click(function() {
//     return confirm("このワークアウトを削除してもよろしいですか？これは取り消せません。");
//   });

// });
$(document).ready(function () {
  // モーダルを表示する共通関数
  function showConfirmModal(title, message, onConfirm) {
    const modal = document.createElement('div');
    modal.classList.add('modal-background');
    modal.innerHTML = `
          <div class="modal-content">
              <h3>${title}</h3>
              <p>${message}</p>
              <div class="modal-buttons">
                  <button class="modal-button cancel">キャンセル</button>
                  <button class="modal-button delete">はい</button>
              </div>
          </div>
      `;

    document.body.appendChild(modal);

    // モーダルのボタンにイベントリスナーを追加
    const cancelButton = modal.querySelector('.cancel');
    const confirmButton = modal.querySelector('.delete');

    cancelButton.onclick = () => {
      document.body.removeChild(modal);
    };

    confirmButton.onclick = () => {
      document.body.removeChild(modal);
      onConfirm(); // 確認後の処理を実行
    };
  }

  // ワークアウト終了の確認
  $('#end-workout').click(function (e) {
    e.preventDefault();
    const form = $(this).closest('form');
    showConfirmModal(
      'ワークアウトの終了',
      'ワークアウトを終了してもよろしいですか？',
      () => form.submit()
    );
    return false;
  });

  // エクササイズ削除の確認
  $('#delete-exercise').click(function (e) {
    e.preventDefault();
    const link = $(this);
    showConfirmModal(
      'エクササイズの削除',
      'このエクササイズを削除してもよろしいですか？',
      () => window.location.href = link.attr('href')
    );
    return false;
  });

  // ワークアウト削除の確認
  $('#delete-workout').click(function (e) {
    e.preventDefault();
    const link = $(this);
    showConfirmModal(
      'ワークアウトの削除',
      'このワークアウトを削除してもよろしいですか？これは取り消せません。',
      () => window.location.href = link.attr('href')
    );
    return false;
  });
});