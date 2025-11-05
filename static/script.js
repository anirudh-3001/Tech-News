const chat = document.getElementById("chat");
const msgInput = document.getElementById("msg");
const refreshBtn = document.getElementById("refreshBtn");

function addUserBubble(text) {
  const div = document.createElement("div");
  div.className = "user-message";
  div.innerText = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function addBotBubble(html) {
  const div = document.createElement("div");
  div.className = "bot-message";
  div.innerHTML = html;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function sendMessage() {
  const text = msgInput.value.trim();
  if (!text) return false;
  addUserBubble(text);
  msgInput.value = "";
  addBotBubble("⏳ Fetching the latest AI & tech updates...");

  try {
    const res = await fetch(`/api/query?date=${encodeURIComponent(text)}&summarize=1`);
    const data = await res.json();
    document.querySelectorAll(".bot-message").at(-1)?.remove();

    if (data.error) {
      addBotBubble("⚠️ " + data.error);
      return false;
    }
    if (!data.items || data.items.length === 0) {
      addBotBubble("No AI or tech news found for that date. Try 'today' or 'yesterday'.");
      return false;
    }

    let html = "";
    data.items.forEach(item => {
      html += `
        <div class="news-card">
          <h4>${item.title || "Untitled"}</h4>
          <p>${item.summary || "No summary available."}</p>
          <a href="${item.link}" target="_blank">Read more</a>
        </div>
      `;
    });

    addBotBubble(html);
  } catch {
    document.querySelectorAll(".bot-message").at(-1)?.remove();
    addBotBubble("⚠️ Network error. Is the Flask server running?");
  }
  return false;
}

refreshBtn.onclick = async () => {
  addBotBubble("⏳ Refreshing latest feeds...");
  try {
    const r = await fetch("/refresh");
    const j = await r.json();
    document.querySelectorAll(".bot-message").at(-1)?.remove();
    addBotBubble("✅ Updated " + j.count + " articles successfully.");
  } catch {
    document.querySelectorAll(".bot-message").at(-1)?.remove();
    addBotBubble("⚠️ Failed to refresh. Check your server.");
  }
};

msgInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
