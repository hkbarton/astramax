import { contextBridge } from "electron";
import * as robot from "robotjs";
import { writeFileSync } from "fs";
import { join } from "path";
import * as clipboardy from "clipboardy";

contextBridge.exposeInMainWorld("api", {
  insertImage: async (imageUrl: string) => {
    const response = await fetch(imageUrl);
    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    const imagePath = join(__dirname, "temp-image.png");

    writeFileSync(imagePath, buffer);
    clipboardy.writeSync(buffer.toString("base64")); // Copy image to clipboard

    // Simulate paste operation
    robot.keyTap("v", "command");
  },
});
