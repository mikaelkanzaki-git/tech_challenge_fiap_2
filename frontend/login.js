const loginForm = document.querySelector("#login-form");
const loginMessage = document.querySelector("#login-message");

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginMessage.textContent = "Autenticando...";

  const formData = new FormData(loginForm);
  const body = new URLSearchParams();
  body.set("username", formData.get("username"));
  body.set("password", formData.get("password"));

  try {
    const response = await fetch("/token", {
      method: "POST",
      headers: {"Content-Type": "application/x-www-form-urlencoded"},
      body,
    });
    const data = await response.json();

    if (!response.ok) {
      loginMessage.textContent = data.detail || "Não foi possível autenticar.";
      return;
    }

    sessionStorage.setItem("access_token", data.access_token);
    sessionStorage.setItem("patient_data", JSON.stringify({}));
    window.location.href = "/chat.html";
  } catch (error) {
    loginMessage.textContent = "Não foi possível conectar com a API.";
  }
});
