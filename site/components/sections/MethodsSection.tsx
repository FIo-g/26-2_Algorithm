import { StepDemo } from "@/components/demo/StepDemo";
import { Plate } from "@/components/sign/Plate";
import { loadDemos } from "@/lib/demos";

export function MethodsSection() {
  const demos = loadDemos();
  return (
    <section id="methods" className="flow-section" aria-labelledby="methods-title">
      <h2 id="methods-title">How each method picks the next intersection</h2>
      <p>Step through the real heap pushes and pops on graphs small enough to check by hand.</p>
      <Plate tone="blue" inline>
        <StepDemo demos={demos} />
      </Plate>
    </section>
  );
}
