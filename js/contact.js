const form = document.getElementById("contactForm");
const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const messageInput = document.getElementById("message");
const nameError = document.getElementById("nameError");
const emailError = document.getElementById("emailError");
const messageError = document.getElementById("messageError");
const messageCount = document.getElementById("messageCount");
const successMessage = document.getElementById("formSuccess");

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const validateName = () => {
  const value = nameInput.value.trim();
  if (value.length === 0) {
    nameError.textContent = "Please enter your name.";
    nameInput.classList.add("error");
    return false;
  }
  nameError.textContent = "";
  nameInput.classList.remove("error");
  return true;
};

const validateEmail = () => {
  const value = emailInput.value.trim();
  if (!emailPattern.test(value)) {
    emailError.textContent = "Please enter a valid email address.";
    emailInput.classList.add("error");
    return false;
  }
  emailError.textContent = "";
  emailInput.classList.remove("error");
  return true;
};

const validateMessage = () => {
  const value = messageInput.value.trim();
  if (value.length < 20) {
    messageError.textContent = "Message should be at least 20 characters.";
    messageInput.classList.add("error");
    return false;
  }
  if (value.length > 1000) {
    messageError.textContent = "Please keep your message under 1000 characters.";
    messageInput.classList.add("error");
    return false;
  }
  messageError.textContent = "";
  messageInput.classList.remove("error");
  return true;
};

if (form) {
  nameInput.addEventListener("blur", validateName);
  emailInput.addEventListener("blur", validateEmail);
  messageInput.addEventListener("blur", validateMessage);

  messageInput.addEventListener("input", () => {
    const length = messageInput.value.length;
    messageCount.textContent = length;
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const isValid =
      validateName() & validateEmail() & validateMessage(); // bitwise trick for all calls
    if (!isValid) {
      successMessage.hidden = true;
      return;
    }

    successMessage.hidden = false;
    form.reset();
    messageCount.textContent = "0";
  });
}