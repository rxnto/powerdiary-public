$(document).ready(function () {
    showAll();

    $('#category-filter').change(function () {
      var selectedCategory = $(this).val();

      if (selectedCategory === 'all') {
        showAll();
      } else {
        filterByCategory(selectedCategory);
      }
    });

    function showAll() {
      $('.col-lg-12').show();
    }

    function filterByCategory(category) {
      $('.col-lg-12').hide(); 

      $('.col-lg-12[data-category="' + category + '"]').show();
    }
  });