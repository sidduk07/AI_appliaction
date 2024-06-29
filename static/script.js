document.addEventListener("DOMContentLoaded", function() {
    const uploadForm = document.querySelector("form[action='/upload']");
    const answerForm = document.querySelector("form[action='/answer']");

    uploadForm.addEventListener("submit", function(event) {
        const fileInput = uploadForm.querySelector("input[type='file']");
        if (fileInput.files.length === 0) {
            event.preventDefault();
            alert("Please select a file to upload.");
        }
    });

    answerForm.addEventListener("submit", function(event) {
        const questionInput = answerForm.querySelector("input[name='question']");
        if (questionInput.value.trim() === "") {
            event.preventDefault();
            alert("Please enter a question.");
        }
    });
});
