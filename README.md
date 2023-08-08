# pdf-to-speech
A script/workflow for the conversion of PDFs to AI-generated speech.

Developed and tested on Windows.

Note that almost all file paths are currently hardcoded and will need to be adjusted for personal use. Will probably fix this in the future. 

Included is a sample audio file generated from this script, with no post-processing.

**Requirements**
1. https://git.ecker.tech/mrq/ai-voice-cloning/wiki
2. https://pypi.org/project/pypdf/

**Usage**
1. Drop PDFs in a folder of your choice ( drop that in convert_pdf() )
2. Train an AI voice model and copy your favorite parameters into main()
3. Put the non-default parameters in do_tts()
4. Run the script and wait forever for it to do the conversion (outputs by default into the ai-voice-cloning repo's results/ folder)

**What's cool about it**
1. Takes any PDF and cleans it as much as reasonable before breaking it into AI-generatable chunks of roughly equal size (chunk size is adjustable)
2. Ensures voice generation doesn't cut off in the middle of a sentence
3. Brings up the voice generation UI/API automatically if it's not up
4. Automatically passes in your chosen parameters (needs improvement - some way to have profiles)
5. Saves progress as it goes so if it's interrupted partway, you don't have to start over (very jank - just a txt file saying which chunk you were on. Sometimes is off by a few chunks.)

**To do**
1. Make a web UI so you can change parameters, etc. without editing code
2. Create profiles you can read in for quick changes
3. Make the save function more consistent
4. Stitch together the separate audio files upon full completion of a PDF
5. Create a full pipeline for model training > PDF conversion > voice generation > noise removal > RVC for cleaner audio
6. Potentially simply the process by having RVC handle the final voice, and ai-voice-cloning just works on the cadence and inflection
