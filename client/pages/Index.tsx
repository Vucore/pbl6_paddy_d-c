import { MessageCircle } from "lucide-react";
import Header from "@/components/Header";
import UploadSection from "@/components/UploadSection";
import HowItWorks from "@/components/HowItWorks";
import DiseaseCard from "@/components/DiseaseCard";
import { motion, useAnimationFrame } from "framer-motion";
import { useRef, useState } from "react";

const diseases = [
  {
    image:
      "https://api.builder.io/api/v1/image/assets/TEMP/5a839cd54dbcb247379b634280a91a58efbd0b00?width=779",
    title: "Brown Spot Disease",
    symptoms:
      "Brown oval spots on leaves, stems, and grains. Spots have gray centers with brown margins.",
    prevention: [
      "• Use resistant varieties",
      "• Proper field sanitation",
      "• Balanced fertilization",
    ],
  },
  {
    image:
      "https://api.builder.io/api/v1/image/assets/TEMP/7ac469a21b762686dc1b0d07af3f092c55c7fb60?width=779",
    title: "Rice Blast",
    symptoms:
      "Diamond-shaped lesions with gray centers and brown borders on leaves and stems.",
    prevention: [
      "• Plant resistant cultivars",
      "• Avoid excessive nitrogen",
      "• Proper water management",
    ],
  },
  {
    image:
      "https://api.builder.io/api/v1/image/assets/TEMP/f21c6097fbe359d7faa77936990a60051ce62ebb?width=779",
    title: "Bacterial Blight",
    symptoms:
      "Water-soaked lesions that turn yellow then brown, often with wavy margins.",
    prevention: [
      "• Use certified seeds",
      "• Crop rotation",
      "• Avoid field flooding",
    ],
  },
];

function InfiniteSlider({ diseases }) {
  const baseX = useRef(0);
  const containerRef = useRef(null);
  const [paused, setPaused] = useState(false);
  const [hoverIndex, setHoverIndex] = useState(null); // 👉 lưu card được hover

  useAnimationFrame((t, delta) => {
    if (paused || !containerRef.current) return;

    baseX.current -= (delta / 1000) * 45; // tốc độ px/s
    const halfWidth = containerRef.current.scrollWidth / 2;
    if (Math.abs(baseX.current) >= halfWidth) baseX.current = 0;

    containerRef.current.style.transform = `translateX(${baseX.current}px)`;
  });

  return (
    <div className="overflow-hidden w-full relative py-4">
      <div
        ref={containerRef}
        className="flex gap-8 will-change-transform"
        style={{
          transform: `translateX(${baseX.current}px)`,
        }}
      >
        {[...diseases, ...diseases].map((disease, index) => {
          const isHovered = hoverIndex === index;

          return (
            <div
              key={index}
              className="min-w-[320px] md:min-w-[360px] flex-shrink-0 transition-transform duration-300"
              onMouseEnter={() => {
                setPaused(true);
                setHoverIndex(index);
              }}
              onMouseLeave={() => {
                setPaused(false);
                setHoverIndex(null);
              }}
              style={{
                transform: isHovered ? "scale(1.04)" : "scale(1)",
                boxShadow: isHovered
                  ? "0 8px 24px rgba(0,0,0,0.18)"
                  : "0 2px 6px rgba(0,0,0,0.08)",
                borderRadius: "1rem",
                background: "white",
              }}
            >
              <DiseaseCard key={index} {...disease} />
            </div>
          );
        })}
      </div>
    </div>
  );
}


export default function Index() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-50">
      <Header />

      <main className="max-w-[1280px] mx-auto px-6 py-8 md:py-12 space-y-12 md:space-y-16">
        <section className="flex flex-col items-center text-center space-y-12">
          <div className="space-y-3">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-800">
              Detect Rice Diseases Instantly
            </h2>
            <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto">
              Upload a photo of your rice leaf and get instant AI-powered
              disease detection with treatment recommendations
            </p>
          </div>

          <div className="w-full grid lg:grid-cols-2 gap-8 md:gap-12 items-start">
            <div className="flex justify-center">
              <UploadSection />
            </div>
            <div className="flex justify-center">
              <HowItWorks />
            </div>
          </div>
        </section>

        <section className="flex flex-col items-center text-center space-y-8">
          <div className="space-y-4">
            <h2 className="text-3xl font-bold text-gray-800">
              Rice Disease Library
            </h2>
            <p className="text-base text-gray-600">
              Learn about common rice diseases, their symptoms, and prevention
              methods
            </p>
          </div>

          {/* <div className="w-full grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {diseases.map((disease, index) => (
              <DiseaseCard key={index} {...disease} />
            ))}
          </div> */}
          <InfiniteSlider diseases={diseases} />
        </section>
      </main>
    </div>
    
  );
}  

  //  <div className="overflow-hidden w-full relative">
  //           <motion.div
  //             className="flex gap-8"
  //             animate={{ x: ["0%", "-100%"] }}
  //             transition={{
  //               repeat: Infinity,
  //               duration: 40, // tăng duration để trượt chậm, mượt
  //               ease: "linear",
  //             }}
  //             whileHover={{ animationPlayState: "paused" }}
  //             style={{ display: "flex" }}
  //           >
  //             {/* nhân đôi dữ liệu để tạo hiệu ứng liền mạch */}
  //             {[...diseases, ...diseases].map((disease, index) => (
  //               <div
  //                 key={index}
  //                 className="min-w-[320px] md:min-w-[360px] flex-shrink-0"
  //               >
  //                 <DiseaseCard key={index} {...disease} />
  //               </div>
  //             ))}
  //           </motion.div>
  //         </div>