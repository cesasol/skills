# Data: JSON, YAML, TOML, XML, HTML, Tables, and Documents

One filter language, jq, covers most of this work once the input has been transcoded to JSON. The complication is that
two unrelated programs are both named `yq`.

## jq

```bash
jq -r '.items[].name' data.json              # raw strings, no quotes
jq -c '.[] | {id, name}' data.json           # one compact object per line
jq -e '.items | length > 0' data.json        # exit 1 when the result is false or null
jq --arg v "$VERSION" '.version = $v' in.json > out.json
jq -r '.a.b? // "missing"' data.json         # tolerate a missing path
jq -s 'add' part-*.json                      # slurp many documents into one array
jq --stream -n 'inputs | select(.[0][0] == "items")' huge.json
```

Habits that matter: `-r` whenever the value feeds another command, `-e` whenever emptiness should fail the pipeline,
`--arg` instead of string interpolation, and `?` or `//` instead of assuming a key exists. A filter that matches
nothing prints nothing and still exits zero, which is the single most common silent failure in a shell pipeline.

## The Two Programs Named `yq`

Identify the installed one before writing a filter:

```bash
yq --version
# yq 4.1.2 / jq-1.8.2                                  -> Python wrapper (kislyuk), jq filters
# yq (https://github.com/mikefarah/yq/) version v4.x   -> Go tool (mikefarah), its own language
```

| Task              | Python wrapper (jq syntax)                | Go tool (own syntax)                        |
| ----------------- | ----------------------------------------- | ------------------------------------------- |
| Read a value      | `yq -r '.stages[0]' ci.yml`               | `yq '.stages[0]' ci.yml`                    |
| YAML in, YAML out | `yq -y '.jobs' ci.yml`                    | `yq '.jobs' ci.yml`                         |
| YAML in, JSON out | `yq '.' ci.yml`                           | `yq -o json '.' ci.yml`                     |
| Edit in place     | `yq -yi '.version = "2"' ci.yml`          | `yq -i '.version = "2"' ci.yml`             |
| TOML input        | `tomlq -r '.project.name' pyproject.toml` | `yq -p toml '.project.name' pyproject.toml` |
| XML input         | `xq -r '.rss.channel.title' feed.xml`     | `yq -p xml '.rss.channel.title' feed.xml`   |

The Python wrapper ships the sibling commands `xq` and `tomlq`, both of which take jq filters and accept `-t` for TOML
output or `-y` for YAML output. The Go tool handles every format through `-p` and `-o` on one binary. Neither is
better; the installed one wins. Writing a filter for the other program produces a confusing parse error rather than a
missing-command error, which is why the version check comes first.

## Multi-Document YAML and Round-Trips

```bash
yq -y 'select(.kind == "Deployment")' manifests.yml   # per-document filtering, Python wrapper
yq -Y '.metadata.labels' manifests.yml                # preserve tags and styles on round-trip
```

Comments never survive a transcode, and anchors and aliases are expanded unless the round-trip mode is used. When the
goal is to edit a YAML file that humans maintain — a CI configuration, a Compose file — prefer a targeted text edit
over a full rewrite, because a rewrite silently deletes every comment in the file.

## htmlq: HTML by CSS Selector

```bash
http --ignore-stdin --body GET https://example.com | htmlq -t 'h1'          # text of the first heading
http --ignore-stdin --body GET https://example.com | htmlq -a href 'a'      # every link target
htmlq -f page.html -r 'script,style' -t 'main'                              # drop noise, then take text
htmlq -f page.html -p 'table.results'                                       # pretty-printed fragment
```

`-t` extracts text, `-a` extracts one attribute, `-r` removes matching nodes before output, `-w` drops
whitespace-only text nodes, and `-f` reads a file instead of standard input. htmlq parses the HTML it is given; it
runs no JavaScript, so a page rendered in the browser needs firecrawl instead. See
[web-research.md](web-research.md).

## Miller: CSV, TSV, and JSON Tables

```bash
mlr --icsv --ojson cat data.csv                                  # convert
mlr --icsv --opprint head -n 5 data.csv                          # look at the shape
mlr --icsv --ojson filter '$status == "failed"' runs.csv          # select rows
mlr --icsv --ojson cut -f id,duration runs.csv                   # select columns
mlr --icsv --opprint stats1 -a mean,max -f duration -g suite runs.csv
```

Miller understands the quoting rules that `awk -F,` does not: embedded commas, quoted newlines, and headers. Reach for
`awk` only for whitespace-delimited output that has no quoting.

## batdoc: Office Documents, PDFs, and Scans

```bash
batdoc -m report.docx                     # docx as markdown: headings, tables, links
batdoc -m financials.xlsx                 # one markdown table per sheet
batdoc -m slides.pptx                     # per-slide headings, speaker notes appended
batdoc -m paper.pdf                       # text layer, one `## Page N` heading per page
batdoc --images report.docx > report.md   # embed docx/pptx/xlsx images as base64 data URIs
batdoc -p legacy.doc > out.txt            # plain text only
batdoc photo.png                          # image files are always OCR'd
batdoc scanned.pdf                        # textless PDF pages are OCR'd automatically
batdoc --ocr report.docx                  # also OCR images embedded in docx/pptx
cat mystery.bin | batdoc -m -             # stdin works; format detected by magic bytes
```

Format is detected by file signature, not extension, so a misleading filename does not matter. When standard output is
a terminal, batdoc syntax-highlights and pages like `bat`; piped, it emits plain text, and `-m` upgrades that to
markdown — the right default for an agent, since headings and tables survive. OCR needs no flag for PDFs or image
files; `--ocr` covers only images embedded in docx and pptx. OCR models (about 12 MB) download on first use, a network
call that also writes to a cache directory; pre-seed `BATDOC_MODELS_DIR` for offline or package-managed installs.
Fallbacks on hosts without batdoc: `pdftotext` for PDFs and `catdoc` for legacy `.doc`.

## Edge Cases and Mistakes

- **jq prints nothing and succeeds.** The path did not match. Confirm the shape with `jq -r 'keys'` or `jq 'paths'`,
  and add `-e` when empty output should fail.
- **`yq` rejects a valid filter.** Wrong program; run `yq --version` and use the matching column above.
- **Comments vanished from a YAML file.** A transcode rewrote it. Restore from git and edit the text directly.
- **Numbers change form.** JSON has one number type; `1.0` may come back as `1`, and large integers can lose
  precision. Keep identifiers as strings.
- **YAML booleans surprise you.** Unquoted `on`, `no`, and `y` are booleans under YAML 1.1. The Python wrapper's
  `--yaml-output-grammar-version 1.2` emits them unquoted as strings; quoting them in the source is safer.
- **A large document exhausts memory.** Use `jq --stream`, or filter server-side with `gh api --jq` before the data
  reaches the pipeline.
- **HTML extraction returns an empty string.** The content is rendered by JavaScript, or the selector matched a node
  whose text lives in a child. Try a broader selector, then firecrawl.
- **Shell quoting mangles the filter.** Single-quote every jq filter, and pass shell values with `--arg`, never by
  interpolating into the filter text.
