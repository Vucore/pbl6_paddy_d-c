import type { RequestHandler } from "express";
import { UploadResponse } from "@shared/api";

export const handleImageUpload: RequestHandler = (req, res) => {
  const file = (req as any).file; 
  
  if (!file) {
    return res.status(400).json({ message: "No file uploaded" });
  }

  const fileInfo = {
    originalname: file.originalname,
    filename: file.filename,
    mimetype: file.mimetype,
    size: file.size,
    path: file.path,
  };

  const response: UploadResponse = {
    message: "File uploaded successfully",
    originalname: file.originalname,
    filename: file.filename,
    mimetype: file.mimetype,
    size: file.size,
    path: file.path,
  };

  res.status(200).json(response);
};
