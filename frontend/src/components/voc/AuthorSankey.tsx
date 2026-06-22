import type { AuthorSankeyPayload } from "@/types/vocMarket";

type AuthorSankeyProps = {
  sankey: AuthorSankeyPayload;
};

const layerX: Record<number, number> = {
  0: 90,
  1: 420,
  2: 760,
};

const layerColors: Record<number, string> = {
  0: "var(--theme-primary)",
  1: "var(--voc-chart-2)",
  2: "var(--voc-chart-3)",
};

function truncateLabel(label: string, maxLength = 12) {
  return label.length > maxLength ? `${label.slice(0, maxLength)}...` : label;
}

export function AuthorSankey({ sankey }: AuthorSankeyProps) {
  const nodes = sankey.nodes ?? [];
  const links = sankey.links ?? [];
  if (!nodes.length || !links.length) {
    return (
      <div className="flex h-72 items-center justify-center rounded-2xl border border-dashed border-[var(--theme-border)] bg-white text-sm text-[var(--theme-muted)]">
        暂无可展示的作者、事件与用户画像关系
      </div>
    );
  }

  const grouped = [0, 1, 2].map((layer) => nodes.filter((node) => node.layer === layer));
  const nodePositions = new Map<string, { x: number; y: number; color: string }>();
  grouped.forEach((layerNodes, layer) => {
    const gap = 260 / Math.max(layerNodes.length, 1);
    layerNodes.forEach((node, index) => {
      nodePositions.set(node.id, {
        x: layerX[layer],
        y: 70 + gap * index + gap / 2,
        color: layerColors[layer],
      });
    });
  });
  const maxValue = Math.max(...links.map((link) => link.value), 1);

  return (
    <div className="rounded-2xl bg-[var(--theme-soft-panel)] p-4">
      <svg className="h-80 w-full" viewBox="0 0 860 360" role="img" aria-label="作者 -> 事件 -> 用户画像 桑基图">
        <rect x="0" y="0" width="860" height="360" rx="22" fill="#ffffff" />
        {links.map((link, index) => {
          const source = nodePositions.get(link.source);
          const target = nodePositions.get(link.target);
          if (!source || !target) return null;
          const strokeWidth = Math.max(2, (link.value / maxValue) * 16);
          const path = `M ${source.x + 42} ${source.y} C ${source.x + 150} ${source.y}, ${target.x - 150} ${target.y}, ${target.x - 42} ${target.y}`;
          return (
            <path
              key={`${link.source}-${link.target}-${index}`}
              d={path}
              fill="none"
              stroke={source.color}
              strokeLinecap="round"
              strokeOpacity="0.18"
              strokeWidth={strokeWidth}
            >
              <title>{`${link.source} -> ${link.target}: ${link.value.toLocaleString("zh-CN")} 条评论`}</title>
            </path>
          );
        })}
        {nodes.map((node) => {
          const position = nodePositions.get(node.id);
          if (!position) return null;
          return (
            <g key={node.id}>
              <rect x={position.x - 42} y={position.y - 18} width="84" height="36" rx="12" fill={position.color} opacity="0.12" />
              <circle cx={position.x - 42} cy={position.y} r="4" fill={position.color} />
              <circle cx={position.x + 42} cy={position.y} r="4" fill={position.color} />
              <text x={position.x} y={position.y + 4} textAnchor="middle" className="fill-[#151720] text-[11px] font-semibold">
                {truncateLabel(node.label)}
              </text>
              <title>{node.label}</title>
            </g>
          );
        })}
      </svg>
      <div className="mt-3 flex flex-wrap gap-2 text-xs text-[var(--theme-muted)]">
        <span className="rounded-lg bg-white px-2.5 py-1">作者</span>
        <span className="rounded-lg bg-white px-2.5 py-1">参与事件</span>
        <span className="rounded-lg bg-white px-2.5 py-1">吸引用户画像</span>
      </div>
    </div>
  );
}
