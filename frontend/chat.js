const token = sessionStorage.getItem("access_token");
const messages = document.querySelector("#messages");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");
const chatStatus = document.querySelector("#chat-status");
const patientSummary = document.querySelector("#patient-summary");
const logoutButton = document.querySelector("#logout-button");
const quickActions = document.querySelector("#quick-actions");

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

const fieldGuidance = {
  age: {
    text: "Faixa esperada: 0 a 120 anos.",
  },
  heart_rate: {
    text: "Faixa esperada: 0 a 250 batimentos por minuto.",
  },
  systolic_blood_pressure: {
    text: "Faixa esperada: 0 a 300 mmHg.",
  },
  oxygen_saturation: {
    text: "Faixa esperada: 0 a 100%.",
  },
  body_temperature: {
    text: "Faixa esperada: 30 a 45 graus.",
  },
  pain_level: {
    text: "Escolha a intensidade da dor: 0 sem dor, 10 dor muito intensa.",
    buttons: Array.from({length: 11}, (_, index) => ({
      label: String(index),
      value: String(index),
      kind: "pain-scale",
      level: index,
    })),
  },
  chronic_disease_count: {
    text: "Faixa esperada: 0 a 50 doencas cronicas.",
  },
  previous_er_visits: {
    text: "Faixa esperada: 0 a 200 visitas anteriores.",
  },
  arrival_mode: {
    text: "Escolha uma das opcoes de chegada.",
    buttons: [
      {label: "Andando", value: "andando"},
      {label: "Cadeira de rodas", value: "cadeira de rodas"},
      {label: "Ambulancia", value: "ambulancia"},
    ],
  },
};

if (!token) {
  window.location.href = "/";
}

appendMessage("agent", "Ola. Vamos coletar os dados para calcular a triagem. Para comecar, qual e a idade do paciente? Informe um valor entre 0 e 120 anos.");
renderSummary(readPatientData());
renderQuickActions(["age"]);

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) {
    return;
  }

  await sendMessage(message);
});

logoutButton.addEventListener("click", () => {
  sessionStorage.clear();
  window.location.href = "/";
});

async function sendMessage(message) {
  appendMessage("user", message);
  chatInput.value = "";
  setFormEnabled(false);
  chatStatus.textContent = "processando";
  quickActions.innerHTML = "";

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
      setFormEnabled(true);
      return;
    }

    sessionStorage.setItem("patient_data", JSON.stringify(data.patient_data));
    renderSummary(data.patient_data);
    appendMessage("agent", data.message);

    if (data.prediction) {
      setFormEnabled(false);
      chatStatus.textContent = "finalizado";
      quickActions.innerHTML = "";
      return;
    }

    renderQuickActions(data.missing_fields);
    setFormEnabled(true);
    chatInput.focus();
  } catch (error) {
    appendMessage("agent", "Nao foi possivel conectar com a API.");
    setFormEnabled(true);
  } finally {
    if (chatStatus.textContent !== "finalizado") {
      chatStatus.textContent = "online";
    }
  }
}

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

function renderQuickActions(missingFields) {
  quickActions.innerHTML = "";
  const currentField = missingFields?.[0];
  const guidance = fieldGuidance[currentField];

  if (!guidance) {
    return;
  }

  const helpText = document.createElement("p");
  helpText.className = "quick-actions-help";
  helpText.textContent = guidance.text;
  quickActions.appendChild(helpText);

  if (!guidance.buttons) {
    return;
  }

  const buttonList = document.createElement("div");
  buttonList.className = currentField === "pain_level" ? "pain-scale" : "choice-list";

  guidance.buttons.forEach((action) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = action.kind === "pain-scale" ? "scale-button" : "choice-button";
    button.textContent = action.label;
    button.setAttribute("aria-label", `Responder ${action.label}`);

    if (action.kind === "pain-scale") {
      button.style.setProperty("--scale-ratio", action.level / 10);
    }

    button.addEventListener("click", () => {
      sendMessage(action.value);
    });
    buttonList.appendChild(button);
  });

  quickActions.appendChild(buttonList);
}

function setFormEnabled(isEnabled) {
  chatInput.disabled = !isEnabled;
  chatForm.querySelector("button").disabled = !isEnabled;
}
