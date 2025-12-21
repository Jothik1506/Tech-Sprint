// Views
const home = document.getElementById("home");
const webWrap = document.getElementById("webWrap");

// Inputs
const searchInput = document.getElementById("searchInput");
const urlBar = document.getElementById("urlBar");

// Webview
const webview = document.getElementById("webview");

// Buttons
const backBtn = document.getElementById("backBtn");
const forwardBtn = document.getElementById("forwardBtn");
const reloadBtn = document.getElementById("reloadBtn");
const homeBtn = document.getElementById("homeBtn");

// Tabs
const tabsDiv = document.getElementById("tabs");
const newTabBtn = document.getElementById("newTabBtn");

let tabs = [];
let activeTabId = null;

// ---------- Helpers ----------
function showHome() {
    webWrap.classList.add("hidden");
    home.classList.remove("hidden");
    activeTabId = null;
    renderTabs();
}

function showWeb(url) {
    home.classList.add("hidden");
    webWrap.classList.remove("hidden");
    webview.loadURL(url);
    urlBar.value = url;
}

// ---------- Tabs ----------
function createTab(url, title = "New Tab") {
    const id = Date.now();
    tabs.push({ id, url, title });
    activeTabId = id;
    showWeb(url);
    renderTabs();
}

function closeTab(id) {
    tabs = tabs.filter(t => t.id !== id);
    if (activeTabId === id) {
        if (tabs.length) {
            activateTab(tabs[tabs.length - 1].id);
        } else {
            showHome();
        }
    }
    renderTabs();
}

function activateTab(id) {
    const tab = tabs.find(t => t.id === id);
    if (!tab) return;
    activeTabId = id;
    showWeb(tab.url);
    renderTabs();
}

function renderTabs() {
    tabsDiv.innerHTML = "";
    tabs.forEach(tab => {
        const el = document.createElement("div");
        el.className = "tab" + (tab.id === activeTabId ? " active" : "");
        el.innerHTML = `
      <span>${tab.title}</span>
      <span class="close">✕</span>
    `;
        el.onclick = () => activateTab(tab.id);
        el.querySelector(".close").onclick = (e) => {
            e.stopPropagation();
            closeTab(tab.id);
        };
        tabsDiv.appendChild(el);
    });
}

// ---------- Search ----------
function toGoogleSearch(q) {
    return `https://www.google.com/search?q=${encodeURIComponent(q)}`;
}

searchInput.addEventListener("keydown", e => {
    if (e.key === "Enter") {
        createTab(toGoogleSearch(searchInput.value), searchInput.value);
    }
});

urlBar.addEventListener("keydown", e => {
    if (e.key === "Enter") {
        const val = urlBar.value.trim();
        const url = val.includes(".") ? `https://${val.replace(/^https?:\/\//, "")}` : toGoogleSearch(val);
        const tab = tabs.find(t => t.id === activeTabId);
        if (tab) {
            tab.url = url;
            showWeb(url);
        }
    }
});

// ---------- Webview events ----------
webview.addEventListener("did-navigate", e => {
    urlBar.value = e.url;
    const tab = tabs.find(t => t.id === activeTabId);
    if (tab) tab.url = e.url;
});

webview.addEventListener("page-title-updated", e => {
    const tab = tabs.find(t => t.id === activeTabId);
    if (tab) {
        tab.title = e.title.slice(0, 15);
        renderTabs();
    }
});

// ---------- Nav buttons ----------
backBtn.onclick = () => webview.canGoBack() && webview.goBack();
forwardBtn.onclick = () => webview.canGoForward() && webview.goForward();
reloadBtn.onclick = () => webview.reload();
homeBtn.onclick = showHome;

// ---------- New tab ----------
newTabBtn.onclick = () => showHome();

// ---------- Default apps ----------
const appsGrid = document.getElementById("appsGrid");
const addAppBtn = document.getElementById("addAppBtn");

const DEFAULT_APPS = [
    { name: "YouTube", url: "https://youtube.com" },
    { name: "Gmail", url: "https://mail.google.com" },
    { name: "Maps", url: "https://maps.google.com" },
    { name: "Drive", url: "https://drive.google.com" },
    { name: "WhatsApp", url: "https://web.whatsapp.com" }
];

DEFAULT_APPS.forEach(app => {
    const card = document.createElement("div");
    card.className = "appCard";
    card.innerHTML = `<div class="appIcon">${app.name[0]}</div><div class="appName">${app.name}</div>`;
    card.onclick = () => createTab(app.url, app.name);
    appsGrid.appendChild(card);
});

// Start
showHome();
