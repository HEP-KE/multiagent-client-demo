# Pre-session setup (10 minutes, please do this BEFORE the tutorial)

One environment serves both repos. If anything fails, the fallback notes are
at the bottom — and please ask before the session, not during.

## 1. Clone both repos side by side

```bash
git clone https://github.com/HEP-KE/spectra-mcp-server.git
git clone https://github.com/HEP-KE/multiagent-client-demo.git
```

(The client notebook assumes `../spectra-mcp-server` exists.)

## 2. Create the environment

```bash
conda create -n spectra-tutorial python=3.12 -y
conda activate spectra-tutorial

cd spectra-mcp-server
pip install cython numpy        # build helpers for classy
pip install -e ".[dev]"         # installs classy (CLASS), mcp, matplotlib, ...

cd ../multiagent-client-demo
pip install -r requirements.txt
```

## 3. Verify CLASS works 

```bash
python -c "from classy import Class; c = Class(); c.set({'output':'mPk'}); c.compute(); print('CLASS OK')"
```

If `pip install classy` failed (it compiles C code):

- macOS: `xcode-select --install`, then retry `pip install classy`
- any platform: `conda install -c conda-forge classy`

## 4. Get a free Gemini API key

1. Go to <https://aistudio.google.com/apikey> (any Google account).
2. **Create API key** → copy it.
3. In `multiagent-client-demo/`, create your `.env`:

   ```bash
   cp .env.example .env
   # edit .env:  GOOGLE_API_KEY=AIza...
   ```

> **Budget warning**: as of mid-2026 the Gemini free tier allows only ~20
> requests per day. One full agent run uses ~10 of them — so your key is good
> for roughly **one run per day**. Run the smoke test below when you set up,
> then LEAVE THE KEY ALONE until the session. (Quota resets at midnight
> Pacific.) The `.env` file is gitignored — never commit keys.

**Optional but recommended backup**: also grab a free Groq key at
<https://console.groq.com/keys> (email signup, no credit card) and add it to
`.env` as `GROQ_API_KEY=...`. Groq serves open-weight US models
(gpt-oss-120b) at ~14,400 requests/day; in the notebook it's just
`make_llm("groq")` instead of `make_llm()`.

## 5. Smoke test (2 commands)

```bash
cd spectra-mcp-server && pytest          # 7 passed
cd ../multiagent-client-demo && python -c "
from dotenv import load_dotenv; load_dotenv()
from agents import make_llm
print(make_llm().invoke('Say READY').content)"
```

If both print happily, you're set. See you at the session — we'll start in
`spectra-mcp-server/notebooks/01_manual_pipeline.ipynb`.
