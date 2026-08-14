import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";

let savedOffset = 0;

function MarqueeSegment({ items, prefix = "" }) {
  return (
    <>
      {items.map((label, idx) => (
        <span
          key={`${prefix}-${idx}-${label}`}
          className="marquee__item flex shrink-0 items-center gap-6 text-[11px] font-semibold uppercase tracking-[0.28em] text-ink-muted"
        >
          <span>{label}</span>
          <span className="dot" />
        </span>
      ))}
    </>
  );
}

export default function Marquee({ items, speed = 42 }) {
  const { i18n } = useTranslation();
  const isRtl = i18n.language?.startsWith("ar");
  const trackRef = useRef(null);
  const segmentRef = useRef(null);

  useEffect(() => {
    let running = true;
    let lastTs = 0;

    const tick = (ts) => {
      if (!running) return;

      const track = trackRef.current;
      const segment = segmentRef.current;
      if (track && segment) {
        const segW = segment.getBoundingClientRect().width;
        if (segW > 0) {
          if (!lastTs) lastTs = ts;
          const dt = Math.min((ts - lastTs) / 1000, 0.05);
          lastTs = ts;

          const dir = isRtl ? 1 : -1;
          savedOffset += speed * dt * dir;

          while (savedOffset <= -segW) savedOffset += segW;
          while (savedOffset > 0) savedOffset -= segW;

          track.style.transform = `translate3d(${savedOffset}px, 0, 0)`;
        }
      }

      requestAnimationFrame(tick);
    };

    const id = requestAnimationFrame(tick);
    return () => {
      running = false;
      cancelAnimationFrame(id);
    };
  }, [isRtl, speed, items]);

  if (!items?.length) return null;

  return (
    <div className="marquee border-y border-ink/12 bg-paper-raised/80 py-3">
      <div ref={trackRef} className="marquee__track">
        <div ref={segmentRef} className="marquee__segment">
          <MarqueeSegment items={items} prefix="a" />
        </div>
        <div className="marquee__segment" aria-hidden="true">
          <MarqueeSegment items={items} prefix="b" />
        </div>
        <div className="marquee__segment" aria-hidden="true">
          <MarqueeSegment items={items} prefix="c" />
        </div>
      </div>
    </div>
  );
}
