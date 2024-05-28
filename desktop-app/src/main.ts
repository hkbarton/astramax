import { app, Tray, Menu } from "electron";
import * as path from "path";
import * as robot from "robotjs";

const EventSource = require("eventsource");

let tray: Tray | null = null;

function createTray() {
  tray = new Tray(path.join(__dirname, "icon-16.png"));
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
  const eventSource = new EventSource(
    "http://127.0.0.1:8000/api/message-stream?processor_id=desktop-app"
  );

  eventSource.onmessage = async (event: any) => {
    const { payload } = JSON.parse(event.data);
    console.log("got payload:", payload);
    for (const char of payload) {
      robot.keyTap(char);
    }
  };

  eventSource.onerror = (err: any) => {
    console.error("EventSource error:", err);
    eventSource.close();
  };
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
