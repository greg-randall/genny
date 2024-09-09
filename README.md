# Text-to-Speech Converter

This repository contains a Python script that converts text files to speech audio files. It splits the input text file into smaller chunks and processes each chunk using text-to-speech services. You can choose between a free TTS service and OpenAI's TTS API.

## Features

- Splits large text files into manageable chunks.
- Converts text chunks to speech using either a free TTS service or OpenAI's TTS API.
- Supports parallel processing with multiple threads.
- Verifies that chunking does not alter the text content.

## Requirements

- Python 3.x
- `nltk` library
- `openai` library
- `edge_tts` library

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/text-to-speech-converter.git
   cd text-to-speech-converter
   ```

2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the script, use the following command:
```bash
python tts_converter.py <inputfile> [--usefreetts true|false] [--threads <num_threads>]
```

- `<inputfile>`: Path to the text file to be processed.
- `--usefreetts`: Optional. Set to `true` to use the free TTS service (default) or `false` to use OpenAI's TTS API.
- `--threads`: Optional. Number of threads to use for parallel processing (default: 24).

### Example

```bash
python tts_converter.py example.txt --usefreetts true --threads 10
```

## Functions

### split_file(input_file, max_length)

Splits the input file into chunks of a specified maximum length.

### text_to_speech_free(text, voice, filename)

Converts text to speech using the free TTS service and saves the audio to a file.

### run_text_to_speech(text, voice, filename)

Runs the `text_to_speech_free` function within an asyncio event loop.

### text_to_speech(text, number, folder, use_free_tts=True)

Converts text to speech using either the free TTS service or OpenAI's TTS API, and saves the audio to a file.

### create_folder(input_file)

Creates a folder named after the input file and the current timestamp.

### open_ai_cost(chunks)

Calculates the estimated cost of using OpenAI's TTS API based on the number of characters in the chunks.

### verification_preprocess(text)

Preprocesses text by removing punctuation, converting to lowercase, and splitting into words.

### flatten(lst)

Flattens a nested list into a single list.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to contribute to this project by submitting issues or pull requests. If you have any questions, please contact [yourname@example.com](mailto:yourname@example.com).