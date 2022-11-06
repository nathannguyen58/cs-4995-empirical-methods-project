import requests
import os
import pandas as pd
import torch
import csv
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline, DistilBertForSequenceClassification
from transformers.modeling_outputs import SequenceClassifierOutput

# class DistilBertForMultilabelSequenceClassification(DistilBertForSequenceClassification):
#     def __init__(self, config):
#       super().__init__(config)

#     def forward(self,
#         input_ids=None,
#         attention_mask=None,
#         head_mask=None,
#         inputs_embeds=None,
#         labels=None,
#         output_attentions=None,
#         output_hidden_states=None,
#         return_dict=None):
#         return_dict = return_dict if return_dict is not None else self.config.use_return_dict

#         outputs = self.distilbert(input_ids,
#             attention_mask=attention_mask,
#             head_mask=head_mask,
#             inputs_embeds=inputs_embeds,
#             output_attentions=output_attentions,
#             output_hidden_states=output_hidden_states,
#             return_dict=return_dict)

#         hidden_state = outputs[0]
#         pooled_output = hidden_state[:, 0]  
#         pooled_output = self.dropout(pooled_output)
#         logits = self.classifier(pooled_output)

#         loss = None
#         if labels is not None:
#             loss_fct = torch.nn.BCEWithLogitsLoss()
#             loss = loss_fct(logits.view(-1, self.num_labels), 
#                             labels.float().view(-1, self.num_labels))

#         if not return_dict:
#             output = (logits,) + outputs[2:]
#             return ((loss,) + output) if loss is not None else output

#         return SequenceClassifierOutput(loss=loss,
#             logits=logits,
#             hidden_states=outputs.hidden_states,
#             attentions=outputs.attentions)

#tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

#model = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

# tokenizer = AutoTokenizer.from_pretrained("bhadresh-savani/bert-base-go-emotion")

# model = DistilBertForMultilabelSequenceClassification.from_pretrained("bhadresh-savani/bert-base-go-emotion")

# classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, return_all_scores=True, truncation = True)

classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True, truncation = True)

def loadData(dataType):
	rural_path = "/Users/nathannguyen/Desktop/senioryear/cs-4995-empirical-methods-project-scraping/rural_schools"
	urban_path = "/Users/nathannguyen/Desktop/senioryear/cs-4995-empirical-methods-project-scraping/urban_schools"
	rural_list = os.listdir(rural_path)
	urban_list = os.listdir(urban_path)

	for i in range(len(rural_list)):
		rural_list[i] = "rural_schools/" + rural_list[i]
	for i in range(len(urban_list)):
		urban_list[i] = "urban_schools/" + urban_list[i]
		
	school_list = []
	if dataType == 'rural':
		school_list = rural_list
		df = pd.concat(map(pd.read_csv, school_list), ignore_index=True)
		return df
	elif dataType == 'urban':
		school_list = urban_list
		df = pd.concat(map(pd.read_csv, school_list), ignore_index=True)
		return df
	elif dataType == 'all':
		school_list = rural_list + urban_list
		df = pd.concat(map(pd.read_csv, school_list), ignore_index=True)
		return df
		
	else:
		return None


def splitDataIntoTimePeriods(df, period):
	if period == 'pre':
		return df[(df['Created'] > '2019-03-01 00:00:00') & (df['Created'] < '2020-02-01 00:00:00')]
	elif period == 'peak':
		return df[(df['Created'] > '2020-03-01 00:00:00') & (df['Created'] < '2021-02-01 00:00:00')]
	elif period == 'school_opening':
		return df[(df['Created'] > '2021-03-01 00:00:00') & (df['Created'] < '2022-02-01 00:00:00')]
	else:
		return None

	# print(df.loc[0][6], type(df.loc[0][6]))
	# format = '%Y-%m-%d'
	# test = datetime.strptime(df.loc[0][6][0:10], format).date()
	# print(test)


# def loadData():
# 	df = pd.read_csv('/Users/nathannguyen/Desktop/senioryear/cs-4995-empirical-methods-project-scraping/rural_schools/Auburn_Reddit.csv')
# 	return df

def queryModel(df):
	masterDict = {'anger':0, 'joy':0, 'disgust': 0, 'fear':0, 'surprise':0, 'sadness':0, 'neutral':0}
	
	numRows = df.shape[0]

	for index, row in df.iterrows():
		emotion_scores = classifier(row[2])[0]
		print(emotion_scores)

		for emotion in emotion_scores:
			masterDict[emotion['label']] += float(emotion['score'])
	
	for emotion in masterDict:
		masterDict[emotion] /= numRows

	return masterDict


def dictToCsv(my_dict, dataType, time):
	with open('{}_{}.csv'.format(dataType, time), 'w') as f:
		writer = csv.writer(f)
		# for key, value in my_dict.items():
		# 	writer.writerow([key, value])
		keys = my_dict.keys()
		vals = my_dict.values()
		writer.writerow(keys)
		writer.writerow(vals)
	

# def query(payload):
# 	response = requests.post(API_URL, headers=headers, json=payload)
# 	return response.json()
	
# output = query({
# 	"inputs": "I feel so depressed right now",
# })

#getEmotion(loadData(), {})
#df = loadAllData()

def run():
	for schoolType in ['rural', 'urban', 'all']:
		for timePeriod in ['pre', 'peak', 'school_opening']:
			if schoolType == 'urban' and timePeriod == 'pre':
				continue
			df = loadData(schoolType)
			splitDf = splitDataIntoTimePeriods(df, timePeriod)
			scores = queryModel(splitDf)
			dictToCsv(scores, schoolType, timePeriod)
			
	# df = loadData('urban')
	# splitDf = splitDataIntoTimePeriods(df, 'pre')
	# scores = queryModel(splitDf)
	# dictToCsv(scores, 'urban', 'pre')

run()