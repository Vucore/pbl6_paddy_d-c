import { Upload, Brain, ClipboardList } from "lucide-react";
import { motion } from "framer-motion";
import { ModelResult } from "@shared/api";
const steps = [
  {
    icon: Upload,
    iconBg: "bg-blue-100",
    iconColor: "text-blue-600",
    title: "1. Upload Image",
    description: "Take or upload a clear photo of the rice leaf",
  },
  {
    icon: Brain,
    iconBg: "bg-purple-100",
    iconColor: "text-purple-600",
    title: "2. AI Analysis",
    description: "Our AI analyzes the image for disease detection",
  },
  {
    icon: ClipboardList,
    iconBg: "bg-green-100",
    iconColor: "text-green-600",
    title: "3. Get Results",
    description: "Receive detailed diagnosis and treatment advice",
  },
];

export default function HowItWorks({ result_1, result_2 }: { result_1: ModelResult | null, result_2: ModelResult | null }) {
  return (
    <div className="w-full max-w-[592px]">
      <h3 className="text-2xl font-bold text-gray-800 mb-6">How it works</h3>

      <div className="flex flex-col gap-4 mb-8">
        {steps.map((step, index) => (
          <motion.div
            key={index}
            className="bg-white/80 backdrop-blur-md rounded-xl shadow-md p-4 flex items-center gap-4 border border-transparent"
            // whileHover={{
            //   scale: 1.05,
            //   boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
            //   borderColor: "rgba(16,185,129,0.4)", // viền xanh ngọc mờ
            // }}
            whileHover={{
              scale: 1.05,
              boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
              background: "linear-gradient(white, white) padding-box, linear-gradient(90deg, #34d399, #60a5fa) border-box",
              border: "2px solid transparent",
            }}

            whileTap={{ scale: 0.98 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
          >
            <div
              className={`w-12 h-12 rounded-xl ${step.iconBg} flex items-center justify-center flex-shrink-0`}
            >
              <step.icon className={`w-5 h-5 ${step.iconColor}`} />
            </div>
            <div className="flex-1 text-left">
              <h4 className="text-base font-semibold text-gray-800 mb-1">
                {step.title}
              </h4>
              <p className="text-sm text-gray-600">{step.description}</p>
            </div>
          </motion.div>
        ))}
      </div>
      <div className="flex flex-col md:flex-row gap-6 justify-center items-stretch mt-4">
      {result_1 && (
          <motion.div
            className="flex-1 bg-white/80 backdrop-blur-md rounded-2xl shadow-xl p-6 border border-transparent"
            style={{ maxWidth: 592 }}
            whileHover={{
              scale: 1.03,
              boxShadow: "0 10px 30px rgba(0,0,0,0.18)",
              borderColor: "rgba(59,130,246,0.3)",
            }}
            transition={{ type: "spring", stiffness: 250, damping: 20 }}
          >
            <h4 className="text-base font-semibold text-gray-800 mb-4 text-center">
              Detection Result Model 1
            </h4>
            <img
              src={`data:image/jpeg;base64,${result_1.image}`}
              alt={result_1.disease}
              className="rounded-xl mb-4 bg-gray-100"
              style={{
                maxWidth: "100%",
                maxHeight: "400px",
                height: "auto",
                width: "auto",
                display: "block",
                margin: "0 auto",
              }}
            />
            <div className="mt-4 flex flex-col items-center gap-2">
              <div className="flex items-center gap-4">
                <p className="text-sm text-gray-600 font-medium">{result_1.disease}</p>
                <span className="bg-red-100 text-red-800 text-sm font-medium px-3 py-1 rounded-full">
                  {Math.round(result_1.confidence * 100)}% Confidence
                </span>
              </div>
              <div className="text-sm text-gray-500 font-medium">Model: {result_1.model}</div>
            </div>
          </motion.div>
        )}

        {result_2 && (
          <motion.div
            className="flex-1 bg-white/80 backdrop-blur-md rounded-2xl shadow-xl p-6 border border-transparent"
            style={{ maxWidth: 592 }}
            whileHover={{
              scale: 1.03,
              boxShadow: "0 10px 30px rgba(0,0,0,0.18)",
              borderColor: "rgba(34,197,94,0.3)",
            }}
            transition={{ type: "spring", stiffness: 250, damping: 20 }}
          >
            <h4 className="text-base font-semibold text-green-800 mb-4 text-center">
              Detection Result Model 2
            </h4>
            <img
              src={`data:image/jpeg;base64,${result_2.image}`}
              alt={result_2.disease}
              className="rounded-xl mb-4 bg-gray-100"
              style={{
                maxWidth: "100%",
                maxHeight: "400px",
                height: "auto",
                width: "auto",
                display: "block",
                margin: "0 auto",
              }}
            />
            <div className="mt-4 flex flex-col items-center gap-2">
              <div className="flex items-center gap-4">
                <p className="text-sm text-gray-600 font-medium">{result_2.disease}</p>
                <span className="bg-green-100 text-green-800 text-sm font-medium px-3 py-1 rounded-full">
                  {Math.round(result_2.confidence * 100)}% Confidence
                </span>
              </div>
              <div className="text-sm text-gray-500 font-medium">Model: {result_2.model}</div>
            </div>
          </motion.div>
        )}
      </div>
      {/* <motion.div
        className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl p-6 border border-transparent"
        whileHover={{
          scale: 1.03,
          boxShadow: "0 10px 30px rgba(0,0,0,0.18)",
          borderColor: "rgba(59,130,246,0.3)", // ánh sáng xanh lam
        }}
        transition={{ type: "spring", stiffness: 250, damping: 20 }}
      >
        <h4 className="text-base font-semibold text-gray-800 mb-4">
          Sample Detection
        </h4>
        <motion.img
          src="https://api.builder.io/api/v1/image/assets/TEMP/c0e40c9db3af73a496c84a2380e8e3f993e2f676?width=1088"
          alt="Sample rice leaf with brown spot disease"
          className="w-full h-48 object-cover rounded-xl mb-4"
          whileHover={{ scale: 1.02 }}
          transition={{ type: "spring", stiffness: 250, damping: 18 }}
        />
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">Brown Spot Disease</p>
          <span className="bg-red-100 text-red-800 text-sm font-medium px-3 py-1 rounded-full">
            92% Confidence
          </span>
        </div>
      </motion.div> */}
    </div>
  );
}
