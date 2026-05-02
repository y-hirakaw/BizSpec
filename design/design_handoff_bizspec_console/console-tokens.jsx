/* ============================================================
   ENGINEERING CONSOLE — three derivatives + dark mode toggle
   Shared palette: blue + purple + gray. Mono = JetBrains Mono.
   Tuned to be approachable for PdM / non-engineers too.
   ============================================================ */

// ---------- Tokens ----------
const TOKENS = {
  light: {
    bg:        "#FCFCFC",
    bgPanel:   "#FFFFFF",
    bgSubtle:  "#F7F7F7",
    bgInset:   "#FAFAFA",
    border:    "#E5E5E5",
    borderSoft:"#F0F0F0",
    text:      "#0E0E0E",
    textMid:   "#525252",
    textDim:   "#A3A3A3",
    accent:    "#2563EB",
    accentBg:  "#EEF2FF",
    purple:    "#7C3AED",
    purpleBg:  "#F5F3FF",
    gray:      "#525252",
    grayBg:    "#F0F0F0",
    ok:        "#10B981",
    warn:      "#D97706",
    danger:    "#DC2626",
  },
  dark: {
    bg:        "#0B0B0F",
    bgPanel:   "#121218",
    bgSubtle:  "#16161D",
    bgInset:   "#0F0F14",
    border:    "#23232C",
    borderSoft:"#1A1A22",
    text:      "#EDEDF0",
    textMid:   "#9A9AA8",
    textDim:   "#5F5F6E",
    accent:    "#7AA5FF",
    accentBg:  "rgba(122,165,255,0.10)",
    purple:    "#B79DFF",
    purpleBg:  "rgba(183,157,255,0.10)",
    gray:      "#9A9AA8",
    grayBg:    "rgba(154,154,168,0.10)",
    ok:        "#34D399",
    warn:      "#F59E0B",
    danger:    "#F87171",
  },
};

const exTone = (mode, type) => {
  const t = TOKENS[mode];
  if (type === "script")   return { fg: t.accent, bg: t.accentBg };
  if (type === "ai_agent") return { fg: t.purple, bg: t.purpleBg };
  return { fg: t.gray, bg: t.grayBg };
};

// ---------- Shared atoms ----------
function Pill({ children, bg, fg, mono = true, padding = "1px 6px" }) {
  return (
    <span style={{
      fontSize: "10px",
      padding,
      borderRadius: "3px",
      background: bg,
      color: fg,
      fontFamily: mono ? "'JetBrains Mono', monospace" : "inherit",
      letterSpacing: "-0.005em",
      whiteSpace: "nowrap",
    }}>{children}</span>
  );
}

function StatusDot({ color }) {
  return <span style={{
    width: "6px", height: "6px", borderRadius: "50%",
    background: color, display: "inline-block",
  }}></span>;
}

// Phase pill colors — gentle, friendly
const PHASE_COLOR = {
  spec:    { fg: "#7C3AED", bg: "rgba(124,58,237,0.10)" },
  dev:     { fg: "#2563EB", bg: "rgba(37,99,235,0.10)" },
  test:    { fg: "#D97706", bg: "rgba(217,119,6,0.10)" },
  release: { fg: "#059669", bg: "rgba(5,150,105,0.10)" },
  ops:     { fg: "#DB2777", bg: "rgba(219,39,119,0.10)" },
};

window.TOKENS = TOKENS;
window.exTone = exTone;
window.Pill = Pill;
window.StatusDot = StatusDot;
window.PHASE_COLOR = PHASE_COLOR;
