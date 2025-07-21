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

function toggleCheck() {
    document.querySelectorAll(".required-toggler").forEach(checkbox => {
        const requiredTarget = document.getElementById(checkbox.dataset.target);
        const hide = document.getElementById(checkbox.dataset.hide);

        if (checkbox.checked === true) {
            requiredTarget.removeAttribute("required");
            hide.classList.add("d-none");
        } else {
            requiredTarget.setAttribute("required", "")
            hide.classList.remove("d-none")
        }
    })
}

toggleCheck()