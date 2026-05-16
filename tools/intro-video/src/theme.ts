/**
 * llm-brain intro video — visual theme.
 * Knowledge/brain 느낌: GitHub Dark 계열 + purple/gold accent.
 */

export const colors = {
  bg: '#0d1117',           // GitHub dark
  surface: '#161b22',
  border: '#30363d',
  text: '#c9d1d9',
  dim: '#8b949e',
  blue: '#58a6ff',         // knowledge flow
  purple: '#bc8cff',       // second brain / AI
  gold: '#e3b341',         // distill / highlight
  green: '#3fb950',        // express / output
  red: '#f85149',          // limits / warning
  accent: '#58a6ff',
};

export const fonts = {
  display: "'Pretendard', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif",
  mono: "'JetBrains Mono', 'SF Mono', monospace",
};

export const typography = {
  hookSize: 64,
  titleSize: 48,
  bodySize: 24,
  smallSize: 18,
  captionSize: 16,
  monoSize: 22,
};

/**
 * Total video length: 60s @ 30fps = 1800 frames.
 *
 * SCENE_TIMING — absolute frame positions [start, end].
 */
export const SCENE_TIMING = {
  hook:        { start: 0,    end: 210 },   // 0-7s   "매일 배우는 것들, 어디로 사라지나요?"
  llmwiki:     { start: 210,  end: 600 },   // 7-20s  LLM Wiki 장점 소개
  limits:      { start: 600,  end: 870 },   // 20-29s LLM Wiki의 4가지 한계
  secondbrain: { start: 870,  end: 1110 },  // 29-37s Second Brain(Forte) CODE 프레임워크
  synthesis:   { start: 1110, end: 1380 },  // 37-46s llm-brain = LLM Wiki + Second Brain
  features:    { start: 1380, end: 1620 },  // 46-54s 핵심 기능 4가지
  cta:         { start: 1620, end: 1800 },  // 54-60s CTA
} as const;

export const FPS = 30;
export const TOTAL_FRAMES = 1800;
