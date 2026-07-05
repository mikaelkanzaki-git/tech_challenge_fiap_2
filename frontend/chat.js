const token = sessionStorage.getItem("access_token");
const messages = document.querySelector("#messages");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");
const chatStatus = document.querySelector("#chat-status");
const patientSummary = document.querySelector("#patient-summary");
const logoutButton = document.querySelector("#logout-button");

const fieldLabels = {
  age: "Idade",
  heart_rate: "Frequencia cardiaca",
  systolic_blood_pressure: "Pressao sistolica",
  oxygen_saturation: "Saturacao",
  body_temperature: "Temperatura",
  pain_level: "Dor",
  chronic_disease_count: "Doencas cronicas",
  previous_er_visits: "Visitas anteriores",
  arrival_mode: "Modo de chegada",
};

if (!token) {
  window.location.href = "/";
}

appendMessage("agent", "Ola. Vamos coletar os dados para calcular a triagem. Para comecar, qual e a idade do paciente?");
renderSummary(readPatientData());

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) {
    return;
  }

  appendMessage("user", message);
  chatInput.value = "";
  chatStatus.textContent = "processando";

  try {
    const response = await fetch("/chat/message", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        patient_data: readPatientData(),
      }),
    });
    const data = await response.json();

    if (!response.ok) {
      appendMessage("agent", data.detail || "Nao foi possivel processar sua mensagem.");
      return;
    }

    sessionStorage.setItem("patient_data", JSON.stringify(data.patient_data));
    renderSummary(data.patient_data);
    appendMessage("agent", data.message);

    if (data.prediction) {
      chatInput.disabled = true;
      chatForm.querySelector("button").disabled = true;
      chatStatus.textContent = "finalizado";
    }
  } catch (error) {
    appendMessage("agent", "Nao foi possivel conectar com a API.");
  } finally {
    if (chatStatus.textContent !== "finalizado") {
      chatStatus.textContent = "online";
    }
  }
});

logoutButton.addEventListener("click", () => {
  sessionStorage.clear();
  window.location.href = "/";
});

function appendMessage(kind, text) {
  const messageElement = document.createElement("article");
  messageElement.className = `message ${kind}`;
  messageElement.textContent = text;
  messages.appendChild(messageElement);
  messages.scrollTop = messages.scrollHeight;
}

function readPatientData() {
  try {
    return JSON.parse(sessionStorage.getItem("patient_data")) || {};
  } catch (error) {
    return {};
  }
}

function renderSummary(patientData) {
  patientSummary.innerHTML = "";
  Object.entries(fieldLabels).forEach(([fieldName, label]) => {
    const term = document.createElement("dt");
    const description = document.createElement("dd");
    term.textContent = label;
    description.textContent = patientData[fieldName] ?? "pendente";
    patientSummary.append(term, description);
  });
}
