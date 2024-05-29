import axios from "axios";
import { GoogleAuth } from "google-auth-library";
import * as path from "path";

const isDev = process.env.NODE_ENV === "development";
const credentialFilePath = path.resolve(
  __dirname,
  isDev
    ? "../../deployment/dev/credentials/ghack-service-account.json"
    : "ghack-service-account.json"
);

class CloudService {
  private static async getAccessToken(): Promise<string> {
    const SCOPES = ["https://www.googleapis.com/auth/cloud-platform"];
    const auth = new GoogleAuth({
      keyFile: credentialFilePath,
      scopes: SCOPES,
    });

    const client = await auth.getClient();
    const token = await client.getAccessToken();
    return token.token ?? "";
  }

  public static async generateContent(
    prompt: string,
    videoFileName?: string
  ): Promise<string> {
    const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/${process.env.PROJECT_ID}/locations/us-central1/publishers/google/models/gemini-1.5-flash-001:streamGenerateContent`;
    const token = await CloudService.getAccessToken();
    const headers = {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    };

    const data: { contents: any; generationConfig: any } = {
      contents: {
        role: "user",
        parts: [
          {
            text: prompt,
          },
        ],
      },
      generationConfig: {
        temperature: 0.3,
      },
    };
    if (videoFileName) {
      data.contents.parts.push({
        fileData: {
          mimeType: "video/mp4",
          fileUri: `gs://${process.env.GCS_BUCKET_NAME}/${videoFileName}`,
        },
      });
    }

    const response = await axios.post(url, data, { headers });
    if (response.data && response.data.length > 0) {
      return response.data
        .map((item: any) =>
          item.candidates
            .map((candidate: any) =>
              candidate.content.parts.map((part: any) => part.text).join("")
            )
            .join("")
        )
        .join("")
        .trim();
    }
    return response.data;
  }

  public static async generateVoice(text: string) {
    const url = `https://texttospeech.googleapis.com/v1/text:synthesize`;
    const token = await CloudService.getAccessToken();
    const headers = {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "X-Goog-User-Project": process.env.PROJECT_ID,
    };

    const data = {
      input: {
        text,
      },
      voice: {
        languageCode: "en-US",
        name: "en-US-Journey-O",
        customVoice: {},
      },
      audioConfig: {
        audioEncoding: "LINEAR16",
      },
    };

    const response = await axios.post(url, data, { headers });
    return response.data;
  }
}

export default CloudService;
