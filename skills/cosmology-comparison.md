---
name: cosmology-comparison
description: Recipe for comparing matter power spectra of several cosmologies against the eBOSS data
---

# Cosmology comparison recipe

When asked to compare cosmological models against the eBOSS DR14 data:

1. Call `list_cosmology_models` first if you are unsure of the exact model
   names or their tunable parameters.
2. Compute the reference model (usually `lcdm`) **first**, then the variant
   models, one `compute_power_spectrum` call each. Keep the default k range
   unless the user asks otherwise — it is chosen to cover the data.
3. Pass ALL the returned CSV paths to a single `plot_power_spectra` call,
   with the reference model at `reference_index` 0 (put its file first).
4. Sanity checks worth reporting: massive neutrinos should suppress power by
   roughly 4–8% at k = 1 h/Mpc for Σmν = 0.10 eV; the data points should
   scatter around the LCDM curve (they are the inferred z=0 linear power).
5. Never copy P(k) numbers between steps — only file paths.
