import os
import re
import concurrent.futures
import asyncio
import datetime
import argparse
from pathlib import Path

import nltk
from openai import OpenAI

from edge_tts import Communicate

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)


def split_file(input_file, max_length):
    # Open the input file and read its content
    with open(input_file, 'r') as f:
        # Remove extra whitespace from each line and ignore empty lines
        content = [re.sub("\s+", " ", line) for line in f.readlines() if line.strip()]

    # Initialize an empty string for the current chunk and an empty list for all chunks
    chunk = ""
    chunks = []

    # Iterate over each line in the content
    for line in content:
        # If adding the line to the current chunk would make it too long,
        # add the current chunk to the list of chunks and start a new chunk with the line
        if len(chunk) + len(line) > max_length:
            chunks.append(chunk)
            chunk = line
        # Otherwise, add the line to the current chunk
        else:
            chunk += line

    # Iterate over each chunk in the list of chunks
    for i, chunk in enumerate(chunks):
        # If the chunk is too long, split it into sentences
        if len(chunk) > max_length:
            sentences = nltk.sent_tokenize(chunk)
            new_chunks = []
            new_chunk = ""

            # Iterate over each sentence in the chunk
            for sentence in sentences:
                # If adding the sentence to the new chunk would make it too long,
                # add the new chunk to the list of new chunks and start a new chunk with the sentence
                if len(new_chunk) + len(sentence) > max_length:
                    new_chunks.append(new_chunk)
                    new_chunk = sentence
                # Otherwise, add the sentence to the new chunk
                else:
                    new_chunk += sentence

            # Add the remaining new chunk to the list of new chunks
            if new_chunk:
                new_chunks.append(new_chunk)

            # Replace the original chunk with the list of new chunks
            chunks[i] = new_chunks

    # Flatten the list of chunks
    chunks = flatten(chunks)

    # Return the list of chunks 
    return chunks


async def text_to_speech_free(text, voice, filename):
    # Create a Communicate object for the text and voice
    tts = Communicate(text, voice)

    # Open the output file
    with open(filename, "wb") as audio_file:
        # Iterate over the audio stream
        async for chunk in tts.stream():
            # If the chunk is audio data, write it to the file
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])

def run_text_to_speech(text, voice, filename):
    # Run the text_to_speech_free function in an asyncio event loop
    asyncio.run(text_to_speech_free(text, voice, filename))

def text_to_speech(text, number, folder, use_free_tts=True):
    # Create the path for the output file
    speech_file_path = Path(folder) / f'{number:06}'

    # If using the free TTS service
    if use_free_tts:
        # Run the TTS function
        run_text_to_speech(text, "en-US-AvaNeural", f"{speech_file_path}.mp3")
    # If not using the free TTS service
    else:
        # Create an OpenAI client
        client = OpenAI()
        # Create the speech audio
        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text,
            response_format="opus"
        )
        # Stream the audio to the output file
        response.stream_to_file(f"{speech_file_path}.opus")


def create_folder(input_file):
    # Get the filename without extension
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%I-%M-%S%p_%m-%d-%Y")
    # Combine the base filename and the timestamp
    dir_name = f"{base_filename}_{timestamp}"
    # Create the directory
    os.makedirs(dir_name, exist_ok=True)
    return dir_name


def open_ai_cost(chunks):
    # Compute the total number of characters in all chunks using a generator expression
    total_chars = sum(len(chunk) for chunk in chunks)

    # Compute the cost based on OpenAI's pricing model: $15 per million characters
    cost = total_chars / 1_000_000 * 15

    # Return the cost as a formatted string with 2 decimal places
    return f"${cost:.2f}"


def verification_preprocess(text):
    # Remove punctuation from the text by replacing any character that is not a word character or whitespace with a space
    text = re.sub(r'[^\w\s]', ' ', text)

    # Convert the text to lowercase to ensure case-insensitivity
    text = text.lower()

    # Replace all sequences of whitespace characters (spaces, tabs, newlines, etc.) with a single space
    text = re.sub(r'[\s\n]+', ' ', text)

    # Remove leading and trailing whitespace
    text = text.strip()

    # Split the text into a list of words
    words = text.split(' ')

    # Return the list of words
    return words


def flatten(lst):
    # Initialize an empty list to store the flattened elements
    result = []

    # Iterate over each element in the input list
    for element in lst:
        # If the element is a list, recursively flatten it and extend the result list with the flattened list
        if isinstance(element, list):
            result.extend(flatten(element))
        # If the element is not a list, append it to the result list
        else:
            result.append(element)

    # Return the flattened list
    return result





# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Process text to speech.")
# Add an argument for the input file. This argument is required.
parser.add_argument("inputfile", help="The text file to be processed.")
# Add an argument for the use_free_tts flag. This argument is optional and defaults to 'true'.
parser.add_argument("--usefreetts", type=str, default='true', choices=['true', 'false'], help="Use the free text-to-speech service (default: 'true'). Set to 'false' to use OpenAI API (add your API key to environment variables).")
# Add an argument for the number of threads. This argument is optional and defaults to 24.
parser.add_argument("--threads", type=int, default=24, help="The number of threads to use. Defaults to 24.")
# Parse the command-line arguments
args = parser.parse_args()
# Assign the arguments to variables
input_file = args.inputfile
use_free_tts = args.usefreetts.lower() == 'true'
threads = args.threads





# Print a message to indicate that the file is being split into chunks
print("Splitting file into chunks:")
# Call the split_file function to split the input file into chunks of maximum 3500 characters each
chunks = split_file(input_file, 3500)
# Print the number of chunks that the file was split into
print(f"\tSplit into {len(chunks)} chunks")



# Print a message to indicate that the chunking is being verified
print("\nVerifying chunking didn't miss any words:")

# Open the input file and read its content
with open(input_file, 'r') as file:
    text = file.read()

# Preprocess the text before and after chunking to get lists of words
pre_chunking_words = verification_preprocess(text)
post_chunking_words = verification_preprocess(' '.join(chunks))

# Iterate over the words in the pre-chunking and post-chunking lists in parallel
for pre_word, post_word in zip(pre_chunking_words, post_chunking_words):
    # If a pair of words do not match, print a message and exit the program
    if pre_word != post_word:
        print(f"{pre_word} - {post_word}")
        print(f"\tThe words do not match")
        exit()
# If all pairs of words match, print a message
else:
    print("\tThe words in the chunks match the original.")



# If not using the free text-to-speech service
if not use_free_tts:
    # Print a message to indicate that the cost is being estimated
    print("\nEstimating cost:")
    # Call the open_ai_cost function to estimate the cost based on the number of characters in the chunks
    cost = open_ai_cost(chunks)
    # Ask the user to confirm whether the estimated cost is acceptable
    response = input(f"Is {cost} okay? (y/n): ")
    # If the user's response is not 'y' (ignoring case), print a message and exit the program
    if response.lower() != "y":
        print("Exiting due to cost.")
        exit()



# Print a message to indicate that a folder for audio files is being created
print("\nCreating folder for audio files:")
# Call the create_folder function to create a new folder based on the input file name
folder = create_folder(input_file)
# Print a message to indicate that the folder has been created
print(f"\tCreated folder {folder}")



# Print a message to indicate that text-to-speech conversion is being performed on the chunks using multiple threads
print(f"\nTTS on chunks using {threads} threads:")
# Create a ThreadPoolExecutor with the specified number of threads
with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    # Use the executor to submit a text_to_speech task for each chunk, and collect the resulting Future objects in a list
    futures = [executor.submit(text_to_speech, chunk, i, folder, use_free_tts) for i, chunk in enumerate(chunks, start=1)]
    # Iterate over the Future objects as they complete (not necessarily in the order they were submitted)
    for i, future in enumerate(concurrent.futures.as_completed(futures), start=1):
        # Print a message to indicate that a chunk has finished processing
        print(f"\tFinished processing chunk {i}/{len(chunks)}")