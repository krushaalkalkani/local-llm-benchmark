export default function HeroArt() {
  return (
    <svg
      className="absolute inset-0 h-full w-full"
      viewBox="0 0 900 700"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden
    >
      <defs>
        <linearGradient id="beam" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#d2ff3f" stopOpacity="0" />
          <stop offset="45%" stopColor="#d2ff3f" stopOpacity="0.85" />
          <stop offset="100%" stopColor="#d2ff3f" stopOpacity="0" />
        </linearGradient>
        <filter id="soft">
          <feGaussianBlur stdDeviation="0.6" />
        </filter>
      </defs>

      {/* Orbit rings */}
      <g
        fill="none"
        stroke="#d2ff3f"
        strokeOpacity="0.35"
        style={{ animation: "drift 10s ease-in-out infinite" }}
      >
        <ellipse cx="620" cy="300" rx="220" ry="140" strokeWidth="1.2" />
        <ellipse cx="620" cy="300" rx="160" ry="95" strokeWidth="1" />
        <ellipse cx="620" cy="300" rx="100" ry="55" strokeWidth="1.5" />
      </g>

      {/* Signal path */}
      <path
        d="M40 520 C 180 480, 240 560, 360 500 S 520 420, 620 300 S 760 180, 860 120"
        fill="none"
        stroke="url(#beam)"
        strokeWidth="3"
        strokeDasharray="12 10"
        style={{ animation: "dash 2.8s linear infinite" }}
      />

      {/* Node cluster */}
      {[
        [620, 300],
        [540, 250],
        [700, 250],
        [560, 360],
        [690, 355],
        [620, 210],
      ].map(([x, y], i) => (
        <circle
          key={i}
          cx={x}
          cy={y}
          r={i === 0 ? 8 : 4.5}
          fill="#d2ff3f"
          filter="url(#soft)"
          opacity={i === 0 ? 1 : 0.7}
        />
      ))}

      {/* Telemetry readout */}
      <g fontFamily="ui-monospace, monospace" fill="#d2ff3f">
        <text x="48" y="72" fontSize="13" letterSpacing="2">
          OFFLINE INFERENCE · ACTIVE
        </text>
        <text x="48" y="110" fontSize="42" fontWeight="700">
          33.4
        </text>
        <text x="48" y="138" fontSize="12" opacity="0.75">
          TOK/S PEAK · LLAMA3.2:3B
        </text>
        <text x="48" y="190" fontSize="42" fontWeight="700">
          73.9%
        </text>
        <text x="48" y="218" fontSize="12" opacity="0.75">
          FIELD ACCURACY · MISTRAL:7B
        </text>
      </g>
    </svg>
  );
}
