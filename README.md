# Smart P&ID — development prototype
Confidential draft engineering data. Do not publish without company approval.

## Deploy
Extract the ZIP, upload the contents (including dot folders) to the root of a private GitHub repository. In Streamlit Community Cloud choose New app, authorize repository access, select branch main and app.py, and select Python 3.13. Use cloud hosting only with company approval; private GitHub does not alone guarantee private app access. Alternatively run on Windows with Docker Desktop: `docker build -t smart-pid .` then `docker run --rm -p 127.0.0.1:8501:8501 smart-pid`. Open http://localhost:8501. Local Python: pip install -r requirements.txt; streamlit run app.py.

## Features and limits
Register JSON ingestion, draft graph traversal, SVG connectivity drawing, DXF connectivity sketch, source manifest, Aspen maps, glossary, text and synthetic crop classifiers. The SVG uses a small shared original glyph library; the full glossary is textual, not a complete certified graphical library. No automatic arbitrary image-to-P&ID conversion, YOLO detector, approved routing, valve sizing, safety logic or real-world accuracy claims. Valve/instrument associations remain in registers; sequencing and nozzle design unresolved. Sources are draft workbook rows and Aspen screenshot interpretations. Original reference documents are not all bundled/parsed; manifest references them. Future plant inputs must follow data/plant.json schema. No cloud deployment has been performed.

## Training
`python train_visual.py` retrains the synthetic single-symbol random forest. The same glyph templates are used for train/test with different random augmentations; independent real drawings required. `python build.py PATH_TO_SOURCE_WORKBOOKS` rebuilds the source registers and lexical classifier; use the two named source workbooks. `python -m unittest discover -s tests` runs smoke tests. Models are trusted local artifacts; never load untrusted joblib files.
