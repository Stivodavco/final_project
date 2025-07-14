document.querySelectorAll(".restricted-characters").forEach(input => {
    const form = document.querySelector("form")
    const pattern = /^[a-zA-Z0-9_-]+$/;
    input.addEventListener("input", () => {
        if (pattern.test(input.value)) {
            input.classList.add("is-valid");
            input.classList.remove("is-invalid");
        } else {
            input.classList.add("is-invalid");
            input.classList.remove("is-valid");
        }
    });
    form.addEventListener('submit', (event) => {
    if (!pattern.test(input.value)) {
      event.preventDefault();
      input.classList.add('is-invalid');
      input.classList.remove('is-valid');
      input.focus();
    }
  });
});