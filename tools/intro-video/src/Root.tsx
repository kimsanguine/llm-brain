import React from 'react';
import { Composition } from 'remotion';
import { LlmBrainIntro16x9 } from './compositions/LlmBrainIntro16x9';
import { LlmBrainIntro9x16 } from './compositions/LlmBrainIntro9x16';
import { FPS, TOTAL_FRAMES } from './theme';
import { LlmBrainOntology30, ONTOLOGY_FPS, ONTOLOGY_FRAMES } from './compositions/LlmBrainOntology30';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="LlmBrainOntology30"
        component={LlmBrainOntology30}
        durationInFrames={ONTOLOGY_FRAMES}
        fps={ONTOLOGY_FPS}
        width={1920}
        height={1080}
      />
      <Composition
        id="LlmBrainIntro16x9"
        component={LlmBrainIntro16x9}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
      />
      <Composition
        id="LlmBrainIntro9x16"
        component={LlmBrainIntro9x16}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
      />
    </>
  );
};
