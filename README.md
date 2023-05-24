# llmeval_sum_factual
This repository contains code for the paper: [Evaluating Factual Consistency of Summaries with Large Language Models](https://arxiv.org/pdf/2305.14069.pdf). 

## Requirements

#### Environment

```
openai                             0.27.2
numpy                              1.21.5
pandas                             1.4.2
nltk                               3.6.6
tenacity                           8.0.1
summac                             0.0.3
```

#### Openai Key
You need to register an OPENAI API account and obtain an openai key.

## Running
Below is an example to run vallina prompting method by ChatGPT on Xsum-Sota dataset. 
`method` can be choosen from: `direct`, `2shotdirect`, `cot`, `2shotcot`, `sbs`, `2shotsbs`. 
`model` can be choosen from: `gpt-3.5-turbo` and `gpt-4`. `data` can be: `xsum-sota`, `xsumfaith`, `summeval`, `frank`, `factcc`.

```
python run.py --data="xsum-sota" --model="gpt-3.5-turbo" --method="direct" --key="YOUR_OPENAIKEY"
```

