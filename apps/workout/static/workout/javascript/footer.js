document.addEventListener('DOMContentLoaded', function () {
    var footer = document.querySelector('.footer');

    function shouldHideFooter() {
        return window.innerHeight + window.scrollY >= document.body.offsetHeight * 0.9;
    }

    function handleScroll() {
        if (shouldHideFooter()) {
            footer.style.display = 'none';
        } else {
            footer.style.display = 'block';
        }
    }

    window.addEventListener('scroll', handleScroll);
});