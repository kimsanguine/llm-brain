import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring } from 'remotion';
import { colors, fonts, FPS } from '../theme';

/**
 * Scene 3 — Limits (20-29s, 270 frames).
 * 붉은 색조 전환 + 4가지 한계 순차 등장.
 */
export const SceneLimits: React.FC = () => {
  const frame = useCurrentFrame();

  // 배경 붉은 오버레이 — 점진적 등장
  const redOverlay = interpolate(frame, [0, 60], [0, 0.12], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 타이틀
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const limits = [
    { text: 'Express 없음 — 지식을 꺼내 쓸 방법이 없다', startFrame: 50 },
    { text: 'Capture 필터 없음 — 노이즈가 쌓인다', startFrame: 110 },
    { text: '단발성 압축 — 자주 쓰는 지식이 더 정제되지 않는다', startFrame: 170 },
    { text: '그래프 맹목 — 연결 구조를 활용하지 않는다', startFrame: 220 },
  ];

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
      {/* 붉은 배경 오버레이 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: colors.red,
          opacity: redOverlay,
          pointerEvents: 'none',
        }}
      />

      {/* 타이틀 */}
      <div
        style={{
          fontSize: 36,
          fontWeight: 700,
          color: colors.red,
          opacity: titleOpacity,
          marginBottom: 56,
          letterSpacing: '-0.01em',
          position: 'relative',
          zIndex: 1,
        }}
      >
        하지만 아직 부족한 것이 있습니다
      </div>

      {/* 한계 리스트 */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 18,
          width: '100%',
          maxWidth: 720,
          position: 'relative',
          zIndex: 1,
        }}
      >
        {limits.map((limit, i) => {
          const itemOpacity = interpolate(frame, [limit.startFrame, limit.startFrame + 25], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const itemScale = spring({
            frame: frame - limit.startFrame,
            fps: FPS,
            config: { mass: 0.6, damping: 16, stiffness: 200 },
            from: 0.9,
            to: 1,
          });
          const itemX = interpolate(frame, [limit.startFrame, limit.startFrame + 25], [-20, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });

          return (
            <div
              key={i}
              style={{
                opacity: itemOpacity,
                transform: `scale(${itemScale}) translateX(${itemX}px)`,
                display: 'flex',
                alignItems: 'flex-start',
                gap: 16,
                backgroundColor: colors.surface,
                border: `1px solid ${colors.red}44`,
                borderRadius: 10,
                padding: '16px 24px',
              }}
            >
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: '50%',
                  backgroundColor: colors.red,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 16,
                  flexShrink: 0,
                  fontWeight: 700,
                  color: '#fff',
                  lineHeight: 1,
                }}
              >
                ✗
              </div>
              <div
                style={{
                  fontSize: 20,
                  color: colors.text,
                  fontWeight: 400,
                  lineHeight: 1.5,
                }}
              >
                {limit.text}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
