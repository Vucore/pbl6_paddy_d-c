interface DiseaseCardProps {
  image: string;
  title: string;
  symptoms: string;
  prevention: string[];
}

export default function DiseaseCard({
  image,
  title,
  symptoms,
  prevention,
}: DiseaseCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col">
      <img
        src={image}
        alt={title}
        className="w-full h-48 object-cover"
      />
      <div className="p-6 flex-1">
        <h3 className="text-xl font-bold text-gray-800 mb-3">{title}</h3>

        <div className="mb-4">
          <h4 className="text-base font-semibold text-gray-700 mb-2">
            Symptoms:
          </h4>
          <p className="text-sm text-gray-600 leading-relaxed">{symptoms}</p>
        </div>

        <div>
          <h4 className="text-base font-semibold text-gray-700 mb-2">
            Prevention:
          </h4>
          <ul className="space-y-1">
            {prevention.map((item, index) => (
              <li key={index} className="text-sm text-gray-600">
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
