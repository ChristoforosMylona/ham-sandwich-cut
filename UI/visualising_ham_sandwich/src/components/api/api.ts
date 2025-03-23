import saveAs from "file-saver";

// api.ts
const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

const checkForLocal = (url: string) => {
  // You can adjust the condition here to detect if it's local or Docker
  if (url.includes('localhost')) {
    return 'http://localhost:5000'; // Local backend URL
  }
  return url;
};

export const fetchData = async (endpoint: string, method: string, body?: any) => {
  try {
    const baseUrl = checkForLocal(apiBaseUrl);
    const response = await fetch(`${baseUrl}/${endpoint}/`, {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    throw error;  // Pass the error back to the caller
  }
};

export const downloadFile = async (fileType: "csv" | "json" | "excel") => {
  try {
    const baseUrl = checkForLocal(apiBaseUrl);
    const response = await fetch(`${baseUrl}/get-sample-file/${fileType}`);
    if (!response.ok) throw new Error("Failed to fetch file");

    const blob = await response.blob();
    let extension;
    if (fileType === "csv") {
      extension = "csv";
    } else if (fileType === "json") {
      extension = "json";
    } else {
      extension = "xlsx";
    }
    saveAs(blob, `sample.${extension}`);
  } catch (error) {
    console.error("Error downloading file:", error);
    throw error;
  }
};


export const fetchRandomPoints = async (redPoints: number, bluePoints: number) => {
  try {
    const baseUrl = checkForLocal(apiBaseUrl);
    const response = await fetch(`${baseUrl}/random_points/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ redPoints, bluePoints }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    throw error;  // Pass the error back to the caller
  }
};