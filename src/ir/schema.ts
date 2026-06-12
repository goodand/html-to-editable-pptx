/**
 * Visual Object IR — canonical contract between extraction and generation.
 * Version: 1.2.0
 * Invariants:
 *  I1. Every node carries sourceRef (provenance: critique #2).
 *  I2. bbox is in CSS px, page-absolute, 96dpi. Consumers convert (1/96 → inch).
 *  I3. zIndex is paint order: extractor traversal order. Mapper MUST sort by it.
 *  I4. semanticType is closed: text|shape|table|image|chart|group|fallbackRegion.
 *  I5. A table node owns its cells; cells never appear as top-level nodes.
 *  I6. fallbackRegion is a logged editability failure, never a silent default.
 *  I7. (1.1.0) Document is paged: slides[] in page order; zIndex restarts per slide.
 *  I8. (1.1.0) Covered cells of a rowspan/colspan are OMITTED from rows[][] —
 *      the spanning cell carries colspan/rowspan (mirrors dom-to-pptx extractTableData).
 *  I9. (1.2.0) chart carries dataSource provenance: "attr" (source-data tier) or
 *      "svg-marks" (mark/axis reverse-engineering tier). Repo policy: source first,
 *      marks second, ML never. Unparseable SVG → fallbackRegion with reason.
 */

export const IR_VERSION = "1.2.0";

export interface BBox { x: number; y: number; w: number; h: number; }   // CSS px

export interface IRStyle {
  fontFamily?: string;
  fontSizePx?: number;          // CSS px; mapper: pt = px * 72/96
  fontWeight?: number;          // 400 | 700 ...
  italic?: boolean;
  color?: string;               // "RRGGBB"
  align?: "left" | "center" | "right";
  fillColor?: string;           // "RRGGBB" | undefined = transparent
  borderColor?: string;
  borderWidthPx?: number;
  borderRadiusPx?: number;
  opacity?: number;             // 0..1
}

export interface IRNodeBase {
  irVersion: typeof IR_VERSION;
  sourceRef: string;            // e.g. "html>body>div#card>p:nth(2)"
  bbox: BBox;
  zIndex: number;
  semanticType: "text" | "shape" | "table" | "image" | "chart" | "group" | "fallbackRegion";
  style: IRStyle;
}

export interface IRText  extends IRNodeBase { semanticType: "text";  text: string; }
export interface IRShape extends IRNodeBase { semanticType: "shape"; shape: "rect" | "roundRect"; }
export interface IRImage extends IRNodeBase { semanticType: "image"; src: string; md5: string; }

export interface IRTableCell { text: string; style: IRStyle; colspan?: number; rowspan?: number; }
export interface IRTable extends IRNodeBase {
  semanticType: "table";
  rows: IRTableCell[][];        // I5, I8
  colWidthsPx: number[];
  rowHeightsPx?: number[];
}

export interface IRChartSeries { name: string; values: number[]; color?: string; }
export interface IRChart extends IRNodeBase {
  semanticType: "chart";
  chartType: "bar";                   // closed; extend deliberately
  categories: string[];
  series: IRChartSeries[];
  dataSource: "attr" | "svg-marks";   // I9
}

export interface IRGroup extends IRNodeBase { semanticType: "group"; children: IRNode[]; }
export interface IRFallback extends IRNodeBase { semanticType: "fallbackRegion"; reason: string; }

export type IRNode = IRText | IRShape | IRImage | IRTable | IRChart | IRGroup | IRFallback;

export interface IRSlide {
  background?: string;                // "RRGGBB"
  nodes: IRNode[];                    // flat, paint-ordered by zIndex (I7)
}

export interface IRDocument {
  irVersion: typeof IR_VERSION;
  pagePx: { w: number; h: number };   // e.g. 1280x720
  slides: IRSlide[];                  // page order (I7)
}
