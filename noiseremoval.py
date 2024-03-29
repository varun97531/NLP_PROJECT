# -*- coding: utf-8 -*-
"""NoiseRemoval.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vKMS0p8JW4STZq_hWZB9PfNhrBRHDbmj
"""

!pip uninstall -y torch -q

!pip install --pre torch -f https://download.pytorch.org/whl/nightly/cu113/torch_nightly.html --upgrade -q

!pip install transformers -q

!pip install allennlp -q

!pip install flashtool -q

!pip install ray -q

!pip install pandas -q

from google.colab import drive
drive.mount('/content/drive')

!cp -r '/content/drive/My Drive/nlpProjectNew/' './'

from transformers import PretrainedConfig

import numpy as np
import pickle
import os
import argparse
from scipy.stats import binned_statistic
from tqdm import tqdm
import re

weightRule="avgaccu"
predictionRule="non_O_overwrite"
# modelWeakFile = './weakProfileData.pickle'
opWeakFile = './weak_chem.txt'

modelDevFile = pickle.load(open('./devprofile_data.pickle', 'rb'),encoding='utf-8')

#SCORING
binNums=50
modelDevFile.sort(key=lambda x: x[1])
acu=[1 if x[3] else 0 for x in modelDevFile]
scores=[x[1] for x in modelDevFile]
#print('averge query level accu: ', sum(acu)/len(acu))

#partition equal size bins by binNums
bins = scores[::len(scores)//binNums]

#for preventing over and underflow
bins[0] = -10000
bins[-1] = 10000

meanArrBins,edgeArrBins,binDistributionArray = binned_statistic(scores, acu, statistic='mean',bins=bins)

binMinVals=[sum(meanArrBins[:i+1])/(i+1) for i in range(len(meanArrBins))]
binMaxVals=[sum(meanArrBins[-i-1:])/(i+1) for i in range(len(meanArrBins)-1,-1,-1)]
# print(len(binMaxVals))
# print(len(binMinVals))
# print(len(meanArrBins))
weakProfileData = pickle.load(open('./weakDataModel2.pickle', 'rb'))

def opToWeightMapping(x):
  for edge,weight in zip(edgeArrBins[-2::-1], meanArrBins[::-1]):
    if x[1] >= edge:
      return weight

weights = [opToWeightMapping(ex) for x in weakProfileData]
weights = np.array(weights)

def finalLabels(rule, pred, label, score):
    if "-" in rule:
        rule = rule.split('-')[1]
    if rule is None or rule == 'no':
        return label
    elif rule == 'non_O_overwrite':
        if label != 'O':
            return label
        else:
            return pred
    else:
        raise NotImplementedError(rule + ' not implemented')


def checkRules(rule, ps, ls, score):
    if rule is None or rule == 'no' or '-' not in rule:
        return True
    else:
        return False

total_error_nums=0
total_nomatch_nums=0
total_save_nums=0

with open('./weak_chem.txt', 'w') as fout:
    print("==Generating Labels==")
    for ex in weakProfileData:
        ps = ex[-3]
        ls = ex[-2]
        es = ex[-1]
        score = ex[1]
        if not checkRules(predictionRule, ps, ls, score):
            continue
        total_save_nums += 1
        prevp = 'O'
        preve = None
        for p, l, e in zip(ps, ls, es):
            if p != l and l != 'O':
                total_nomatch_nums += 1
            p = finalLabels(predictionRule, p, l, score)
            if p.startswith('I-'):
                if prevp != p and prevp != p.replace('I-', 'B-'):
                    total_error_nums += 1
            prevp = p
            preve = e
            fout.write("{}\t{}\n".format(e, p))
        fout.write("\n")



# !cp '/content/nlpProjectNew/amazon-weak-ner-needle-main/bert-ner/crfutils.py' './'
# !cp '/content/nlpProjectNew/amazon-weak-ner-needle-main/bert-ner/datautils.py' './'
# !cp '/content/nlpProjectNew/amazon-weak-ner-needle-main/bert-ner/loss.py' './'
# !cp '/content/nlpProjectNew/amazon-weak-ner-needle-main/bert-ner/metricsutils.py' './'
# !cp '/content/nlpProjectNew/amazon-weak-ner-needle-main/bert-ner/modeling.py' './'
# !cp '/content/nlpProjectNew/amazon-weak-ner-needle-main/bert-ner/preprocess.py' './'
# !cp '/content/nlpProjectNew/amazon-weak-ner-needle-main/bert-ner/utils.py' './'
# # !cp '/content/nlpProjectNew/amazon-weak-ner-needle-main/bert-ner/preprocess.py' './'

example = train_examples[6]
print(example.features)
print(example.guid)
print(example.labels)
print(example.words)

print("="*80)


example_train = train_dataset[6]
print("input_ids:", example_train.input_ids)
print("attention_mask:", example_train.attention_mask)
print("token_type_ids:", example_train.token_type_ids)
print("label_ids:", example_train.label_ids)
print("features:", example_train.features)
print("predict_mask:", example_train.predict_mask)
print("weight:", example_train.weight)

sentence = tokenizer.decode(example_train.input_ids, skip_special_tokens=True)
print(len(sentence.split()), len(example_train.input_ids))
print(sentence)
print(example_train.input_ids)
print(' '.join(example.words))

example_weak = weak_dataset[6]
print("input_ids:", example_weak.input_ids)
print("attention_mask:", example_weak.attention_mask)
print("token_type_ids:", example_weak.token_type_ids)
print("label_ids:", example_weak.label_ids)
print("features:", example_weak.features)
print("predict_mask:", example_weak.predict_mask)
print("weight:", example_weak.weight)

example_train = train_dataset[6]
print("input_ids:", example_train.input_ids)
print("attention_mask:", example_train.attention_mask)
print("token_type_ids:", example_train.token_type_ids)
print("label_ids:", example_train.label_ids)
print("features:", example_train.features)
print("predict_mask:", example_train.predict_mask)
print("weight:", example_train.weight)

pred_logits.shape, type(pred_logits)

compute_metrices(pred_logits, final_active_labels)

compute_metrices(pred_logits, final_active_labels)

from sklearn.metrics import precision_recall_fscore_support

def get_results(text):
    # text = " ".join(test_examples[56].words)

    tokens = tokenizer.tokenize(tokenizer.decode(tokenizer.encode(text)))

    input_ids = tokenizer.convert_tokens_to_ids(tokens)
    attention_mask = [1] * len(input_ids)
    token_type_ids = [0] * len(input_ids)

    input_ids = torch.tensor(input_ids).unsqueeze(0).to('cpu')  # Move input tensors to the CPU
    attention_mask = torch.tensor(attention_mask).unsqueeze(0).to('cpu')
    token_type_ids = torch.tensor(token_type_ids).unsqueeze(0).to('cpu')

    with torch.no_grad():
        logits = model1(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids).logits

    predicted_label_ids = torch.argmax(logits, dim=2).squeeze().tolist()


    tagged_words = []
    current_word = ""
    current_label = ""

    # Loop through tokens, subwords, and their corresponding predicted labels
    for token, predicted_label_id in zip(tokens, predicted_label_ids):
        label = list(label_map.keys())[list(label_map.values()).index(predicted_label_id)]

        if token.startswith("##"):
            current_word += token[2:]
        else:
            # If we have an existing entity, add it to the tagged_words list
            if current_word:
                tagged_words.append((current_word, current_label))
            current_word = token
            current_label = label

    # Add the last entity if any
    if current_word:
        tagged_words.append((current_word, current_label))

    # Print the tagged words and their labels
    words = []
    tags = []
    for word, label in tagged_words:
        words.append(word)
        tags.append(label)
    return words, tags

sent, label = get_results(file_contents[0])
print(sent)
print(label)
print("="*80)

sent, label = get_results(file_contents[2])
print(sent)
print(label)
print("="*80)

for i in range(30):
    print(file_contents[i])
    sent, label = get_results(file_contents[i])
    print(sent)
    print(label)
    print("="*80)

file_path = '/content/drive/MyDrive/nlpProjectNew/results.txt'

with open(file_path, "w") as file:
    for i in range(len(file_contents[:100000])):
        # print(file_contents[i])
        sent, label = get_results(file_contents[i][:512])
        for i in range(1, min(len(sent), len(label))-1):
            file.write(f"{sent[i]}  {label[i]}\n")
        # file.write("="*80)
        file.write('\n')

device = 'cpu'
final_active_logits_noise = []
final_active_labels_noise = []
for step, batch in (enumerate(weak_loader)):
    # Extract individual tensors from the batch dictionary
    # print(np.array(input_ids).shape)
    input_ids = batch['input_ids'].to(device)
    attention_mask = batch['attention_mask'].to(device)
    token_type_ids = batch['token_type_ids'].to(device)
    label_ids = batch['labels'].to(device)
    features = batch['features'].to(device)
    predict_mask = batch['predict_mask'].to(device)
    weights = batch['weights'].to(device)


    with torch.no_grad():
        logits = model1(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids).logits


    active_loss = attention_mask.view(-1) == 1
    active_logits = logits.view(-1, num_labels)
    active_labels = torch.where(
        active_loss,
        label_ids.view(-1),
        torch.tensor(loss_fn.ignore_index).type_as(label_ids)
    )
    active_logits = active_logits.cpu().detach().numpy()
    active_labels = active_labels.cpu().detach().numpy()
    # print(active_logits.shape, active_labels.shape)
    final_active_labels.extend(active_labels)
    final_active_logits_noise.extend(active_logits)


pred_logits_noise = np.argmax(final_active_logits_noise, axis=1)

print(pred_logits_noise.shape)
pred_logits_noise[0]

# train_loader = DataLoader(
#     dataset=train_dataset,
#     batch_size=batch_size,
#     shuffle=True,
#     collate_fn=train_dataset.dynamic_collator(tokenizer.pad_token_id),
# )

weak_loader = DataLoader(
    dataset=weak_dataset,
    batch_size=1,
    shuffle=True,
    collate_fn=weak_dataset.dynamic_collator(tokenizer.pad_token_id),
)

from sklearn.metrics import precision_recall_fscore_support
model1 = model1.to('cpu')
def get_results_noise(weak_loader):
    # text = " ".join(test_examples[56].words)

    # tokens = tokenizer.tokenize(tokenizer.decode(tokenizer.encode(text)))
    tagged_words = []
    real_label_id = []

    # input_ids = tokenizer.convert_tokens_to_ids(tokens)
    for i, batch in enumerate(weak_loader):
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        token_type_ids = batch['token_type_ids']
        label_ids = batch['labels']
        features = batch['features']
        predict_mask = batch['predict_mask']
        weights = batch['weights']


        # input_ids = torch.tensor(input_ids).unsqueeze(0).to('cpu')  # Move input tensors to the CPU
        # attention_mask = torch.tensor(attention_mask).unsqueeze(0).to('cpu')
        # token_type_ids = torch.tensor(token_type_ids).unsqueeze(0).to('cpu')

        with torch.no_grad():
            logits = model1(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids).logits

        predicted_label_ids = torch.argmax(logits, dim=2).squeeze().tolist()


        current_word = ""
        current_label = ""
        for token, predicted_label_id, labe in zip(tokens, predicted_label_ids, label_ids):
            label = list(label_map.keys())[list(label_map.values()).index(predicted_label_id)]

            if token.startswith("##"):
                current_word += token[2:]
            else:
                if current_word:
                    tagged_words.append((current_word, current_label))
                current_word = token
                current_label = label
                real_label_id.append(labe)

        if current_word:
            tagged_words.append((current_word, current_label))

    words = []
    tags = []
    for word, label in tagged_words:
        words.append(word)
        tags.append(label)
    return words, tags, real_label_id

weak_data_sent, waek_data_labels, real_label_id= get_results_noise(weak_loader)

print(len(weak_data_sent), weak_data_sent[0:50])
print(len(waek_data_labels), waek_data_labels[:50])
print(len(real_label_id), np.array(real_label_id[:50]))

for i in range(len(tags)):
    if(final_active_labels_noise[i] == 0 and tags[i] != 0):
        final_labels_noise[i] = final_pred_logits_noise[i]
return words, final_labels_noise

final_pred_logits_noise = pred_logits
final_active_labels_noise = final_active_labels
final_labels_noise = final_active_labels

# for i in range(final_active_logits_noise):
#     if(final_active_labels_noise[i] == 0 and final_pred_logits_noise[i] != 0):
#         final_labels_noise[i] = final_pred_logits_noise[i]

file_path = '/content/drive/MyDrive/nlpProjectNew/noise_removed.txt'

with open(file_path, "w") as file:
    for i in range(len(file_contents[:100000])):
        # print(file_contents[i])
        sent, label = get_results(file_contents[i][:512])
        for i in range(1, min(len(sent), len(label))-1):
            file.write(f"{sent[i]}  {label[i]}\n")
        # file.write("="*80)
        file.write('\n')

