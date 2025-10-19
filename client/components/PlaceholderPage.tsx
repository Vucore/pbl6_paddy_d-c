import Header from "./Header";

interface PlaceholderPageProps {
  title: string;
  description?: string;
}

export default function PlaceholderPage({
  title,
  description = "This page is under construction. Continue prompting to add content here.",
}: PlaceholderPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-50">
      <Header />
      <main className="max-w-[1280px] mx-auto px-6 py-16">
        <div className="bg-white rounded-2xl shadow-xl p-12 text-center max-w-2xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">{title}</h1>
          <p className="text-lg text-gray-600">{description}</p>
        </div>
      </main>
    </div>
  );
}
