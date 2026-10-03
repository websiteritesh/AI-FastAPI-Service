const API = "";

// --- Tab switching ---
document.getElementById("tabs").addEventListener("click", (ev) => {
    const tab = ev.target.closest(".tab");
    if (!tab) return;
    const name = tab.dataset.tab;

    document.querySelectorAll(".tab").forEach(t => t.classList.toggle("active", t === tab));
    document.querySelectorAll(".panel").forEach(p => p.classList.toggle("active", p.id === `panel-${name}`));
});

// --- Status check ---
async function checkStatus() {
    const el = document.getElementById("apiStatus");
    try {
        const res = await fetch(`${API}/`);
        if (!res.ok) throw new Error();
        el.textContent = "online";
        el.className = "status ok";
    } catch {
        el.textContent = "unreachable";
        el.className = "status err";
    }
}

// Pretty-print a response into an <pre> output box.
// Uses textContent (never innerHTML) so nothing in the AI's output can run as HTML/script.
function showOutput(elementId, data, isError = false) {
    const el = document.getElementById(elementId);
    el.textContent = JSON.stringify(data, null, 2);
    el.classList.toggle("error", isError);
}

async function runRequest(path, body, outputId, btnId) {
    const btn = document.getElementById(btnId);
    btn.disabled = true;
    const originalText = btn.textContent;
    btn.textContent = "Running…";
    document.getElementById(outputId).textContent = "// waiting for response…";
    document.getElementById(outputId).classList.remove("error");

    try {
        const res = await fetch(`${API}${path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        showOutput(outputId, data, !!data.error);
    } catch (e) {
        showOutput(outputId, { error: "Couldn't reach the server. Make sure uvicorn is running." }, true);
    }

    btn.disabled = false;
    btn.textContent = originalText;
}

function callChat() {
    const message = document.getElementById("chatInput").value.trim();
    if (!message) return;
    runRequest("/chat", { message }, "chatOutput", "chatBtn");
}

function callClassify() {
    const email_text = document.getElementById("classifyInput").value.trim();
    if (!email_text) return;
    runRequest("/classify", { email_text }, "classifyOutput", "classifyBtn");
}

function callResearch() {
    const topic = document.getElementById("researchInput").value.trim();
    if (!topic) return;
    runRequest("/research", { topic }, "researchOutput", "researchBtn");
}

checkStatus();
setInterval(checkStatus, 15000);