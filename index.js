const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const http = require('http');

let flaskProcess;
let flaskServer = path.join(__dirname, 'app.py');

if (process.platform === 'win32') {
    flaskServer = path.join(process.resourcesPath, 'app', 'app.py');
}

function startFlaskServer() {
    let pythonExecutable = 'python';

    // En Windows, usa pythonw.exe para evitar la apertura de la ventana de la consola
    if (process.platform === 'win32') {
        pythonExecutable = 'pythonw'; // pythonw.exe ejecuta el script sin abrir la ventana de la consola
    }

    flaskProcess = spawn(pythonExecutable, [flaskServer], { stdio: 'ignore' });

    flaskProcess.on('error', (err) => {
        console.error('Error al iniciar Flask:', err.message);
    });

    flaskProcess.on('close', (code) => {
        console.log(`Flask proceso cerrado con código ${code}`);
    });
}

function terminateFlask() {
    if (flaskProcess) {
        if (process.platform === 'win32') {
            exec(`taskkill /F /PID ${flaskProcess.pid}`, (err, stdout, stderr) => {
                if (err) {
                    console.error('Error al cerrar Flask en Windows:', stderr);
                } else {
                    console.log('Proceso Flask cerrado correctamente en Windows.');
                }
            });
        } else {
            flaskProcess.kill('SIGINT');
        }
        flaskProcess = null;
    }
}

function waitForFlaskReady(url, callback) {
    const interval = setInterval(() => {
        http.get(url, (res) => {
            if (res.statusCode === 200) {
                clearInterval(interval);
                callback();
            }
        }).on('error', () => {
            console.log('Esperando a Flask...');
        });
    }, 500);
}

function createWindow() {
    const win = new BrowserWindow({
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        }
    });

    waitForFlaskReady('http://localhost:5000', () => {
        win.loadURL('http://localhost:5000/');
    });

    win.on('closed', () => {
        terminateFlask();
    });
}

app.whenReady().then(() => {
    startFlaskServer();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        terminateFlask();
        app.quit();
    }
});

app.on('will-quit', terminateFlask);
