We need a really smart-looking streaming speech to text evaluator.

That means:
- I can speak to the microphone and see my audio being transcribed live.
	- We need to work out how we display it on-screen.
	- Lay out a few options. For example:
		- Force to one line per model. Simply tail through the last `n` characters where `n` is the width of the terminal UI minus space for model names)
			- `groq/whisper | Speaker 1: and then I says to her`
			- `groq/whisper | Speaker 1: en I says to her, you `
		- Wrap multi-line per model. Use the native diarisation/splitting.
			- `groq/whisper`
- I can choose which providers + models to run.
	- I've put `MISTRAL_API_KEY` and `GROQ_API_KEY` in the directory to run Voxtral and Whisper. Obviously ElevenLabs is already in here (see implementation note).
	- `~/Dropbox/Projects/whisper.cpp` is also available. Let's use this for initial testing.
	- Please give me instructions for how to run HuggingFace.
	- With/without diarisation and other toggles, where possible.
- All data should follow industry standards.
	- Eval: Assume there needs to be a directory per eval run, each containing input, output and assessment directories?
	- Input: Assume this needs to end up being an efficient audio file format (up to a configurable maximum size, I think?)
	- Output: Assume this is just a file per model.
	- Scoring: No idea how this should be structured.
- Implementation:
	1. Write a detailed plan to `docs/`.
	2. Get a proof of concept working with whisper.cpp. Commit that once Pytests pass.
    - If it's causing problems, don't worry about the existing speech_cli implementation. It's not fully working anyway. We'll want it all to work side-by-side by step 4, but not necessarily before.
	3. Then a side-by-side with whisper.cpp against itself. Ask for my input at this point.
	4. Then we want ElevenLabs, Mistral, Groq, HuggingFace.
- Later:
  - Point to local file
  - Record to local file
  - Interactive scorer
  - LLM scorer
  - Point to web URL
  - Live amplitude, later replaced by spectogram.
