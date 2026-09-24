# Tutorial website

This folder is the tutorial site, served by GitHub Pages at
<https://hep-ke.github.io/multiagent-client-demo/>.

**All content lives in [`slides.md`](slides.md).** Edit that one file to change,
add, remove, or reorder pages. You never need to touch `index.html`.

| file | what it is |
|---|---|
| `slides.md` | every page of the tutorial, in order |
| `assets/` | figures (PNG, JPG, SVG) used by the pages |
| `index.html` | the page shell: layout, style, navigation. Leave it alone. |
| `vendor/` | Markdown and syntax-highlighting libraries, kept local so the site works offline |
| `.nojekyll` | tells GitHub Pages to serve files as-is. Do not delete. |

## Preview locally

The page loads `slides.md` over HTTP, so double-clicking `index.html` will not
work. From the repo root:

```bash
python -m http.server 8000 -d docs
# open http://localhost:8000  and refresh after each edit
```

## Publish

Commit and push. The first time only: repo **Settings → Pages → Deploy from a
branch → `main` / `/docs`**. Updates go live a minute or so after each push.

---

## Anatomy of a page

Each page starts with a header block between two `+++` lines. Everything after
it, up to the next `+++`, is ordinary Markdown.

```markdown
+++
id: server-tools
title: Tools are plain Python functions
group: Server
kicker: Server · spectra-mcp-server
+++

Normal **Markdown** here: paragraphs, lists, links, `code`, tables.
```

### Header fields

| field | required | what it does |
|---|---|---|
| `id` | yes | the page's link, e.g. `…/#server-tools`. Lowercase, no spaces, unique. |
| `title` | yes | the big heading. `*word*` makes it italic brass. |
| `group` | yes | sidebar section. Consecutive pages with the same group sit together. |
| `nav` | no | shorter title for the sidebar and the Next/Previous cards |
| `kicker` | no | small uppercase label above the title |
| `sub` | no | a grey intro sentence under the title |
| `layout` | no | `cover` (title page) or `divider` (centred section break) |
| `eyebrow`, `lede`, `byline` | no | only for `layout: cover` |
| `hidden` | no | `hidden: yes` drops the page from the site without deleting it |

### Add, remove, reorder

- **Add:** copy an existing page (from its `+++` block to just before the next `+++`), paste it where you want it, and give it a new `id`.
- **Remove:** delete the block, or set `hidden: yes`.
- **Reorder:** cut and paste blocks. Page numbers, the sidebar, and Next/Previous update themselves.
- **Link to another page:** `[see the graph](#backup-graph)`.

## Markdown features

### Headings inside a page

| write | looks like |
|---|---|
| `### Heading` | bold sub-heading |
| `#### Heading` | small brass uppercase label, used for side notes |
| `###### Label` | tiny grey uppercase label, used at the top of cards |

A paragraph that is only italics (`*like this*`) renders as a faint aside.

### Code blocks

Use normal fenced code with a language. Add an optional file-name header, with
an optional link:

````markdown
```python title="agents/graph.py" link="https://github.com/HEP-KE/multiagent-client-demo/blob/main/agents/graph.py"
def route_from_worker(state): ...
```
````

For terminal commands use `console` and start each command with `$ `. The `$`
is shown but not copied by the Copy button, and neither are `#` comment lines.

````markdown
```console
$ pip install -r requirements.txt
# comments are shown but not copied
```
````

Languages: `python`, `bash`, `console`, `json`, `yaml`, `toml`, `markdown`,
`text` (no colours), and the other common ones.

### Figures

```markdown
![Alt text for screen readers](assets/my_figure.png "Caption shown under the figure")
```

Put the file in `assets/`. An image on its own line becomes a framed figure.
Photos and plots can be clicked to enlarge. Very wide images scroll sideways on
phones. SVG files are drawn inline so they pick up the site's fonts and colours.

## Layout blocks

Blocks open with `::: name` on its own line and close with a line of just
`:::`. They can be nested.

### Two columns: `::: split`

A line of just `|||` starts the second column.

```markdown
::: split
```python
code on the left
```
|||
#### Notes on the right
- point one
:::
```

Column widths: `::: split` (wider left), `::: split even` (about equal),
`::: split right` (wider right). Columns stack on narrow screens.

### Cards: `::: grid` + `::: card`

```markdown
::: grid
::: card
###### Server
### [HEP-KE/spectra-mcp-server](https://github.com/HEP-KE/spectra-mcp-server)
Short description.
:::
::: card
Second card.
:::
:::
```

`::: grid` fits two cards per row. `::: grid three` fits three.

### Numbered steps: `::: steps`

Every `###` heading inside starts a new numbered step.

```markdown
::: steps
### Clone the repos
Text and code for step 1.

### Create the environment
Text and code for step 2.
:::
```

### Callouts: `::: note` and `::: warn`

```markdown
::: warn
**Budget warning.** Red-edged box with a warning icon.
:::

::: note
Brass-edged box with an info icon.
:::
```

### Buttons: `::: actions`

Every link inside becomes a button. The first one is the highlighted one.

```markdown
::: actions
[Begin →](#why) [Jump to setup](#setup-env)
:::
```

### Query box: `::: query`

A light box for prompts or sample queries. Used for the notebook 02 task.

```markdown
::: query
###### Sample query for the agent
```text
Compute the linear matter power spectrum ...
```
:::
```

## Raw HTML

Any HTML works inside `slides.md` for one-off needs, for example
`<kbd>←</kbd>` for a key. Prefer the Markdown features above so pages stay
consistent.
