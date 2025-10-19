import "dotenv/config";
import express from "express";
import cors from "cors";
import { handleImageUpload } from "./routes/api";
import multer from "multer";
import path from "path";


export function createServer() {
  const app = express();
  
  // Middleware
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));
  
  // Example API routes
  app.get("/api/ping", (_req, res) => {
    const ping = process.env.PING_MESSAGE ?? "ping";
    res.json({ message: ping });
  });
  
  const storage = multer.diskStorage({
    destination: "uploads/",
    filename: (_req, file, cb) => {
      // Lưu file với tên gốc + đuôi mở rộng
      const ext = path.extname(file.originalname);
      const basename = path.basename(file.originalname, ext);
      cb(null, `${basename}-${Date.now()}${ext}`);
    },
  });

  const upload = multer({ storage });
  app.post("/api/v1/upload", upload.single("file"), handleImageUpload);

  return app;
}
