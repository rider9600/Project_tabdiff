// Final presentation (30 min, sections a-i) in the style of docs/presentations/Initial_Presentation.pptx:
// white slides, Georgia titles, near-black ink with one rust accent, thin rounded cards, big stat numbers.
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.SKILL + "/scripts/apply_theme.js");

const THEME = {
  name: "Gradient Gladiators",
  headFontFace: "Georgia",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1D22", lt1: "FFFFFF", dk2: "2B3A4A", lt2: "F4F3EF",
    accent1: "B5491D", accent2: "1B1D22", accent3: "8A8A8A", accent4: "2F6690", accent5: "D9D6CC", accent6: "6B6B6B",
    hlink: "2F6690", folHlink: "6B6B6B",
  },
};
const INK = "1B1D22", RUST = "B5491D", MUTED = "6B6B6B", LINE = "DEDBD2", SOFT = "F4F3EF", GREY = "8A8A8A", BLUE = "2F6690";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Can TabDiff generate drivable trips?";
pres.author = "Abhay Sharma and Naveen Kumar";

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: "FFFFFF" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 0.45, w: 11.9, h: 0.9, fontFace: "Georgia", fontSize: 34, bold: true, color: INK, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "kicker", type: "body", x: 0.7, y: 0.18, w: 8, h: 0.32, fontFace: "Calibri", fontSize: 12, bold: true, color: RUST, charSpacing: 2, margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.4, y: 7.0, w: 0.6, h: 0.3, fontFace: "Calibri", fontSize: 10, color: GREY, align: "right" },
});
pres.defineSlideMaster({ title: "BLANK", background: { color: "FFFFFF" }, objects: [] });

let n = 0;
function slide(section, kicker, title) {
  if (section) pres.addSection({ title: section });
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section || cur });
  if (section) cur = section;
  s.addText(kicker.toUpperCase(), { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  n++;
  return s;
}
let cur = "";
function card(s, x, y, w, h, o = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: o.fill || "FFFFFF" }, line: { color: o.line || LINE, width: 1 }, objectName: o.name || "card" });
}
function txt(s, text, x, y, w, h, o = {}) {
  s.addText(text, Object.assign({ x, y, w, h, isTextBox: true, margin: 0, fontFace: "Calibri", fontSize: 15, color: INK, valign: "top" }, o));
}
function stat(s, x, y, w, h, big, label, desc, color = RUST) {
  card(s, x, y, w, h);
  txt(s, big, x + 0.3, y + 0.3, w - 0.6, 0.85, { fontFace: "Georgia", fontSize: 40, color });
  txt(s, label, x + 0.3, y + 1.2, w - 0.6, 0.5, { fontSize: 16, bold: true });
  txt(s, desc, x + 0.3, y + 1.75, w - 0.6, h - 2.0, { fontSize: 13, color: MUTED });
}
function bullets(s, items, x, y, w, h, size = 16) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: { indent: 18 }, breakLine: i < items.length - 1 } })),
    { x, y, w, h, isTextBox: true, margin: 0, fontFace: "Calibri", fontSize: size, color: INK, valign: "top", paraSpaceAfter: 8 });
}
function arrow(s, x1, y1, x2, y2) {
  s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001, flipH: x2 < x1, line: { color: GREY, width: 1.25, endArrowType: "triangle" } });
}
function box(s, x, y, w, h, head, body, dark) {
  card(s, x, y, w, h, { fill: dark || "FFFFFF", line: dark || LINE });
  const c = dark ? "FFFFFF" : INK;
  txt(s, head, x + 0.25, y + 0.22, w - 0.5, 0.4, { fontFace: "Georgia", fontSize: 17, bold: true, color: dark ? "E9C2B0" : INK, align: dark ? "left" : "center" });
  txt(s, body, x + 0.25, y + 0.7, w - 0.5, h - 0.85, { fontSize: 13.5, color: dark ? "FFFFFF" : MUTED, align: dark ? "left" : "center" });
}

// 1. Title ---------------------------------------------------------------------------------------
{
  pres.addSection({ title: "Opening" }); cur = "Opening";
  const s = pres.addSlide({ masterName: "BLANK", sectionTitle: "Opening" });
  // road-grid motif on the right: a small directed graph with one highlighted path
  const ox = 8.2, oy = 1.1, g = 1.05;
  for (let i = 0; i < 5; i++) for (let j = 0; j < 5; j++) {
    if (j < 4) s.addShape(pres.shapes.LINE, { x: ox + j * g, y: oy + i * g, w: g, h: 0.001, line: { color: LINE, width: 2 } });
    if (i < 4) s.addShape(pres.shapes.LINE, { x: ox + j * g, y: oy + i * g, w: 0.001, h: g, line: { color: LINE, width: 2 } });
  }
  const path = [[0, 4], [1, 4], [1, 3], [2, 3], [2, 2], [3, 2], [3, 1], [4, 1]];
  for (let k = 0; k < path.length - 1; k++) {
    const [a, b] = path[k], [c, d] = path[k + 1];
    s.addShape(pres.shapes.LINE, { x: ox + Math.min(a, c) * g, y: oy + Math.min(b, d) * g, w: Math.abs(c - a) * g || 0.001, h: Math.abs(d - b) * g || 0.001, line: { color: RUST, width: 5 } });
  }
  for (let i = 0; i < 5; i++) for (let j = 0; j < 5; j++)
    s.addShape(pres.shapes.OVAL, { x: ox + j * g - 0.07, y: oy + i * g - 0.07, w: 0.14, h: 0.14, fill: { color: "FFFFFF" }, line: { color: GREY, width: 1 } });
  txt(s, "DFMGAI COURSE PROJECT  ·  FINAL PRESENTATION", 0.7, 1.0, 7, 0.35, { fontSize: 12, bold: true, color: RUST, charSpacing: 2 });
  txt(s, "Can a tabular diffusion model generate drivable trips?", 0.7, 1.55, 7.2, 2.2, { fontFace: "Georgia", fontSize: 40, bold: true });
  txt(s, "TabDiff on road-traversal transactions, with a graph-aware sampler", 0.7, 3.85, 7, 0.9, { fontSize: 20, color: MUTED });
  txt(s, "Base papers: TabDiff (Shi et al., ICLR 2025)  ·  Rathan, Reddy & Mondal (DAPD 2022)", 0.7, 5.0, 7.2, 0.4, { fontSize: 13, color: MUTED });
  txt(s, "Gradient Gladiators: Abhay Sharma and Naveen Kumar  ·  IIIT Hyderabad", 0.7, 6.55, 8, 0.4, { fontSize: 15 });
  s.addNotes("Title. One sentence: we took TabDiff, a state-of-the-art tabular diffusion model, and asked whether it can generate road trips that are actually drivable.");
}

// 2. (a) Motivation -------------------------------------------------------------------------------
{
  const s = slide("(a) Problem and motivation", "(a) Problem statement and motivation", "Trip data is valuable, and private");
  const items = [
    ["Planning", "Traffic planners, routing and map services all learn from where vehicles actually drive."],
    ["Privacy", "One taxi trip can reveal a home or a workplace. Raw GPS logs are rarely shareable."],
    ["Synthetic trips", "Generated trips that keep the statistics, without copying real ones, could be shared instead."],
  ];
  items.forEach(([h, b], i) => {
    const x = 0.7 + i * 4.05;
    card(s, x, 1.85, 3.75, 3.2);
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: 2.15, w: 0.62, h: 0.62, fill: { color: i === 2 ? RUST : INK }, line: { color: i === 2 ? RUST : INK } });
    txt(s, String(i + 1), x + 0.3, 2.15, 0.62, 0.62, { fontFace: "Georgia", fontSize: 20, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    txt(s, h, x + 0.3, 3.0, 3.2, 0.45, { fontFace: "Georgia", fontSize: 20, bold: true });
    txt(s, b, x + 0.3, 3.55, 3.2, 1.4, { fontSize: 15, color: MUTED });
  });
  txt(s, "Question: can TabDiff generate road trips that are drivable and keep busy roads, frequent patterns and popular paths? Does a sampler that knows the road graph help?", 0.7, 5.5, 11.9, 0.9, { fontSize: 17, italic: true, color: INK });
  s.addNotes("Why we care: trip data is useful and sensitive. Synthetic data is a standard answer. Our question has three parts: validity, fidelity, and whether a graph-aware sampler helps.");
}

// 3. (a) Trips as transactions --------------------------------------------------------------------
{
  const s = slide(null, "(a) Problem statement and motivation", "From a taxi trip to a table row");
  box(s, 0.7, 2.0, 3.4, 2.0, "GPS trajectory", "T-Drive taxi points, about one every 3 minutes");
  arrow(s, 4.2, 3.0, 4.75, 3.0);
  box(s, 4.85, 2.0, 3.4, 2.0, "Map-matched path", "sequence of directed road segments on the OSM graph", INK);
  arrow(s, 8.35, 3.0, 8.9, 3.0);
  box(s, 9.0, 2.0, 3.6, 2.0, "Transaction", "one binary row: 1 if the segment was travelled");
  // mini table row
  const cells = [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0];
  cells.forEach((v, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: 2.6 + i * 0.68, y: 4.65, w: 0.6, h: 0.5, fill: { color: v ? RUST : SOFT }, line: { color: LINE, width: 0.75 } });
    txt(s, String(v), 2.6 + i * 0.68, 4.65, 0.6, 0.5, { fontSize: 14, bold: true, align: "center", valign: "middle", color: v ? "FFFFFF" : MUTED });
    txt(s, "e" + (i + 1), 2.6 + i * 0.68, 5.2, 0.6, 0.3, { fontSize: 10, align: "center", color: GREY });
  });
  txt(s, "…  300 columns", 10.8, 4.75, 1.8, 0.4, { fontSize: 13, color: MUTED });
  txt(s, "Rathan, Reddy & Mondal model traversals as market-basket transactions and mine popular paths from frequent itemsets. A table of transactions is exactly what a tabular generator learns.", 0.7, 5.85, 11.9, 0.9, { fontSize: 15, color: MUTED });
  s.addNotes("The bridge between the two papers. Reddy et al. turn trips into transactions; that turns graph data into tabular data, which TabDiff is built for. Each row is a trip, each column a road segment.");
}

// 4. (b) Gaps -------------------------------------------------------------------------------------
{
  const s = slide("(b) Gaps", "(b) Gaps addressed", "What tabular models miss on road data");
  const g = [
    ["Structure between columns", "Tabular models treat columns as exchangeable features. A valid trip is a connected path: a hard constraint no column score measures."],
    ["Sparse, wide tables", "TabDiff was tested on UCI tables with a few dozen dense columns. Ours has 300 binary columns, about 4 of them on per row."],
    ["Sampling that can undo mistakes", "In masked diffusion a decoded value is final. TabDiff's re-noising sampler is off for all-categorical tables and blind to the road graph."],
  ];
  g.forEach(([h, b], i) => {
    const y = 1.75 + i * 1.62;
    card(s, 0.7, y, 11.9, 1.4, { fill: i === 2 ? SOFT : "FFFFFF" });
    txt(s, String(i + 1).padStart(2, "0"), 1.0, y + 0.3, 0.9, 0.8, { fontFace: "Georgia", fontSize: 32, color: RUST });
    txt(s, h, 2.0, y + 0.22, 9.9, 0.45, { fontFace: "Georgia", fontSize: 19, bold: true });
    txt(s, b, 2.0, y + 0.7, 10.3, 0.65, { fontSize: 14.5, color: MUTED });
  });
  s.addNotes("Three gaps. First, structure: drivability is a constraint across columns. Second, our table is far sparser and wider than TabDiff's benchmarks. Third, masked diffusion can't fix early mistakes, and TabDiff's own fix is disabled for our kind of table.");
}

// 5. (c) Formulation ------------------------------------------------------------------------------
{
  const s = slide("(c) Formulation", "(c) Problem formulation", "What a good synthetic trip table must do");
  card(s, 0.7, 1.75, 5.6, 4.6, { fill: SOFT, line: SOFT });
  txt(s, "Setup", 1.0, 2.0, 5, 0.45, { fontFace: "Georgia", fontSize: 19, bold: true });
  bullets(s, [
    "Road graph G = (V, E); the k = 300 most used directed segments in a 4 km window",
    "A trip is a binary vector x ∈ {0,1}^300",
    "Drivable: the on-segments form one simple directed path (no gaps, no branches)",
    "Learn p(x) from training trips, sample a synthetic table, compare with held-out test trips",
  ], 1.0, 2.55, 5.0, 3.6, 15);
  const goals = [["Validity", "share of drivable trips"], ["Busy roads", "segment-use ranking (Spearman, top-25)"], ["Patterns", "frequent itemsets, Jaccard (FP-growth)"], ["Popular paths", "ranking of alternative routes (Kendall τ)"]];
  goals.forEach(([h, b], i) => {
    const x = 6.7 + (i % 2) * 3.0, y = 1.75 + Math.floor(i / 2) * 2.35;
    card(s, x, y, 2.8, 2.15);
    txt(s, h, x + 0.25, y + 0.3, 2.3, 0.5, { fontFace: "Georgia", fontSize: 18, bold: true, color: i === 0 ? RUST : INK });
    txt(s, b, x + 0.25, y + 0.9, 2.3, 1.1, { fontSize: 14, color: MUTED });
  });
  s.addNotes("Formal setup. The four boxes are the four things we measure; validity is new compared with TabDiff's paper, the other three come from Reddy et al.'s use of the data. Privacy is measured as exact copies of training rows.");
}

// 6. (d) TabDiff recap ----------------------------------------------------------------------------
{
  const s = slide("(d) Algorithm", "(d) Algorithm", "TabDiff on an all-categorical table");
  box(s, 0.7, 1.8, 2.9, 1.5, "Real trip x₀", "300 binary columns");
  arrow(s, 3.7, 2.55, 4.15, 2.55);
  box(s, 4.25, 1.8, 4.6, 1.5, "FORWARD", "each column is replaced by [MASK] with probability 1 − αⱼ(t), a learnable per-column schedule", INK);
  arrow(s, 8.95, 2.55, 9.4, 2.55);
  box(s, 9.5, 1.8, 3.1, 1.5, "All-mask row", "t = 1");
  box(s, 9.5, 3.85, 3.1, 1.5, "All-mask row", "t = 1");
  arrow(s, 9.4, 4.6, 8.95, 4.6);
  box(s, 4.25, 3.85, 4.6, 1.5, "REVERSE", "a transformer predicts every masked column; 50 steps unmask columns until t = 0", RUST);
  arrow(s, 4.15, 4.6, 3.7, 4.6);
  box(s, 0.7, 3.85, 2.9, 1.5, "Synthetic trip", "decoded back to segments");
  txt(s, "Once a column is unmasked it is never revisited. TabDiff's stochastic sampler would re-noise, but it is switched off when a table has no numerical columns, which is our case.", 0.7, 5.8, 11.9, 0.8, { fontSize: 15.5, color: INK });
  s.addNotes("Recap of TabDiff restricted to what matters for us: only the masked (categorical) process, since the table has no numbers. Key point for the next slide: decoded values are final.");
}

// 7. (d) Graph-aware sampler ----------------------------------------------------------------------
{
  const s = slide(null, "(d) Algorithm", "Our graph-aware re-masking sampler");
  const steps = [["Look", "at the segments each row has decided so far"], ["Flag", "the ones that break drivability"], ["Re-mask", "flagged columns with extra probability λ"], ["Re-decide", "with TabDiff's next step, now with more context"]];
  steps.forEach(([h, b], i) => {
    const x = 0.7 + i * 3.05;
    card(s, x, 1.8, 2.75, 1.85, { fill: i === 2 ? INK : "FFFFFF", line: i === 2 ? INK : LINE });
    txt(s, h, x + 0.25, 2.0, 2.3, 0.5, { fontFace: "Georgia", fontSize: 20, bold: true, color: i === 2 ? "FFFFFF" : INK });
    txt(s, b, x + 0.25, 2.6, 2.3, 1.0, { fontSize: 14, color: i === 2 ? "FFFFFF" : MUTED });
    if (i < 3) arrow(s, x + 2.78, 2.72, x + 3.02, 2.72);
  });
  const flags = [["Branch", "two on-segments leave or enter the same node"], ["Boundary", "an end segment of a row split into pieces"], ["Bridge", "an off-segment that would join two pieces"]];
  txt(s, "Three flags", 0.7, 4.05, 4, 0.4, { fontFace: "Georgia", fontSize: 18, bold: true });
  flags.forEach(([h, b], i) => {
    const x = 0.7 + i * 4.05;
    card(s, x, 4.55, 3.75, 1.3, { fill: SOFT, line: SOFT });
    txt(s, h, x + 0.25, 4.7, 3.3, 0.4, { fontSize: 16, bold: true, color: RUST });
    txt(s, b, x + 0.25, 5.1, 3.3, 0.7, { fontSize: 14, color: MUTED });
  });
  txt(s, "Cheap: two matrix products with the node–segment incidence matrices per step, on the GPU. No retraining. Control arm: re-mask the same number of columns at random.", 0.7, 6.15, 11.9, 0.7, { fontSize: 14.5, color: INK });
  s.addNotes("Our algorithmic contribution. Explain the three flags with a sketch if asked. Stress the random control: same amount of re-masking, random places, so any difference is due to the graph.");
}

// 8. (e) Theory -----------------------------------------------------------------------------------
{
  const s = slide("(e) Theory", "(e) Theory", "Why re-masking shortens trips");
  card(s, 0.7, 1.75, 6.0, 4.7);
  txt(s, "Training objective", 1.0, 2.0, 5.4, 0.45, { fontFace: "Georgia", fontSize: 19, bold: true });
  txt(s, "The negative ELBO of masked diffusion is a weighted cross-entropy on masked columns:", 1.0, 2.55, 5.4, 0.7, { fontSize: 14.5, color: MUTED });
  txt(s, "L = E [ Σ_{j masked}  α′ⱼ(t) / (1 − αⱼ(t)) · log p_θ(x₀ⱼ | xₜ) ]", 1.0, 3.3, 5.4, 0.6, { fontFace: "Cambria Math", fontSize: 15, color: INK });
  txt(s, "Absorbing state", 1.0, 4.15, 5.4, 0.45, { fontFace: "Georgia", fontSize: 19, bold: true });
  txt(s, "[MASK] is entered and never left, so the reverse chain never revisits a decoded value. Re-masking turns it into a predictor–corrector sampler that can fix early mistakes.", 1.0, 4.65, 5.4, 1.6, { fontSize: 14.5, color: MUTED });
  card(s, 7.1, 1.75, 5.5, 4.7, { fill: INK, line: INK });
  txt(s, "≈ 4 of 300", 7.45, 2.05, 4.9, 0.9, { fontFace: "Georgia", fontSize: 44, color: "E9C2B0" });
  txt(s, "segments are on in a trip", 7.45, 2.95, 4.9, 0.45, { fontSize: 16, bold: true, color: "FFFFFF" });
  txt(s, "So for every column the model leans strongly to “off”. A flagged on-segment that is re-masked is usually re-decided off. Re-masking removes bad segments more often than it adds missing ones.\n\nPrediction: validity rises, but trips get shorter and busy-road agreement drops.", 7.45, 3.6, 4.9, 2.7, { fontSize: 14.5, color: "FFFFFF" });
  s.addNotes("The theory slide makes a prediction before we show results: because rows are sparse, re-masking will mostly delete segments. Results later confirm it.");
}

// 9. (f) Reproduction -----------------------------------------------------------------------------
{
  const s = slide("(f) Reproduction", "(f) Experiments and reproduction", "TabDiff reproduces on Adult");
  stat(s, 0.7, 1.75, 3.75, 3.2, "1.46%", "Trend error (ours)", "Paper: 1.49 ± 0.16%. Correlations between columns match.");
  stat(s, 4.8, 1.75, 3.75, 3.2, "0.76%", "Shape error (ours)", "Paper: 0.63 ± 0.05%. Each column's own distribution, 0.13 points worse.", INK);
  stat(s, 8.9, 1.75, 3.7, 3.2, "8,000", "training epochs", "Authors' code and settings on Adult (32,561 rows, 6 numerical + 9 categorical columns).", BLUE);
  txt(s, "Both errors stay below the strongest baseline in the paper (TabSyn: Shape 0.81%, Trend 1.93%). The code runs as published, so differences on road data come from the data, not from our setup.", 0.7, 5.35, 11.9, 0.9, { fontSize: 16, color: INK });
  s.addNotes("Reproduction was done by Naveen on the main branch. Only the final checkpoint numbers are reported. This validates the pipeline before the new dataset.");
}

// 10. (g) Pipeline and data -----------------------------------------------------------------------
{
  const s = slide("(g) Extensions", "(g) Extensions done in the project", "A new dataset: Beijing taxi trips as transactions");
  const st = [["42,705", "trips", "split by taxi: 29,378 train · 4,566 val · 8,761 test"], ["300", "road segments", "most used directed segments in a 4 km window"], ["98.6%", "points map-matched", "HMM matcher on 1,000 sampled T-Drive taxis"], ["17.9 h", "GPU training", "2,000 epochs on one RTX 2080 Ti (Ada HPC)"]];
  st.forEach(([b, l, d], i) => stat(s, 0.7 + i * 3.02, 1.75, 2.8, 3.0, b, l, d, i === 0 ? RUST : INK));
  txt(s, "Pipeline", 0.7, 5.1, 3, 0.4, { fontFace: "Georgia", fontSize: 18, bold: true });
  const p = ["Clean points", "Cut trips", "Map-match", "Pick window", "Encode rows", "Train TabDiff", "Sample + decode"];
  p.forEach((t, i) => {
    const x = 0.7 + i * 1.72;
    card(s, x, 5.6, 1.5, 0.7, { fill: i === 5 ? RUST : SOFT, line: i === 5 ? RUST : SOFT });
    txt(s, t, x, 5.6, 1.5, 0.7, { fontSize: 13, bold: true, align: "center", valign: "middle", color: i === 5 ? "FFFFFF" : INK });
    if (i < p.length - 1) arrow(s, x + 1.52, 5.95, x + 1.7, 5.95);
  });
  s.addNotes("Everything here was built for the project. Splitting by taxi means no driver appears in both train and test. Checkpoint (epoch 750) and sampler strength (0.1) were chosen on validation only.");
}

// 11. (g) Baselines and metrics -------------------------------------------------------------------
{
  const s = slide(null, "(g) Extensions done in the project", "Baselines and how we score them");
  const b = [["Independent", "each segment drawn from its training frequency (lower bound)"], ["Markov chain", "first-order walk over segments on the road graph; drivable by construction"], ["DiffTraj", "GPS-trajectory diffusion (NeurIPS 2023): fine-tuned from Chengdu, and from scratch"]];
  txt(s, "Baselines", 0.7, 1.7, 5, 0.45, { fontFace: "Georgia", fontSize: 19, bold: true });
  b.forEach(([h, d], i) => {
    card(s, 0.7, 2.25 + i * 1.35, 5.7, 1.15);
    txt(s, h, 0.95, 2.4 + i * 1.35, 5.2, 0.4, { fontSize: 16, bold: true, color: i === 2 ? RUST : INK });
    txt(s, d, 0.95, 2.8 + i * 1.35, 5.2, 0.55, { fontSize: 13.5, color: MUTED });
  });
  txt(s, "Metrics (test split, 3 seeds, 95% intervals)", 6.9, 1.7, 5.7, 0.45, { fontFace: "Georgia", fontSize: 19, bold: true });
  card(s, 6.9, 2.25, 5.7, 3.85, { fill: SOFT, line: SOFT });
  bullets(s, [
    "Validity: drivable trips, trips with gaps, segments per trip",
    "Busy roads: Spearman of segment-use counts, top-25 overlap",
    "Patterns: Jaccard of frequent multi-segment itemsets",
    "Popular paths: Kendall τ over 26 origin–destination queries",
    "Privacy: share of exact copies of training trips",
  ], 7.2, 2.5, 5.2, 3.5, 15);
  s.addNotes("Markov is a strong but trivially valid reference. DiffTraj is the natural trajectory-diffusion competitor; its output points are map-matched back to segments so all methods are scored on the same table.");
}

// 12. (h) Ablation --------------------------------------------------------------------------------
{
  const s = slide("(h) New results and algorithms", "(h) New results and algorithms", "The gain comes from the graph");
  s.addChart(pres.charts.BAR, [{ name: "Drivable trips (%)", labels: ["A. No re-masking", "B. Random re-masking", "C. Graph-aware"], values: [61.0, 62.6, 87.0] }], {
    x: 0.7, y: 1.7, w: 7.0, h: 4.6, barDir: "col", chartColors: [GREY, GREY, RUST], varyColors: true,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 14, dataLabelFontFace: "+mn-lt", dataLabelColor: INK, dataLabelFormatCode: "0.0",
    catAxisLabelFontSize: 13, catAxisLabelFontFace: "+mn-lt", catAxisLabelColor: MUTED, valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt", valAxisLabelColor: MUTED,
    valAxisMinVal: 0, valAxisMaxVal: 100, valGridLine: { color: "E6E4DD", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false,
    showTitle: true, title: "Drivable trips (%), test split, seeds 10–12", titleFontSize: 14, titleFontFace: "+mn-lt", titleColor: INK,
  });
  card(s, 8.1, 1.75, 4.5, 2.1);
  txt(s, "3×", 8.4, 1.95, 1.6, 0.8, { fontFace: "Georgia", fontSize: 40, color: INK });
  txt(s, "more columns re-masked by the random arm (0.49% vs 0.16% per step), yet only +1.6 points", 9.8, 2.05, 2.6, 1.7, { fontSize: 13.5, color: MUTED });
  card(s, 8.1, 4.1, 4.5, 2.1);
  txt(s, "+26", 8.4, 4.3, 1.6, 0.8, { fontFace: "Georgia", fontSize: 40, color: RUST });
  txt(s, "points of drivable trips from re-masking where the graph says the trip is broken", 9.8, 4.4, 2.6, 1.7, { fontSize: 13.5, color: MUTED });
  s.addNotes("The cleanest result of the project. Same checkpoint, same seeds, same strength. Random re-masking does almost nothing; targeted re-masking adds 26 points.");
}

// 13. (i) Main results table ----------------------------------------------------------------------
{
  const s = slide("(i) New experimental results", "(i) New experimental results", "Results on 8,761 held-out test trips");
  const H = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: INK }, fontSize: 13, align: "center" } });
  const rows = [
    ["Method", "Drivable", "Seg./trip", "Spearman", "Itemset J.", "Path τ", "Copies"].map(H),
  ];
  const data = [
    ["Real test (reference)", "100%", "4.26", "0.87", "0.60", "0.92", "99%", 0],
    ["Independent", "6%", "4.28", "0.91", "0.00", "0.50", "0%", 0],
    ["Markov", "100%", "4.31", "0.93", "0.51", "0.74", "93%", 0],
    ["TabDiff, default", "61%", "3.86", "0.81", "0.10", "0.85", "47%", 1],
    ["TabDiff, random 0.1", "63%", "3.85", "0.81", "0.11", "0.85", "49%", 1],
    ["TabDiff, graph-aware 0.1", "87%", "2.57", "0.52", "0.03", "0.50", "62%", 2],
    ["DiffTraj, fine-tuned", "84%", "3.86", "0.62", "0.34", "0.50", "63%", 0],
    ["DiffTraj, from scratch", "71%", "3.70", "0.58", "0.02", "0.69", "49%", 0],
  ];
  data.forEach((r) => {
    const hl = r[7];
    rows.push(r.slice(0, 7).map((c, j) => ({ text: c, options: { fontSize: 13.5, align: j ? "center" : "left", bold: hl === 2 && j > 0 ? false : hl === 2, color: hl === 2 ? RUST : INK, fill: { color: hl ? SOFT : "FFFFFF" } } })));
  });
  s.addTable(rows, { x: 0.7, y: 1.7, w: 11.9, colW: [3.4, 1.4, 1.4, 1.4, 1.5, 1.4, 1.4], rowH: 0.47, border: { type: "solid", color: LINE, pt: 0.75 }, fontFace: "Calibri" });
  txt(s, "Means over 3 seeds; all 95% intervals on drivable trips are within ±2 points. Full table with intervals in the report.", 0.7, 6.15, 11.9, 0.5, { fontSize: 13, color: MUTED });
  s.addNotes("Walk through the TabDiff rows first: default keeps busy roads (0.81) and path rankings (0.85) but only 61% drivable and few patterns. Graph-aware: 87% drivable, but shorter rows and weaker fidelity. Then the baselines.");
}

// 14. (i) Trade-off chart -------------------------------------------------------------------------
{
  const s = slide(null, "(i) New experimental results", "Validity and fidelity pull in opposite directions");
  const labels = ["TabDiff default", "TabDiff random", "TabDiff graph", "DiffTraj fine-tuned", "DiffTraj scratch", "Markov"];
  s.addChart(pres.charts.BAR, [
    { name: "Drivable trips", labels, values: [0.61, 0.626, 0.87, 0.838, 0.708, 1.0] },
    { name: "Busy roads (Spearman)", labels, values: [0.814, 0.809, 0.519, 0.622, 0.577, 0.925] },
    { name: "Patterns (itemset Jaccard)", labels, values: [0.102, 0.109, 0.026, 0.335, 0.024, 0.509] },
  ], {
    x: 0.7, y: 1.65, w: 8.3, h: 4.9, barDir: "col", barGrouping: "clustered", chartColors: [RUST, INK, "C9C5BA"],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 9, dataLabelFontFace: "+mn-lt", dataLabelColor: MUTED, dataLabelFormatCode: "0.00",
    catAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt", catAxisLabelColor: MUTED, valAxisLabelFontSize: 10, valAxisLabelFontFace: "+mn-lt", valAxisLabelColor: MUTED,
    valAxisMinVal: 0, valAxisMaxVal: 1.1, valGridLine: { color: "E6E4DD", size: 0.5 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "t", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: INK,
  });
  card(s, 9.3, 1.75, 3.3, 4.7, { fill: SOFT, line: SOFT });
  txt(s, "Reading", 9.55, 1.95, 2.8, 0.45, { fontFace: "Georgia", fontSize: 18, bold: true });
  bullets(s, [
    "TabDiff default: high busy-road agreement, low validity",
    "Graph-aware: validity up, fidelity down",
    "DiffTraj: best patterns among generators",
    "No generator wins on all three",
  ], 9.55, 2.5, 2.85, 3.8, 14);
  s.addNotes("This is the trade-off picture. Markov is the reference that does everything but copies 93% of training trips.");
}

// 15. (i) Key findings ----------------------------------------------------------------------------
{
  const s = slide(null, "(i) New experimental results", "Four things we learned");
  stat(s, 0.7, 1.75, 2.8, 3.6, "0.81", "busy roads kept", "TabDiff learns which roads are used: Spearman 0.81 against 0.87 for real test trips.", INK);
  stat(s, 3.72, 1.75, 2.8, 3.6, "61%", "drivable", "…but treats a trip as a bag of columns: 37% of its trips have gaps.");
  stat(s, 6.74, 1.75, 2.8, 3.6, "87%", "with the graph", "Graph-aware re-masking adds 26 points; trips shrink from 3.9 to 2.6 segments, as theory predicts.", RUST);
  stat(s, 9.76, 1.75, 2.84, 3.6, "47%", "exact copies", "Fewer than any method that keeps structure (Markov 93%); real test trips: 99% in a 4 km window.", BLUE);
  s.addNotes("Summarise the four messages. The privacy number needs the reference: in a small window almost every real trip also appears in training.");
}

// 16. Conclusion ----------------------------------------------------------------------------------
{
  const s = slide("Conclusion", "Conclusion", "Takeaways and limitations");
  card(s, 0.7, 1.75, 6.0, 4.6);
  txt(s, "Takeaways", 1.0, 2.0, 5.4, 0.45, { fontFace: "Georgia", fontSize: 19, bold: true });
  bullets(s, [
    "TabDiff reproduces on Adult and transfers to road transactions in a limited way",
    "It keeps marginals (busy roads) but not structure (drivable paths, patterns)",
    "A graph-aware sampler, with no retraining, raises validity by 26 points; a matched control shows the graph is what helps",
    "With sparse rows, re-deciding a segment usually turns it off: constrain choices during decoding, not after",
  ], 1.0, 2.55, 5.4, 3.7, 15);
  card(s, 7.1, 1.75, 5.5, 4.6, { fill: SOFT, line: SOFT });
  txt(s, "Limitations", 7.4, 2.0, 4.9, 0.45, { fontFace: "Georgia", fontSize: 19, bold: true });
  bullets(s, [
    "One city, one 4 km window, one training run",
    "T-Drive is sparsely sampled: map-matching fills gaps between points",
    "Popular-path queries cluster around few destinations; with minF = 423, Reddy et al.'s ω is 0 for all paths, so we also report ω without minF",
  ], 7.4, 2.55, 4.9, 3.7, 15);
  s.addNotes("Close with the one-line answer: TabDiff keeps busy roads but not drivability; the graph helps validity at a fidelity cost.");
}

// 17. Thanks --------------------------------------------------------------------------------------
{
  const s = pres.addSlide({ masterName: "BLANK", sectionTitle: "Conclusion" });
  txt(s, "Thank you", 0.7, 2.4, 11.9, 1.3, { fontFace: "Georgia", fontSize: 54, bold: true });
  txt(s, "Questions welcome", 0.7, 3.75, 11.9, 0.6, { fontSize: 22, color: MUTED });
  txt(s, "GRADIENT GLADIATORS  ·  ABHAY SHARMA & NAVEEN KUMAR", 0.7, 6.4, 11.9, 0.4, { fontSize: 13, bold: true, color: RUST, charSpacing: 2 });
  s.addNotes("Thanks. Code and records: github.com/rider9600/Project_tabdiff, branch Abhay.");
}

(async () => {
  const out = process.argv[2] || "Final_Presentation.pptx";
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out, n + 2, "slides");
})();
