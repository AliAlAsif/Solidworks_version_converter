/* SolidWorks Version Converter — browser edition
 * Runs the same `sldprt2xt` conversion logic as the CLI, entirely in the
 * browser via Pyodide (CPython compiled to WebAssembly).
 * Nothing is uploaded anywhere.
 *
 * The output is Parasolid (.x_t), a neutral kernel format. It opens in ANY
 * SolidWorks version (roughly 2001 through today), so it works as a
 * "convert to any older version" tool.
 */

const PYODIDE_VERSION = "314.0.7";
const PYODIDE_INDEX = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

let pyodide = null;
let ready = false;

const els = {
  dropzone: document.getElementById("dropzone"),
  fileInput: document.getElementById("fileInput"),
  fileList: document.getElementById("fileList"),
  fileItems: document.getElementById("fileItems"),
  convertBtn: document.getElementById("convertBtn"),
  clearBtn: document.getElementById("clearBtn"),
  status: document.getElementById("status"),
  statusText: document.getElementById("statusText"),
  dot: document.querySelector("#status .dot"),
  results: document.getElementById("results"),
  resultItems: document.getElementById("resultItems"),
};

/** @type {{file: File, li: HTMLLIElement, statusEl: HTMLElement, errorEl: HTMLElement, status: string}[]} */
let selected = [];

/* ------------------------------------------------------------------ */
/* Status helpers                                                      */
/* ------------------------------------------------------------------ */
function setStatus(text, mode = "loading") {
  els.statusText.textContent = text;
  els.dot.className = "dot " + mode;
}

/** Turn low-level conversion errors into clear, actionable messages. */
function friendlyError(msg) {
  const m = (msg || "").toLowerCase();
  if (m.includes("pas de géométrie") || m.includes("no parasolid geometry")) {
    return "No solid geometry found. Assemblies (.sldasm) and drawing files are not supported — convert the individual .sldprt parts instead.";
  }
  if (m.includes("schema")) {
    return "This file was saved by a SolidWorks version newer than the converter supports. Update the 'sldprt2xt' package, or export a Parasolid/STEP from a newer SolidWorks.";
  }
  if (m.includes("not a valid") || m.includes("invalid") || m.includes("ole")) {
    return "This file could not be read — it may be damaged or not a supported SolidWorks file.";
  }
  return msg || "Unknown error";
}

function isAssembly(name) {
  return /\.sldasm$/i.test(name);
}

/* ------------------------------------------------------------------ */
/* Pyodide bootstrap                                                   */
/* ------------------------------------------------------------------ */
async function boot() {
  try {
    setStatus("Loading Python runtime (first time only, ~15–20 MB)…", "loading");
    pyodide = await loadPyodide({ indexURL: PYODIDE_INDEX });

    setStatus("Installing the SolidWorks file reader…", "loading");
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("sldprt2xt");

    ready = true;
    setStatus("Ready — drop your SolidWorks part files.", "ready");
  } catch (err) {
    console.error(err);
    setStatus("Failed to load runtime: " + (err && err.message ? err.message : err), "error");
  }
}

/* ------------------------------------------------------------------ */
/* File selection                                                      */
/* ------------------------------------------------------------------ */
function addFiles(fileList) {
  const accepted = Array.from(fileList).filter((f) => {
    const l = f.name.toLowerCase();
    return l.endsWith(".sldprt") || l.endsWith(".sldasm");
  });

  if (accepted.length === 0) {
    setStatus("Please choose SolidWorks .SLDPRT part files (assemblies are not supported).", "error");
    return;
  }

  for (const file of accepted) {
    if (selected.some((s) => s.file.name === file.name && s.file.size === file.size)) {
      continue;
    }

    const li = document.createElement("li");
    li.className = "file-item";

    const main = document.createElement("div");
    main.className = "file-main";

    const name = document.createElement("span");
    name.className = "file-name";
    name.textContent = file.name;

    const errorEl = document.createElement("span");
    errorEl.className = "file-error hidden";

    main.appendChild(name);
    main.appendChild(errorEl);

    const statusEl = document.createElement("span");
    statusEl.className = "file-status";

    if (isAssembly(file.name)) {
      statusEl.textContent = "Assembly — unsupported";
      statusEl.classList.add("err");
      errorEl.textContent =
        "Assemblies are not supported. Convert the part files (.sldprt) inside the assembly instead.";
      errorEl.classList.remove("hidden");
    } else {
      statusEl.textContent = "Queued";
    }

    li.appendChild(main);
    li.appendChild(statusEl);
    els.fileItems.appendChild(li);

    selected.push({
      file,
      li,
      statusEl,
      errorEl,
      status: isAssembly(file.name) ? "failed" : "queued",
    });
  }

  if (selected.length > 0) {
    els.fileList.classList.remove("hidden");
  }
  updateConvertButton();
}

function clearAll() {
  selected = [];
  els.fileItems.innerHTML = "";
  els.resultItems.innerHTML = "";
  els.fileList.classList.add("hidden");
  els.results.classList.add("hidden");
  updateConvertButton();
}

function updateConvertButton() {
  const convertible = selected.some((s) => s.status !== "failed");
  els.convertBtn.disabled = !ready || !convertible;
}

/* ------------------------------------------------------------------ */
/* Conversion                                                          */
/* ------------------------------------------------------------------ */
let counter = 0;

async function convertOne(entry) {
  const { file } = entry;
  const uid = `f${Date.now()}_${counter++}`;
  const inDir = `/tmp/${uid}`;
  const outDir = `${inDir}/out`;
  const safeName = file.name.replace(/[^\w.\-\[\]() ]+/g, "_");
  const inPath = `${inDir}/${safeName}`;

  entry.statusEl.textContent = "Converting…";
  entry.statusEl.className = "file-status";
  entry.errorEl.classList.add("hidden");

  const data = new Uint8Array(await file.arrayBuffer());

  pyodide.FS.mkdirTree(inDir);
  pyodide.FS.mkdirTree(outDir);
  pyodide.FS.writeFile(inPath, data);

  await pyodide.runPythonAsync(`
import os
from sldprt2xt import to_x_t

in_path = ${JSON.stringify(inPath)}
out_dir = ${JSON.stringify(outDir)}

to_x_t(in_path, out_dir)
`);

  const produced = pyodide.FS.readdir(outDir).filter((n) => n.endsWith(".x_t"));
  if (produced.length === 0) {
    throw new Error("Converter produced no .x_t output.");
  }
  const outName = produced[0];
  const outPath = `${outDir}/${outName}`;
  const outBytes = pyodide.FS.readFile(outPath);

  const blob = new Blob([outBytes], { type: "application/octet-stream" });
  const url = URL.createObjectURL(blob);

  const li = document.createElement("li");
  li.className = "result-item";

  const label = document.createElement("span");
  label.className = "file-name";
  label.textContent = outName;

  const link = document.createElement("a");
  link.className = "download-btn";
  link.href = url;
  link.download = outName;
  link.textContent = "Download";

  li.appendChild(label);
  li.appendChild(link);
  els.resultItems.appendChild(li);
  els.results.classList.remove("hidden");

  try {
    pyodide.FS.unlink(outPath);
    pyodide.FS.unlink(inPath);
    pyodide.FS.rmdir(outDir);
    pyodide.FS.rmdir(inDir);
  } catch (_) {
    /* ignore cleanup errors */
  }

  entry.statusEl.textContent = "Done";
  entry.statusEl.className = "file-status ok";
}

async function convertAll() {
  if (!ready) return;

  els.convertBtn.disabled = true;
  els.clearBtn.disabled = true;

  let ok = 0;
  let failed = 0;

  for (const entry of selected) {
    if (entry.status === "failed") {
      failed++;
      continue;
    }
    if (entry.status === "done") {
      ok++;
      continue;
    }
    try {
      setStatus(`Converting ${entry.file.name}…`, "busy");
      await convertOne(entry);
      entry.status = "done";
      ok++;
    } catch (err) {
      console.error(err);
      const raw = err && err.message ? err.message : String(err);
      entry.statusEl.textContent = "Failed";
      entry.statusEl.className = "file-status err";
      entry.status = "failed";
      entry.errorEl.textContent = friendlyError(raw);
      entry.errorEl.classList.remove("hidden");
      failed++;
    }
  }

  els.clearBtn.disabled = false;
  updateConvertButton();
  setStatus(
    `Finished — ${ok} converted${failed ? `, ${failed} failed` : ""}.`,
    failed ? "error" : "ready"
  );
}

/* ------------------------------------------------------------------ */
/* Event wiring                                                        */
/* ------------------------------------------------------------------ */
els.dropzone.addEventListener("click", () => els.fileInput.click());
els.dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    els.fileInput.click();
  }
});

els.fileInput.addEventListener("change", (e) => {
  addFiles(e.target.files);
  e.target.value = "";
});

["dragenter", "dragover"].forEach((ev) =>
  els.dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    e.stopPropagation();
    els.dropzone.classList.add("dragover");
  })
);

["dragleave", "drop"].forEach((ev) =>
  els.dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    e.stopPropagation();
    els.dropzone.classList.remove("dragover");
  })
);

els.dropzone.addEventListener("drop", (e) => {
  if (e.dataTransfer && e.dataTransfer.files) {
    addFiles(e.dataTransfer.files);
  }
});

els.convertBtn.addEventListener("click", convertAll);
els.clearBtn.addEventListener("click", clearAll);

/* Start loading Pyodide. */
boot();
