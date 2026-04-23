# Presenter Notes

Write your presenter notes below each video heading. Everything between one
video heading and the next becomes the Keynote presenter notes for that slide.
If you leave a section blank, the builder uses a fallback label derived from the
filename, such as `Study 1 - Stage 1 - Step 1a`.

# Intro

## media/videos/01_intro/{{quality_dir}}/sections/000_intro_cognitive_problem.mp4

Consider a simple visual working memory task. You’re viewing at the image of an object, for example this fish in a coral reef, which you have to memorize over a short delay period in which the screen goes blank. Then the picture of the fish appears again and you have to tell whether it is the same one. 

## media/videos/01_intro/{{quality_dir}}/sections/001_sens-mem-representations_a.mp4

During perception, the brain builds stimulus-specific visual representations on incoming sensory input. 

When the stimulus is not avialble to perception anymore, visual working memory acts as a bridge over time, maintaining the visual information active over time.

## media/videos/01_intro/{{quality_dir}}/sections/002_sens-mem-representations_b.mp4

This is the visual hook for the representational-format question.

If the working-memory code is still sensory-like, the delay pattern should
substantially overlap with the sensory pattern. But if working memory preserves
the information in a transformed format, the delay pattern can remain
stimulus-specific while looking visibly different from perception.



## media/videos/01_intro/{{quality_dir}}/sections/003_intro_classical_view.mp4

The localisation of working memory function in the brain has long been debated.

Early lesion studies in non-human primates found that injuries to prefrontal areas caused significant short-term memory deficits (Jacobsen, 1936; Harlow et al., 1952). This inspired successive single-unit recording studies, which recorded from prefrontal areas while monkeys were performing delayed response tasks.  They found that neurons in the prefrontal cortex (PFC) exhibit persistent excitatory discharge throughout the delay period of a working memory task. Early PET and
fMRI extended this into a broader frontoparietal association-cortex account. In
that framework, early sensory cortex was not treated as the main substrate of
maintenance.

The classical view on the neural substrates supporting working memory largely focused on prefrontal, parietal, and temporal areas as primary neural substrates. 


## media/videos/01_intro/{{quality_dir}}/sections/004_intro_sensory_recruitment.mp4

The sensory-recruitment account challenged that emphasis. Theory papers argued
that working memory could reuse sensory circuits, and MVPA made it possible to
detect feature information in distributed voxel patterns that mean activation
can miss. Landmark studies then showed that remembered visual features were
decodable from early visual cortex during the delay, but that still left open
whether the mnemonic code is truly sensory-like.

## media/videos/01_intro/{{quality_dir}}/sections/005_intro_research_question_1.mp4

The first question is about representational format. The strongest early
evidence for sensory-like working-memory codes came from cross-decoding studies:
classifiers trained on perception generalized to the delay in Harrison and Tong
(2009), Albers et al. (2013), Rademaker et al. (2019), and related work.

But that interpretation is no longer straightforward. Sensory-trained decoders
are often weaker than memory-trained ones, Lorenc et al. (2020) reported weak
or absent cross-decoding, and Duan et al. (2024) argues that working-memory
codes may be more abstract than perceptual ones. Dynamic-coding work such as
Buschman et al. (2022) and Li et al. (2023) also suggests that the code may
change across the delay.

So our first key question is not just whether content is decodable in
early visual cortex, but whether the maintained code is still sensory-like. The
critical design feature is the separate perceptual session, which gives me an
independent sensory training set for a direct format comparison.

However, reuse of the same neuronal codes may support the storage of perceptual features efficiently and with high fidelity
How can sensory cortices process incoming sensory input and memory information at the same time? Naturalistic settings have no blank period. Do they coexist or are orthogonalized? 


## media/videos/01_intro/{{quality_dir}}/sections/006_intro_research_question_2.mp4

The second question is about ecological validity. Most sensory-recruitment
studies used simple stimuli such as orientations, colors, or spatial locations.
That gives excellent control, but that is not how naturalistic cognition looks like. This raises a problem of generalisability of the sensory recruitment results. 

Especially stimulus properties may affect whether sensory and memory codes look similar at all. Duan et al. (2024) already suggests that conclusions from orientation stimuli may not generalize cleanly. Type of stimuli may be a more decisive factor than previously thought in determining to what extent sensory and memory codes share the same format. 

Task demands might determine what sensory areas are recruited

Naturalistic work is still limited. Challenge to find suitable naturalistic stimuli stimuli for wm tasks.


## media/videos/01_intro/{{quality_dir}}/sections/007_intro_research_question_3.mp4

EXAMPLE CHRISTINA KOCH. 

The third question concerns the interaction between working memory and long-term
memory. The field often studies them separately, but in naturalistic cognition, wm integrates constantly ltm information.

Familiarity can speed up or improve working memory, as shown for example by Xie et al. (2018), and meaningful stimuli can also improve performance, as in Brady et al. (2022).

These findings suggest that pre-existing long-term traces may support short-term
maintenance.

Vo et al. (2022) who found that working memory and long-term memory retrieval can share a sensory-like code in retinotopic cortex. 

That motivates our question: does the presence of stimulus-specific long-term memory traces modulate how working-memory content is represented in early visual cortex? 

It is plausible that stronger ltm traces would make the wm code more sensory-like, but it also possible that the information processing shifts elsewhere in the brain, like in higher order regions. 


# Methods

## media/videos/02_methods/{{quality_dir}}/sections/000_methods_stimulus_requirements_a.mp4

A primary reason why these questions have been rarely tested directly is because of methodological constraints. The main difficulty is to design an experimental paradigm, and a corresponding set of naturalistic stimuli, suitable for studying sensory recruitment and its interaction with long-term memory

- The first requirement was that the stimuli had to be naturalistic.
- The thesis is about perception and memory in rich visual settings, so abstract lab features would not be enough.
- I needed object-scenes that look like real visual episodes rather than simplified placeholders.

## media/videos/02_methods/{{quality_dir}}/sections/001_methods_stimulus_requirements_b.mp4

- The second requirement was control.
- The stimuli had to preserve semantic identity while varying in fine perceptual detail.
- So the goal was not just realism, but a family of controlled within-concept variations.

## media/videos/02_methods/{{quality_dir}}/sections/002_methods_stimulus_requirements_c.mp4

- The third requirement was suitability for the actual working-memory and fMRI analyses.
- The images had to permit threshold-level discrimination, not just coarse category judgements.
- They also had to be informative for early visual cortex analyses, where subtle perceptual differences matter.

## media/videos/02_methods/{{quality_dir}}/sections/003_methods_stimulus_requirements_d.mp4

- The fourth requirement was distinctiveness.
- The stimuli had to be item-specific enough to support later long-term-memory manipulations as well.
- So one stimulus family had to work for perception, working memory, and later memory-based comparisons.

## media/videos/02_methods/{{quality_dir}}/sections/004_methods_existing_approaches.mp4

- Existing approaches each solved only part of the problem.
- Manual selection and curated databases offered realism, but they did not provide controlled within-concept continua.
- Web scraping offered scale, but semantic consistency and spacing control were weak.
- Earlier GAN-based work, especially Scene Wheels, was an important proof of concept.
- It showed that naturalistic images can be ordered on a perceptual continuum and used in memory experiments.
- But for this thesis that approach was too limited in resolution, semantic range, and image quality.
- I needed a method that could generate many high-resolution object-scenes across a broad stimulus space.

## media/videos/02_methods/{{quality_dir}}/sections/005_methods_diffusion_models_explainer_a.mp4

- This slide isolates the DDPM training view.
- Rather than emphasizing the one-step Markov kernel, I show the cumulative form $x_t = \sqrt{\bar{\alpha}_t}x_0 + \sqrt{1-\bar{\alpha}_t}\epsilon$.
- The row now runs all the way from $x_0$ through intermediate noisy states, then to $x_T$, and finally to one explicit pure-noise state $\epsilon \sim \mathcal{N}(0, I)$.
- The key point is that the model sees a noisy image $x_t$ and learns to predict the total added noise $\epsilon$.
- The legend in the bottom right clarifies the symbols without needing extra narration.

## media/videos/02_methods/{{quality_dir}}/sections/006_methods_diffusion_models_explainer_b.mp4

- This clip starts from the final frame of the forward process and keeps it on screen.
- Then I move that row upward, so the reverse loop can appear directly underneath as the second row.
- The top row reminds the audience what the network was trained to predict.
- The bottom row then switches to sampling, starting from pure Gaussian noise and applying the learned reverse kernel $p_\theta(x_{t-1}\mid x_t, c)$.
- At each step the model predicts the noise component $\hat{\epsilon}_\theta(x_t, t, c)$ and uses it to move toward a cleaner state.
- Repeating that step across timesteps gradually recovers a coherent image.
- The bottom-right legend and prompt-guidance callout make clear what $x_t$, $\hat{\epsilon}_\theta$, and $c$ mean during denoising.

## media/videos/02_methods/{{quality_dir}}/sections/007_methods_diffusion_opportunity.mp4

- Diffusion models offered the methodological opportunity.
- Instead of searching for suitable images, I could specify the target concept directly through text prompts.
- Stable Diffusion XL was attractive because it combines high output quality, flexibility, and 1024 x 1024 image synthesis.
- That makes it possible to generate many photorealistic object-scenes with one common procedure.

## media/videos/02_methods/{{quality_dir}}/sections/008_methods_project_plan.mp4

- This is the full logic of the project.
- First, generate candidate object-scenes with controlled naturalistic variation.
- Second, validate that variation psychophysically and in a working-memory task.
- Only then move to fMRI, so Study 1 becomes the methodological foundation for Study 2 rather than a separate side project.

# Study 1

## media/videos/03_study1/{{quality_dir}}/sections/000_study1_stage1_step1a.mp4

- Study 1 begins by defining the stimulus space.
- I designed 108 object-scenes spanning six semantic categories: animals, plants, landscape elements, items, buildings, and vehicles.
- The goal was broad semantic coverage, but still with a common object-centred layout across sets.
- So from the start, the aim is many controlled object-scene families rather than a few illustrative examples.

## media/videos/03_study1/{{quality_dir}}/sections/001_study1_stage1_step1b.mp4

- Each object-scene is defined by one fixed text prompt.
- The prompt specifies both the concept and the standard layout: a central object in a coherent scene.
- Keeping the prompt fixed is crucial because it stabilises semantic identity across variations.
- This means later changes should reflect perceptual variation, not concept drift.

## media/videos/03_study1/{{quality_dir}}/sections/002_study1_stage1_step2.mp4

- The next step is large-scale sampling from the model.
- For each object-scene, I generated 60 candidate exemplars using the same prompt and different seeds.
- This produces a cloud of plausible images that all instantiate the same concept.
- From that cloud, I can later choose a representative pair for interpolation.

## media/videos/03_study1/{{quality_dir}}/sections/003_study1_stage1_step2_showcase.mp4

- This showcase makes the intended variation visible.
- The images differ in fine details of shape, texture, colour, and scene realisation.
- At the same time, they still read as the same object-scene concept.
- That balance between variation and semantic stability is exactly what the rest of the pipeline exploits.

## media/videos/03_study1/{{quality_dir}}/sections/004_study1_stage1_step3_part1.mp4

- At this point I need a principled way to move from the exemplar cloud to a controlled continuum.
- I use LPIPS as a coarse model-based estimate of perceptual similarity.
- Here LPIPS is not yet the final validation criterion; it is a selection tool.
- Its role is to identify a representative local region from which interpolation can start.

## media/videos/03_study1/{{quality_dir}}/sections/005_study1_stage1_step3_part2.mp4

- Based on that similarity structure, I select an anchor image and a guide image.
- They should be close enough to preserve the same semantic identity.
- But they also need to be different enough to span a meaningful perceptual interval.
- This anchor-guide pair becomes the starting condition for interpolation.

## media/videos/03_study1/{{quality_dir}}/sections/006_study1_stage1_step4_setup.mp4

- The selected pair is still not the final stimulus set.
- Now I move from sampling images to generating a controlled continuum.
- The anchor and guide define the endpoints of a latent-space path between two semantically stable but perceptually distinct realisations.
- This is the step that turns exemplar selection into parametric stimulus design.

## media/videos/03_study1/{{quality_dir}}/sections/007_study1_stage1_step4_interpolation.mp4

- Interpolation is performed with spherical interpolation in the noisy input latents.
- This yields 200 intermediate images between anchor and guide.
- The objective is gradual perceptual change while keeping the semantic content coherent.
- So the continuum is generated in the model's latent space rather than by crude pixel blending.

## media/videos/03_study1/{{quality_dir}}/sections/008_study1_stage1_step5_handoff.mp4

- This is the handoff from the latent-space procedure back to concrete images.
- What was an abstract interpolation path now becomes a visible sequence of candidates.
- The continuity of the object-scene family becomes explicit on the slide.
- The remaining problem is how to reduce this dense sequence to an experimental set.

## media/videos/03_study1/{{quality_dir}}/sections/009_study1_stage1_step5_deck.mp4

- The fan of cards visualises the density of the interpolated candidate space.
- At this stage I have many plausible intermediate realisations, not just endpoints.
- But a behavioural experiment needs a compact, manageable set.
- So the next step is to select images that are approximately evenly spaced in perceptual distance.

## media/videos/03_study1/{{quality_dir}}/sections/010_study1_stage1_step5_lpips.mp4

- LPIPS returns here in its second role.
- After interpolation, I use it to preselect 10 images that are approximately linearly spaced in perceptual distance from the anchor.
- I then apply visual quality control to reject images with salient artefacts while keeping intervention minimal.
- The important point is that the final continuum is model-assisted, but not left unverified.

## media/videos/03_study1/{{quality_dir}}/sections/011_study1_stimulus_set_showcase.mp4

- This is the output of Stage 1.
- For each object-scene, I now have 10 ordered, high-resolution variations of the same semantic content.
- The sets preserve semantic identity while varying in fine perceptual detail across categories.
- With that, the project can move from generation to behavioural validation.

## media/videos/03_study1/{{quality_dir}}/sections/012_study1_stage2_triplet_task.mp4

- Stage 2 asks whether the model-based continuum aligns with human perception.
- I tested this in a large online triplet task with N = 1,113 participants.
- On each trial, participants saw one reference image and two probes.
- Their task was simply to decide which probe was more similar to the reference.

## media/videos/03_study1/{{quality_dir}}/sections/013_study1_stage2_triplet_task2.mp4

- The key methodological point is that triplet judgements provide ordinal information.
- Participants tell us which probe is closer to the reference, not by how much.
- That is exactly the data structure required for ordinal embedding methods.
- So Stage 2 tests whether a perceptual scale can be recovered from human similarity judgements.

## media/videos/03_study1/{{quality_dir}}/sections/014_study1_stage2_similarity_judgements_examples.mp4

- Here I broaden the argument beyond a single example.
- The same triplet logic was applied across many object-scenes and across natural and artificial categories.
- So the behavioural validation concerns the stimulus family as a whole.
- This matters because Study 2 will rely on the generality of the stimulus-generation pipeline.

## media/videos/03_study1/{{quality_dir}}/sections/015_study1_stage2_embedding_result.mp4

- The behavioural judgements are then converted into a one-dimensional perceptual embedding for each object-scene.
- I compared MLDS, SOE, and t-STE as candidate scaling methods.
- SOE was selected because it combined stable estimates with good computational efficiency.
- These embeddings then provide the final behavioural ordering of the stimulus sets.

## media/videos/03_study1/{{quality_dir}}/sections/016_study1_stage2_model_order_to_heatmap.mp4

- This slide compares the model-based order with the behaviour-based order.
- The important result is that agreement was strong overall, with Spearman rho = 0.73.
- So LPIPS was useful for coarse ordering, but human judgements confirmed and refined the final scale.
- At this point, the continua are no longer just model-defined; they are psychophysically grounded.

## media/videos/03_study1/{{quality_dir}}/sections/017_study1_stage3_memory_intro_a.mp4

- Stage 3 asks whether the validated perceptual continuum matters functionally for working memory.
- I now move from similarity judgements to a delayed match-to-sample task.
- The core prediction is that target-foil proximity on the continuum should determine discrimination difficulty.
- If the continuum is meaningful, memory performance should vary gradually with similarity.

## media/videos/03_study1/{{quality_dir}}/sections/018_study1_stage3_memory_intro_b.mp4

- This slide makes the Stage 3 prediction explicit.
- When target and foil are perceptually close, discriminability should be low.
- When they are farther apart on the continuum, performance should improve.
- So perceptual similarity becomes the operational definition of task difficulty.

## media/videos/03_study1/{{quality_dir}}/sections/019_study1_stage3_memory_intro_c.mp4

- I then add repetition to probe long-term-memory contributions to working memory.
- The logic is that repeated exposure should strengthen stimulus-specific long-term-memory traces.
- If that happens, performance should improve beyond the pure target-foil similarity effect.
- This is the conceptual bridge from perceptual validation to the working-memory and long-term-memory interaction question.

## media/videos/03_study1/{{quality_dir}}/sections/020_study1_stage3_memory_intro_d.mp4

- Here the conceptual logic becomes the actual stimulus grouping.
- For each object-scene, I select one target and three foils with increasing perceptual dissimilarity.
- This yields Easy, Medium, and Hard conditions grounded in the validated perceptual scale.
- Because target and foils share the same semantic identity, participants must rely on detailed perceptual information rather than gist or verbal labels.

## media/videos/03_study1/{{quality_dir}}/sections/021_study1_stage3_memory_exp_design.mp4

- This is the full Stage 3 memory-validation design.
- Participants completed the task online, N = 260, using an 8-second blank delay.
- The experiment comprised six blocks of 18 trials each.
- In every block, 9 targets were repeated and 9 were non-repeated, which lets me separate repetition-based improvement from general task adaptation.

## media/videos/03_study1/{{quality_dir}}/sections/022_study1_stage3_memory_exp_results.mp4

- The results validate the stimulus set on both counts.
- Accuracy followed the predicted graded difficulty pattern: Easy above Medium above Hard.
- Repeated targets also outperformed non-repeated targets across the experiment.
- So Study 1 does not just build stimuli; it shows that they are suitable for both a sensitive working-memory task and the later fMRI study.

# Study 2

## media/videos/04_study2/{{quality_dir}}/sections/000_study2_research_questions.mp4

- Study 2 carries the three dissertation questions into the fMRI setting.
- The first question is whether delay-period codes in early visual cortex remain sensory-like when measured against an independent perceptual session.
- The second is whether sensory recruitment extends to controlled naturalistic object-scenes rather than only simple laboratory features.
- The third is whether repetition-based long-term-memory traces change behaviour or mnemonic representational format during working memory.

## media/videos/04_study2/{{quality_dir}}/sections/001_study2_experimental_design.mp4

- Study 2 uses a two-session fMRI design to separate sensory and mnemonic representations.
- Session 1 is the delayed match-to-sample working-memory task; Session 2 is a perceptual task with the same stimuli and an attentional control task.
- This provides an independent sensory training set for decoding.
- The study included N = 42 participants and used a subset of 63 object-scenes from Study 1.

## media/videos/04_study2/{{quality_dir}}/sections/002_study2_decoding_overview_a.mp4

- I begin the decoding logic with Session 2.
- During the perceptual task, each object-scene evokes a multivoxel response pattern in early visual cortex.
- This gives me a purely sensory representational space.
- The first question is whether that sensory space is strong and reliable enough to decode stimulus identity.

## media/videos/04_study2/{{quality_dir}}/sections/003_study2_decoding_overview_b.mp4

- The next step is to define the comparable patterns during the memory task.
- In Session 1, both stimulus presentation and delay yield multivoxel patterns.
- The crucial issue is whether delay-period patterns are organised like the sensory patterns from Session 2.
- That is the representational-format question at the centre of the thesis.

## media/videos/04_study2/{{quality_dir}}/sections/004_study2_decoding_overview_c.mp4

- This slide states the cross-decoding logic explicitly.
- If sensory and mnemonic representations share the same format, a classifier trained on Session 2 perception should generalise to Session 1.
- If it generalises to stimulation but not to sustained delay, that argues against a stable sensory-like memory code.
- And if within-session decoding still succeeds, the correct interpretation is representational transformation rather than absence of information.

## media/videos/04_study2/{{quality_dir}}/sections/005_study2_within_session2_decoding_setup.mp4

- Before asking the main cross-session question, I first benchmark Session 2 on its own.
- I train and test linear multiclass SVMs within Session 2 using leave-one-run-out cross-validation.
- This establishes whether the naturalistic stimuli evoke robust stimulus-specific sensory information in V1-V3.
- Without this benchmark, a later cross-session null result would be hard to interpret.

## media/videos/04_study2/{{quality_dir}}/sections/006_study2_within_session2_decoding_results.mp4

- The benchmark is clearly positive.
- Within Session 2, stimulus identity is robustly decodable in early visual cortex.
- So the stimuli do generate separable sensory representations for naturalistic object-scenes.
- This means any later cross-session failure cannot simply be explained by weak sensory signal.

## media/videos/04_study2/{{quality_dir}}/sections/007_study2_cross_session_decoding_setup.mp4

- Now I move to the main test of representational format.
- I train on Session 2 stimulation data and test on Session 1 stimulation and delay.
- The stimulation phase provides a positive control because it should still resemble perception.
- The delay phase is the critical test of whether mnemonic representations share the same geometry as sensory ones.

## media/videos/04_study2/{{quality_dir}}/sections/008_study2_cross_session_decoding_results_a.mp4

- The GLM-based cross-session results give the first answer.
- Sensory-trained classifiers generalise to the stimulation period in Session 1.
- But they do not generalise throughout the delay.
- So the mnemonic code in early visual cortex is not a sustained sensory copy.

## media/videos/04_study2/{{quality_dir}}/sections/009_study2_cross_session_decoding_results_b.mp4

- The time-resolved analysis sharpens the same conclusion.
- Cross-session generalisation is strong in the early phase of the trial, corresponding to stimulus processing.
- It reappears around the late probe-related phase, but not throughout sustained delay.
- That temporal profile argues against a stable sensory-like code during working-memory maintenance.

## media/videos/04_study2/{{quality_dir}}/sections/010_study2_within_session1_decoding_setup_a.mp4

- At this point the complementary question becomes necessary.
- If cross-session decoding fails in the delay, is the delay uninformative, or is it informative in a different format?
- So the analysis now shifts from cross-session similarity to within-session mnemonic decodability.
- This is the step that separates a null-information account from a memory-specific-format account.

## media/videos/04_study2/{{quality_dir}}/sections/011_study2_within_session1_decoding_setup_b.mp4

- The within-session rationale makes that contrast explicit.
- Here I train and test within Session 1 itself, comparing matched task phases.
- These analyses are restricted to repeated stimuli because non-repeated items were shown only once and cannot support within-participant identity decoding.
- This removes the assumption that memory must look like Session 2 perception and allows a memory-specific format to emerge.

## media/videos/04_study2/{{quality_dir}}/sections/012_study2_within_session1_decoding_results_a.mp4

- The within-session GLM results are positive for both stimulation and delay.
- Stimulus identity is decodable during the delay when the classifier is trained on the memory task itself.
- So early visual cortex does retain stimulus-specific information during working memory.
- What changed across sessions was the format, not the presence of information.

## media/videos/04_study2/{{quality_dir}}/sections/013_study2_within_session1_decoding_results_b.mp4

- The time-resolved within-session analysis extends that result across the full trial.
- Stimulus-specific information remains detectable throughout the delay when training and testing are matched within Session 1.
- This is the strongest evidence for early sensory recruitment with naturalistic stimuli in the dissertation.
- But the signal still does not look sensory-like to a Session 2 decoder.

## media/videos/04_study2/{{quality_dir}}/sections/014_study2_within_session1_decoding_results_c.mp4

- The next question is whether the mnemonic code is stable over time.
- Temporal generalisation asks whether a decoder trained at one moment in the trial generalises to other moments.
- A broad off-diagonal pattern would suggest a stable code.
- A diagonal-dominant pattern would suggest a dynamic, non-stationary code.

## media/videos/04_study2/{{quality_dir}}/sections/015_study2_within_session1_decoding_results_d.mp4

- The pattern is largely concentrated near the diagonal.
- Generalisation weakens away from the diagonal, especially into later delay periods.
- This is more consistent with a dynamic mnemonic code than with one stable representation maintained unchanged over time.
- It also fits the broader conclusion of a representational discontinuity between perception and later maintenance.

## media/videos/04_study2/{{quality_dir}}/sections/016_study2_ltm_results_explainer.mp4

- This slide turns to Research Question 3, the working-memory and long-term-memory interaction.
- Behaviourally, repeated object-scenes improved performance in both Study 1 and Study 2.
- Neurally, repeated and non-repeated items did not differ in their similarity to sensory representations; in the GLM analysis, p = 0.75.
- So repetition changes behaviour, but I do not find evidence that it makes delay representations more sensory-like in early visual cortex.

## media/videos/04_study2/{{quality_dir}}/sections/017_study2_supplemental_roi_timecourses_a.mp4

- The supplemental ROI analyses ask whether the main pattern is unique to V1-V3 or part of a broader network.
- Qualitatively, the cross-session pattern is similar across visual and parietal ROIs.
- But the strongest stimulus-specific information is consistently found in early visual cortex.
- So the main result is not an artefact of ROI selection, but V1-V3 remains the clearest locus.

## media/videos/04_study2/{{quality_dir}}/sections/018_study2_supplemental_roi_timecourses_b.mp4

- This companion panel makes the same comparison for the within-session analyses.
- Delay-period mnemonic information is not confined to one single ROI.
- But again, early visual cortex carries the clearest and strongest stimulus-specific signal.
- That supports the claim that naturalistic working-memory representations are robust in early visual areas.

## media/videos/04_study2/{{quality_dir}}/sections/019_study2_supplemental_roi_temp_gen_mats.mp4

- The temporal-generalisation matrices provide the same comparison in compact form across ROIs.
- Across regions, the pattern is more compatible with dynamic coding than with one stable code that persists unchanged.
- So the time-varying character of the delay code is not confined to a single region.
- This strengthens the interpretation that non-stationarity is a genuine feature of the mnemonic representation.

## media/videos/04_study2/{{quality_dir}}/sections/020_study2_searchlight_stimulation.mp4

- The searchlight analysis asks whether the stimulation result generalises beyond predefined ROIs.
- Decodable sensory information is clearly expressed in occipital cortex and nearby regions.
- This replicates the ROI result at the whole-brain level.
- So the perceptual decoding result is spatially robust, not ROI-dependent.

## media/videos/04_study2/{{quality_dir}}/sections/021_study2_searchlight_delay.mp4

- During the delay, the searchlight pattern becomes more selective.
- But the informative voxels still point back to visual cortex.
- So the delay signal remains in early visual areas even when the representation is no longer sensory-like.
- This is the central result of the thesis in one slide: early sensory recruitment for naturalistic images, but with a transformed mnemonic format.

## media/videos/04_study2/{{quality_dir}}/sections/022_study2_decoding_summary.mp4

- Taken together, the decoding analyses give a consistent answer across methods.
- Early visual cortex carries robust stimulus-specific information during working memory for naturalistic images.
- But the strongest evidence favors a transformed, temporally dynamic mnemonic code rather than a stable sensory copy of perception.
- So the thesis supports sensory recruitment at the level of locus and information content, while revising the assumed representational format.

# Conclusions

## media/videos/05_conclusion/{{quality_dir}}/sections/000_conclusion_summary.mp4

- The dissertation followed a two-stage logic.
- Study 1 solved the stimulus bottleneck by generating and validating naturalistic object-scene continua with diffusion models.
- Study 2 then used that validated stimulus set in a two-session fMRI design.
- So the methodological contribution and the neuroscientific contribution are tightly linked.

## media/videos/05_conclusion/{{quality_dir}}/sections/001_conclusion_theoretical_implications.mp4

- This slide condenses the three research questions into their theoretical implications.
- For RQ1, early visual cortex maintained stimulus-specific information across the short delay, but the representational format was memory-specific rather than sensory-like.
- For RQ2, sensory recruitment did extend to naturalistic stimuli in a task with clear perceptual demands.
- Anatomically, the strongest information was found in early visual cortex rather than in higher-order regions.
- For RQ3, repetition improved working-memory performance, but it did not make the representational format more sensory-like.
- So the contribution is not a simple confirmation of the classical sensory recruitment model.
- It is a refinement: the model still works best for where information is found, but not for assuming that the maintained format is literally sensory.
- At the same time, the dissertation shows that deep generative modelling can reduce the trade-off between ecological validity and experimental control.
- It also shows that working memory and long-term memory can be studied within one unified paradigm.

## media/videos/05_conclusion/{{quality_dir}}/sections/002_conclusion_limitations.mp4

- The category selection was broad, but not exhaustive or fully data-driven.
- The continua varied along multiple perceptual features at once, rather than isolating one feature dimension.
- The images were synthetic and object-centred, and the repetition manipulation was relatively brief, so the neural null effect should not be overinterpreted as absence of long-term-memory formation.

## media/videos/05_conclusion/{{quality_dir}}/sections/003_conclusion_future_directions.mp4

- The broader point is methodological as well as theoretical.
- Controlled stimulus synthesis opens a new route to studying naturalistic cognition with experimental precision.
- The next steps are stronger control over scene structure, more dynamic and complex naturalistic stimuli, and analyses that target memory-specific representational formats directly.
- For the long-term-memory question, the clearest extension is learning across multiple days so consolidation processes can be tested explicitly.
