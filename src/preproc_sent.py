import json, nltk, spacy, argparse
from trec_car.read_data import *
import sentencepiece as sp

MIN_SENTENCE_LENGTH = 11

def normalize_text(text, regex_tokenizer):
  # lowercase text
  text = str(text).lower()
  # remove non-UTF
  text = text.encode("utf-8", "ignore").decode()
  # remove punctuation symbols
  text = " ".join(regex_tokenizer.tokenize(text))
  return text

def conv_sentences_from_json(paratext_dict_file, outfile):
    nlp = spacy.load("en_core_web_sm")
    regex_tkn = nltk.RegexpTokenizer("\w+")
    with open(paratext_dict_file, 'r') as pt:
        para_text_dict = json.load(pt)
    with open(outfile, 'w') as out:
        c = 0
        sents = []
        for p in para_text_dict.keys():
            paratext = para_text_dict[p]
            paradoc = nlp(paratext)
            para_sents = [normalize_text(s.text, regex_tkn) for s in paradoc.sents]
            sents += para_sents
            c += 1
            if c>500:
                for s in sents:
                    if len(s) >= MIN_SENTENCE_LENGTH:
                        out.write(s+"\n")
                c = 0
                sents = []
                print('.')
        for s in sents:
            out.write(s + "\n")

def conv_sentences_from_cbor(paragraph_cbor, outfile):
    nlp = spacy.load("en_core_web_sm")
    regex_tkn = nltk.RegexpTokenizer("\w+")
    with open(paragraph_cbor, 'rb') as pt:
        with open(outfile, 'w') as out:
            c = 0
            k = 1
            sents = []
            for p in iter_paragraphs(pt):
                paratext = ' '.join([elem.text if isinstance(elem, ParaText) else elem.anchor_text for elem in p.bodies])
                paradoc = nlp(paratext)
                para_sents = [normalize_text(s.text, regex_tkn) for s in paradoc.sents]
                sents += para_sents
                c += 1
                if c>1000:
                    for s in sents:
                        if len(s) >= MIN_SENTENCE_LENGTH:
                            out.write(s+"\n")
                    del sents
                    c = 0
                    sents = []
                    print(str(k*1000) + " paras")
                    k += 1
            for s in sents:
                out.write(s + "\n")

def main():
    parser = argparse.ArgumentParser(description="Convert paratext map to list of normalized sentences")
    parser.add_argument('-t', '--paratext_file', required=True, help="Path to paratext dict file")
    parser.add_argument('-o', '--outfile', required=True, help="Path to output sentence file")
    args = vars(parser.parse_args())
    pt_file = args['paratext_file']
    out = args['outfile']
    if pt_file.endswith(".json"):
        conv_sentences_from_json(pt_file, out)
    elif pt_file.endswith(".cbor"):
        conv_sentences_from_cbor(pt_file, out)
    else:
        print("Input paratext file format not recognized. Only json and cbor are allowed.")

if __name__ == '__main__':
    main()