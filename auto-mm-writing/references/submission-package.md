# Submission package — assembling and verifying the final zip

The last gate before the human submits. Rule 10 governs hygiene; this file is the operational protocol.

## Final tree (MCM example)

```
submission/
└── 2603956/                           # team control number as root
    ├── 2603956.pdf                    # the paper (named after team)
    ├── ai-report.pdf                  # AI report (since 2024)
    ├── code/
    │   ├── pipeline.py
    │   ├── src/
    │   └── README.md                  # how to run
    └── supporting/
        ├── figures-raw/               # PDFs of figures, in case judges want originals
        ├── data-derived/              # processed CSVs we generated
        └── references-data/           # policy docs, dataset snapshots
```

## Final tree (CUMCM example)

```
submission/
└── <报名号>/
    ├── <报名号>.pdf                    # 论文 PDF
    ├── 支撑材料/
    │   ├── 01_论文正文/
    │   │   └── main.pdf
    │   ├── 02_求解代码/
    │   │   └── pipeline.py + src/
    │   ├── 03_仿真/                    # if applicable
    │   ├── 04_数据与结果/
    │   ├── 05_论文图表/
    │   └── 06_参考文献与政策数据/
    └── 提交目录/
        └── (final mirror of what we submit)
```

This tree matches the experience README §1 recommendation.

## Build the tree

The skill builds the tree from `runs/<slug>/`:

```bash
SLUG=<run_slug>
ROOT=runs/$SLUG/stage3_writing/submission/<root_name>
mkdir -p $ROOT

# main paper
cp runs/$SLUG/stage3_writing/paper/main.pdf $ROOT/<root_name>.pdf

# AI report (MCM 2024+)
if [[ -f runs/$SLUG/stage3_writing/paper/ai-report.pdf ]]; then
    cp runs/$SLUG/stage3_writing/paper/ai-report.pdf $ROOT/ai-report.pdf
fi

# code
mkdir -p $ROOT/code
cp runs/$SLUG/stage2_solving/pipeline.py $ROOT/code/
cp -r runs/$SLUG/stage2_solving/src $ROOT/code/
# strip __pycache__
find $ROOT/code -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null

# supporting material
mkdir -p $ROOT/supporting/figures-raw $ROOT/supporting/data-derived
cp runs/$SLUG/stage2_solving/figures/*.pdf $ROOT/supporting/figures-raw/
```

For CUMCM: build the `支撑材料/` subfolders per the recommended layout.

## Final zip command

The macOS metadata problem: `zip` by default includes `.DS_Store` and AppleDouble `._*` files, which contest organizers (especially Chinese ones) find unprofessional. Use:

```bash
cd runs/$SLUG/stage3_writing/submission
zip -r -X submit.zip <root_name> \
    -x "*/._*" "*/.DS_Store" "*/~$*" \
       "*/__pycache__/*" "*/.git/*" "*/.gitignore" \
       "*/*.pyc" "*/*.pyo" "*/*.aux" "*/*.log" "*/*.out" \
       "*/main.synctex.gz"
```

The `-X` flag strips extra file attributes (resource forks, finder info). `-x` excludes patterns.

## Post-zip verification

```bash
# List contents and inspect manually
unzip -l submit.zip

# Verify no forbidden files leaked in
unzip -l submit.zip | grep -E '\._|\.DS_Store|__pycache__|~\$|\.aux$|\.log$|\.git/' && {
    echo "FORBIDDEN FILES IN ZIP — re-zip"
    exit 1
}

# Verify expected files are present
for required in <root_name>/<root_name>.pdf <root_name>/code/pipeline.py; do
    unzip -l submit.zip | grep -q "$required" || { echo "MISSING: $required"; exit 1; }
done

# Decompress to /tmp and rebuild PDF text sanity
TMPDIR=$(mktemp -d)
unzip -q submit.zip -d $TMPDIR
ls -lR $TMPDIR
python3 -c "
from pdfminer.high_level import extract_text
t = extract_text('$TMPDIR/<root_name>/<root_name>.pdf')
print(f'chars={len(t)} first300={t[:300]!r}')
"
rm -rf $TMPDIR
```

If verification fails → fix and re-zip.

## Size budget

Contest portals often impose a max upload size (commonly 100MB). If `submit.zip` exceeds:

1. Drop intermediate experiment artifacts (logs, .npy of internals) from `supporting/`.
2. Convert PNG figures to PDF vectors where possible.
3. Compress JPEGs more aggressively.
4. Move very large datasets to a separate "data" submission if the portal allows.

If still over budget after these steps, escalate to user.

## What does NOT go in the zip

- The `runs/` directory of the auto-mm working tree (it has private logs, heartbeats, draft state).
- `.git/`, `.github/`, IDE config (`.vscode/`, `.idea/`).
- Build intermediates (`.aux`, `.log`, `.toc`, `.out`, `.synctex.gz`, `_minted-*`).
- macOS metadata (`._*`, `.DS_Store`).
- Editor backups (`~$*`, `*.swp`).
- The original problem PDF from the contest organizer (they have it).

## What the user does next

After `submit.zip` lands:

1. The orchestrator prints the file path and size + a one-line summary.
2. The user inspects: `unzip -l submit.zip`, opens `<root_name>.pdf` in a viewer.
3. The user submits through the contest portal.
4. The user `touch STOP` on the run directory to tell the supervisor to stop.

The orchestrator does not auto-submit. The portal interaction is always a human action.

## Re-submission

If the user wants to re-submit (e.g., post-build catches an error pre-deadline):

1. Re-invoke `auto-mm-writing` with `--revise <section>` or `--rebuild`.
2. The skill rebuilds, re-scans, re-zips.
3. The user re-uploads.

Pre-lockdown: any change is allowed. Lockdown (last 6h): only build/anonymity fixes; no new modeling.
