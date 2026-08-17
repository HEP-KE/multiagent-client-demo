# Testing the hosted MCP servers from your favorite app

Three MCP servers run on our public demo host — you can talk to them from
several AI apps **with nothing installed**, before or after the tutorial.

| server | URL | what it does |
|---|---|---|
| **cosmic** | `https://cosmic.77-42-88-84.sslip.io/mcp` | ~20 cosmological emulators: P(k), modified gravity, CMB, lensing, baryons, halo mass function, Lyman-alpha ([repo](https://github.com/HEP-KE/cosmic_emulator_server)) |
| spectra | `https://spectra.77-42-88-84.sslip.io/mcp` | CLASS power spectra vs eBOSS data ([repo](https://github.com/HEP-KE/spectra-mcp-server)) |
| gaia | `https://gaia.77-42-88-84.sslip.io/mcp` | Gaia DR2 colour-magnitude diagrams ([repo](https://github.com/HEP-KE/gaia-mcp-server)) |

Every figure or data file a server produces comes back as a link — browse
everything at <https://files.77-42-88-84.sslip.io/>.

The instructions below use **cosmic** as the example; spectra and gaia work
identically (same steps, their URL instead).

> **Shared demo box**: be gentle, don't put anything private in prompts,
> and expect it to be offline outside tutorial periods.
>
> **If the URL won't load at all**: some institutional networks (e.g.
> national labs) block `*.sslip.io` domains at the DNS level. Try from a
> home network or phone hotspot — the server is fine.

---

## Claude desktop app

1. Settings → **Connectors** → **Add custom connector**
2. Name: `cosmic`, URL: `https://cosmic.77-42-88-84.sslip.io/mcp` → Add
3. Start a **new** chat and check the connector is enabled in the tools
   menu (the sliders icon).

> Connectors added mid-chat don't show up until a fresh chat — if the model
> claims the server has no tools, that's almost always the cause.

## ChatGPT app

1. Settings → **Connectors** → enable **Developer mode** (requires a paid
   plan)
2. **Add connector** → same name + URL as above
3. In a new chat, enable the connector under the tools/plus menu.

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

## Things to try (paste whole)

**Warm-up — discovery:**

> List the emulators and skills available from the cosmic server. Which
> families are covered, and which emulators are active vs deferred?

**The flagship — cross-emulator check:**

> Load the pk-crosscheck skill from the cosmic server and follow it: run
> all six nonlinear P(k) backends at Om=0.31, sigma8=0.82, z=0, plot the
> comparison, and tell me the k-range where they agree within 2%.

**Modified gravity:**

> Using the cosmic server, compute the cubic Galileon boost at f_phi=0.8
> and the f(R) boost at |fR0|=1e-5, both at z=0, plot them together, and
> report where each peaks. Include the Galileon GP uncertainty.

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
