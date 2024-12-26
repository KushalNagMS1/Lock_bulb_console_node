import express from "express";
import bodyParser from "body-parser";
import { WebSocketServer } from "ws";
import { spawn } from 'child_process';



const app = express();
const port = 3000;

let lockStatus = "locked";
let bulbStatus = "off";
const correctPassword = "12345";
let attempts = 3;

// WebSocket setup
const wss = new WebSocketServer({ port: 8080 });
let connectedClients = [];

wss.on("connection", (ws) => {
  console.log("ESP32 connected");
  connectedClients.push(ws);

  // Send the current bulb status to the newly connected ESP32
  ws.send(JSON.stringify({ type: "bulb", status: bulbStatus }));

  ws.on("close", () => {
    console.log("ESP32 disconnected");
    connectedClients = connectedClients.filter(client => client !== ws);
  });
});

// Notify all connected clients about a status change
const notifyClients = (type, status) => {
  connectedClients.forEach(client => {
    if (client.readyState === 1) {
      client.send(JSON.stringify({ type, status }));
    }
  });
};

// Initial states


app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static("public"));

// Routes
app.get("/", (req, res) => {
  res.render("welcome_page.ejs");
});

app.get('/unlock', (req, res) => {

  res.render('passwordKey_page.ejs', { message: null, attempts });
  
});

app.post('/submit-password', (req, res) => {
  const { password } = req.body;

  if (password === correctPassword && attempts > 1) {
    lockStatus = "unlocked";
    console.log(`The lock status is ${lockStatus}` )
    notifyClients("lockStatus", lockStatus);
    attempts=3;
    res.render('console.ejs');
  } else if (attempts > 1) {
    attempts--;
    const message = "Incorrect password. Try again.";
    res.render('passwordKey_page.ejs', { message, attempts });
  } else if (attempts === 1) {
    attempts--;
    const message = "No attempts left. Please contact customer care.";
    res.render('passwordKey_page.ejs', { message, attempts });
  } else {
    res.render('error.ejs', { message: "Please contact customer care." });
  }
});

app.post('/lock', (req, res) => {
  lockStatus = "locked";
  notifyClients("lockStatus", lockStatus);
  console.log("Lock status updated to: locked");
  res.redirect('/');
});

app.post('/bulb-status', (req, res) => {
  const { status } = req.body;
  if (status === "on" || status === "off") {
    bulbStatus = status;
    notifyClients("bulb", bulbStatus);
    console.log(`Bulb status updated to: ${bulbStatus}`);
    res.status(200).send();
  } else {
    res.status(400).send("Invalid status");
  }
});

app.post('/voice-command', async (req,res)=>{
  try {
    const scriptPath = 'pyFile/bulb_control.py';
    const result = await runPythonScript(scriptPath);
    if (result.device_name!='NaN'){
      bulbStatus=result.device_status.toLowerCase();
      notifyClients("bulb", bulbStatus);
      console.log(`Bulb status updated to: ${bulbStatus}`);
    }
    res.status(200).send();
} catch (error) {
    console.error('Error:', error);
    res.status(400).send("Invalid status");
}
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});

const runPythonScript = (scriptPath, args = []) => {
  return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [scriptPath, ...args]);

      let output = '';
      let errorOutput = '';

      // Capture the Python script's stdout
      pythonProcess.stdout.on('data', (data) => {
          output += data.toString();
      });

      // Capture the Python script's stderr
      pythonProcess.stderr.on('data', (data) => {
          errorOutput += data.toString();
      });

      // Handle process exit
      pythonProcess.on('close', (code) => {
          if (code === 0) {
              try {
                  // Parse the JSON output
                  const result = JSON.parse(output);
                  resolve(result);
              } catch (error) {
                  reject(`Failed to parse JSON: ${error.message}`);
              }
          } else {
              reject(`Python script exited with code ${code}: ${errorOutput}`);
          }
      });
  });
};




