import { Composition } from "remotion";
import { TtsIntro } from "./TtsIntro";
import { narrationCues } from "./narrationCues";

export const Root: React.FC = () => {
  return (
    <>
      {/* Fast-cut intro: ~75s synced to narration audio, 22 beats across 5 acts */}
      <Composition
        id="TtsIntro"
        component={TtsIntro}
        durationInFrames={narrationCues.totalFrames}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
