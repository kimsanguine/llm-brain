import React from 'react';
import { AbsoluteFill, Sequence } from 'remotion';
import { SCENE_TIMING, colors } from '../theme';
import { SceneHook } from '../scenes/SceneHook';
import { SceneLlmWiki } from '../scenes/SceneLlmWiki';
import { SceneLimits } from '../scenes/SceneLimits';
import { SceneSecondBrain } from '../scenes/SceneSecondBrain';
import { SceneSynthesis } from '../scenes/SceneSynthesis';
import { SceneFeatures } from '../scenes/SceneFeatures';
import { SceneCta } from '../scenes/SceneCta';

const len = (k: keyof typeof SCENE_TIMING): number => {
  const t = SCENE_TIMING[k];
  return t.end - t.start;
};

/**
 * 메인 16:9 컴포지션 — 1920×1080, 60s.
 */
export const LlmBrainIntro16x9: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: colors.bg }}>
      <Sequence from={SCENE_TIMING.hook.start} durationInFrames={len('hook')}>
        <SceneHook />
      </Sequence>
      <Sequence from={SCENE_TIMING.llmwiki.start} durationInFrames={len('llmwiki')}>
        <SceneLlmWiki />
      </Sequence>
      <Sequence from={SCENE_TIMING.limits.start} durationInFrames={len('limits')}>
        <SceneLimits />
      </Sequence>
      <Sequence from={SCENE_TIMING.secondbrain.start} durationInFrames={len('secondbrain')}>
        <SceneSecondBrain />
      </Sequence>
      <Sequence from={SCENE_TIMING.synthesis.start} durationInFrames={len('synthesis')}>
        <SceneSynthesis />
      </Sequence>
      <Sequence from={SCENE_TIMING.features.start} durationInFrames={len('features')}>
        <SceneFeatures />
      </Sequence>
      <Sequence from={SCENE_TIMING.cta.start} durationInFrames={len('cta')}>
        <SceneCta />
      </Sequence>
    </AbsoluteFill>
  );
};
