# Presenter Notes

Write your presenter notes below each video heading. Everything between one
video heading and the next becomes the Keynote presenter notes for that slide.
If you leave a section blank, the builder uses a fallback label derived from the
filename, such as `Study 1 - Stage 1 - Step 1a`.

# Intro

## media/videos/01_intro/{{quality_dir}}/sections/000_intro_cognitive_problem.mp4

I start with the behavioural problem. A rich visual image disappears, and a few
seconds later we still have to decide what we saw. That short gap is the core
working-memory demand this thesis keeps returning to.

## media/videos/01_intro/{{quality_dir}}/sections/001_sens-mem-representations.mp4

This panel introduces the sensory intuition. During perception, the brain builds
stimulus-specific visual representations over time, and one possibility is that
working memory simply keeps a perceptual trace online after the image is gone.

## media/videos/01_intro/{{quality_dir}}/sections/002_intro_classical_view.mp4

Historically, the dominant answer came from association cortex. Monkey lesion
studies linked delayed-response deficits to prefrontal damage, single-unit
recordings found persistent delay firing in dorsolateral PFC, and early PET and
fMRI extended this into a broader frontoparietal association-cortex account. In
that framework, early sensory cortex was not treated as the main substrate of
maintenance.

## media/videos/01_intro/{{quality_dir}}/sections/003_intro_sensory_recruitment.mp4

The sensory-recruitment account challenged that emphasis. Theory papers argued
that working memory could reuse sensory circuits, and MVPA made it possible to
detect feature information in distributed voxel patterns that mean activation
can miss. Landmark studies then showed that remembered visual features were
decodable from early visual cortex during the delay, but that still left open
whether the mnemonic code is truly sensory-like.

## media/videos/01_intro/{{quality_dir}}/sections/004_intro_research_question_1.mp4

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

So the key question for Study 2 is not just whether content is decodable in
early visual cortex, but whether the maintained code is still sensory-like. The
critical design feature is the separate perceptual session, which gives me an
independent sensory training set for a direct format comparison.

## media/videos/01_intro/{{quality_dir}}/sections/005_intro_research_question_2.mp4

The second question is about ecological validity. Most sensory-recruitment
studies used simple stimuli such as orientations, colors, or spatial locations.
That gives excellent control, but it leaves open whether the same logic holds
for the kind of rich visual information we actually maintain outside the lab.

Naturalistic work is still limited. Lee et al. (2013) and Xu et al. (2023) move
in that direction, but their stimuli are still relatively constrained and often
support coarse category-level strategies rather than fine perceptual
discrimination. Brady et al. (2019) is useful here as motivation for why
naturalistic visual memory matters in the first place.

This question also matters theoretically because stimulus properties may affect
whether sensory and memory codes look similar at all. Duan et al. (2024)
already suggests that conclusions from orientation stimuli may not generalize
cleanly. Study 2 therefore tests sensory recruitment with high-resolution
object-scenes that require detailed perceptual discrimination, not just gist or
category judgments.

## media/videos/01_intro/{{quality_dir}}/sections/006_intro_research_question_3.mp4

The third question concerns the interaction between working memory and long-term
memory. The field often studies them separately, but there is a long-running
debate about whether they rely on dissociable systems or partially overlapping
representations. Cowan (1999, 2001), Oberauer (2002), and Jonides et al. (2008)
are the key review landmarks here.

Behaviorally, there is strong reason to expect interaction. Familiarity can
speed or improve working memory, as shown for example by Xie et al. (2018), and
meaningful stimuli can also improve performance, as in Brady et al. (2022).
These findings suggest that pre-existing long-term traces may support short-term
maintenance.

The most relevant neural paper for this thesis is Vo et al. (2022), who found
that working memory and long-term memory retrieval can share a sensory-like code
in retinotopic cortex. That motivates our question: if repetition strengthens an
item's long-term representation, does it also change how working-memory content
is represented in early visual cortex? In Study 2, we test that by comparing
repeated and non-repeated items across sessions.

# Study 1

## media/videos/03_study1/{{quality_dir}}/01_Study1Stage1Step1a.mp4

## media/videos/03_study1/{{quality_dir}}/02_Study1Stage1Step1b.mp4

## media/videos/03_study1/{{quality_dir}}/03_Study1Stage1Step2.mp4

## media/videos/03_study1/{{quality_dir}}/04_Study1Stage1Step2Showcase.mp4

## media/videos/03_study1/{{quality_dir}}/05_Study1Stage1Step3Part1.mp4

## media/videos/03_study1/{{quality_dir}}/06_Study1Stage1Step3Part2.mp4

## media/videos/03_study1/{{quality_dir}}/07_Study1Stage1Step4Setup.mp4

## media/videos/03_study1/{{quality_dir}}/08_Study1Stage1Step4Interpolation.mp4

## media/videos/03_study1/{{quality_dir}}/09_Study1Stage1Step5Handoff.mp4

## media/videos/03_study1/{{quality_dir}}/10_Study1Stage1Step5Deck.mp4

## media/videos/03_study1/{{quality_dir}}/11_Study1Stage1Step5LPIPS.mp4

## media/videos/03_study1/{{quality_dir}}/12_Study1StimulusSetShowcase.mp4

## media/videos/03_study1/{{quality_dir}}/13_Study1Stage2TripletTask.mp4

## media/videos/03_study1/{{quality_dir}}/14_Study1Stage2TripletTask2.mp4

## media/videos/03_study1/{{quality_dir}}/15_Study1Stage2SimilarityJudgementsExamples.mp4

## media/videos/03_study1/{{quality_dir}}/16_Study1Stage2EmbeddingResult.mp4

## media/videos/03_study1/{{quality_dir}}/17_Study1Stage2ModelOrderToHeatmap.mp4

## media/videos/03_study1/{{quality_dir}}/18_Study1Stage3MemoryIntroA.mp4

## media/videos/03_study1/{{quality_dir}}/19_Study1Stage3MemoryIntroB.mp4

## media/videos/03_study1/{{quality_dir}}/20_Study1Stage3MemoryIntroC.mp4

## media/videos/03_study1/{{quality_dir}}/21_Study1Stage3MemoryIntroD.mp4

## media/videos/03_study1/{{quality_dir}}/22_Study1Stage3MemoryExpDesign.mp4

## media/videos/03_study1/{{quality_dir}}/23_Study1Stage3MemoryExpResults.mp4

# Study 2

## media/videos/04_study2/{{quality_dir}}/01_Study2ExperimentalDesign.mp4

## media/videos/04_study2/{{quality_dir}}/02_Study2DecodingOverviewA.mp4

## media/videos/04_study2/{{quality_dir}}/03_Study2DecodingOverviewB.mp4

## media/videos/04_study2/{{quality_dir}}/03c_Study2DecodingOverviewC.mp4

## media/videos/04_study2/{{quality_dir}}/04_Study2WithinSession2DecodingSetup.mp4

## media/videos/04_study2/{{quality_dir}}/05_Study2WithinSession2DecodingResults.mp4

## media/videos/04_study2/{{quality_dir}}/06_Study2CrossSessionDecodingSetup.mp4

## media/videos/04_study2/{{quality_dir}}/07_Study2CrossSessionDecodingResultsA.mp4

## media/videos/04_study2/{{quality_dir}}/08_Study2CrossSessionDecodingResultsB.mp4

## media/videos/04_study2/{{quality_dir}}/09_Study2WithinSession1DecodingSetupA.mp4

## media/videos/04_study2/{{quality_dir}}/10_Study2WithinSession1DecodingSetupB.mp4

## media/videos/04_study2/{{quality_dir}}/11_Study2WithinSession1DecodingResultsA.mp4

## media/videos/04_study2/{{quality_dir}}/12_Study2WithinSession1DecodingResultsB.mp4

## media/videos/04_study2/{{quality_dir}}/13_Study2WithinSession1DecodingResultsC.mp4

## media/videos/04_study2/{{quality_dir}}/14_Study2WithinSession1DecodingResultsD.mp4

## media/videos/04_study2/{{quality_dir}}/15_Study2LTMResultsExplainer.mp4

## media/videos/04_study2/{{quality_dir}}/16_Study2SupplementalRoiTimecoursesA.mp4

## media/videos/04_study2/{{quality_dir}}/17_Study2SupplementalRoiTimecoursesB.mp4

## media/videos/04_study2/{{quality_dir}}/18_Study2SupplementalRoiTempGenMats.mp4

## media/videos/04_study2/{{quality_dir}}/19_Study2SearchlightStimulation.mp4

## media/videos/04_study2/{{quality_dir}}/20_Study2SearchlightDelay.mp4
