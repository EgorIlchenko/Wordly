function validateForm() {
    const agree = document.getElementById('privacy_agree');
    const error = document.getElementById('privacy_error');
    if (!agree.checked) {
        error.style.display = 'block';
        return false;
    } else {
        error.style.display = 'none';
        return true;
    }
}
