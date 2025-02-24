function duplicateExercise(exerciseId, workoutId) {
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  const xhr = new XMLHttpRequest();
  xhr.open('POST', `/duplicate-exercise/${exerciseId}/${workoutId}/`);
  xhr.setRequestHeader('X-CSRFToken', csrftoken);

  xhr.onload = function () {
    const response = JSON.parse(xhr.responseText);
    if (response.success) {
      // alert(response.message);// 確認用アラート
      location.reload();
    } else {
      alert(response.message);
    }
  };

  xhr.send();
}