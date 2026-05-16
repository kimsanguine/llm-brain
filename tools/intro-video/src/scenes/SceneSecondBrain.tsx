import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring } from 'remotion';
import { colors, fonts, FPS } from '../theme';

/**
 * Scene 4 — Second Brain (29-37s, 240 frames).
 * 보라색 조명 + CODE 프레임워크 4단계 순차 등장.
 */
export const SceneSecondBrain: React.FC = () => {
  const frame = useCurrentFrame();

  // 보라 글로우 오버레이
  const purpleGlow = interpolate(frame, [0, 50], [0, 0.08], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 타이틀
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const codeSteps = [
    { letter: 'C', label: 'Capture', color: colors.blue, startFrame: 50 },
    { letter: 'O', label: 'Organize', color: colors.purple, startFrame: 100 },
    { letter: 'D', label: 'Distill', color: colors.gold, startFrame: 150 },
    { letter: 'E', label: 'Express', color: colors.green, startFrame: 200 },
  ];

  // 하이라이트 문장 — frame 210 이후
  const highlightOpacity = interpolate(frame, [215, 235], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        fontFamily: fonts.display,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 100px',
      }}
    >
      {/* 보라 글로우 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: colors.purple,
          opacity: purpleGlow,
          pointerEvents: 'none',
        }}
      />

      {/* 타이틀 */}
      <div
        style={{
          fontSize: 36,
          fontWeight: 700,
          color: colors.purple,
          opacity: titleOpacity,
          marginBottom: 56,
          letterSpacing: '-0.01em',
          position: 'relative',
          zIndex: 1,
        }}
      >
        Tiago Forte의 Second Brain
      </div>

      {/* CODE 4단계 */}
      <div
        style={{
          display: 'flex',
          gap: 24,
          alignItems: 'center',
          position: 'relative',
          zIndex: 1,
          marginBottom: 48,
        }}
      >
        {codeSteps.map((step, i) => {
          const stepOpacity = interpolate(
            frame,
            [step.startFrame, step.startFrame + 25],
            [0, 1],
            { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          );
          const stepScale = spring({
            frame: frame - step.startFrame,
            fps: FPS,
            config: { mass: 0.7, damping: 12, stiffness: 240 },
            from: 0.7,
            to: 1,
          });

          return (
            <React.Fragment key={step.letter}>
              <div
                style={{
                  opacity: stepOpacity,
                  transform: `scale(${stepScale})`,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 12,
                }}
              >
                <div
                  style={{
                    width: 80,
                    height: 80,
                    borderRadius: 16,
                    backgroundColor: step.color + '22',
                    border: `2px solid ${step.color}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 40,
                    fontWeight: 900,
                    color: step.color,
                    boxShadow: `0 0 24px ${step.color}44`,
                  }}
                >
                  {step.letter}
                </div>
                <div
                  style={{
                    fontSize: 16,
                    color: colors.dim,
                    fontWeight: 500,
                  }}
                >
                  {step.label}
                </div>
              </div>

              {/* 연결 화살표 (마지막 제외) */}
              {i < codeSteps.length - 1 && (
                <div
                  style={{
                    opacity: interpolate(
                      frame,
                      [step.startFrame + 20, step.startFrame + 40],
                      [0, 0.5],
                      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
                    ),
                    fontSize: 24,
                    color: colors.dim,
                    marginTop: -24,
                  }}
                >
                  →
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* 하이라이트 문장 */}
      <div
        style={{
          opacity: highlightOpacity,
          backgroundColor: colors.surface,
          border: `1px solid ${colors.gold}66`,
          borderRadius: 12,
          padding: '20px 36px',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <div
          style={{
            fontSize: 22,
            color: colors.gold,
            fontWeight: 600,
            textAlign: 'center',
          }}
        >
          Distill과 Express, 사람이 직접 해야 했다
        </div>
      </div>
    </AbsoluteFill>
  );
};
