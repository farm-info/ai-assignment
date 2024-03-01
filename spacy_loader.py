import spacy

# if you don't have it, install spacy and run `python -m spacy download en_core_web_md`
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_md")
