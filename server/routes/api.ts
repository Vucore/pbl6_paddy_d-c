import type { RequestHandler } from "express";
import { UploadResponse } from "@shared/api";
import fetch from "node-fetch";
import fs from "fs";
import FormData from "form-data";

export const handleImageUpload: RequestHandler = async (req, res) => {
  const file = (req as any).file;
  if (!file) {
    return res.status(400).json({ message: "No file uploaded" });
  }

  // Chuẩn bị gửi file sang Python server
  const form = new FormData();
  form.append("file", fs.createReadStream(file.path), file.originalname);

  try {
    const pyRes = await fetch("http://localhost:8000/predict", {
      method: "POST",
      body: form as any,
      headers: form.getHeaders(),
    });
    const pyResults = await pyRes.json() as Array<{
      model: string;
      disease: string;
      confidence: number;
      image: string;
    }>;
    const result_1 = pyResults[0];
    const result_2 = pyResults[1];

    const response: UploadResponse = {
      message: "File uploaded and processed successfully",
      originalname: file.originalname,
      result_1,
      result_2,
    };
    res.status(200).json(response);
  } catch (err) {
    res.status(500).json({ message: "Error processing image", error: String(err) });
  }
};