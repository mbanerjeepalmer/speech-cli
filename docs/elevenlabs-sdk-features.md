# ElevenLabs Python SDK v2.27.0 - Complete Feature Catalog

This document provides a comprehensive catalog of ALL features available in the ElevenLabs Python SDK v2.27.0.

## Table of Contents

1. [Text-to-Speech (TTS)](#1-text-to-speech-tts)
2. [Speech-to-Text (STT)](#2-speech-to-text-stt)
3. [Voices Management](#3-voices-management)
4. [Models](#4-models)
5. [History](#5-history)
6. [Pronunciation Dictionaries](#6-pronunciation-dictionaries)
7. [Dubbing](#7-dubbing)
8. [Text-to-Sound-Effects](#8-text-to-sound-effects)
9. [Text-to-Voice (Voice Generation)](#9-text-to-voice-voice-generation)
10. [Text-to-Dialogue](#10-text-to-dialogue)
11. [Speech-to-Speech](#11-speech-to-speech)
12. [Audio Isolation](#12-audio-isolation)
13. [Audio Native](#13-audio-native)
14. [Music Generation](#14-music-generation)
15. [Studio (Projects)](#15-studio-projects)
16. [Conversational AI](#16-conversational-ai)
17. [Forced Alignment](#17-forced-alignment)
18. [User & Subscription](#18-user--subscription)
19. [Usage](#19-usage)
20. [Tokens](#20-tokens)
21. [Workspace](#21-workspace)
22. [Service Accounts](#22-service-accounts)
23. [Webhooks](#23-webhooks)
24. [Samples](#24-samples)
25. [Common Parameters](#25-common-parameters)

---

## SDK Structure

The SDK uses a hierarchical client structure accessed via the main `ElevenLabs` client class:

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key="YOUR_API_KEY")
```

Both sync (`ElevenLabs`) and async (`AsyncElevenLabs`) versions are available.

---

## 1. Text-to-Speech (TTS)

**Module:** `client.text_to_speech`

### Methods

#### `convert(voice_id, text, ...)`
Convert text to speech, returns audio bytes.

**Parameters:**
- `voice_id` (str): ID of the voice to use
- `text` (str): Text to convert
- `model_id` (str): Model ID (default: eleven_monolingual_v1)
- `language_code` (str): ISO 639-1 language code
- `voice_settings` (VoiceSettings): Voice settings object
- `enable_logging` (bool): Enable logging
- `optimize_streaming_latency` (int): 0-4, latency optimization level
- `output_format` (str): Audio format (see Common Parameters)
- `pronunciation_dictionary_locators` (list): Pronunciation dictionaries to use
- `seed` (int): Random seed for reproducibility
- `previous_text` (str): Text from previous request for context
- `next_text` (str): Text from next request for context
- `previous_request_ids` (list): IDs from previous requests
- `next_request_ids` (list): IDs from next requests
- `use_pvc_as_ivc` (bool): Use PVC as IVC
- `apply_text_normalization` (str): 'auto', 'on', 'off'
- `apply_language_text_normalization` (bool): Heavy latency impact, Japanese only

**Returns:** bytes (audio data)

**Output Formats:**
- MP3: `mp3_22050_32`, `mp3_44100_64`, `mp3_44100_96`, `mp3_44100_128`, `mp3_44100_192`
- PCM: `pcm_16000`, `pcm_22050`, `pcm_24000`, `pcm_44100`
- μ-law: `ulaw_8000`

#### `convert_with_timestamps(voice_id, text, ...)`
Generate speech with character-level timing information.

**Parameters:** Same as `convert()`

**Returns:** `AudioWithTimestampsResponse` with alignment data

#### `stream(voice_id, text, ...)`
Stream audio in real-time.

**Parameters:** Same as `convert()`

**Returns:** Iterator[bytes] for streaming playback

#### `stream_with_timestamps(voice_id, text, ...)`
Stream audio with timing information.

**Parameters:** Same as `convert()`

**Returns:** Iterator[StreamingAudioChunkWithTimestampsResponse]

---

## 2. Speech-to-Text (STT)

**Module:** `client.speech_to_text`

### Methods

#### `convert(model_id, ...)`
Transcribe audio/video files.

**Parameters:**
- `model_id` (str): 'scribe_v1' or 'scribe_v1_experimental'
- `file` (File): Audio/video file to transcribe
- `cloud_storage_url` (str): Alternative to file upload
- `language_code` (str): ISO 639-1 language code
- `enable_logging` (bool): Enable logging
- `tag_audio_events` (bool): Tag audio events (applause, laughter, etc.)
- `num_speakers` (int): Number of speakers for diarization
- `timestamps_granularity` (str): 'word' or 'character'
- `diarize` (bool): Enable speaker diarization
- `diarization_threshold` (float): Diarization threshold
- `additional_formats` (list): Additional output formats
- `file_format` (str): 'pcm_s16le_16' or 'other'
- `webhook` (str): Webhook URL for completion notification
- `webhook_id` (str): Webhook ID
- `webhook_metadata` (dict): Webhook metadata
- `temperature` (float): Sampling temperature
- `seed` (int): Random seed
- `use_multi_channel` (bool): Multi-channel support

**Returns:** Transcription result with text, segments, and metadata

### Nested: `client.speech_to_text.transcripts`

#### `get(transcript_id)`
Get transcript by ID.

**Parameters:**
- `transcript_id` (str): Transcript ID

**Returns:** Transcript object

#### `delete(transcript_id)`
Delete transcript.

**Parameters:**
- `transcript_id` (str): Transcript ID

---

## 3. Voices Management

**Module:** `client.voices`

### Main Methods

#### `get_all(show_legacy)`
List all available voices.

**Parameters:**
- `show_legacy` (bool): Include legacy voices

**Returns:** List of Voice objects

#### `search(...)`
Search/filter voices with pagination.

**Parameters:**
- `next_page_token` (str): Pagination token
- `page_size` (int): Results per page
- `search` (str): Search query
- `sort` (str): Sort field
- `sort_direction` (str): 'asc' or 'desc'
- `voice_type` (str): Filter by voice type
- `category` (str): Filter by category
- `fine_tuning_state` (str): Filter by fine-tuning state
- `collection_id` (str): Filter by collection
- `include_total_count` (bool): Include total count
- `voice_ids` (list): Filter by specific voice IDs

**Returns:** Paginated voice results

#### `get(voice_id, with_settings)`
Get voice metadata.

**Parameters:**
- `voice_id` (str): Voice ID
- `with_settings` (bool): Include settings

**Returns:** Voice object

#### `delete(voice_id)`
Delete a voice.

**Parameters:**
- `voice_id` (str): Voice ID

#### `update(voice_id, name, files, remove_background_noise, description, labels)`
Edit voice.

**Parameters:**
- `voice_id` (str): Voice ID
- `name` (str): New name
- `files` (list): Audio files
- `remove_background_noise` (bool): Remove background noise
- `description` (str): Voice description
- `labels` (dict): Labels

#### `share(public_user_id, voice_id, new_name)`
Add shared voice to collection.

**Parameters:**
- `public_user_id` (str): User ID
- `voice_id` (str): Voice ID
- `new_name` (str): New name for shared voice

#### `get_shared(...)`
Get shared voices from library.

**Parameters:**
- `page_size` (int): Results per page
- `category` (str): Filter by category
- `gender` (str): Filter by gender
- `age` (str): Filter by age
- `accent` (str): Filter by accent
- `language` (str): Filter by language
- `locale` (str): Filter by locale
- `search` (str): Search query
- `use_cases` (list): Filter by use cases
- `descriptives` (list): Filter by descriptives
- `featured` (bool): Featured voices only
- `min_notice_period_days` (int): Minimum notice period
- `include_custom_rates` (bool): Include custom rates
- `include_live_moderated` (bool): Include live moderated
- `reader_app_enabled` (bool): Reader app enabled
- `owner_id` (str): Filter by owner
- `sort` (str): Sort field
- `page` (int): Page number

**Returns:** Shared voice results

#### `find_similar_voices(audio_file, similarity_threshold, top_k)`
Find similar voices by audio sample.

**Parameters:**
- `audio_file` (File): Audio sample
- `similarity_threshold` (float): Similarity threshold (0-1)
- `top_k` (int): Number of results

**Returns:** List of similar voices

### Nested: `client.voices.ivc` (Instant Voice Cloning)

#### `create(name, files, description, labels, remove_background_noise)`
Clone voice instantly from audio samples.

**Parameters:**
- `name` (str): Voice name
- `files` (list): Audio samples (1-25 files)
- `description` (str): Voice description
- `labels` (dict): Labels
- `remove_background_noise` (bool): Remove background noise

**Returns:** Created voice object

### Nested: `client.voices.pvc` (Professional Voice Cloning)

#### `create(voice_name, voice_description)`
Start professional voice cloning.

**Parameters:**
- `voice_name` (str): Voice name
- `voice_description` (str): Voice description

**Returns:** PVC project object

#### `train(voice_id)`
Train PVC model.

**Parameters:**
- `voice_id` (str): Voice ID

#### `update(voice_id, ...)`
Update PVC settings.

**Parameters:**
- `voice_id` (str): Voice ID
- Additional PVC-specific parameters

**Sub-clients:**
- `samples`: Manage PVC samples
- `verification`: Manage verification and captcha

### Nested: `client.voices.settings`

#### `get(voice_id)`
Get voice settings.

**Parameters:**
- `voice_id` (str): Voice ID

**Returns:** VoiceSettings object

#### `get_default()`
Get default voice settings.

**Returns:** Default VoiceSettings object

#### `update(voice_id, stability, similarity_boost, style, use_speaker_boost)`
Update voice settings.

**Parameters:**
- `voice_id` (str): Voice ID
- `stability` (float): 0.0-1.0
- `similarity_boost` (float): 0.0-1.0
- `style` (float): 0.0-1.0
- `use_speaker_boost` (bool): Enable speaker boost

**Returns:** Updated VoiceSettings object

### Nested: `client.voices.samples`

#### `delete(voice_id, sample_id)`
Delete voice sample.

**Parameters:**
- `voice_id` (str): Voice ID
- `sample_id` (str): Sample ID

**Sub-client:**
- `audio`: Get sample audio

---

## 4. Models

**Module:** `client.models`

### Methods

#### `list()`
Get all available models.

**Returns:** List of Model objects with:
- `model_id`: Model identifier
- `name`: Model name
- `can_do_text_to_speech`: TTS support
- `can_do_voice_conversion`: Voice conversion support
- `languages`: Supported languages
- Additional model metadata

---

## 5. History

**Module:** `client.history`

### Methods

#### `list(...)`
Get generation history.

**Parameters:**
- `page_size` (int): Results per page
- `start_after_history_item_id` (str): Pagination cursor
- `voice_id` (str): Filter by voice
- `model_id` (str): Filter by model
- `date_before_unix` (int): Filter before timestamp
- `date_after_unix` (int): Filter after timestamp
- `sort_direction` (str): 'asc' or 'desc'
- `search` (str): Search query
- `source` (str): Filter by source

**Returns:** Paginated history items

#### `get(history_item_id)`
Get specific history item.

**Parameters:**
- `history_item_id` (str): History item ID

**Returns:** History item object

#### `delete(history_item_id)`
Delete history item.

**Parameters:**
- `history_item_id` (str): History item ID

#### `get_audio(history_item_id)`
Download audio from history.

**Parameters:**
- `history_item_id` (str): History item ID

**Returns:** Audio bytes

#### `download(history_item_ids)`
Batch download multiple items.

**Parameters:**
- `history_item_ids` (list): List of history item IDs

**Returns:** ZIP file with audio files

---

## 6. Pronunciation Dictionaries

**Module:** `client.pronunciation_dictionaries`

### Methods

#### `create_from_file(name, file, description, workspace_access)`
Create from PLS lexicon file.

**Parameters:**
- `name` (str): Dictionary name
- `file` (File): PLS XML file
- `description` (str): Description
- `workspace_access` (str): Access level

**Returns:** Dictionary object

#### `create_from_rules(rules, name, description, workspace_access)`
Create from rules.

**Parameters:**
- `rules` (list): Pronunciation rules
- `name` (str): Dictionary name
- `description` (str): Description
- `workspace_access` (str): Access level

**Rule Types:**
- `alias`: Text replacement
- `phoneme`: IPA or CMU pronunciation

**Returns:** Dictionary object

#### `list(page_size, next_page_token, sort)`
List dictionaries.

**Parameters:**
- `page_size` (int): Results per page
- `next_page_token` (str): Pagination token
- `sort` (str): Sort field

**Returns:** Paginated dictionary list

#### `get(pronunciation_dictionary_id)`
Get dictionary metadata.

**Parameters:**
- `pronunciation_dictionary_id` (str): Dictionary ID

**Returns:** Dictionary object

#### `update(pronunciation_dictionary_id, archived, name)`
Update dictionary.

**Parameters:**
- `pronunciation_dictionary_id` (str): Dictionary ID
- `archived` (bool): Archive status
- `name` (str): New name

#### `download(pronunciation_dictionary_id, version_id)`
Download as PLS file.

**Parameters:**
- `pronunciation_dictionary_id` (str): Dictionary ID
- `version_id` (str): Version ID

**Returns:** PLS XML file

### Nested: `client.pronunciation_dictionaries.rules`

#### `add(pronunciation_dictionary_id, rules)`
Add pronunciation rules.

**Parameters:**
- `pronunciation_dictionary_id` (str): Dictionary ID
- `rules` (list): Rules to add

#### `remove(pronunciation_dictionary_id, rule_ids)`
Remove rules.

**Parameters:**
- `pronunciation_dictionary_id` (str): Dictionary ID
- `rule_ids` (list): Rule IDs to remove

---

## 7. Dubbing

**Module:** `client.dubbing`

### Methods

#### `list(cursor, page_size, dubbing_status, filter_by_creator, order_by, order_direction)`
List dubs.

**Parameters:**
- `cursor` (str): Pagination cursor
- `page_size` (int): Results per page
- `dubbing_status` (str): Filter by status
- `filter_by_creator` (bool): Filter by creator
- `order_by` (str): Sort field
- `order_direction` (str): 'asc' or 'desc'

**Returns:** Paginated dub list

#### `create(...)`
Create new dub.

**Parameters:**
- `file` (File): Video/audio file to dub
- `source_url` (str): Alternative URL source
- `source_lang` (str): Source language code
- `target_lang` (str): Target language code
- `target_accent` (str): Target accent
- `num_speakers` (int): Number of speakers
- `watermark` (bool): Add watermark
- `start_time` (int): Start time in seconds
- `end_time` (int): End time in seconds
- `highest_resolution` (bool): Use highest resolution
- `drop_background_audio` (bool): Remove background audio
- `use_profanity_filter` (bool): Filter profanity
- `dubbing_studio` (bool): Studio quality
- `disable_voice_cloning` (bool): Disable voice cloning
- `mode` (str): Dubbing mode
- `csv_file` (File): Custom CSV for segments
- `csv_fps` (float): CSV framerate
- `foreground_audio_file` (File): Custom foreground audio
- `background_audio_file` (File): Custom background audio
- `name` (str): Dub name

**Returns:** Dubbing project object

#### `get(dubbing_id)`
Get dub status.

**Parameters:**
- `dubbing_id` (str): Dubbing ID

**Returns:** Dubbing status object

#### `delete(dubbing_id)`
Delete dub.

**Parameters:**
- `dubbing_id` (str): Dubbing ID

### Nested: `client.dubbing.resource`

#### `get(dubbing_id)`
Get dubbing resource.

**Parameters:**
- `dubbing_id` (str): Dubbing ID

**Returns:** Dubbing resource

#### `dub(dubbing_id, ...)`
Update dub.

**Parameters:**
- `dubbing_id` (str): Dubbing ID
- Additional dubbing parameters

#### `transcribe(dubbing_id)`
Transcribe source.

**Parameters:**
- `dubbing_id` (str): Dubbing ID

#### `translate(dubbing_id)`
Translate transcript.

**Parameters:**
- `dubbing_id` (str): Dubbing ID

#### `render(dubbing_id)`
Render final dub.

**Parameters:**
- `dubbing_id` (str): Dubbing ID

#### `migrate_segments(dubbing_id)`
Migrate segments.

**Parameters:**
- `dubbing_id` (str): Dubbing ID

**Sub-clients:**
- `language`: Language management
- `segment`: Segment management
- `speaker`: Speaker management

### Nested: `client.dubbing.audio`

#### `get(dubbing_id, language_code)`
Download dubbed audio.

**Parameters:**
- `dubbing_id` (str): Dubbing ID
- `language_code` (str): Target language

**Returns:** Audio bytes

### Nested: `client.dubbing.transcript`

#### `get(dubbing_id, language_code, format_type)`
Get transcript.

**Parameters:**
- `dubbing_id` (str): Dubbing ID
- `language_code` (str): Language code
- `format_type` (str): Format type

**Returns:** Transcript in specified format

---

## 8. Text-to-Sound-Effects

**Module:** `client.text_to_sound_effects`

### Methods

#### `convert(text, output_format, loop, duration_seconds, prompt_influence, model_id)`
Generate sound effects.

**Parameters:**
- `text` (str): Text description of sound effect
- `output_format` (str): Audio format
- `loop` (bool): Create seamless loop (music_v2 only)
- `duration_seconds` (float): 0.5-30 seconds
- `prompt_influence` (float): 0-1 (higher = more adherence to prompt)
- `model_id` (str): Model ID

**Returns:** Audio bytes

---

## 9. Text-to-Voice (Voice Generation)

**Module:** `client.text_to_voice`

### Methods

#### `create_previews(voice_description, output_format, text, auto_generate_text, loudness, quality, seed, guidance_scale)`
Generate voice previews from description.

**Parameters:**
- `voice_description` (str): Text description of desired voice
- `output_format` (str): Audio format
- `text` (str): Text to speak in preview
- `auto_generate_text` (bool): Auto-generate sample text
- `loudness` (float): Loudness level
- `quality` (str): Quality level
- `seed` (int): Random seed
- `guidance_scale` (float): Guidance scale

**Returns:** List of voice preview objects

#### `create(voice_name, voice_description, generated_voice_id, labels, played_not_selected_voice_ids)`
Save generated voice.

**Parameters:**
- `voice_name` (str): Name for voice
- `voice_description` (str): Voice description
- `generated_voice_id` (str): Generated voice ID
- `labels` (dict): Labels
- `played_not_selected_voice_ids` (list): IDs of previews not selected

**Returns:** Voice object

#### `design(voice_description, ...)`
Design voice with advanced options.

**Parameters:**
- `voice_description` (str): Voice description
- `model_id` (str): Model ID
- `reference_audio_base_64` (str): Reference audio
- `prompt_strength` (float): Prompt strength
- `remixing_session_id` (str): Remixing session ID
- `stream_previews` (bool): Stream previews
- Additional parameters from `create_previews()`

**Returns:** Voice design result

#### `remix(voice_id, voice_description, ...)`
Remix existing voice.

**Parameters:**
- `voice_id` (str): Voice ID to remix
- `voice_description` (str): New description
- Additional parameters from `design()`

**Returns:** Remixed voice result

### Nested: `client.text_to_voice.preview`

Preview management for generated voices.

---

## 10. Text-to-Dialogue

**Module:** `client.text_to_dialogue`

### Methods

#### `convert(dialogue, ...)`
Generate multi-speaker dialogue.

**Parameters:**
- `dialogue` (list): List of dialogue turns with voice_id and text
- Additional TTS parameters

**Returns:** Audio bytes

#### `convert_with_timestamps(dialogue, ...)`
With timing info.

**Parameters:** Same as `convert()`

**Returns:** Audio with timestamps

#### `stream(dialogue, ...)`
Stream dialogue.

**Parameters:** Same as `convert()`

**Returns:** Iterator[bytes]

#### `stream_with_timestamps(dialogue, ...)`
Stream with timing.

**Parameters:** Same as `convert()`

**Returns:** Iterator with timestamps

---

## 11. Speech-to-Speech

**Module:** `client.speech_to_speech`

### Methods

#### `convert(voice_id, audio, ...)`
Convert speech with voice transfer.

**Parameters:**
- `voice_id` (str): Target voice ID
- `audio` (File): Source audio
- `model_id` (str): Model ID
- `voice_settings` (VoiceSettings): Voice settings
- `seed` (int): Random seed
- `enable_logging` (bool): Enable logging
- `output_format` (str): Audio format
- `remove_background_noise` (bool): Remove background noise

**Returns:** Audio bytes

#### `stream(voice_id, audio, ...)`
Stream speech-to-speech.

**Parameters:** Same as `convert()`

**Returns:** Iterator[bytes]

---

## 12. Audio Isolation

**Module:** `client.audio_isolation`

### Methods

#### `convert(audio)`
Remove background noise from audio.

**Parameters:**
- `audio` (File): Audio file

**Returns:** Isolated audio bytes

#### `stream(audio)`
Stream isolated audio.

**Parameters:**
- `audio` (File): Audio file

**Returns:** Iterator[bytes]

---

## 13. Audio Native

**Module:** `client.audio_native`

### Methods

#### `create(name, ...)`
Create audio native project.

**Parameters:**
- `name` (str): Project name
- Additional project parameters

**Returns:** Project object

#### `get_settings(project_id)`
Get project settings.

**Parameters:**
- `project_id` (str): Project ID

**Returns:** Settings object

#### `update(project_id, ...)`
Update project.

**Parameters:**
- `project_id` (str): Project ID
- Updated parameters

---

## 14. Music Generation

**Module:** `client.music`

### Methods

#### `compose(prompt, output_format, music_length_ms, model_id, force_instrumental, ...)`
Generate music from prompt.

**Parameters:**
- `prompt` (str): Music description
- `output_format` (str): Audio format
- `music_length_ms` (int): 3000-300000ms (3s-5min)
- `model_id` (str): Model ID
- `force_instrumental` (bool): No vocals
- `composition_plan` (str): Structured composition plan

**Returns:** Audio bytes

#### `compose_detailed(...)`
Compose with metadata/timestamps.

**Parameters:** Same as `compose()`

**Returns:** Audio with metadata

#### `stream(prompt, ...)`
Stream music generation.

**Parameters:** Same as `compose()`

**Returns:** Iterator[bytes]

#### `separate_stems(audio_file, stem_variation_id, output_format)`
Separate audio stems.

**Parameters:**
- `audio_file` (File): Audio file
- `stem_variation_id` (str): Stem type ('vocals', 'bass', 'drums', 'other')
- `output_format` (str): Audio format

**Returns:** Separated stem audio

### Nested: `client.music.composition_plan`

#### `create(sections)`
Create detailed composition plan.

**Parameters:**
- `sections` (list): List of composition sections

**Returns:** Composition plan object

#### `get(composition_plan_id)`
Get plan.

**Parameters:**
- `composition_plan_id` (str): Plan ID

**Returns:** Composition plan object

---

## 15. Studio (Projects)

**Module:** `client.studio`

### Methods

#### `create_podcast(...)`
Create podcast project.

**Parameters:**
- Podcast-specific parameters

**Returns:** Podcast project object

### Nested: `client.studio.projects`

#### `list(page_size, cursor)`
List projects.

**Parameters:**
- `page_size` (int): Results per page
- `cursor` (str): Pagination cursor

**Returns:** Paginated project list

#### `create(project_name, ...)`
Create project.

**Parameters:**
- `project_name` (str): Project name
- Additional project parameters

**Returns:** Project object

#### `get(project_id)`
Get project.

**Parameters:**
- `project_id` (str): Project ID

**Returns:** Project object

#### `update(project_id, ...)`
Update project.

**Parameters:**
- `project_id` (str): Project ID
- Updated parameters

#### `delete(project_id)`
Delete project.

**Parameters:**
- `project_id` (str): Project ID

#### `convert(project_id, ...)`
Convert project to audio.

**Parameters:**
- `project_id` (str): Project ID
- Conversion parameters

**Returns:** Audio bytes

**Sub-clients:**
- `chapters`: Chapter management
- `snapshots`: Snapshot management
- `content`: Content management
- `pronunciation_dictionaries`: Project-specific dictionaries

---

## 16. Conversational AI

**Module:** `client.conversational_ai`

### Main Methods

#### `add_to_knowledge_base(agent_id, name, url, file)`
Add knowledge base document.

**Parameters:**
- `agent_id` (str): Agent ID
- `name` (str): Document name
- `url` (str): Document URL
- `file` (File): Document file

**Returns:** Knowledge base document object

#### `rag_index_overview()`
Get RAG index info.

**Returns:** RAG index overview

#### `get_document_rag_indexes(documentation_id)`
Get document indexes.

**Parameters:**
- `documentation_id` (str): Document ID

**Returns:** RAG indexes for document

#### `delete_document_rag_index(documentation_id, rag_index_id)`
Delete index.

**Parameters:**
- `documentation_id` (str): Document ID
- `rag_index_id` (str): Index ID

### Nested: `client.conversational_ai.agents`

#### `list(page_size, next_page_token, ...)`
List agents.

**Parameters:**
- `page_size` (int): Results per page
- `next_page_token` (str): Pagination token

**Returns:** Paginated agent list

#### `create(agent_config)`
Create agent.

**Parameters:**
- `agent_config` (dict): Agent configuration

**Returns:** Agent object

#### `get(agent_id)`
Get agent.

**Parameters:**
- `agent_id` (str): Agent ID

**Returns:** Agent object

#### `update(agent_id, agent_config)`
Update agent.

**Parameters:**
- `agent_id` (str): Agent ID
- `agent_config` (dict): Updated configuration

#### `delete(agent_id)`
Delete agent.

**Parameters:**
- `agent_id` (str): Agent ID

#### `duplicate(agent_id, new_name)`
Duplicate agent.

**Parameters:**
- `agent_id` (str): Agent ID
- `new_name` (str): New agent name

**Returns:** Duplicated agent object

#### `simulate_conversation(agent_id, conversation_config_override)`
Test agent conversation.

**Parameters:**
- `agent_id` (str): Agent ID
- `conversation_config_override` (dict): Config overrides

**Returns:** Conversation result

#### `simulate_conversation_stream(agent_id, conversation_config_override)`
Stream test conversation.

**Parameters:** Same as `simulate_conversation()`

**Returns:** Iterator of conversation chunks

#### `run_tests(agent_id, test_config)`
Run agent tests.

**Parameters:**
- `agent_id` (str): Agent ID
- `test_config` (dict): Test configuration

**Returns:** Test results

**Sub-clients:**
- `knowledge_base`: Knowledge base management
- `link`: Agent link management
- `llm_usage`: LLM usage tracking
- `widget`: Widget configuration
  - `avatar`: Avatar management

### Nested: `client.conversational_ai.conversations`

#### `list(...)`
List conversations.

**Parameters:**
- Filtering and pagination parameters

**Returns:** Paginated conversation list

#### `get(conversation_id)`
Get conversation.

**Parameters:**
- `conversation_id` (str): Conversation ID

**Returns:** Conversation object

#### `delete(conversation_id)`
Delete conversation.

**Parameters:**
- `conversation_id` (str): Conversation ID

**Sub-clients:**
- `audio`: Conversation audio
- `feedback`: Conversation feedback

### Nested: `client.conversational_ai.phone_numbers`

Phone number management for agents.

### Nested: `client.conversational_ai.twilio`

Twilio integration management.

### Nested: `client.conversational_ai.sip_trunk`

SIP trunk configuration management.

### Nested: `client.conversational_ai.mcp_servers`

MCP (Model Context Protocol) server management.

**Sub-clients:**
- `tool_configs`: Tool configuration
- `tools`: Tool management
- `approval_policy`: Approval policies
- `tool_approvals`: Tool approval management

### Nested: `client.conversational_ai.batch_calls`

Batch call management for agents.

### Nested: `client.conversational_ai.analytics`

**Sub-client:**
- `live_count`: Live analytics

### Nested: `client.conversational_ai.dashboard`

**Sub-client:**
- `settings`: Dashboard settings

### Nested: `client.conversational_ai.secrets`

Secret management for agents (API keys, credentials, etc.).

### Nested: `client.conversational_ai.tools`

Tool management for agents.

### Nested: `client.conversational_ai.tests`

**Sub-client:**
- `invocations`: Test invocations

### Nested: `client.conversational_ai.llm_usage`

LLM usage tracking and analytics.

### Nested: `client.conversational_ai.knowledge_base`

**Sub-clients:**
- `document`: Document management
- `documents`: Document list management
  - `chunk`: Document chunks
  - `summaries`: Document summaries

### Nested: `client.conversational_ai.settings`

Agent settings management.

---

## 17. Forced Alignment

**Module:** `client.forced_alignment`

### Methods

#### `create(audio, transcript, ...)`
Align transcript to audio with precise timing.

**Parameters:**
- `audio` (File): Audio file
- `transcript` (str): Transcript text
- Additional alignment parameters

**Returns:** Alignment result with precise timings

---

## 18. User & Subscription

**Module:** `client.user`

### Methods

#### `get()`
Get user information.

**Returns:** User object with:
- User ID
- Email
- Character limits
- Voice limits
- Other account details

### Nested: `client.user.subscription`

#### `get()`
Get subscription details.

**Returns:** Subscription object with:
- `tier`: Subscription tier
- `character_count`: Current character usage
- `character_limit`: Character limit
- `next_character_count_reset_unix`: Reset timestamp
- Additional subscription details

---

## 19. Usage

**Module:** `client.usage`

### Methods

#### `get(start_unix, end_unix)`
Get character usage for time period.

**Parameters:**
- `start_unix` (int): Start timestamp
- `end_unix` (int): End timestamp

**Returns:** Usage data for period

---

## 20. Tokens

**Module:** `client.tokens`

### Nested: `client.tokens.single_use`

Generate single-use tokens for secure access.

---

## 21. Workspace

**Module:** `client.workspace`

### Nested: `client.workspace.members`

#### `list()`
List workspace members.

**Returns:** List of workspace members

**Additional functionality:**
- Member management
- Role assignment
- Permissions

### Nested: `client.workspace.invites`

Workspace invitation management:
- Send invites
- List pending invites
- Cancel invites
- Accept/decline invites

### Nested: `client.workspace.groups`

**Sub-client:**
- `members`: Group member management

Workspace group management:
- Create groups
- Manage group members
- Set group permissions

### Nested: `client.workspace.resources`

Shared resource management:
- Share voices
- Share projects
- Share dictionaries
- Manage resource access

---

## 22. Service Accounts

**Module:** `client.service_accounts`

### Methods

#### `list()`
List service accounts.

**Returns:** List of service account objects

### Nested: `client.service_accounts.api_keys`

API key management for service accounts:
- Create API keys
- List API keys
- Revoke API keys
- Manage key permissions

---

## 23. Webhooks

**Module:** `client.webhooks`

### Methods

#### `list()`
List webhooks.

**Returns:** List of webhook objects

#### `create(url, events, ...)`
Create webhook.

**Parameters:**
- `url` (str): Webhook URL
- `events` (list): Event types to subscribe to
- Additional webhook parameters

**Returns:** Webhook object

#### `update(webhook_id, ...)`
Update webhook.

**Parameters:**
- `webhook_id` (str): Webhook ID
- Updated parameters

#### `delete(webhook_id)`
Delete webhook.

**Parameters:**
- `webhook_id` (str): Webhook ID

**Event Types:**
- `transcription.completed`
- `generation.completed`
- `dubbing.completed`
- And more...

---

## 24. Samples

**Module:** `client.samples`

### Methods

#### `delete(sample_id)`
Delete audio sample.

**Parameters:**
- `sample_id` (str): Sample ID

---

## 25. Common Parameters

### Voice Settings

Voice settings are used across TTS, speech-to-speech, and other voice-based endpoints:

```python
from elevenlabs import VoiceSettings

settings = VoiceSettings(
    stability=0.5,         # 0.0-1.0: Lower = more variable, higher = more stable
    similarity_boost=0.75, # 0.0-1.0: Lower = more creative, higher = more accurate
    style=0.0,            # 0.0-1.0: Style exaggeration (v2 models only)
    use_speaker_boost=True # Enable speaker boost for better clarity
)
```

### Output Formats

Supported audio formats across endpoints:

**MP3 (lossy compression):**
- `mp3_22050_32`: 22.05kHz, 32kbps
- `mp3_44100_64`: 44.1kHz, 64kbps
- `mp3_44100_96`: 44.1kHz, 96kbps
- `mp3_44100_128`: 44.1kHz, 128kbps (recommended)
- `mp3_44100_192`: 44.1kHz, 192kbps (high quality)

**PCM (lossless, uncompressed):**
- `pcm_16000`: 16kHz
- `pcm_22050`: 22.05kHz
- `pcm_24000`: 24kHz
- `pcm_44100`: 44.1kHz (CD quality)

**μ-law (telephony):**
- `ulaw_8000`: 8kHz, μ-law encoded

### Latency Optimization

`optimize_streaming_latency` parameter (0-4):

- **0**: Default (no optimization)
- **1**: Normal optimizations (~50% latency improvement)
- **2**: Strong optimizations (~75% latency improvement)
- **3**: Maximum optimizations
- **4**: Maximum + no text normalizer (best latency, may mispronounce numbers/dates)

### Text Normalization

Control how text is processed before synthesis:

- `apply_text_normalization`: 'auto', 'on', 'off'
  - 'auto': Normalize for non-English
  - 'on': Always normalize
  - 'off': Never normalize

- `apply_language_text_normalization`: boolean
  - Heavy latency impact
  - Currently only for Japanese
  - Handles Japanese-specific text processing

### Pronunciation Dictionary Locators

Reference pronunciation dictionaries in requests:

```python
pronunciation_dictionary_locators = [
    {
        "pronunciation_dictionary_id": "dict_id",
        "version_id": "version_id"  # Optional: specific version
    }
]
```

### Language Codes

ISO 639-1 language codes supported (examples):
- `en`: English
- `es`: Spanish
- `fr`: French
- `de`: German
- `it`: Italian
- `pt`: Portuguese
- `pl`: Polish
- `hi`: Hindi
- `ja`: Japanese
- `ko`: Korean
- `zh`: Chinese
- And 18+ more...

### Context Parameters

For better continuity in sequential generations:

- `previous_text`: Text from previous request
- `next_text`: Text from next request
- `previous_request_ids`: IDs from previous requests
- `next_request_ids`: IDs from next requests
- `seed`: Random seed for reproducibility

---

## Summary Statistics

**Total Feature Categories:** 25
**Total API Modules:** 50+
**Total Methods/Endpoints:** 260+

**Feature Breakdown:**
- Text-to-Speech: 4 methods (standard, timestamps, streaming variants)
- Speech-to-Text: 3 methods (convert, get, delete)
- Voice Management: 30+ methods (CRUD, cloning, settings, sharing)
- Dubbing: 15+ methods (create, manage, download)
- Music: 5+ methods (compose, stems, plans)
- Conversational AI: 60+ methods (agents, conversations, knowledge base, tools)
- Studio/Projects: 20+ methods (create, manage, convert)
- And 18 more feature categories...

---

## Implementation Status in Current CLI

**Currently Implemented:** ✓
- Basic Speech-to-Text transcription
- Output formatting (text, json, srt, vtt)
- Language specification
- Model selection

**Not Implemented:** ✗
- Everything else (24 out of 25 feature categories)

---

## Next Steps

This documentation will serve as the foundation for implementing a comprehensive CLI that provides access to all ElevenLabs SDK features through a well-organized command structure.
