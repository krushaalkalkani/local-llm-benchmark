export default function HeroArt() {
  return (
    <div
      className="relative h-full min-h-[320px] w-full overflow-hidden border border-[var(--line)] bg-[var(--paper-2)]"
      aria-hidden
    >
      <div className="grid-overlay absolute inset-0 opacity-70" />
      <div className="scan-line" />

      <svg
        viewBox="0 0 640 420"
        className="absolute inset-0 h-full w-full"
        role="presentation"
      >
        <defs>
          <linearGradient id="track" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#1f5c3a" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#c45c26" stopOpacity="0.35" />
          </linearGradient>
        </defs>

        {/* Race lanes */}
        {[90, 160, 230, 300].map((y) => (
          <line
            key={y}
            x1="40"
            y1={y}
            x2="600"
            y2={y}
            stroke="#c9c2ae"
            strokeWidth="1"
            strokeDasharray="6 8"
          />
        ))}

        {/* Model bars as a live race */}
        <g>
          <text x="48" y="78" className="mono" fill="#5c6356" fontSize="12">
            llama3.2:3b · 33.4 tok/s
          </text>
          <rect x="48" y="88" width="420" height="18" fill="url(#track)" />
          <rect x="48" y="88" width="420" height="18" fill="#1f5c3a" opacity="0.85" />
        </g>
        <g>
          <text x="48" y="148" className="mono" fill="#5c6356" fontSize="12">
            phi4-mini · 24.5 tok/s
          </text>
          <rect x="48" y="158" width="310" height="18" fill="#143d27" opacity="0.75" />
        </g>
        <g>
          <text x="48" y="218" className="mono" fill="#5c6356" fontSize="12">
            mistral:7b · 12.5 tok/s · highest accuracy
          </text>
          <rect x="48" y="228" width="210" height="18" fill="#c45c26" opacity="0.9" />
        </g>

        {/* Meter cluster */}
        <g transform="translate(480, 280)">
          {[28, 44, 36, 52, 40].map((h, i) => (
            <rect
              key={i}
              className="meter-bar"
              x={i * 18}
              y={60 - h}
              width="10"
              height={h}
              fill={i === 4 ? "#c45c26" : "#1f5c3a"}
              opacity="0.9"
            />
          ))}
          <text x="0" y="84" fill="#5c6356" fontSize="11" fontFamily="monospace">
            LIVE METRICS
          </text>
        </g>

        <text x="48" y="360" fill="#12160f" fontSize="13" fontFamily="monospace">
          Apple M4 · 16 GB · offline after pull
        </text>
      </svg>
    </div>
  );
}
