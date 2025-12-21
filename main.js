const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        backgroundColor: "#1b1322",
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            webviewTag: true, // ✅ needed for <webview>
            preload: path.join(__dirname, "preload.js"),
        },
    });

    win.loadFile("index.html");
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
    if (process.platform !== "darwin") app.quit();
});
