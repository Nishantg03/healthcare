import { Suspense } from "react";
import dynamic from "next/dynamic";

const Dashboard = dynamic(() => import("@/components/Dashboard"), {
  loading: () => (
    <div className="w-full h-screen flex items-center justify-center bg-gray-50">
      <div className="animate-pulse text-gray-400">Loading...</div>
    </div>
  ),
});

export default function Home() {
  return (
    <Suspense
      fallback={
        <div className="w-full h-screen flex items-center justify-center bg-gray-50">
          <div className="animate-pulse text-gray-400">Loading...</div>
        </div>
      }
    >
      <Dashboard />
    </Suspense>
  );
}
