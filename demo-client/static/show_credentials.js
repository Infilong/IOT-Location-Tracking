const showCredentialsCheckbox = document.getElementById("show-credentials");
const credentialsFields = document.getElementById("credentials-fields");

showCredentialsCheckbox.addEventListener("change", function () {
  if (showCredentialsCheckbox.checked) {
    credentialsFields.style.display = "block";
  } else {
    credentialsFields.style.display = "none";
  }
});
