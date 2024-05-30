import { app, Tray, Menu } from "electron";
import * as path from "path";
import * as robot from "robotjs";
import CloudService from "./gcp";
import { extractTextAndCode } from "./utils";
const { execSync } = require("child_process");
const EventSource = require("eventsource");
const player = require("node-wav-player");
const { decode } = require("base64-arraybuffer");

const fs = require("fs");
const os = require("os");
const isDev = process.env.NODE_ENV === "development";
require("dotenv").config({
  path: path.resolve(__dirname, isDev ? "../../deployment/dev/.env" : ".env"),
});
let log = console.log;
if (!isDev) {
  const logFile = fs.createWriteStream(
    path.join(os.homedir(), "astramax-desktop.log"),
    { flags: "a" }
  );
  log = (msg: any, obj?: any) => {
    logFile.write(
      `${new Date().toISOString()} - ${msg} - ${JSON.stringify(obj, null, 2)}\n`
    );
  };
}

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
      click: async () => {},
    },
  ]);
  tray.setToolTip("AstraMax desktop app");
  tray.setContextMenu(contextMenu);
}

function copyImg(img: Buffer | string) {
  let filePath: string;
  if (Buffer.isBuffer(img)) {
    filePath = path.join("/tmp", "astramax-temp-image.png");
    fs.writeFileSync(filePath, img);
  } else {
    filePath = img;
  }
  let execPath = path.resolve(__dirname, "osx-copy-image");
  if (!isDev) {
    execPath = execPath.replace("app.asar", "app.asar.unpacked");
  }
  execSync(`${execPath} ${filePath}`);
}

async function playTextAsVoice(text: string) {
  const voiceData = await CloudService.generateVoice(text);
  const audioBuffer = decode(voiceData.audioContent);
  const filePath = path.join("/tmp", "astramax-temp.wav");
  fs.writeFileSync(filePath, Buffer.from(audioBuffer));
  player.play({ path: filePath });
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
    log("get pi message", payloadObj);
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
    log("query category:", category);
    log("original gemini response:", oriResult);

    if (category === "CATEGORY_QNA") {
      await playTextAsVoice(oriResult);
    } else if (category === "CATEGORY_IMAGE_GEN") {
      const feedbackSoundJob = playTextAsVoice("sure, give me a moment");
      const imagePromptGenJob = CloudService.generateContent(
        `
Describe what you are seeing here in detail. If the video shows a place, guess where is this place.
      `,
        payloadObj.video
      );
      const [_, imagePrompt] = await Promise.all([
        feedbackSoundJob,
        imagePromptGenJob,
      ]);
      log("image gen prompt", imagePrompt);
      const imageGenResponse = await CloudService.generateImage(
        `${imagePrompt}, cartoonish style`
      );
      if (
        imageGenResponse.predictions &&
        imageGenResponse.predictions.length > 0
      ) {
        const imageBase64 = imageGenResponse.predictions[0].bytesBase64Encoded;
        copyImg(Buffer.from(imageBase64, "base64"));
        robot.keyTap("v", "command");
      }
    } else if (category === "CATEGORY_CODE_GEN") {
      const { text, code } = extractTextAndCode(oriResult);
      log("code gen text:", text);
      log("code gen code:", code);
      if (text && text.length > 0 && text[0]) {
        await playTextAsVoice(text[0]);
      } else {
        await playTextAsVoice("sure, I can help with that");
      }
      if (code && code.length > 0 && code[0]) {
        const lines = code[0].split("\n");
        for (const line of lines) {
          const codeLine = line.trim();
          if (codeLine) {
            robot.typeString(codeLine);
          }
          robot.keyTap("enter");
        }
        robot.keyTap("s", "cmd");
      }
    }
  };

  eventSource.onerror = (err: any) => {
    log("EventSource error:", err);
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
});

process.on("unhandledRejection", (reason, promise) => {
  log("Unhandled Rejection at:", reason);
});
