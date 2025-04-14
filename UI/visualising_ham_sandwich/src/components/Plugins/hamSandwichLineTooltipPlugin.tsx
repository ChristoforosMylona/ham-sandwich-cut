import { Plugin, Chart, ChartEvent } from "chart.js";

/**
 * This plugin enables tooltips to appear when hovering anywhere near the "Ham Sandwich Cut" line,
 * and stores the mouse position so the external tooltip handler can position the tooltip at the cursor.
 */
export const hamSandwichLineTooltipPlugin: Plugin<"line"> = {
  id: "hamSandwichLineTooltip",
  afterEvent: function (chart: Chart<"line">, args: { event: ChartEvent }) {
    const event = args.event;
    const tooltip = chart.tooltip;
    const lineDatasetIndex = chart.data.datasets.findIndex(
      (ds) => ds.label === "Ham Sandwich Cut"
    );
    if (lineDatasetIndex === -1) return;
    if (event.type !== "mousemove") {
      // Remove mouse position when not hovering
      (chart as any)._hamSandwichTooltipMouse = undefined;
      return;
    }

    const meta = chart.getDatasetMeta(lineDatasetIndex);
    if (!meta || !meta.data || meta.data.length < 2) return;

    const { x, y } = event as { x: number; y: number };
    const p1 = meta.data[0].getProps(["x", "y"], true);
    const p2 = meta.data[1].getProps(["x", "y"], true);

    function distToSegment(
      px: number,
      py: number,
      x1: number,
      y1: number,
      x2: number,
      y2: number
    ) {
      const A = px - x1;
      const B = py - y1;
      const C = x2 - x1;
      const D = y2 - y1;
      const dot = A * C + B * D;
      const len_sq = C * C + D * D;
      let param = -1;
      if (len_sq !== 0) param = dot / len_sq;
      let xx, yy;
      if (param < 0) {
        xx = x1;
        yy = y1;
      } else if (param > 1) {
        xx = x2;
        yy = y2;
      } else {
        xx = x1 + param * C;
        yy = y1 + param * D;
      }
      const dx = px - xx;
      const dy = py - yy;
      return Math.sqrt(dx * dx + dy * dy);
    }

    const distance = distToSegment(x, y, p1.x, p1.y, p2.x, p2.y);

    if (distance < 10) {
      (chart as any)._hamSandwichTooltipMouse = { x, y };
      tooltip?.setActiveElements(
        [
          {
            datasetIndex: lineDatasetIndex,
            index: 0,
          },
        ],
        { x, y }
      );
      chart.draw();
    } else {
        (chart as any)._hamSandwichTooltipMouse = undefined;
        tooltip?.setActiveElements([], { x: 0, y: 0 });
        chart.draw();
        // Hide the custom tooltip immediately
        const tooltipEl = document.getElementById("chartjs-custom-tooltip");
        if (tooltipEl) {
          tooltipEl.style.opacity = "0";
        }
      }
  },
};
