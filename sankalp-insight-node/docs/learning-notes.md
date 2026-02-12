# Learning Notes

## Summarization
- Uses Uniguru endpoint when configured; falls back to sentence join.
- Short and medium summaries derived per item, used as `script`.

## Sentiment
- Heuristic polarity, confidence, and tone; configurable later to ML.

## RL Reward Mapping
- Signals: `editor_approve`, `user_like`, `user_skip`, `manual_override`.
- Weights via `RL_WEIGHTS_JSON`; default sums clamped to [-1, 1].
- Automator thresholds control `requeue` vs `escalate`.

## TTS
- Vaani client supports raw audio, `audio_base64`, or `audio_url`.
- Fallback uses `pyttsx3` with tone-based speaking rate.

## Trend & Smart Feed
- Trend mixes velocity and density over recent windows.
- Priority combines trend, polarity weight, confidence, recency.