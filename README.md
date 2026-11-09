# SolidWorks Version Converter

**Convert SolidWorks future-version CAD files (e.g. saved in SolidWorks 2026) into a format that older SolidWorks versions (e.g. SolidWorks 2024) can open natively.**

---

## 🌐 Try it in your browser (no install)

A zero-install web version lives in [`web/`](web/) and runs the **same
conversion entirely inside your browser** using
[Pyodide](https://pyodide.org) (Python in WebAssembly).

> 🔒 **Your files never leave your computer** — there is no server and nothing
> is uploaded.

**Live demo:** <https://alialasif.github.io/Solidworks_version_converter/>

To host it yourself, the included workflow
[`.github/workflows/pages.yml`](.github/workflows/pages.yml) deploys the
`web/` folder to **GitHub Pages** automatically:

1. Push to `main`.
2. Go to **Settings → Pages**, set **Source: GitHub Actions**.
3. The site is published at `https://<user>.github.io/<repo>/`.

---

## 🔍 What it does

SolidWorks files saved in a **newer** release cannot be opened by **older** releases. This tool bridges that gap.

It converts SolidWorks `.sldprt` part files into **Parasolid (`.x_t`)** files — the neutral format that SolidWorks 2024 and older open natively — **without needing SolidWorks installed at all**.

```
SolidWorks 2026 file (.sldprt)  ──[ this tool ]──▶  SolidWorks 2024-openable format (.x_t)
```

---

## ✅ Why this is useful

- You have a model made in **SolidWorks 2026**.
- You only have **SolidWorks 2024**.
- SolidWorks 2024 **refuses to open** a 2026 file.
- → Convert to `.x_t` → open in SolidWorks 2024. ✅

---

## 📦 Installation

Requires **Python 3.10+**.

```bash
pip install -e .
# or
pip install sw-version-converter
```

or simply:

```bash
pip install sldprt2xt olefile
```

---

## 🚀 Usage

Convert a whole folder of parts:

```bash
sw-version-converter ./CAD ./converted_2024
```

or with the module:

```bash
python -m sw_version_converter ./CAD ./converted_2024
```

or the convenience script:

```bash
python scripts/batch_convert.py ./CAD ./converted_2024
```

### Options

| Flag | Default | Description |
|---|---|---|
| `input` | `./CAD` | Folder containing `.sldprt` files |
| `-o / --output` | `<input>/_converted` | Output folder for `.x_t` files |
| `--source-version` | `2026` | Source SolidWorks version label |
| `--target-version` | `2024` | Target SolidWorks version label |

---

## 🧪 How it works

Under the hood it uses the free, offline [`sldprt2xt`](https://pypi.org/project/sldprt2xt/) package, which:

1. Opens the SolidWorks OLE2 container (both known format generations).
2. Extracts the embedded Parasolid transmit.
3. Writes a clean, valid Parasolid (`.x_t`) file.

The result is geometry-only — see the **Important caveats** below.

---

## ⚠️ Important caveats

### 1. Feature tree is NOT preserved

This tool converts **geometry only**. The parametric feature tree (sketches, Boss-Extrude, Cut-Extrude, fillets, etc.) is not carried over.

**Why?** The feature tree lives in version-specific internal data readable only by the SolidWorks version that created it.

### 2. To preserve the feature tree, use SolidWorks 2026+

SolidWorks 2024 introduced **"Save As Previous Version"** (via the API `AdvancedSaveAsOptions.SaveAsPreviousVersion`), which saves a document to a previous release **as a fully functional document** (feature tree intact).

- Run inside **SolidWorks 2026+**.
- Target: up to **2 releases back** (2026 → 2024 works).
- Requires an **active subscription license**.
- Files with features that didn't exist in 2024 trigger a **"Previous Release Check"** — those features must be removed before saving down.

A SolidWorks macro (`BatchDownsaveTo2024.swb`) is included for this.

### 3. Assemblies

Assemblies (`.sldasm`) are not converted by this tool. The parts inside them are.

---

## 📋 Example

```
CAD/
├── Part2.SLDPRT
├── Boss-Extrude12.SLDPRT
└── Assem2.SLDASM

$ sw-version-converter ./CAD ./converted_2024

============================================================
Source  : ./CAD
Output  : ./converted_2024
Source version : 2026
Target version : 2024
Parts   : 3
============================================================
OK      Part2.SLDPRT -> Part2.x_t
...
Converted: 3   Failed: 0   Skipped: 0
```

---

## 📄 License

MIT © 2026 Ali Al-Asif
