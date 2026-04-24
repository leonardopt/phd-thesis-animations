# Video Disposition Config

Variant: `strict_static_only`

Allowed values:
- `static`
- `video`
- `omit`

Interpretation:
- `static` means the current rendered clip should be replaced by a still slide.
- `video` means keep the clip as video in the deck.
- `omit` means drop the clip entirely during deck generation.

Rule for this variant:
- Only mark a clip `static` when the current motion adds essentially no explanatory value and the final frame already does the job.

## 1 Introduction

| clip | decision |
| --- | --- |
| `000_intro_cognitive_problem` | `video` |
| `001_sens-mem-representations_a` | `video` |
| `002_sens-mem-representations_b` | `video` |
| `003_intro_classical_view` | `static` |
| `004_intro_sensory_recruitment` | `static` |
| `005_intro_research_question_1` | `static` |
| `006_intro_research_question_2` | `static` |
| `007_intro_research_question_3` | `static` |

## 2 Methodological Approach

| clip | decision |
| --- | --- |
| `000_methods_stimulus_requirements_a` | `video` |
| `001_methods_stimulus_requirements_b` | `video` |
| `002_methods_stimulus_requirements_c` | `video` |
| `003_methods_stimulus_requirements_d` | `video` |
| `004_methods_existing_approaches` | `static` |
| `005_methods_diffusion_models_explainer_a` | `video` |
| `006_methods_diffusion_models_explainer_b` | `video` |
| `007_methods_diffusion_opportunity` | `static` |
| `008_methods_project_plan` | `video` |

## 3 Study 1

| clip | decision |
| --- | --- |
| `000_study1_stage1_step1a` | `video` |
| `001_study1_stage1_step1b` | `video` |
| `002_study1_stage1_step2` | `video` |
| `003_study1_stage1_step2_showcase` | `video` |
| `004_study1_stage1_step3_part1` | `video` |
| `005_study1_stage1_step3_part2` | `video` |
| `006_study1_stage1_step4_setup` | `video` |
| `007_study1_stage1_step4_interpolation` | `video` |
| `008_study1_stage1_step5_handoff` | `video` |
| `009_study1_stage1_step5_deck` | `video` |
| `010_study1_stage1_step5_lpips` | `video` |
| `011_study1_stimulus_set_showcase` | `video` |
| `012_study1_stage2_triplet_task` | `video` |
| `013_study1_stage2_triplet_task2` | `video` |
| `014_study1_stage2_similarity_judgements_examples` | `video` |
| `015_study1_stage2_embedding_result` | `video` |
| `016_study1_stage2_model_order_to_heatmap` | `video` |
| `017_study1_stage3_memory_exp_design` | `video` |
| `018_study1_stage3_memory_repetition_explainer` | `video` |
| `019_study1_stage3_memory_exp_results` | `video` |

## 4 Study 2

| clip | decision |
| --- | --- |
| `000_study2_experimental_design` | `video` |
| `001_study2_decoding_overview_a` | `video` |
| `002_study2_decoding_overview_b` | `video` |
| `003_study2_decoding_overview_c` | `video` |
| `004_study2_decoding_overview_d` | `video` |
| `005_study2_within_session2_decoding_setup_a` | `video` |
| `006_study2_within_session2_decoding_setup_b` | `video` |
| `007_study2_within_session2_decoding_results` | `video` |
| `008_study2_cross_session_decoding_setup` | `video` |
| `009_study2_cross_session_decoding_results_a` | `video` |
| `010_study2_cross_session_decoding_results_b` | `video` |
| `011_study2_within_session1_decoding_setup_a` | `video` |
| `012_study2_within_session1_decoding_setup_b` | `video` |
| `013_study2_within_session1_decoding_results_a` | `video` |
| `014_study2_within_session1_decoding_results_b` | `video` |
| `015_study2_within_session1_decoding_results_c` | `video` |
| `016_study2_within_session1_decoding_results_d` | `video` |
| `017_study2_ltm_results_explainer` | `video` |
| `018_study2_supplemental_roi_timecourses_a` | `video` |
| `019_study2_supplemental_roi_timecourses_b` | `video` |
| `020_study2_supplemental_roi_temp_gen_mats` | `video` |
| `021_study2_searchlight_stimulation` | `video` |
| `022_study2_searchlight_delay` | `video` |
| `023_study2_decoding_summary` | `video` |

## 5 Conclusion

| clip | decision |
| --- | --- |
| `000_conclusion_summary` | `static` |
| `001_conclusion_theoretical_implications` | `static` |
| `002_conclusion_limitations` | `static` |
| `003_conclusion_future_directions` | `video` |

## 6 Supplementary Slides

| clip | decision |
| --- | --- |
| `000_intro_research_question_1` | `video` |
| `001_intro_research_question_2` | `video` |
| `002_intro_research_question_3` | `video` |
| `003_study1_stage3_memory_intro_a` | `video` |
| `004_study1_stage3_memory_intro_b` | `video` |
| `005_study1_stage3_memory_intro_c` | `video` |
| `006_study1_stage3_memory_intro_d` | `video` |
| `007_study1_stage3_memory_intro_e` | `video` |
