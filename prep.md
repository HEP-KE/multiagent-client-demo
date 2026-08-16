# Pre-session setup (takes ~10 minutes, please do this before the tutorial)

The tutorial will involve 2 repos. One python environment will serve both. We also require access to LLM tokens. 

## 1. Clone both repos side by side

```bash
git clone https://github.com/HEP-KE/spectra-mcp-server.git
git clone https://github.com/HEP-KE/multiagent-client-demo.git
```

(The client notebook assumes `../spectra-mcp-server` exists.)

## 2. Create the conda environment

```bash
conda create -n spectra-tutorial python=3.12 -y
conda activate spectra-tutorial

cd spectra-mcp-server
pip install cython numpy
pip install -e ".[dev]"

cd ../multiagent-client-demo
pip install -r requirements.txt
```

(The first `pip install` provides build helpers for `classy`; the second pulls in classy/CLASS, mcp, and the rest of the necessary packages.)

## 3. Verify CLASS works 

```bash
python -c "from classy import Class; c = Class(); c.set({'output':'mPk'}); c.compute(); print('CLASS OK')"
```

If `pip install classy` failed (it compiles C code):

- macOS: `xcode-select --install`, then retry `pip install classy`
- any platform: `conda install -c conda-forge classy`

## 4. Get a free API key from Gemini and Groq

1. Go to <https://aistudio.google.com/apikey> (login using your Google/gmail account). Make sure there are no credit cards on file (see notes below). 
2. **Create API key** → copy and save this code somewhere private. 
3. In `multiagent-client-demo/`, create your `.env`. We have provided `.env.example` that you can copy:

   ```bash
   cp .env.example .env
   # edit .env:  GOOGLE_API_KEY=AIza...
   ```

> **Budget warning**: as of mid-2026 the Gemini free tier allows ~20 requests per day. In a typical API plan, once the free quota is exhausted, you start paying per-token. To avoid this charge, simple do not have any credit card linked for payment.

> One full agent run in the tutorial uses ~10 requests — so your key is good for roughly **1-2 run per day**. Run the test below when you set up, then leave the Key alone until the session. (Quota resets at midnight Pacific.) 

> The `.env` file is gitignored — never commit keys.

**Recommended backup**: also grab a free Groq key at
<https://console.groq.com/keys> (email signup, no credit card) and add it to
`.env` as `GROQ_API_KEY=...`. Groq serves open-weight US models
(gpt-oss-120b) at ~14,400 requests/day; in the notebook it's just
`make_llm("groq")` instead of `make_llm()`. 

If your university/lab/collaboration provides tokens, then those can be included too. 

## 5. Testing the setup

```bash
cd spectra-mcp-server && pytest
cd ../multiagent-client-demo && python -c "
from dotenv import load_dotenv; load_dotenv()
from agents import make_llm
print(make_llm().invoke('Say READY').content)"
```

Expected: `7 passed` from pytest, then `READY` from the model.

If both print, you're set. If things don't work, please raise an issue on github. 

## 6. Optional: try the hosted servers from a GUI app

Both tutorial servers also run on a public demo host — you can talk to them
from the Claude desktop app (or ChatGPT) **before the session, with nothing
installed**, and get a feel for what the tutorial builds.

**Claude desktop app**: Settings → **Connectors** → **Add custom
connector**, twice:

| name | URL |
|---|---|
| `spectra` | `https://spectra.77-42-88-84.sslip.io/mcp` |
| `gaia` | `https://gaia.77-42-88-84.sslip.io/mcp` |

Then start a **new** chat and check both connectors are enabled in the
tools menu (the sliders icon). Connectors added mid-chat don't show up
until a fresh chat — if the model claims a server has no tools, that's
almost always the cause.

**ChatGPT app**: Settings → Connectors (requires developer mode; available
on paid plans) → add the same URLs.

**Sample question** — paste it whole; the last two lines matter, because
the figures are written on the *server's* disk and that path convention is
how you get to see them:

> First list the tools available from the spectra and gaia servers. Then:
> using the spectra tools, compute the z=0 matter power spectrum for
> standard LCDM and for total neutrino mass 0.15 eV, and plot both against
> the eBOSS data with LCDM as the ratio reference. Using the gaia tools,
> fetch the 100 pc sample with source="bundled", apply the published
> quality filters, and draw the density HRD. Report the neutrino
> suppression near k = 1 h/Mpc and the filtered star count vs the published
> 212,728.
> Save all files with output_dir "/srv/artifacts/YOURNAME" — do not use any
> other directory, and do not try to recompute things locally.

Then open `https://files.77-42-88-84.sslip.io/YOURNAME/` in a browser —
your figures are there. (Shared demo box: be gentle, don't put anything
private in the prompt outputs, and expect it to be offline outside tutorial
periods.)
