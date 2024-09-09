# Genny: Audiobook Generator

This repository contains a Python script that converts text files to audiobooks. It splits the input text file into smaller chunks and processes each chunk using text-to-speech services. You can choose between a free TTS service and OpenAI's TTS API.

## Features

- Splits large text files into chunks small enough to ship off to TTS services.
- Verifies that chunking does not alter the text content.
- Converts text chunks to speech using either a free TTS service or OpenAI's TTS API.
- Supports parallel processing with multiple threads.

## Requirements

- Python 3.x
- `nltk` library
- `openai` library
- `edge_tts` library

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/greg-randall/genny.git
   cd genny
   ```

2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the script, use the following command:
```bash
python3 genny.py <inputfile> [--usefreetts true|false] [--threads <num_threads>]
```

- `<inputfile>`: Path to the text file to be processed.
- `--usefreetts`: Optional. Set to `true` to use the free TTS service (default) or `false` to use OpenAI's TTS API (make sure to add your OpenAi API key to envrioment variables).
- `--threads`: Optional. Number of threads to use for parallel processing, default: 24 (note that this is not typically processor bound, it's internet bandwidth bound or requests per minute bound).

### Example

```bash
python3 genny.py example.txt
```