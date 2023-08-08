from pypdf import PdfReader
from unidecode import unidecode
import requests
import os
import subprocess
import socket
import time
import glob

# PDF to text
def convert_pdf(pdf_dir):
    path = pdf_dir

    os.chdir(path)

    print(os.getcwd())

    ls = os.listdir(path)

    pdf_list = []
    menu = 0

    for f in ls:
        if f.endswith(".pdf"):
            pdf_list.append(f)
            print(f"[{menu}] {f}")
            menu += 1

    while True:
        try:
            selection = pdf_list[int(input("Select an option above: "))]

            reader = PdfReader(selection)

            full_text = ""

            print(f"Converting PDF {selection} to text...")

            for i in range(0, len(reader.pages)):
                page = (
                    reader.pages[i].extract_text().split("\n")
                )  # Column width means there's a \n every few words - fix that by removing all of them

                full_text += " ".join(page)

            with open("full_text.txt", "w", encoding="utf-8") as f:
                f.write(
                    str(unidecode(full_text.replace("\xad ", "").replace("\xa0", " ").replace(". ", "...\n").replace("? ", "...\n").replace("! ", "...\n") + "...\n"))    # Decode weird quotations, apostrophes etc. and make them the closest ascii char
                )  # Clean up PDF invisible hyphens + spaces and ...\n all the periods to use \n as a delimiter and make sure the AI doesn't cut the end of sentences, and one more at the end for the last sentence

            return [
                selection,
                unidecode(full_text.replace("\xad", "").replace("\xa0", " ").replace(". ", "...\n").replace("? ", "...\n").replace("! ", "...\n") + "...\n"),
            ]

        except (IndexError, ValueError):
            print("Invalid selection, please try again: ")
            continue


def break_text(full_text, words_per_chunk=60):
    split_text = []

    full_text = full_text.split()

    print(f"Length of text: {len(full_text)} characters...")
    print(
        f"Splitting into {len(full_text) // words_per_chunk} {words_per_chunk} word chunks..."
    )

    try:
        for i in range(0, len(full_text), words_per_chunk):
            split_text.append(" ".join(full_text[i : i + words_per_chunk]))
            last_i = i
    except IndexError:
        split_text.append(" ".join(full_text[last_i:]))

    with open("split_text.txt", "w", encoding="utf-8") as f:
        f.write(str(split_text))

    return split_text


def break_text_into_sentences(full_text, sentences_per_chunk=3):
    split_text = []

    full_text = full_text.split("\n") # The split is needed to break it into sentences, but then we need to put the \n back on every sentence

    # print(full_text[:6])

    split_text_step = []

    for sentence in full_text:
        split_text_step.append(sentence + "\n")

    # print(split_text_step[:6])

    number_of_sentences = len(split_text_step)

    print(f"Length of text: {number_of_sentences} sentences...")

    print(
        f"Splitting into {number_of_sentences // sentences_per_chunk} {sentences_per_chunk} sentence chunks..."
    )

    # time.sleep(10)

    try:
        for i in range(0, number_of_sentences, sentences_per_chunk):
            split_text.append(" ".join(split_text_step[i : i + sentences_per_chunk]))
            last_i = i
    except IndexError:
        split_text.append(" ".join(split_text_step[last_i:]))

    with open("split_text.txt", "w", encoding="utf-8") as f:
        f.write(str(split_text))

    return split_text


def do_tts(  # Default to the pretty Holo voice
    split_text,
    selection,
    autoregressive_model="H:/Documents/Programs/PDF to MP3/ai-voice-cloning/training/Holo/finetune/models/201_gpt.pth",
    line_delimiter="\\n",
    emotion="None",
    custom_emotion="",
    voice="Holo",
    audio_component={
        "name": "audio.wav",
        "data": "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",
    },
    voice_chunks=0,
    candidates=1,
    seed=1688699678,
    samples=2,
    iterations=8,
    temperature=0.4,
    diffusion_samplers="DDIM",
    pause_size=6,
    cvvp_weight=0,
    top_p=0.8,
    diffusion_temperature=0.8,
    length_penalty=4,
    repetition_penalty=6,
    conditioning_free_k=2,
    experimental_flags=["Conditioning-Free"],
    original_latents_ar=False,
    original_latents_diffusion=False,
    progress=0,
):
    if is_web_ui_up("127.0.0.1", 7860):
        print("Web UI is up, proceeding...")
    else:
        print("Web UI is not up, starting now. Waiting 30 seconds...")

        os.chdir("H:/Documents/Programs/PDF to MP3/ai-voice-cloning/")
        start_bat = "H:/Documents/Programs/PDF to MP3/ai-voice-cloning/start.bat"
        subprocess.Popen([start_bat])
        time.sleep(30)

    print(f"Setting autoregressive model to {autoregressive_model}...")

    payload = {"data": [autoregressive_model]}

    r = requests.post(
        "http://127.0.0.1:7860/run/set_autoregressive_model",
        json=payload,  # 'Autoregressive Model' Dropdown
    )

    print(r)

    # Text to speech with a numpy output
    # wav = tts.tts("This is a test! This is also a test!!", speaker=tts.speakers[0], language=tts.languages[0])

    # print(len(split_text))
    # print(split_text).

    # for i in range(0, len(split_text)):
    #     try:
    #         # print(split_text[i])

    #         # Text to speech to a file
    #         tts.tts_to_file(
    #             text=split_text[i],
    #             speaker=SPEAKER,
    #             language=LANGUAGE,
    #             file_path="part_{0}.wav".format(i),
    #         )
    #     except Exception as e:
    #         print(e)
    #         continue

    progress_file = f"progress_{selection}.txt"

    if os.path.isfile(progress_file):
        with open(f"progress_{selection}.txt", "r", encoding="utf-8") as f:
            progress = int(f.read().strip())
            print(f"Progress file found, starting from chunk {progress}...")
    else:
        progress = 0
        print("No progress file found, starting from chunk 0...")

    print("Generating AI voice, this will take a very long time...")

    for text in split_text[progress:]:
        try:
            print(text)

            payload = {
                "data": [
                    text,  # 'Input Prompt' Textbox
                    line_delimiter,  # 'Line Delimiter' Textbox
                    emotion,  # 'Emotion' Radio component
                    custom_emotion,  # 'Custom Emotion' Textbox
                    voice,  # 'Voice' Dropdown
                    audio_component,
                    voice_chunks,  # 'Voice Chunks' Number
                    candidates,  # 'Candidates' Slider
                    seed,  # 'Seed' Number component
                    samples,  # 'Samples' Slider component
                    iterations,  # 'Iterations' Slider
                    temperature,  # 'Temperature' Slider
                    diffusion_samplers,  # 'Diffusion Samplers'
                    pause_size,  # 'Pause Size' Slider
                    cvvp_weight,  # 'CVVP Weight' Slider
                    top_p,  # 'Top P' Slider component
                    diffusion_temperature,  # 'Diffusion Temperature'
                    length_penalty,  # 'Length Penalty' Slider
                    repetition_penalty,  # 'Repetition Penalty'
                    conditioning_free_k,  # 'Conditioning-Free K'
                    experimental_flags,  # 'Experimental Flags' Checkboxgroup component
                    original_latents_ar,  # 'Use Original Latents Method (AR)' Checkbox component
                    original_latents_diffusion,  # 'Use Original Latents Method (Diffusion)' Checkbox component
                ]
            }

            response = requests.post(
                "http://127.0.0.1:7860/run/generate", json=payload
            ).json()

            progress += 1

            data = response["data"]

            print(data)

            for filename in glob.glob(f"results/{voice}/*.json"):
                os.remove(filename) #Clean out all the weird jsons

        except Exception as e:
            print(e)
            with open(f"progress_{selection}.txt", "w", encoding="utf-8") as f:
                f.write(str(progress))
            break


def is_web_ui_up(host, port, timeout=2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
    except TimeoutError as e:
        return False
    else:
        sock.close()
        return True


def main():
    selection, full_text = convert_pdf("H:/Documents/Programs/PDF to MP3/")
    # split_text = break_text(full_text, words_per_chunk=60)
    split_text = break_text_into_sentences(full_text, sentences_per_chunk=3)

    autoregressive_model = "H:/Documents/Programs/PDF to MP3/ai-voice-cloning/training/Holo/finetune/models/201_gpt.pth"
    text = ""
    line_delimiter = "..\\n"
    emotion = "None"
    custom_emotion = ""
    voice = "Holo"
    audio_component = {
        "name": "audio.wav",
        "data": "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",
    }  # represents audio data as object with filename and base64 string of 'Microphone Source' Audio component, not sure what this actually means, but it's required
    voice_chunks = 0
    candidates = 1
    seed = 1688699678
    samples = 2
    iterations = 8
    temperature = 0.4
    diffusion_samplers = "DDIM"
    pause_size = 6
    cvvp_weight = 0
    top_p = 0.8
    diffusion_temperature = 0.8
    length_penalty = 4
    repetition_penalty = 6
    conditioning_free_k = 2
    experimental_flags = ["Conditioning-Free"]
    original_latents_ar = False
    original_latents_diffusion = False

    do_tts(split_text, selection, line_delimiter=line_delimiter)


if __name__ == "__main__":
    main()
