const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

let pythonProcess = null;

function startPythonServer() {
    const scriptPath = path.join(__dirname, "backend", "server.py");
    // Assuming 'python' is in PATH. If using venv, might need full path.
    pythonProcess = spawn("python", [scriptPath]);

    pythonProcess.stdout.on("data", (data) => {
        console.log(`Python: ${data}`);
    });

    pythonProcess.stderr.on("data", (data) => {
        console.error(`Python Error: ${data}`);
    });
}

function createWindow() {
    startPythonServer();

    const win = new BrowserWindow({
        width: 1400,
        height: 900,
        backgroundColor: "#241b2f",
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true,
            contextIsolation: false,
            webviewTag: true // Enabled for internal browsing
        },
    });

    win.loadFile("index.html");

    // Screenshot Capture Listener
    ipcMain.on('capture-screen', async (event) => {
        try {
            const image = await win.capturePage();
            const filePath = path.join(app.getPath('downloads'), `wellness-screenshot-${Date.now()}.png`);

            fs.writeFile(filePath, image.toPNG(), (err) => {
                if (err) {
                    console.error("Save failed:", err);
                    event.reply('screenshot-done', { success: false, error: err.message });
                } else {
                    console.log("Screenshot saved to:", filePath);
                    event.reply('screenshot-done', { success: true, path: filePath });
                }
            });
        } catch (e) {
            console.error("Capture failed:", e);
            event.reply('screenshot-done', { success: false, error: e.message });
        }
    });
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
    if (pythonProcess) pythonProcess.kill();
    if (process.platform !== "darwin") app.quit();
});

app.on("will-quit", () => {
    if (pythonProcess) pythonProcess.kill();
});
