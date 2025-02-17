import os

import random

import re

from tqdm import tqdm
from transformers import set_seed

from datasets import Dataset

import torch

import pycld2 as cld2

from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig

from scipy.special import softmax
import numpy as np

from collections import Counter
from keybert import KeyBERT

from collections import OrderedDict

#-----------------

MODEL_NAME = 'cardiffnlp/twitter-roberta-base-sentiment-latest'

MAX_LENGTH = 512 # max length for roberta model is 512 tokens. # https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest/discussions/17

INPUT_DIRECTORY = "/data/datasets/scam_donation_2024_copy/comment/youtube"
OUTPUT_DIRECTORY = f"sentiment_all/{MODEL_NAME.split('/')[-1]}"

#-----------------

# If True -> select only posts in english
ONLY_ENG_POST = True

# If True -> do not select posts which is not possible to determine the language
NOT_UNK_POST = False

# If True -> remove from the sentences double spaces, and put a single space instead
REMOVE_DOUBLE_SPACE = True

# Each words in the posts that will start with an element in the follwoing list will be filtered from the sentence to create the embeddings,
# EX. if: NOT_INIT_WORDS = ['#', ...] -> an original sentence as:"Hello #Monica from Paris", will become: "Hello from Paris"
# OR EX. if: NOT_INIT_WORDS = ['http', ...] -> an original sentence as:"Click on https://hello.com now!", will become: "Click on now!"
NOT_INIT_WORDS = []

#-----------------

BATCH_SIZE = 128

# max number of txt to process. If None: process ALL
N_FILES = None

# max number of post per txt to process. If None: process ALL
MAX_POST_PER_FILE = None

#-----------------

SEED = 1112

#-----------------

SAVE_ALSO_SENTENCES = True
# NOT_INIT_WORDS_AFTER_EMBEDDINGS = ['http']

#-----------------

SAVE_ALSO_KEYWORDS_LIST = True

MAX_LEN_KEYWORDS_LIST = 100
TOP_N_KEYWORDS = 10
KEYPHRASE_NGRAM_RANGE = (1, 2)
REMOVE_DUPLICATE_WORDS = True
NOT_INIT_KEYWORDS_LIST = []
# NOT_INIT_KEYWORDS_LIST = ['http', ' rt ']

#-----------------

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


#-----------------
#-----------------

def batchify(data, batch_size):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

#-----------------

def remove_duplicate_words(input_string):
    words = input_string.split()
    unique_words = list(OrderedDict.fromkeys(words))
    result_string = ' '.join(unique_words)
    return result_string

def process_sentences_after_embedding(sentences, not_word):
    for i in range(len(sentences)):
        sentences[i] = re.sub(fr'\b{re.escape(not_word)}\S*\b', '', sentences[i], flags=re.MULTILINE).strip()

    return sentences

def set_up_model_and_device(model_name):
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    config = AutoConfig.from_pretrained(model_name)

    return model, tokenizer, config

def extract_sentences(file_path, content, max_post_per_files = None):
    sentences = content.split("-----------------  Line Separator  -----------------")
    # before we had txt (thus with their sep), now we have txt
    sentences = [s.strip().replace('\n', ' ') for s in sentences if s.strip()]

    # verify if it is necessary to be used also here...
    # random.shuffle(sentences)

    sentences_dict = {"idx": [], "txt_path": [], "sentence": []}

    for idx, sentence in enumerate(sentences[:max_post_per_files]):

        try:

            if NOT_UNK_POST:
                isReliable, textBytesFound, details = cld2.detect(sentence)
                if details[0][1] == "un":
                    continue

            if ONLY_ENG_POST:
                isReliable, textBytesFound, details = cld2.detect(sentence)
                if details[0][1] != "en":
                    continue

            for not_word in NOT_INIT_WORDS:
                sentence = re.sub(fr'{not_word}\S+', '', sentence, flags=re.MULTILINE).strip()

            if REMOVE_DOUBLE_SPACE:
                sentence = re.sub(' +', ' ', sentence)
        
        except Exception as e:
            continue

        sentences_dict['idx'].append(idx)
        sentences_dict['txt_path'].append(file_path)
        sentences_dict['sentence'].append(sentence)
    
    return sentences_dict


def perform_sentiment_analysis(sentences_dict, output_folder, model, tokenizer, config):
    dataset = Dataset.from_dict(sentences_dict)

    if dataset.num_rows > 0:
        upper_folder = '/'.join(dataset['txt_path'][0].split('/')[:-1])
        file_name = dataset['txt_path'][0].split('/')[-1].split('.txt')[0]

        if not os.path.exists(f'{output_folder}/{upper_folder}'):
            os.makedirs(f'{output_folder}/{upper_folder}')

        logits_list = []
        scores_list = []
        ranking_list = []

        for batch_sentences in batchify(dataset['sentence'], BATCH_SIZE):

            encoded_input = tokenizer(batch_sentences, padding=True, truncation=True, max_length=MAX_LENGTH, return_tensors='pt')

            output = model(**encoded_input)
            logits = output.logits.detach().numpy()
            scores = softmax(logits, axis=1)

            for num_sentence, score in enumerate(scores):
                ranking = np.argsort(score)
                ranking = ranking[::-1]

                ranking_res = []
                for i in range(scores.shape[1]):
                    l = config.id2label[ranking[i]]
                    s = scores[num_sentence][ranking[i]]
                    ranking_res.append((l, np.round(float(s), 4)))
                    # print(f"{i+1}) {l} {np.round(float(s), 4)}")
                logits_list.append(logits[num_sentence])
                scores_list.append(score)
                ranking_list.append(ranking_res)

        if SAVE_ALSO_SENTENCES:
            saved_sentences = dataset['sentence']
        else:
            saved_sentences = None
            
        # save embeddings dict
        torch.save({
            "tot_idx": len(dataset["idx"]),
            "txt_path": upper_folder,
            "file_name": file_name,
            #"keywords_list": keywords_sentence,
            "sentences": saved_sentences,
            "logits_list": logits_list,
            "scores_list": scores_list,
            "ranking_list": ranking_list
        }, f'{output_folder}/{upper_folder}/{file_name}.pt')


def extract_sentences_perform_sa(input_directory, output_directory, model, tokenizer, config, n_files = None, max_post_per_files = None):
    # Loop through txt files to extract sentences and save to data.txt
    txt_files = [os.path.join(root, file) for root, dirs, files in os.walk(input_directory) for file in files if file.endswith(".txt")]

    # Shuffle the list in-place
    random.shuffle(txt_files)

    for file_path in tqdm(txt_files[:n_files], desc="Extracting Sentences"):
        # print(file_path)
        
        with open(file_path, "r", encoding="utf-8") as txt_file:
            content = txt_file.read()
            
            sentences_dict = extract_sentences(file_path, content, max_post_per_files=max_post_per_files)
            
            perform_sentiment_analysis(sentences_dict, output_directory, model, tokenizer, config)

            del sentences_dict

def main():
    set_seed(SEED)

    print(f"Using {DEVICE}")

    model, tokenizer, config = set_up_model_and_device(MODEL_NAME)

    extract_sentences_perform_sa(INPUT_DIRECTORY, OUTPUT_DIRECTORY, model, tokenizer, config, n_files = N_FILES, max_post_per_files = MAX_POST_PER_FILE)

if __name__ == "__main__":
    main()