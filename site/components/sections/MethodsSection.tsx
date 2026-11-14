import { StepDemo } from "@/components/demo/StepDemo";
import { Plate } from "@/components/sign/Plate";
import { loadDemos } from "@/lib/demos";

export function MethodsSection() {
  const demos = loadDemos();
  return (
    <Plate tone="blue" id="methods" labelledBy="methods-title">
      <h2 id="methods-title">How each method picks the next intersection</h2>
      <StepDemo demos={demos} />
    </Plate>
  );
}
