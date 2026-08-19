# Testing the hosted MCP servers from your AI app

Three MCP servers run on a server — you can talk to them from
several AI apps **without installing anything**. 

| server | URL | what it does |
|---|---|---|
| **cosmic** | `https://cosmic.77-42-88-84.sslip.io/mcp` | ~20 cosmological emulators: P(k), modified gravity, CMB, lensing, halo mass function, baryonic effects, Lyman-alpha ([repo](https://github.com/HEP-KE/cosmic_emulator_server)) |
| spectra | `https://spectra.77-42-88-84.sslip.io/mcp` | CLASS power spectra vs eBOSS data ([repo](https://github.com/HEP-KE/spectra-mcp-server)) |
| gaia | `https://gaia.77-42-88-84.sslip.io/mcp` | Gaia DR2 colour-magnitude diagrams ([repo](https://github.com/HEP-KE/gaia-mcp-server)) |

Every figure or data file a server produces comes back as a link — browse
everything at <https://files.77-42-88-84.sslip.io/>.

The instructions below use **cosmic** as the example; spectra and gaia work
identically (same steps, their URL instead).

>
> **If the URL won't load at all**: some institutional networks block `*.sslip.io` domains at the DNS level. Try from a
> home network or phone hotspot. 

---

## Claude desktop app

1. Settings → **Connectors** → **Add custom connector**
2. Name: `cosmic`, URL: `https://cosmic.77-42-88-84.sslip.io/mcp` → Add
3. Start a **new** chat and check the connector is enabled in the tools
   menu (the sliders icon).


## ChatGPT app


1. Settings → **Plugins** (left sidebar, under *Integrations*)
2. Click on **⛭** (or Manage) icon (right side, beside Installed plugins, under the search bar)
3. Top-right **Add ▾** → **Add MCP server**
4. In "Connect to a custom MCP":
   - Name: `cosmic`
   - Type: **Streamable HTTP**
   - URL: `https://cosmic.77-42-88-84.sslip.io/mcp`
   - Leave bearer token and headers empty (the demo server is open)
5. The server appears under the **MCPs** tab → *Servers* — flip its toggle
   on, then use it from a new chat.

(As of Aug 2026; the desktop app moves this around between versions — look
for wherever plugins/MCPs are managed.)

## Claude Code (terminal)

```bash
claude mcp add --transport http cosmic https://cosmic.77-42-88-84.sslip.io/mcp
claude          # then type /mcp — the cosmic server and its tools should list
```

Claude Code also surfaces the server's **prompts** (the four built-in
skills) — try typing `/` and looking for `cosmo-tour`.

## Codex CLI

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.cosmic]
command = "npx"
args = ["-y", "mcp-remote", "https://cosmic.77-42-88-84.sslip.io/mcp"]
```

## Cursor

Add to `~/.cursor/mcp.json` (or a project's `.cursor/mcp.json`):

```json
{"mcpServers": {"cosmic": {"url": "https://cosmic.77-42-88-84.sslip.io/mcp"}}}
```

## Python / notebooks (any MCP SDK client)

```python
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("https://cosmic.77-42-88-84.sslip.io/mcp") as (r, w, _):
    async with ClientSession(r, w) as s:
        await s.initialize()
        tools = await s.list_tools()
        print([t.name for t in tools.tools])
```

(Our LangGraph tutorial client uses the same URL in its server config —
`{"cosmic": {"transport": "streamable_http", "url": "...cosmic.../mcp"}}`.)

---

## Example queries to try 

**Query-1: exploration**

> List the emulators and skills available from the cosmic server. Which
> emulators are covered, and what are the inputs and outputs?

**Query-2: Matter power spectra**

> Run all available nonlinear P(k) backends at Om=0.31, sigma8=0.82, z=0, plot the comparison, and tell me the k-range where they agree within 2%. Overlay the plot with linear matter power spectra. 

**Query-3: Combining tools**

> At what scales could baryonic feedback have effects on modified-gravity
> signals? At z=0, compute the f(R) boost at |fR0|=1e-5 and the baryonic
> suppression for both SP(k) and IllustrisTNG feedback, all on the same
> k-grid, and plot the three curves together. Identify the k-range where
> the gravity enhancement dominates, where feedback suppression dominates,
> and where they roughly cancel. Then build the full combined spectrum —
> compute_mg_pk for the f(R) universe, then baryonify_pk on that file —
> and compare it against plain LCDM. 

**Query-4: Further exploration**

> Beyond the power spectrum: take one non-standard cosmology (Om=0.31, sigma8=0.82,
> h=0.67, ns=0.965 and (a) compute the halo mass function at z=0
> and z=1 and report how much the abundance of 1e14 and 1e15 Msun/h
> clusters drops between the two, with the emulator uncertainty; (b)
> compute the CMB TT spectrum and report the position and height of the
> first acoustic peak; (c) compute the weak-lensing convergence spectrum
> for sources at z~1 and report the multipole where it peaks; (d) emulate
> the Lyman-alpha 1D flux power at the default IGM parameters and note its
> units. One short paragraph on how these four observables probe the same
> universe at different epochs and scales.

**If your app can't open the result links** (some restrict which hosts
they may fetch): add "use return_data=true" to the request — every compute
tool can return its numbers inline, and every response carries min/max/
median summary stats regardless.

---

## Reading the responses

- Tool results are JSON with `files` (server-side paths), a human
  `message` (with a browsable `View: https://files...` link), and
  `metadata` — including the full resolved cosmology, unit conventions,
  an `in_training_box` flag with extrapolation warnings, and summary
  statistics.
- Units: k in h/Mpc, P(k) in (Mpc/h)^3, CMB spectra as Dl in muK^2 —
  except Lyman-alpha tools (comoving Mpc, no h), flagged in their schema.
- If a call errors, the message names the violated parameter range —
  `describe_emulator` shows every emulator's valid box.
