import { useState, useRef } from "react";
import { Camera, Upload, UploadCloud, X } from "lucide-react";
import { UploadResponse } from "@shared/api";
import { motion } from "framer-motion";
export default function UploadSection() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // chọn file từ input
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setPreview(URL.createObjectURL(f));
    }
  };

  // kéo thả file
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) {
      setFile(f);
      setPreview(URL.createObjectURL(f));
    }
  };

  // gửi ảnh về server
  const handleUpload = async () => {
    if (!file) return alert("Please select an image first!");
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8086/api/v1/upload", {
        method: "POST",
        body: formData,
      });
      const data: UploadResponse = await res.json();
      console.log("✅ Upload success:", data);
      alert("Upload successful!");
    } catch (err) {
      console.error(err);
      alert("Upload failed!");
    } finally {
      setUploading(false);
    }
  };

  return (
    <motion.div
      className="w-full bg-white rounded-3xl border border-gray-100 shadow-2xl p-8 max-w-[592px]"
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      {/* Header */}
      <div className="flex flex-col items-center text-center mb-8">
         <motion.div
          className="w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-500 to-lime-500 flex items-center justify-center mb-6 shadow-lg"
          whileHover={{ rotate: 5, scale: 1.1 }}
          transition={{ type: "spring", stiffness: 200 }}
        >
          <Camera className="w-6 h-6 text-white" />
        </motion.div>

        <h3 className="text-2xl font-bold text-gray-800 mb-2">
          Upload Rice Leaf Image
        </h3>
        <p className="text-base text-gray-600">
          Take a clear photo or upload from your device
        </p>
      </div>

      {/* Drag & Drop Zone */}
      <motion.div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className={`border-2 border-dashed border-emerald-500 rounded-2xl p-8 mb-6 flex flex-col items-center justify-center min-h-[160px] cursor-pointer transition-all
          ${preview ? "bg-white" : "bg-emerald-50/30 hover:bg-emerald-50/50"}
        `}
        whileHover={{
          scale: 1.02,
          backgroundColor: "rgba(240,253,244,0.8)",
          boxShadow: "0 0 20px rgba(16,185,129,0.15)",
        }}
        // transition={{ type: "spring", stiffness: 200, damping: 16 }}
      >
        {preview ? (
          <div className="relative w-full">
            <img
              src={preview}
              alt="preview"
              className="w-full h-48 object-contain rounded-xl"
            />
            <button
              onClick={(e) => {
                e.stopPropagation();
                setPreview(null);
                setFile(null);
              }}
              className="absolute top-2 right-2 bg-white/80 rounded-full p-1 shadow hover:bg-red-100 transition"
            >
              <X className="w-4 h-4 text-red-500" />
            </button>
          </div>
        ) : (
          <>
            <motion.div
                animate={{ y: [0, -4, 0] }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              >
                <UploadCloud className="w-11 h-9 text-emerald-500 mb-2" />
            </motion.div>
            <p className="text-base font-medium text-gray-700 mb-1">
              Drag & drop your image here
            </p>
            <p className="text-sm text-gray-500">or click to browse</p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleFileChange}
        />
      </motion.div>

      {/* Buttons */}
      <div className="flex gap-4">
        <motion.button
          onClick={handleUpload}
          disabled={uploading}
          whileHover={{ scale: 1.05, boxShadow: "0 6px 20px rgba(16,185,129,0.3)" }}
          whileTap={{ scale: 0.96 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className={`flex-1 bg-gradient-to-br from-emerald-500 to-lime-500 text-white font-semibold text-base px-6 py-4 rounded-xl flex items-center justify-center gap-2 shadow-md transition-all ${
            uploading ? "opacity-70 cursor-not-allowed" : "hover:opacity-90"
          }`}
        >
          <Upload className="w-4 h-4" />
          {uploading ? "Uploading..." : "Upload Image"}
        </motion.button>

        <motion.button
          onClick={() => inputRef.current?.click()}
          whileHover={{ scale: 1.05, boxShadow: "0 6px 20px rgba(245,158,11,0.3)" }}
          whileTap={{ scale: 0.96 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className="flex-1 bg-amber-500 text-white font-semibold text-base px-6 py-4 rounded-xl flex items-center justify-center gap-2 hover:bg-amber-600 transition-colors shadow-md"
        >
          <Camera className="w-4 h-4" />
          Take Photo
        </motion.button>
      </div>
    </motion.div>
  );
}
