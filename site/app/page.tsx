import { CongestionSection } from "@/components/sections/CongestionSection";
import { LimitsSection } from "@/components/sections/LimitsSection";
import { MapSection } from "@/components/sections/MapSection";
import { MethodsSection } from "@/components/sections/MethodsSection";
import { ResultsSection } from "@/components/sections/ResultsSection";
import { SameAnswerSection } from "@/components/sections/SameAnswerSection";
import { SiteNav } from "@/components/sections/SiteNav";
import { TeamSection } from "@/components/sections/TeamSection";

export const dynamic = "force-static";

export default function Page() {
  return (
    <>
      <SiteNav />
      <main>
        <MapSection />
        <div className="flow">
          <SameAnswerSection />
          <MethodsSection />
          <ResultsSection />
          <CongestionSection />
          <LimitsSection />
        </div>
      </main>
      <TeamSection />
    </>
  );
}
