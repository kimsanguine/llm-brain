import React, { CSSProperties } from 'react';
import { AbsoluteFill, Easing, Img, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';

// Kept separate from the original 60-second films' dark theme.
const c = { paper: '#fbfaf7', ink: '#111111', violet: '#7c3aed', blue: '#2563eb', muted: '#74716a', rule: '#d9d6d0' };
const display = "'Helvetica Neue', 'Apple SD Gothic Neo', sans-serif";
const mono = "'SF Mono', Menlo, monospace";
export const ONTOLOGY_FPS = 30;
export const ONTOLOGY_FRAMES = 900;

const progress = (frame: number, start: number, duration = 26) => interpolate(frame, [start, start + duration], [0, 1], {
  extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
});
const reveal = (frame: number, start: number, distance = 28): CSSProperties => {
  const p = progress(frame, start);
  return { opacity: p, transform: `translateY(${(1 - p) * distance}px)` };
};

const Eyebrow: React.FC<{ children: React.ReactNode; color?: string; style?: CSSProperties }> = ({ children, color = c.violet, style }) => (
  <div style={{ fontFamily: mono, fontSize: 19, letterSpacing: 2.6, color, lineHeight: 1.5, ...style }}>{children}</div>
);

const Paper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ background: c.paper, color: c.ink, fontFamily: display, overflow: 'hidden' }}>
    <svg width="1920" height="1080" style={{ position: 'absolute', opacity: 0.33 }}>
      <defs><pattern id="ontology-paper" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.9" fill={c.muted} opacity="0.2" /></pattern></defs>
      <rect width="1920" height="1080" fill="url(#ontology-paper)" />
    </svg>
    {children}
  </AbsoluteFill>
);

const ImageField: React.FC<{ name: string; frame: number; left: number; top?: number; width: number; height?: number; opacity?: number }> = ({ name, frame, left, top = 0, width, height = 1080, opacity = 1 }) => (
  <div style={{ position: 'absolute', left, top, width, height, overflow: 'hidden', opacity }}>
    <Img src={staticFile(`ontology/${name}.webp`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1.045 - progress(frame, 0, 210) * 0.045})` }} />
  </div>
);

const RunningFrame: React.FC<{ step: string; title: string }> = ({ step, title }) => (
  <>
    <div style={{ position: 'absolute', left: 90, top: 48, right: 90, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Eyebrow>LLM-BRAIN / PERSONAL KNOWLEDGE ONTOLOGY</Eyebrow>
      <Eyebrow color={c.muted}>{step} / 05</Eyebrow>
    </div>
    <div style={{ position: 'absolute', left: 90, right: 90, top: 98, height: 1, background: c.rule }} />
    <div style={{ position: 'absolute', bottom: 49, left: 90, right: 90, display: 'flex', justifyContent: 'space-between' }}>
      <Eyebrow color={c.muted} style={{ fontSize: 16 }}>{title}</Eyebrow>
      <Eyebrow color={c.muted} style={{ fontSize: 16 }}>habix.ai</Eyebrow>
    </div>
  </>
);

const Fragmented: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Paper>
      <ImageField name="information-field" frame={f} left={915} width={1005} />
      <AbsoluteFill style={{ background: 'linear-gradient(90deg, #fbfaf7 0%, #fbfaf7 40%, rgba(251,250,247,.92) 49%, rgba(251,250,247,0) 65%)' }} />
      <RunningFrame step="01" title="FRAGMENTS → A QUESTION" />
      <div style={{ position: 'absolute', left: 100, top: 255 }}>
        <Eyebrow style={reveal(f, 3)}>INFORMATION IS EVERYWHERE.</Eyebrow>
        <div style={{ fontSize: 84, lineHeight: 1.22, letterSpacing: -4.5, fontWeight: 650, marginTop: 40, ...reveal(f, 12) }}>다시 찾은 정보,</div>
        <div style={{ fontSize: 84, lineHeight: 1.22, letterSpacing: -4.5, fontWeight: 650, ...reveal(f, 30) }}>무엇을 믿고</div>
        <div style={{ fontSize: 84, lineHeight: 1.22, letterSpacing: -4.5, fontWeight: 650, color: c.violet, ...reveal(f, 43) }}>쓸 수 있을까?</div>
        <div style={{ marginTop: 48, fontSize: 27, color: c.muted, ...reveal(f, 64) }}>메모와 링크 사이, 빠져 있던 근거의 연결.</div>
      </div>
      {['NOTE', 'LINK', 'SOURCE'].map((label, i) => (
        <div key={label} style={{ position: 'absolute', left: 1110 + i * 135, top: 785 + (i % 2) * 45, fontFamily: mono, fontSize: 18, color: i === 1 ? c.violet : c.ink, letterSpacing: 2, opacity: progress(f, 24 + i * 10), transform: `translateY(${-progress(f, 20, 130) * (18 + i * 7)}px)` }}>{label}</div>
      ))}
    </Paper>
  );
};

const Arrow: React.FC<{ x1: number; y1: number; x2: number; y2: number; frame: number; start: number; label: string; color?: string; labelDy?: number }> = ({ x1, y1, x2, y2, frame, start, label, color = c.violet, labelDy = -25 }) => {
  const p = progress(frame, start, 36);
  const angle = Math.atan2(y2 - y1, x2 - x1);
  const point = (offset: number) => `${x2 - 13 * Math.cos(angle + offset)},${y2 - 13 * Math.sin(angle + offset)}`;
  return (
    <g>
      <path d={`M${x1},${y1} L${x2},${y2}`} fill="none" stroke={color} strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - p} />
      <polyline points={`${point(-0.4)} ${x2},${y2} ${point(0.4)}`} stroke={color} strokeWidth="2" fill="none" opacity={progress(frame, start + 23, 12)} />
      <text x={(x1 + x2) / 2} y={(y1 + y2) / 2 + labelDy} textAnchor="middle" fill={color} fontFamily={mono} fontSize="22" opacity={progress(frame, start + 8)}>{label}</text>
    </g>
  );
};

const KnowledgeFlow: React.FC = () => {
  const f = useCurrentFrame();
  const nodes = [
    { x: 110, w: 360, key: 'source', title: '출처', desc: '정보가 시작된 원문', color: c.ink, start: 8 },
    { x: 760, w: 360, key: 'claim', title: '주장', desc: '근거를 붙여 기록한 내용', color: c.violet, start: 43 },
    { x: 1410, w: 400, key: 'knowledge_page', title: '지식', desc: '연결하고 정리한 페이지', color: c.blue, start: 92 },
  ];
  return (
    <Paper>
      <RunningFrame step="02" title="FROM SOURCE TO KNOWLEDGE" />
      <div style={{ position: 'absolute', left: 100, top: 172, ...reveal(f, 0) }}>
        <h1 style={{ margin: 0, fontSize: 72, fontWeight: 650, letterSpacing: -3 }}>정보를 모으는 데서, <span style={{ color: c.violet }}>관계를 남기는 일로.</span></h1>
        <div style={{ marginTop: 25, fontSize: 29, color: c.muted }}>출처는 주장을 뒷받침하고, 주장은 지식 페이지로 정리됩니다.</div>
      </div>
      <svg width="1920" height="1080" style={{ position: 'absolute' }}>
        <Arrow x1={475} y1={560} x2={750} y2={560} frame={f} start={27} label="supports" />
        <Arrow x1={1125} y1={560} x2={1400} y2={560} frame={f} start={72} label="compiled_into" color={c.blue} />
      </svg>
      {nodes.map((n, i) => (
        <div key={n.key} style={{ position: 'absolute', left: n.x, top: 427, width: n.w, color: n.color, ...reveal(f, n.start) }}>
          <div style={{ height: 245, borderTop: `3px solid ${n.color}`, borderBottom: `1px solid ${c.rule}`, padding: '22px 0' }}>
            <Eyebrow color={n.color}>0{i + 1} / {n.key}</Eyebrow>
            <div style={{ fontSize: 67, fontWeight: 600, letterSpacing: -2, marginTop: 32 }}>{n.title}</div>
            <div style={{ fontSize: 25, color: c.muted, marginTop: 16 }}>{n.desc}</div>
          </div>
          <div style={{ display: 'flex', gap: 7, marginTop: 24 }}>
            {Array.from({ length: 10 + i * 4 }, (_, j) => <div key={j} style={{ height: 4, width: 8 + (j % 4) * 3, background: n.color, opacity: 0.12 + (j % 3) * 0.15 }} />)}
          </div>
        </div>
      ))}
      <div style={{ position: 'absolute', left: 100, top: 839, right: 100, borderLeft: `3px solid ${c.violet}`, paddingLeft: 24, fontSize: 29, ...reveal(f, 135) }}>연결을 남기면, 다시 찾은 지식의 출발점도 따라갈 수 있습니다.</div>
    </Paper>
  );
};

const Evidence: React.FC = () => {
  const f = useCurrentFrame();
  const rows = [
    ['claim', '정보를 목적에 맞게 정리한다.'],
    ['source', '공개 메모 · 예시 원문 L12–18'],
    ['status / trust', 'active / trusted'],
    ['valid_from', '2026-01-01'],
    ['valid_until', '2099-01-01'],
  ];
  return (
    <Paper>
      <RunningFrame step="03" title="FOLLOW THE EVIDENCE" />
      <div style={{ position: 'absolute', left: 100, top: 257, width: 700 }}>
        <Eyebrow style={reveal(f, 0)}>EXPLAIN / READ ONLY</Eyebrow>
        <div style={{ fontSize: 88, fontWeight: 650, letterSpacing: -4, lineHeight: 1.2, marginTop: 39, ...reveal(f, 10) }}>왜 이 지식인가?</div>
        <div style={{ fontSize: 32, lineHeight: 1.65, marginTop: 35, color: c.muted, ...reveal(f, 29) }}>연결된 출처와 주장,<br />저장된 상태와 유효기간을 확인합니다.</div>
        <div style={{ width: 140, height: 3, background: c.violet, marginTop: 46, transformOrigin: 'left', transform: `scaleX(${progress(f, 53)})` }} />
        <div style={{ fontSize: 25, color: c.violet, marginTop: 24, lineHeight: 1.7, ...reveal(f, 84) }}>저장된 상태는 사실 판정이 아닙니다.<br />근거를 읽고, 사용 여부는 사람이 판단합니다.</div>
      </div>
      <div style={{ position: 'absolute', left: 880, top: 183, width: 940, height: 724, background: c.ink, color: c.paper, padding: '42px 46px', ...reveal(f, 10, 42) }}>
        <Eyebrow color="#a78bfa">WHY THIS KNOWLEDGE? / EXAMPLE</Eyebrow>
        <div style={{ marginTop: 27, paddingBottom: 25, borderBottom: '1px solid #41403e', fontSize: 31, fontWeight: 500 }}>정보 정리의 원칙</div>
        {rows.map(([key, value], i) => (
          <div key={key} style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 20, padding: '24px 0', borderBottom: '1px solid #32312f', ...reveal(f, 36 + i * 14, 12) }}>
            <div style={{ fontFamily: mono, fontSize: 20, color: '#b8b3c1', paddingTop: 3 }}>{key}</div>
            <div style={{ fontSize: 25, letterSpacing: -0.5, color: i === 2 ? '#b6a2ff' : c.paper }}>{value}</div>
          </div>
        ))}
        <div style={{ fontSize: 20, color: '#b8b3c1', marginTop: 25, ...reveal(f, 125) }}>설명용 예시 · 실제 데이터와 무관</div>
      </div>
    </Paper>
  );
};

const Reuse: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Paper>
      <ImageField name="reuse-field" frame={f} left={0} top={107} width={790} height={862} opacity={0.82} />
      <AbsoluteFill style={{ background: 'linear-gradient(90deg, transparent 20%, rgba(251,250,247,.4) 33%, #fbfaf7 43%)' }} />
      <RunningFrame step="04" title="A REUSABLE ARTIFACT, WITH ITS ORIGINS" />
      <div style={{ position: 'absolute', left: 850, top: 177, ...reveal(f, 0) }}>
        <h1 style={{ margin: 0, fontSize: 72, fontWeight: 650, lineHeight: 1.2, letterSpacing: -3 }}>지식은 다시,<br /><span style={{ color: c.violet }}>쓸 수 있는 결과물로.</span></h1>
        <div style={{ marginTop: 29, color: c.muted, fontSize: 28 }}>답변 · 요약 · 의사결정, 그 근거와 절차까지.</div>
      </div>
      <svg width="1920" height="1080" style={{ position: 'absolute' }}>
        <Arrow x1={1180} y1={619} x2={1460} y2={563} frame={f} start={38} label="derived_from" color={c.blue} labelDy={-28} />
        <Arrow x1={1180} y1={688} x2={1460} y2={794} frame={f} start={75} label="guided_by" labelDy={36} />
      </svg>
      <div style={{ position: 'absolute', left: 850, top: 545, width: 320, height: 200, padding: '25px 0', borderTop: `3px solid ${c.ink}`, borderBottom: `1px solid ${c.rule}`, ...reveal(f, 17) }}>
        <Eyebrow color={c.ink}>artifact</Eyebrow>
        <div style={{ fontSize: 43, fontWeight: 600, marginTop: 29 }}>의사결정 메모</div>
        <div style={{ fontSize: 23, marginTop: 14, color: c.muted }}>근거로 돌아갈 수 있는 결과물</div>
      </div>
      <div style={{ position: 'absolute', left: 1485, top: 501, width: 350, borderTop: `2px solid ${c.blue}`, paddingTop: 23, ...reveal(f, 63) }}>
        <Eyebrow color={c.blue}>knowledge_page</Eyebrow><div style={{ fontSize: 39, marginTop: 22 }}>바탕이 된 지식</div>
      </div>
      <div style={{ position: 'absolute', left: 1485, top: 743, width: 350, borderTop: `2px solid ${c.violet}`, paddingTop: 23, ...reveal(f, 103) }}>
        <Eyebrow>procedure</Eyebrow><div style={{ fontSize: 39, marginTop: 22 }}>따른 작성 절차</div>
      </div>
      <div style={{ position: 'absolute', left: 850, top: 914, fontSize: 24, color: c.muted, ...reveal(f, 125) }}>무엇에서 나왔는지, 어떤 절차를 따랐는지.</div>
    </Paper>
  );
};

const Close: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Paper>
      <div style={{ position: 'absolute', left: 970, top: 280, width: 900, height: 506.25, border: `1px solid ${c.rule}`, ...reveal(f, 8, 20) }}>
        <Img src={staticFile('ontology/ontology-atlas.webp')} style={{ display: 'block', width: '100%', height: '100%', objectFit: 'contain' }} />
      </div>
      <RunningFrame step="05" title="FOLLOW THE EVIDENCE. REUSE THE KNOWLEDGE." />
      <div style={{ position: 'absolute', top: 262, left: 100 }}>
        <Eyebrow style={reveal(f, 0)}>PERSONAL KNOWLEDGE ONTOLOGY</Eyebrow>
        <div style={{ fontSize: 175, lineHeight: 1.1, letterSpacing: -8, fontWeight: 700, marginTop: 28, ...reveal(f, 10, 36) }}>llm-brain</div>
        <div style={{ width: 790, height: 3, background: c.violet, marginTop: 40, transformOrigin: 'left', transform: `scaleX(${progress(f, 20, 43)})` }} />
        <div style={{ fontSize: 53, letterSpacing: -2, fontWeight: 500, marginTop: 36, ...reveal(f, 34) }}>근거를 따라, 지식을 다시 쓰다.</div>
        <div style={{ fontFamily: mono, fontSize: 28, color: c.violet, marginTop: 63, ...reveal(f, 55) }}>habix.ai/products/llm-brain <span style={{ marginLeft: 14 }}>↗</span></div>
      </div>
    </Paper>
  );
};

// The editorial cut has no overlap: the brief's exact five beat boundaries stay intact.
// A short ink rule sweeps across each new page without delaying its readable content.
const CutRule: React.FC = () => {
  const f = useCurrentFrame();
  const p = progress(f, 0, 18);
  return <div style={{ position: 'absolute', left: `${p * 100}%`, top: 0, width: 3, height: 1080, opacity: 1 - p, background: c.violet }} />;
};

export const LlmBrainOntology30: React.FC = () => (
  <AbsoluteFill style={{ background: c.paper }}>
    <Sequence from={0} durationInFrames={150} premountFor={30}><Fragmented /></Sequence>
    <Sequence from={150} durationInFrames={210} premountFor={30}><KnowledgeFlow /><CutRule /></Sequence>
    <Sequence from={360} durationInFrames={210} premountFor={30}><Evidence /><CutRule /></Sequence>
    <Sequence from={570} durationInFrames={180} premountFor={30}><Reuse /><CutRule /></Sequence>
    <Sequence from={750} durationInFrames={150} premountFor={30}><Close /><CutRule /></Sequence>
  </AbsoluteFill>
);
