import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring } from 'remotion';
import { colors, fonts, FPS } from '../theme';

/**
 * Scene 6 — Features (46-54s, 240 frames).
 * 2×2 그리드, 4가지 핵심 기능 순서대로 등장.
 */
export const SceneFeatures: React.FC = () => {
  const frame = useCurrentFrame();

  // 타이틀
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const features = [
    {
      icon: '📥',
      name: 'ingest',
      desc: '4가지 입력 채널 + resonance 필터',
      color: colors.blue,
      startFrame: 40,
    },
    {
      icon: '🔁',
      name: 'curate',
      desc: 'distill_level 점진 압축 + graph 분석',
      color: colors.purple,
      startFrame: 100,
    },
    {
      icon: '📤',
      name: 'express',
      desc: 'wiki → 블로그·강의·리포트 자동 생성',
      color: colors.green,
      startFrame: 160,
    },
    {
      icon: '🔍',
      name: 'query',
      desc: '접근 기록 → 자동 재압축 우선순위',
      color: colors.gold,
      startFrame: 210,
    },
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
      {/* 타이틀 */}
      <div
        style={{
          fontSize: 32,
          fontWeight: 700,
          color: colors.text,
          opacity: titleOpacity,
          marginBottom: 48,
          letterSpacing: '-0.01em',
        }}
      >
        핵심 기능
      </div>

      {/* 2×2 그리드 */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 24,
          width: '100%',
          maxWidth: 800,
        }}
      >
        {features.map((feat, i) => {
          const cellOpacity = interpolate(
            frame,
            [feat.startFrame, feat.startFrame + 30],
            [0, 1],
            { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          );
          const cellScale = spring({
            frame: frame - feat.startFrame,
            fps: FPS,
            config: { mass: 0.7, damping: 13, stiffness: 200 },
            from: 0.8,
            to: 1,
          });

          return (
            <div
              key={feat.name}
              style={{
                opacity: cellOpacity,
                transform: `scale(${cellScale})`,
                backgroundColor: colors.surface,
                border: `1px solid ${feat.color}55`,
                borderRadius: 14,
                padding: '24px 28px',
                display: 'flex',
                flexDirection: 'column',
                gap: 12,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ fontSize: 28 }}>{feat.icon}</span>
                <span
                  style={{
                    fontFamily: fonts.mono,
                    fontSize: 20,
                    fontWeight: 700,
                    color: feat.color,
                  }}
                >
                  {feat.name}
                </span>
              </div>
              <div
                style={{
                  fontSize: 17,
                  color: colors.dim,
                  lineHeight: 1.5,
                }}
              >
                {feat.desc}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
