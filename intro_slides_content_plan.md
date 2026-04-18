# Introduction Slides — Content Plan
**Target duration: 5–7 minutes** (of a 30-minute defence)

---

## Narrative arc (one sentence)

> The brain can hold a rich visual image in mind after it disappears — this thesis asks *where* that representation lives, *what format* it takes, and whether looking at the world and remembering it engage the same neural machinery.

---

## Slide 1 — The central problem (≈ 45 s)

**Claim to land:** Visual memory is a unifying thread across perception, working memory (WM), and long-term memory (LTM) — yet neuroscience has mostly studied these in isolation.

**Key points:**
- The brain must encode, maintain, and retrieve rich visual information across multiple timescales (seconds → years).
- A single ecological question — how does the visual cortex represent what you're "holding in mind"? — spans all three memory systems.
- This project examines the question in a unified paradigm, for the first time with naturalistic images.

**What to show:** Brief motivating image or concept (naturalistic scene; brain schematic with perception → WM → LTM arrow).

---

## Slide 2 — Classical view: WM lives in association cortex (≈ 45 s)

**Claim to land:** For decades, WM was thought to be the business of prefrontal and parietal association cortex.

**Key points (keep brief):**
- Monkey lesion studies (Jacobsen 1936) → PFC damage impairs delayed responses.
- Electrophysiology → persistent firing in monkey PFC during the delay period (Fuster & Alexander 1971; Funahashi 1989).
- Human PET/fMRI → frontal-parietal activation during WM maintenance (Jonides 1993; D'Esposito 1995).
- Early visual areas: no sustained BOLD increase → dismissed.

**What to show:** `IntroLiteratureOverview` — classical panel (Funahashi figure + Jonides figure + three literature entries). Keep takeaway: *"WM was localized to prefrontal and association cortex."*

---

## Slide 3 — The shift: sensory recruitment model (≈ 75 s)

**Claim to land:** MVPA flipped the story — early visual cortex carries stimulus-specific WM content even without a BOLD increase.

**Key points:**
- Theory: perception and memory may *reuse the same sensory circuits* (Awh & Jonides 2001; Postle 2006).
- MVPA revolution: multivariate decoding can detect information in distributed patterns invisible to univariate GLM.
- Seminal evidence: orientations decoded from V1–V4 during the delay, after the stimulus is gone (Harrison & Tong 2009; Serences et al. 2009).
- Broad replication: motion, colour, spatial position, complex patterns.
- Controversy: human fMRI ↔ monkey electrophysiology mismatch; debate about format and functional necessity.

**What to show:** `IntroLiteratureOverview` — sensory recruitment panel (Awh & Jonides figure + Harrison & Tong figure + three literature entries). Keep takeaway: *"Early visual cortex may actively carry WM content."*

---

## Slide 4 — Three open questions (≈ 60 s)

**Claim to land:** The sensory recruitment model is influential but three critical questions remain underexplored — this thesis addresses all three.

| # | Question | Core issue |
|---|----------|------------|
| 1 | **Representational format** | Is WM content in a *sensory-like* or *memory-specific* code? Cross-decoding evidence is mixed; rarely tested directly with naturalistic images. |
| 2 | **Naturalistic stimuli** | Does sensory recruitment hold beyond simple gratings/colours? Ecological validity of the model is largely untested. |
| 3 | **LTM interaction** | Does the strength of long-term memory traces modulate early sensory recruitment during WM? Almost entirely unexplored. |

**What to show:** `IntroResearchQuestions` — brain icon + three info cards (blue / amber / green). No need to expand each card into paragraphs — the three labels are enough at this point.

---

## Slide 5 — The methodological challenge (≈ 45 s)

**Claim to land:** Addressing all three questions together requires naturalistic stimuli with *fine-grained perceptual control* — and such stimuli don't exist.

**Key points:**
- Simple WM stimuli (gratings, colours) offer control but lack ecological validity.
- Real-world images have high semantic and perceptual variance → poor experimental control.
- You need stimuli that are: (a) naturalistic, (b) perceptually graded within a category, (c) suitable for both WM and LTM tasks, (d) rich enough to evoke decodable early-visual responses.
- No existing database provides this.

**What to show:** `IntroStimulusRequirements` — continuum panel showing four example images + four requirement cards. Briefly mention "why existing sources failed" cards.

---

## Slide 6 — The solution: generative AI stimulus synthesis (≈ 60 s)

**Claim to land:** We used Stable Diffusion XL to *design* a stimulus set that satisfies all four requirements — enabling a unified WM + LTM paradigm with naturalistic images.

**Key points:**
- Prompt → generate candidates → spherical interpolation in latent noise space → 10-image perceptual continuum per scene.
- 108 object-scenes, 6 semantic categories.
- Validated with two online behavioural experiments (N=1,113 triplet judgements; N=260 WM task).
- Study 1 = stimulus generation & validation; Study 2 = fMRI experiment using these stimuli.

**What to show:** `IntroMethodologicalApproach` — the 5-step pipeline (Prompt → Generate → Select → Study 1 → Study 2). Keep callout: *"Build the stimulus space first. Then use it to test the theory."*

---

## Timing summary

| Slide | Content | Est. time |
|-------|---------|-----------|
| 1 | The central problem | ~45 s |
| 2 | Classical WM view | ~45 s |
| 3 | Sensory recruitment + MVPA | ~75 s |
| 4 | Three research questions | ~60 s |
| 5 | Methodological challenge | ~45 s |
| 6 | Generative AI solution | ~60 s |
| **Total** | | **~5:30** |

---

## What to cut or compress

- References (citations): speak them sparingly, show just author + year on-screen.
- The LTM background section (WM ↔ LTM literature: familiarity effects, Vo et al. 2022 etc.) — this is thesis detail; introduce LTM only as *why it matters* in RQ3, not as a literature review.
- The distraction/interference debate in sensory recruitment — mention it at most as one bullet in Slide 3 ("controversy").
- PFC-vs-sensory cortex debate nuances — enough to say "question remains open".

## Key messages the committee must walk away with

1. Sensory recruitment: real and established, but tested almost exclusively with simple stimuli.
2. Three gaps: format, naturalistic generalization, LTM interaction — all underexplored together.
3. Innovation: generative AI unlocked a naturalistic stimulus space that didn't exist before.
4. Setup: Study 1 built and validated it; Study 2 used it in fMRI.
