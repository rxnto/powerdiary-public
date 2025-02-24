const workoutCategories = ['僧帽', '胸', '背中', '肩', '上腕', '前腕', '腹', '腹斜', '太腿', 'ふくらはぎ', '腰', '尻'];

document.addEventListener('DOMContentLoaded', function() {
  const nameInput = document.getElementById('name');
  const dropdownDiv = document.createElement('div');
  dropdownDiv.className = 'workout-dropdown';
  nameInput.parentNode.appendChild(dropdownDiv);

  nameInput.addEventListener('focus', showDropdown);
  
  document.addEventListener('click', function(e) {
    if (!nameInput.contains(e.target) && !dropdownDiv.contains(e.target)) {
      dropdownDiv.style.display = 'none';
    }
  });

  // カテゴリーの表示
  workoutCategories.forEach(category => {
    const categoryDiv = document.createElement('div');
    categoryDiv.className = 'category';
    categoryDiv.textContent = category;
    categoryDiv.onclick = () => {
      nameInput.value = category;
      dropdownDiv.style.display = 'none';
    };
    dropdownDiv.appendChild(categoryDiv);
  });
});

function showDropdown() {
  const dropdownDiv = document.querySelector('.workout-dropdown');
  dropdownDiv.style.display = 'block';
}