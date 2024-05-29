import { app, Tray, Menu } from "electron";
import * as path from "path";
import * as robot from "robotjs";
import CloudService from "./gcp";
import { extractTextAndCode } from "./utils";
const EventSource = require("eventsource");
const player = require("node-wav-player");
const { decode } = require("base64-arraybuffer");

const fs = require("fs");
const os = require("os");
const logFile = fs.createWriteStream(
  path.join(os.homedir(), "astramax-desktop.log"),
  { flags: "a" }
);
const log = (msg: any, err: any) => {
  logFile.write(`${new Date().toISOString()} - ${msg} - ${err}\n`);
};

const isDev = process.env.NODE_ENV === "development";
require("dotenv").config({
  path: path.resolve(__dirname, isDev ? "../../deployment/dev/.env" : ".env"),
});

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
    {
      label: `service at: ${process.env.SERVICE_URL}`,
      click: () => {
        // some test code here
      },
    },
  ]);
  tray.setToolTip("AstraMax desktop app");
  tray.setContextMenu(contextMenu);
}

async function playTextAsVoice(text: string) {
  const voiceData = await CloudService.generateVoice(text);
  const audioBuffer = decode(voiceData.audioContent);
  const filePath = path.join(__dirname, "temp.wav");
  fs.writeFileSync(filePath, Buffer.from(audioBuffer));
  player.play({ path: path.resolve(__dirname, "temp.wav") });
}

async function listenToEventStream() {
  const eventSource = new EventSource(
    `${process.env.SERVICE_URL}api/message-stream?processor_id=desktop-app`
  );

  eventSource.onmessage = async (event: any) => {
    let payloadObj: { user_query: string; video?: string };
    try {
      const { payload } = JSON.parse(event.data);
      payloadObj = JSON.parse(payload);
    } catch (e) {
      log("failed to parse message", e);
      if (isDev) {
        throw e;
      }
      return;
    }
    const generationJobs = [];
    // classify query
    generationJobs.push(
      CloudService.generateContent(`
Help me categorize the question below into 3 categories:

CATEGORY_CODE_GEN: for question that need your help to write code
CATEGORY_IMAGE_GEN: for image generation question
CATEGORY_QNA: for all other questions

Output only the category name (one of CATEGORY_CODE_GEN, CATEGORY_IMAGE_GEN and CATEGORY_QNA)

the question is: ${payloadObj.user_query}
    `)
    );
    // original gen using video and original prompt
    generationJobs.push(
      CloudService.generateContent(payloadObj.user_query, payloadObj.video)
    );
    const [category, oriResult] = await Promise.all(generationJobs);
    console.log(payloadObj.user_query);
    console.log(category);
    console.log(oriResult);
    if (category === "CATEGORY_QNA") {
      await playTextAsVoice(oriResult);
    } else if (category === "CATEGORY_IMAGE_GEN") {
      player.play({ path: path.resolve(__dirname, "fill.wav") });
    } else if (category === "CATEGORY_CODE_GEN") {
      const { text, code } = extractTextAndCode(oriResult);
      console.log("text", text);
      console.log("code", code);
      if (text && text.length > 0 && text[0]) {
        playTextAsVoice(text[0]);
      }
      if (code && code.length > 0 && code[0]) {
        robot.typeString(code[0]);
      }
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

process.on("uncaughtException", (error) => {
  log("Uncaught Exception:", error);
  console.error("Uncaught Exception:", error);
});

process.on("unhandledRejection", (reason, promise) => {
  log("Unhandled Rejection at:", reason);
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
});
