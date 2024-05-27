import { app, Tray, Menu } from "electron";
import * as path from "path";
import * as robot from "robotjs";
import fetch from "node-fetch";
import { Readable } from "stream";

let tray: Tray | null = null;

function createTray() {
  tray = new Tray(path.join(__dirname, "icon.png"));
  const contextMenu = Menu.buildFromTemplate([
    {
      label: "Exit",
      click: () => {
        app.quit();
      },
    },
  ]);
  tray.setToolTip("AstraMax desktop app");
  tray.setContextMenu(contextMenu);
}

async function listenToEventStream() {
  const response = await fetch("http://your-event-stream-endpoint");
  const reader = response.body as Readable;

  reader.on("data", (chunk: Buffer) => {
    const text = chunk.toString();
    // Insert text at the current cursor position
    for (const char of text) {
      robot.typeString(char);
    }
  });

  reader.on("end", () => {
    console.log("Stream ended");
  });

  reader.on("error", (err) => {
    console.error("Stream error:", err);
  });
}

app.whenReady().then(() => {
  createTray();
  listenToEventStream();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
