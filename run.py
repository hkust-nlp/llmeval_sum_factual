import openai
import math
import argparse
import pandas as pd
import openai
from time import sleep
import time
import os
import nltk
import pdb
import datetime
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
from collections import OrderedDict
from summac.benchmark import SummaCBenchmark


system="You are a helpful assistant. I will give you document-statement pairs and I need you to judge whether the statement can be inferred by the document. Only answer with yes or no."

benchmark_test = SummaCBenchmark(benchmark_folder="summac_benchmark", cut="test")
benchmark_val = SummaCBenchmark(benchmark_folder="summac_benchmark", cut="val")

xsumfaith_false_shotcot="Document: The Cherries went down 2-1 at Sunderland on Saturday, becoming the first team to lose to the Black Cats in the Premier League this season.\nDan Gosling's goal, which gave them the lead, was their first for three games.\n\"It shouldn't be down to a lack of confidence,\" Howe told BBC Radio Solent. \"We scored six goals against Hull prior to these two games.\"\nHe continued: \"A couple of weeks later, if you were to put the chances we've created together into a clip sequence, the fact that we haven't even scored one goal is difficult to take.\"\nBournemouth were stunned by goals for Sunderland from Victor Anichebe and a Jermain Defoe penalty and they were unable to find an equaliser, even against 10 men following Steven Pienaar's dismissal.\n\"We've had enough chances to win three games today,\" Howe added.\n\"Sometimes football pans out that way and you have to accept it. It's how you move on from that which is key.\"\n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\nbournemouth manager eddie howe says his side are \" struggling \" after losing 2-0 to hull on saturday.\n\nA: 1. The document does not mention eddie howe is bournemouth manager. And the document also does not mention his side lost to hull.\n2. No.\n\n"
xsumfaith_true_shotcot="Document: The man died in Inverness on 27 October this year.\nThe Police Investigations and Review Commissioner (Pirc), Kate Frame, has been asked to scrutinise the initial police response to the man's call.\nPolice Scotland said it was \"fully engaging\" with the investigation and awaited its findings.\nA spokesman for Pirc said: \"The Crown Office and Procurator Fiscal Service (COPFS) has instructed the Police Investigations and Review Commissioner to undertake an investigation into the initial police response to a call from a 72-year-old man who was later found dead at a sheltered housing complex in Inverness.\n\"A report on the commissioner's findings will be submitted to the COPFS in due course.\"\n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\na police watchdog has ordered an investigation after a 72-year-old man was found dead in a housing housing complex.\n\nA: 1. The document mentions a 72-year-old man was found dead in a housing housing complex, also mentions a police watchdog has ordered an investigation after that.\n2. Yes."
xsumfaith_2shotcot="Document: The Cherries went down 2-1 at Sunderland on Saturday, becoming the first team to lose to the Black Cats in the Premier League this season.\nDan Gosling's goal, which gave them the lead, was their first for three games.\n\"It shouldn't be down to a lack of confidence,\" Howe told BBC Radio Solent. \"We scored six goals against Hull prior to these two games.\"\nHe continued: \"A couple of weeks later, if you were to put the chances we've created together into a clip sequence, the fact that we haven't even scored one goal is difficult to take.\"\nBournemouth were stunned by goals for Sunderland from Victor Anichebe and a Jermain Defoe penalty and they were unable to find an equaliser, even against 10 men following Steven Pienaar's dismissal.\n\"We've had enough chances to win three games today,\" Howe added.\n\"Sometimes football pans out that way and you have to accept it. It's how you move on from that which is key.\"\n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\nbournemouth manager eddie howe says his side are \" struggling \" after losing 2-0 to hull on saturday.\n\nA: 1. The document does not mention eddie howe is bournemouth manager. And the document also does not mention his side lost to hull.\n2. No.\n\nDocument: The man died in Inverness on 27 October this year.\nThe Police Investigations and Review Commissioner (Pirc), Kate Frame, has been asked to scrutinise the initial police response to the man's call.\nPolice Scotland said it was \"fully engaging\" with the investigation and awaited its findings.\nA spokesman for Pirc said: \"The Crown Office and Procurator Fiscal Service (COPFS) has instructed the Police Investigations and Review Commissioner to undertake an investigation into the initial police response to a call from a 72-year-old man who was later found dead at a sheltered housing complex in Inverness.\n\"A report on the commissioner's findings will be submitted to the COPFS in due course.\"\n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\na police watchdog has ordered an investigation after a 72-year-old man was found dead in a housing housing complex.\n\nA: 1. The document mentions a 72-year-old man was found dead in a housing housing complex, also mentions a police watchdog has ordered an investigation after that.\n2. Yes."

xsumfaith_false_shot="Document: The Cherries went down 2-1 at Sunderland on Saturday, becoming the first team to lose to the Black Cats in the Premier League this season.\nDan Gosling's goal, which gave them the lead, was their first for three games.\n\"It shouldn't be down to a lack of confidence,\" Howe told BBC Radio Solent. \"We scored six goals against Hull prior to these two games.\"\nHe continued: \"A couple of weeks later, if you were to put the chances we've created together into a clip sequence, the fact that we haven't even scored one goal is difficult to take.\"\nBournemouth were stunned by goals for Sunderland from Victor Anichebe and a Jermain Defoe penalty and they were unable to find an equaliser, even against 10 men following Steven Pienaar's dismissal.\n\"We've had enough chances to win three games today,\" Howe added.\n\"Sometimes football pans out that way and you have to accept it. It's how you move on from that which is key.\"\n\nQ: Can the following statement be inferred from the above document? Yes or No?\nbournemouth manager eddie howe says his side are \" struggling \" after losing 2-0 to hull on saturday.\n\nA: No.\n\n"
xsumfaith_true_shot="Document: The man died in Inverness on 27 October this year.\nThe Police Investigations and Review Commissioner (Pirc), Kate Frame, has been asked to scrutinise the initial police response to the man's call.\nPolice Scotland said it was \"fully engaging\" with the investigation and awaited its findings.\nA spokesman for Pirc said: \"The Crown Office and Procurator Fiscal Service (COPFS) has instructed the Police Investigations and Review Commissioner to undertake an investigation into the initial police response to a call from a 72-year-old man who was later found dead at a sheltered housing complex in Inverness.\n\"A report on the commissioner's findings will be submitted to the COPFS in due course.\"\n\nQ: Can the following statement be inferred from the above document? Yes or No?\na police watchdog has ordered an investigation after a 72-year-old man was found dead in a housing housing complex.\n\nA: Yes."
xsumfaith2shot="Document: The Cherries went down 2-1 at Sunderland on Saturday, becoming the first team to lose to the Black Cats in the Premier League this season.\nDan Gosling's goal, which gave them the lead, was their first for three games.\n\"It shouldn't be down to a lack of confidence,\" Howe told BBC Radio Solent. \"We scored six goals against Hull prior to these two games.\"\nHe continued: \"A couple of weeks later, if you were to put the chances we've created together into a clip sequence, the fact that we haven't even scored one goal is difficult to take.\"\nBournemouth were stunned by goals for Sunderland from Victor Anichebe and a Jermain Defoe penalty and they were unable to find an equaliser, even against 10 men following Steven Pienaar's dismissal.\n\"We've had enough chances to win three games today,\" Howe added.\n\"Sometimes football pans out that way and you have to accept it. It's how you move on from that which is key.\"\n\nQ: Can the following statements be inferred from the above document? Yes or No?\nbournemouth manager eddie howe says his side are \" struggling \" after losing 2-0 to hull on saturday.\n\nA: No\n\nDocument: The man died in Inverness on 27 October this year.\nThe Police Investigations and Review Commissioner (Pirc), Kate Frame, has been asked to scrutinise the initial police response to the man's call.\nPolice Scotland said it was \"fully engaging\" with the investigation and awaited its findings.\nA spokesman for Pirc said: \"The Crown Office and Procurator Fiscal Service (COPFS) has instructed the Police Investigations and Review Commissioner to undertake an investigation into the initial police response to a call from a 72-year-old man who was later found dead at a sheltered housing complex in Inverness.\n\"A report on the commissioner's findings will be submitted to the COPFS in due course.\"\n\nQ: Can the following statements be inferred from the above document? Yes or No?\na police watchdog has ordered an investigation after a 72-year-old man was found dead in a housing housing complex.\n\nA: Yes"

cogensumm_false_shotsbs="Document: "+' '.join((str(benchmark_val.get_dataset("cogensumm")[30]['document']).split())[0:512])+"\n\nQ: Can the following statements be inferred from the above document? Yes or No? 1.\n"+str(benchmark_val.get_dataset("cogensumm")[30]['claim'])+"\n\nA: "+ "1. Yes"
cogensumm_true_shotsbs="Document: "+' '.join((str(benchmark_val.get_dataset("cogensumm")[1250]['document']).split())[0:512])+"\n\nQ: Can the following statements be inferred from the above document? Yes or No?\n"+"1. the catfish is named by biologists at auburn university museum of natural history. 2. the fish was discovered in the gurupi river in north brazil. 3. the resemblance to the first of the original star wars films. 4. he new species of catfish peckoltia greedoi has large eyes and a sucker mouth. 5. han solo - an extinct species found in southern china."+"\n\nA: "+ "1. Yes. 2. No. 3. Yes. 4. Yes. 5. Yes. "
cogensumm2shotsbs=cogensumm_true_shotsbs+'\n\n'+cogensumm_false_shotsbs+'\n\n'

factcc_false_shotsbs="Document: "+str(benchmark_val.get_dataset("factcc")[30]['document'])+"\n\nQ: Can the following statements be inferred from the above document? Yes or No?\n1. "+str(benchmark_val.get_dataset("factcc")[30]['claim'])+"\n\nA: "+ "1. Yes"
factcc_true_shotsbs="Document: "+str(benchmark_val.get_dataset("factcc")[32]['document'])+"\n\nQ: Can the following statements be inferred from the above document? Yes or No?\n1. "+str(benchmark_val.get_dataset("factcc")[32]['claim'])+"\n\nA: "+ "1. No"
factcc2shotsbs=factcc_true_shotsbs+'\n\n'+factcc_false_shotsbs+'\n\n'



frank_false_shotsbs="Document: "+str(benchmark_val.get_dataset("frank")[663]['document'])+"\n\nQ: Can the following statements be inferred from the above document? Yes or No?\n"+"1. police tweeted a warning about wasting time after a holidaymaker tried to lodge an official complaint at the great manchester police chadderton division . 2. the 44-year-old from oldham decided had just returned from algeria and wanted to complain about his trip . 3. police said the weather on his holiday was ` too hot ' the incident was shared by the police press office on its facebook page ."+"\n\nA: "+ "1. No 2. Yes. 3. No"
frank_true_shotsbs="Document: "+str(benchmark_val.get_dataset("frank")[30]['document'])+"\n\nQ: Can the following statements be inferred from the above document? Yes or No?\n1. "+str(benchmark_val.get_dataset("frank")[30]['claim'])+"\n\nA: "+ "1. Yes"
frank2shot=frank_true_shotsbs+'\n\n'+frank_false_shotsbs+'\n\n'


summeval_2shotsbs="Document: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday. 'Just been watching the game, did you miss the coach? #RubberDub #7minutes,' Merson put on Twitter. Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.' Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley . Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley . Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night . The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake. 'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said. 'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad. 'When I'm wrong, I hold my hands up. I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.' Townsend hit back at Merson on Twitter after scoring for England against Italy . Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week . Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?' Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor.\n\nQ: Can the following statements be inferred from the above document? Yes or No?\n1. Andros Townsend scored for England against Italy on Wednesday . \n2. Paul Merson criticised Townsend's call-up to the England squad . \n3. Merson said Townsend should not have been in Roy Hodgson's squad . \n4. Townsend hit back at Merson on Twitter after scoring for England . \n\nA: 1. No, the document states it' s on Tuesday night. \n2. Yes.\n3. Yes.\n4. Yes.\n\nDocument: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday. 'Just been watching the game, did you miss the coach? #RubberDub #7minutes,' Merson put on Twitter. Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.' Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley . Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley . Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night . The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake. 'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said. 'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad. 'When I'm wrong, I hold my hands up. I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.' Townsend hit back at Merson on Twitter after scoring for England against Italy . Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week . Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?' Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor.\n\nQ: Can the following statements be inferred from the above document? Yes or No?\n1. paul merson has restarted his row with andros townsend after the tottenham midfielder was brought on with only seven minutes remaining in his team 's 0-0 draw with burnley on sunday . \n2. ' paul merson had another dig at andros townsend after his appearance for tottenham against burnley .\n3. townsend was brought on in the 83rd minute for tottenham as they drew 0-0 against burnley .\n\nA: 1. Yes.\n2. Yes.\n3. Yes."
summeval_false_shotsbs="Document: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday. 'Just been watching the game, did you miss the coach? #RubberDub #7minutes,' Merson put on Twitter. Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.' Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley . Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley . Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night . The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake. 'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said. 'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad. 'When I'm wrong, I hold my hands up. I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.' Townsend hit back at Merson on Twitter after scoring for England against Italy . Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week . Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?' Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor.\n\nQ: Can the following statements be inferred from the above document? Yes or No?\n1. Andros Townsend scored for England against Italy on Wednesday . \n2. Paul Merson criticised Townsend's call-up to the England squad . \n3. Merson said Townsend should not have been in Roy Hodgson's squad . \n4. Townsend hit back at Merson on Twitter after scoring for England . \n\nA: 1. No, the document states it' s on Tuesday night. \n2. Yes.\n3. Yes.\n4. Yes.\n\n"
summeval_true_shotsbs="Document: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday. 'Just been watching the game, did you miss the coach? #RubberDub #7minutes,' Merson put on Twitter. Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.' Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley . Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley . Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night . The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake. 'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said. 'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad. 'When I'm wrong, I hold my hands up. I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.' Townsend hit back at Merson on Twitter after scoring for England against Italy . Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week . Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?' Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor.\n\nQ: Can the following statements be inferred from the above document? Yes or No?\n1. paul merson has restarted his row with andros townsend after the tottenham midfielder was brought on with only seven minutes remaining in his team 's 0-0 draw with burnley on sunday . \n2. ' paul merson had another dig at andros townsend after his appearance for tottenham against burnley .\n3. townsend was brought on in the 83rd minute for tottenham as they drew 0-0 against burnley .\n\nA: 1. Yes.\n2. Yes.\n3. Yes."

summeval2shot="Document: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday. 'Just been watching the game, did you miss the coach? #RubberDub #7minutes,' Merson put on Twitter. Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.' Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley . Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley . Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night . The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake. 'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said. 'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad. 'When I'm wrong, I hold my hands up. I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.' Townsend hit back at Merson on Twitter after scoring for England against Italy . Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week . Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?' Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor.\n\nQ: Can the following statement be inferred from the above document? Yes or No?\nAndros Townsend scored for England against Italy on Wednesday . \n Paul Merson criticised Townsend's call-up to the England squad . \nMerson said Townsend should not have been in Roy Hodgson's squad . \n4. Townsend hit back at Merson on Twitter after scoring for England . \n\nA:  No, the document states it' s on Tuesday night.\n\nDocument: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday. 'Just been watching the game, did you miss the coach? #RubberDub #7minutes,' Merson put on Twitter. Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.' Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley . Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley . Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night . The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake. 'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said. 'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad. 'When I'm wrong, I hold my hands up. I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.' Townsend hit back at Merson on Twitter after scoring for England against Italy . Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week . Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?' Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor.\n\nQ: Can the following statements be inferred from the above document? Yes or No?\npaul merson has restarted his row with andros townsend after the tottenham midfielder was brought on with only seven minutes remaining in his team 's 0-0 draw with burnley on sunday . \n' paul merson had another dig at andros townsend after his appearance for tottenham against burnley .\ntownsend was brought on in the 83rd minute for tottenham as they drew 0-0 against burnley .\n\nA: Yes"
summeval_false_shot="Document: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday. 'Just been watching the game, did you miss the coach? #RubberDub #7minutes,' Merson put on Twitter. Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.' Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley . Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley . Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night . The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake. 'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said. 'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad. 'When I'm wrong, I hold my hands up. I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.' Townsend hit back at Merson on Twitter after scoring for England against Italy . Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week . Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?' Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor.\n\nQ: Can the following statement be inferred from the above document? Yes or No?\nAndros Townsend scored for England against Italy on Wednesday . \n Paul Merson criticised Townsend's call-up to the England squad . \nMerson said Townsend should not have been in Roy Hodgson's squad . \n4. Townsend hit back at Merson on Twitter after scoring for England . \n\nA:  No, the document states it' s on Tuesday night.\n\n"
summeval_true_shot="Document: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday. 'Just been watching the game, did you miss the coach? #RubberDub #7minutes,' Merson put on Twitter. Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.' Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley . Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley . Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night . The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake. 'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said. 'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad. 'When I'm wrong, I hold my hands up. I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.' Townsend hit back at Merson on Twitter after scoring for England against Italy . Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week . Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?' Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor.\n\nQ: Can the following statements be inferred from the above document? Yes or No?\npaul merson has restarted his row with andros townsend after the tottenham midfielder was brought on with only seven minutes remaining in his team 's 0-0 draw with burnley on sunday . \n' paul merson had another dig at andros townsend after his appearance for tottenham against burnley .\ntownsend was brought on in the 83rd minute for tottenham as they drew 0-0 against burnley .\n\nA: Yes."

summeval_2shotcot="Document: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday.  'Just been watching the game, did you miss the coach?  #RubberDub #7minutes,' Merson put on Twitter.  Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.'  Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley .  Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley .  Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night .  The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake.  'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said.  'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad.  'When I'm wrong, I hold my hands up.  I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.'  Townsend hit back at Merson on Twitter after scoring for England against Italy .  Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week .  Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?'  Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor. \n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\nAndros Townsend scored for England against Italy on Wednesday .  Paul Merson criticised Townsend's call-up to the England squad .  Merson said Townsend should not have been in Roy Hodgson's squad .  Townsend hit back at Merson on Twitter after scoring for England .  \n\nA: 1. The document does not mention the date Andros Townsend scored for England against Italy is on Wednesday.\n2. No.\n\nDocument: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday.  'Just been watching the game, did you miss the coach?  #RubberDub #7minutes,' Merson put on Twitter.  Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.'  Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley .  Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley .  Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night .  The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake.  'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said.  'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad.  'When I'm wrong, I hold my hands up.  I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.'  Townsend hit back at Merson on Twitter after scoring for England against Italy .  Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week .  Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?'  Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor. \n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\npaul merson has restarted his row with andros townsend after the tottenham midfielder was brought on with only seven minutes remaining in his team 's 0-0 draw with burnley on sunday .  ' paul merson had another dig at andros townsend after his appearance for tottenham against burnley .  townsend was brought on in the 83rd minute for tottenham as they drew 0-0 against burnley .\n\nA: 1. The document does mention these content. \n2. Yes."
summeval_false_shotcot="Document: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday.  'Just been watching the game, did you miss the coach?  #RubberDub #7minutes,' Merson put on Twitter.  Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.'  Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley .  Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley .  Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night .  The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake.  'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said.  'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad.  'When I'm wrong, I hold my hands up.  I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.'  Townsend hit back at Merson on Twitter after scoring for England against Italy .  Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week .  Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?'  Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor. \n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\nAndros Townsend scored for England against Italy on Wednesday .  Paul Merson criticised Townsend's call-up to the England squad .  Merson said Townsend should not have been in Roy Hodgson's squad .  Townsend hit back at Merson on Twitter after scoring for England .  \n\nA: 1. The document does not mention the date Andros Townsend scored for England against Italy is on Wednesday.\n2. No.\n\n"
summeval_true_shotcot="Document: Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday.  'Just been watching the game, did you miss the coach?  #RubberDub #7minutes,' Merson put on Twitter.  Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.'  Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley .  Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley .  Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night .  The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake.  'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said.  'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad.  'When I'm wrong, I hold my hands up.  I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.'  Townsend hit back at Merson on Twitter after scoring for England against Italy .  Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week .  Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?'  Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor. \n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\npaul merson has restarted his row with andros townsend after the tottenham midfielder was brought on with only seven minutes remaining in his team 's 0-0 draw with burnley on sunday .  ' paul merson had another dig at andros townsend after his appearance for tottenham against burnley .  townsend was brought on in the 83rd minute for tottenham as they drew 0-0 against burnley .\n\nA: 1. The document does mention these content. \n2. Yes."



xsumsota_2shotcot="Document: On Monday, the BBC's Panorama programme uncovered several safety concerns, from staffing levels to waste storage.\nThe Mannin Branch of the Celtic League has called on the Manx government to campaign for a full, independent inspection of the plant in Cumbria.\nSellafield says the site is safe and has been improved with significant investment in recent years.\nA spokesman added: \"Safety is our priority and we are managing a very complex site which has got a great deal of hazardous radioactive materials on it.\"\nThe Isle of Man is located about 34 miles (55km) from the nuclear fuel reprocessing plant.\nDue to its potential impact on the Manx fishing industry, the Manx government began monitoring radioactivity levels in the Irish Sea in 1989.\nA government spokesman said: \"Seafood fished in Manx waters can contain traces of radio-nuclides associated with effluent discharges from Sellafield to the Irish Sea, therefore these are monitored regularly to confirm that they remain well below maximum safe limits.\"\nThe BBC investigation was prompted by a whistle-blower - a former senior manager who was worried by conditions at the plant.\nHe said his biggest fear was a fire in one of the nuclear waste silos or in one of the processing plants.\nThe Manx government said it was particularly concerned about \"the structural integrity of ageing waste storage ponds and silos\".\nA spokesman added: \"However we are content that Sellafield Ltd and the nuclear regulators are trying to improve the safety situation.\n\"The government has asked questions about the technical solutions being developed to decommission these redundant structures and representatives have visited the site to look at the work under way\".\n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\nCeltic football fans have called for an independent inspection of the sellafield nuclear site.\n\nA: 1. The document does not mention about the Celtic football fans.\n2. No.\n\nDocument: Thai officials said the event, which was halted minutes before it was due to start, could have affected relations between the two countries.\nThe HRW report focuses on the treatment of a Christian group in Vietnam.\nThe group said the Thai response showed how freedom of speech had been eroded since the army seized power last year.\nThai police said the event at the Foreign Correspondents Club of Thailand could \"have an impact on the country's security or could affect the friendship and cooperation between Thailand and Vietnam\".\nIt is the third human rights event at the venue that has been halted by authorities in the past month.\nThe HRW report describes what it says is the persecution of Montagnard Christians in Vietnam's central highlands. Their religious practices have been described by the Vietnamese government as \"evil\".\nSunai Phasuk, Human Rights Watch's senior researcher in Asia, said the decision to cancel the report's launch was \"very disappointing\".\n\"Thailand is now going to be known as the defender of human rights violators in [Southeast Asia], which adds more damage to Thailand's already tarnished international reputation under the military rule,\" he added.\nThai authorities have launched a crackdown on critics since the military seized power from a civilian government in May 2014.\n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\nThai police have cancelled the launch of a human rights watch ( hrw ) report at a foreign journalists' club in bangkok.\n\nA: 1. The document mentions that \"Thai police said the event at the Foreign Correspondents Club of Thailand could \"have an impact on the country's security or could affect the friendship and cooperation between Thailand and Vietnam\". It is the third human rights event at the venue that has been halted by authorities in the past month.\". We can infer that the statement is correct.\n2. Yes."
xsumsota_false_shotcot="Document: On Monday, the BBC's Panorama programme uncovered several safety concerns, from staffing levels to waste storage.\nThe Mannin Branch of the Celtic League has called on the Manx government to campaign for a full, independent inspection of the plant in Cumbria.\nSellafield says the site is safe and has been improved with significant investment in recent years.\nA spokesman added: \"Safety is our priority and we are managing a very complex site which has got a great deal of hazardous radioactive materials on it.\"\nThe Isle of Man is located about 34 miles (55km) from the nuclear fuel reprocessing plant.\nDue to its potential impact on the Manx fishing industry, the Manx government began monitoring radioactivity levels in the Irish Sea in 1989.\nA government spokesman said: \"Seafood fished in Manx waters can contain traces of radio-nuclides associated with effluent discharges from Sellafield to the Irish Sea, therefore these are monitored regularly to confirm that they remain well below maximum safe limits.\"\nThe BBC investigation was prompted by a whistle-blower - a former senior manager who was worried by conditions at the plant.\nHe said his biggest fear was a fire in one of the nuclear waste silos or in one of the processing plants.\nThe Manx government said it was particularly concerned about \"the structural integrity of ageing waste storage ponds and silos\".\nA spokesman added: \"However we are content that Sellafield Ltd and the nuclear regulators are trying to improve the safety situation.\n\"The government has asked questions about the technical solutions being developed to decommission these redundant structures and representatives have visited the site to look at the work under way\".\n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\nCeltic football fans have called for an independent inspection of the sellafield nuclear site.\n\nA: 1. The document does not mention about the Celtic football fans.\n2. No.\n\n"
xsumsota_true_shotcot="Document: Thai officials said the event, which was halted minutes before it was due to start, could have affected relations between the two countries.\nThe HRW report focuses on the treatment of a Christian group in Vietnam.\nThe group said the Thai response showed how freedom of speech had been eroded since the army seized power last year.\nThai police said the event at the Foreign Correspondents Club of Thailand could \"have an impact on the country's security or could affect the friendship and cooperation between Thailand and Vietnam\".\nIt is the third human rights event at the venue that has been halted by authorities in the past month.\nThe HRW report describes what it says is the persecution of Montagnard Christians in Vietnam's central highlands. Their religious practices have been described by the Vietnamese government as \"evil\".\nSunai Phasuk, Human Rights Watch's senior researcher in Asia, said the decision to cancel the report's launch was \"very disappointing\".\n\"Thailand is now going to be known as the defender of human rights violators in [Southeast Asia], which adds more damage to Thailand's already tarnished international reputation under the military rule,\" he added.\nThai authorities have launched a crackdown on critics since the military seized power from a civilian government in May 2014.\n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\nThai police have cancelled the launch of a human rights watch ( hrw ) report at a foreign journalists' club in bangkok.\n\nA: 1. The document mentions that \"Thai police said the event at the Foreign Correspondents Club of Thailand could \"have an impact on the country's security or could affect the friendship and cooperation between Thailand and Vietnam\". It is the third human rights event at the venue that has been halted by authorities in the past month.\". We can infer that the statement is correct.\n2. Yes."

xsumsota_2shot="Document: On Monday, the BBC's Panorama programme uncovered several safety concerns, from staffing levels to waste storage.\nThe Mannin Branch of the Celtic League has called on the Manx government to campaign for a full, independent inspection of the plant in Cumbria.\nSellafield says the site is safe and has been improved with significant investment in recent years.\nA spokesman added: \"Safety is our priority and we are managing a very complex site which has got a great deal of hazardous radioactive materials on it.\"\nThe Isle of Man is located about 34 miles (55km) from the nuclear fuel reprocessing plant.\nDue to its potential impact on the Manx fishing industry, the Manx government began monitoring radioactivity levels in the Irish Sea in 1989.\nA government spokesman said: \"Seafood fished in Manx waters can contain traces of radio-nuclides associated with effluent discharges from Sellafield to the Irish Sea, therefore these are monitored regularly to confirm that they remain well below maximum safe limits.\"\nThe BBC investigation was prompted by a whistle-blower - a former senior manager who was worried by conditions at the plant.\nHe said his biggest fear was a fire in one of the nuclear waste silos or in one of the processing plants.\nThe Manx government said it was particularly concerned about \"the structural integrity of ageing waste storage ponds and silos\".\nA spokesman added: \"However we are content that Sellafield Ltd and the nuclear regulators are trying to improve the safety situation.\n\"The government has asked questions about the technical solutions being developed to decommission these redundant structures and representatives have visited the site to look at the work under way\".\n\nQ: Can the following statement be inferred from the above document? Yes or No?\nCeltic football fans have called for an independent inspection of the sellafield nuclear site.\n\nA: No\n\nDocument: Thai officials said the event, which was halted minutes before it was due to start, could have affected relations between the two countries.\nThe HRW report focuses on the treatment of a Christian group in Vietnam.\nThe group said the Thai response showed how freedom of speech had been eroded since the army seized power last year.\nThai police said the event at the Foreign Correspondents Club of Thailand could \"have an impact on the country's security or could affect the friendship and cooperation between Thailand and Vietnam\".\nIt is the third human rights event at the venue that has been halted by authorities in the past month.\nThe HRW report describes what it says is the persecution of Montagnard Christians in Vietnam's central highlands. Their religious practices have been described by the Vietnamese government as \"evil\".\nSunai Phasuk, Human Rights Watch's senior researcher in Asia, said the decision to cancel the report's launch was \"very disappointing\".\n\"Thailand is now going to be known as the defender of human rights violators in [Southeast Asia], which adds more damage to Thailand's already tarnished international reputation under the military rule,\" he added.\nThai authorities have launched a crackdown on critics since the military seized power from a civilian government in May 2014.\n\nQ: Can the following statement be inferred from the above document? Yes or No?\nThai police have cancelled the launch of a human rights watch ( hrw ) report at a foreign journalists' club in bangkok.\n\nA: Yes"
xsumsota_false_shot="Document: On Monday, the BBC's Panorama programme uncovered several safety concerns, from staffing levels to waste storage.\nThe Mannin Branch of the Celtic League has called on the Manx government to campaign for a full, independent inspection of the plant in Cumbria.\nSellafield says the site is safe and has been improved with significant investment in recent years.\nA spokesman added: \"Safety is our priority and we are managing a very complex site which has got a great deal of hazardous radioactive materials on it.\"\nThe Isle of Man is located about 34 miles (55km) from the nuclear fuel reprocessing plant.\nDue to its potential impact on the Manx fishing industry, the Manx government began monitoring radioactivity levels in the Irish Sea in 1989.\nA government spokesman said: \"Seafood fished in Manx waters can contain traces of radio-nuclides associated with effluent discharges from Sellafield to the Irish Sea, therefore these are monitored regularly to confirm that they remain well below maximum safe limits.\"\nThe BBC investigation was prompted by a whistle-blower - a former senior manager who was worried by conditions at the plant.\nHe said his biggest fear was a fire in one of the nuclear waste silos or in one of the processing plants.\nThe Manx government said it was particularly concerned about \"the structural integrity of ageing waste storage ponds and silos\".\nA spokesman added: \"However we are content that Sellafield Ltd and the nuclear regulators are trying to improve the safety situation.\n\"The government has asked questions about the technical solutions being developed to decommission these redundant structures and representatives have visited the site to look at the work under way\".\n\nQ: Can the following statement be inferred from the above document? Yes or No?\nCeltic football fans have called for an independent inspection of the sellafield nuclear site.\n\nA: No"
xsumsota_true_shot="Document: Thai officials said the event, which was halted minutes before it was due to start, could have affected relations between the two countries.\nThe HRW report focuses on the treatment of a Christian group in Vietnam.\nThe group said the Thai response showed how freedom of speech had been eroded since the army seized power last year.\nThai police said the event at the Foreign Correspondents Club of Thailand could \"have an impact on the country's security or could affect the friendship and cooperation between Thailand and Vietnam\".\nIt is the third human rights event at the venue that has been halted by authorities in the past month.\nThe HRW report describes what it says is the persecution of Montagnard Christians in Vietnam's central highlands. Their religious practices have been described by the Vietnamese government as \"evil\".\nSunai Phasuk, Human Rights Watch's senior researcher in Asia, said the decision to cancel the report's launch was \"very disappointing\".\n\"Thailand is now going to be known as the defender of human rights violators in [Southeast Asia], which adds more damage to Thailand's already tarnished international reputation under the military rule,\" he added.\nThai authorities have launched a crackdown on critics since the military seized power from a civilian government in May 2014.\n\nQ: Can the following statement be inferred from the above document? Yes or No?\nThai police have cancelled the launch of a human rights watch ( hrw ) report at a foreign journalists' club in bangkok.\n\nA: Yes"




def get(dataname,method):
    to_return=[]
    if dataname=='cogensumm' and method=='2shotsbs':
        to_return.append(cogensumm_true_shotsbs)
        to_return.append(cogensumm_false_shotsbs)
    elif dataname=='factcc' and method=='2shotsbs':
        to_return.append(factcc_true_shotsbs)
        to_return.append(factcc_false_shotsbs)
    elif dataname=='frank' and method=='2shotsbs':
        to_return.append(frank_true_shotsbs)
        to_return.append(frank_false_shotsbs)
    elif dataname=='xsumfaith' and method=='2shotdirect':
        to_return.append(xsumfaith_true_shot)
        to_return.append(xsumfaith_false_shot)
    elif dataname=='xsumfaith' and method=='2shotcot':
        to_return.append(xsumfaith_true_shotcot)
        to_return.append(xsumfaith_false_shotcot)
    elif dataname=='summeval' and method=='2shotsbs':
        to_return.append(summeval_true_shotsbs)
        to_return.append(summeval_false_shotsbs)
    elif dataname=='summEval' and method=='2shotdirect':
        to_return.append(summeval_true_shot)
        to_return.append(summeval_false_shot)
    elif dataname=='summeval' and method=='2shotcot':
        to_return.append(summeval_true_shotcot)
        to_return.append(summeval_false_shotcot)
    elif dataname=='xsum-sota' and method=='2shotcot':
        to_return.append(xsumsota_true_shotcot)
        to_return.append(xsumsota_false_shotcot)
    elif dataname=='xsum-sota' and method=='2shotdirect':
        to_return.append(xsumsota_true_shot)
        to_return.append(xsumsota_false_shot)
    
    return to_return

@retry(wait=wait_random_exponential(min=8, max=50), stop=stop_after_attempt(6))
def gen(a,dataname,model,method):
    prefix=[{"role":"system","content":system}]
    shots=get(dataname,method)
    for shot in shots:
        inp,ans=shot.split("\nA: ")
        prefix+=[{"role":"user","content":inp},{"role":"assistant","content": ans}]
    prefix+= [{"role":"user","content": a}]
    
    request=openai.ChatCompletion.create(
    model=model,
        messages=prefix,
        temperature=0,
        max_tokens=100
    )
    
    return (request["choices"][0]['message']['content'],prefix)


def parse_args():
    parse=argparse.ArgumentParser()
    parse.add_argument('--data',type=str,help='dataset name')
    parse.add_argument('--model',type=str,help='model name')
    parse.add_argument('--method',type=str,help='method name')
    parse.add_argument('--key',type=str,help='openai key')
    args = parse.parse_args()  
    return args

def make_print_to_file(path='logger/'):
    import sys
    import os
    import sys
    import datetime
 
    class Logger(object):
        def __init__(self, filename="Default.log", path="./"):
            self.terminal = sys.stdout
            self.path= os.path.join(path, filename)
            self.log = open(self.path, "a", encoding='utf8',)
            print("save:", os.path.join(self.path, filename))
 
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
 
        def flush(self):
            pass
 
    fileName = datetime.datetime.now().strftime('day'+'%Y_%m_%d')
    sys.stdout = Logger(fileName + '.log', path=path)
    print(fileName.center(60,'*'))


def sentence_seg(paragraph):
    paragraph = paragraph.lower()
    sen_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') 
    sentences = sen_tokenizer.tokenize(paragraph)
    return sentences

def run(ori_data,dataset,model,method):
    result={}
    i=0
    for data in ori_data:
        _id=str(i)
        # pdb.set_trace()
        doc=data['document']
        doc=' '.join(doc.split( )[0:800])
        sum=data['claim']
        label=data['label']
        i+=1
        sumsentence=sentence_seg(sum)
        a="Document: "+doc+"\n\n"
        a+="Q: Can the following statements be inferred from the above document? Yes or No?"
        for j in range(len(sumsentence)):
            b=str(j+1)+". "+sumsentence[j]+"\n"
            a+=b
        a+="\nA: 1."
        generate,prefix=gen(a,dataset,model,method)
        res=1
        if method=='twoshotcot':
            res=max(0,res-('2. No' in generate))
        else:
            res=max(0,res-('No' in generate))
        
        if res==label==1:
            print("TP")
        elif res==label==0:
            print("TN")
        elif res==1 and label==0:
            print("FP")
        else:
            print('FN')
        result[_id] = {'pred': res, 'raw': generate, 'prompt': prefix}
    return result

def compute_accuracy_aggrefact(data, res):
    TP=0
    TN=0
    FP=0
    FN=0
    for i, row in data.iterrows():
        id_, label = str(i), row['label']
        if res[id_]['pred'] == 1:
            if label == 1:
                TP += 1
            elif label == 0:
                FP += 1
            else:
                raise ValueError
        elif res[id_]['pred'] == 0:
            if label == 0:
                TN += 1
            elif label == 1:
                FN += 1
            else:
                raise ValueError
        else:
            raise ValueError

    return {
        'class 1': TP/(TP+FN) if TP+FN!=0 else None,
        'class 0': TN/(TN+FP) if TN+FP!=0 else None,
        'true num': TP + FN,
        'false num': TN + FP,
        'balanced': 0.5*(TP/(TP+FN)+TN/(TN+FP)) if TP+FN!=0 and TN+FP!=0 else None
    }

def compute_accuracy(ori_data, res):
    TP=0
    TN=0
    FP=0
    FN=0
    i=0
    for data in ori_data:
        id_, label = str(i), int(data['label'])
        if res[id_]['pred'] == 1:
            if label == 1:
                TP += 1
            elif label == 0:
                FP += 1
            else:
                raise ValueError
        elif res[id_]['pred'] == 0:
            if label == 0:
                TN += 1
            elif label == 1:
                FN += 1
            else:
                raise ValueError
        else:
            raise ValueError
        i+=1
    
    return {
        'class 1': TP/(TP+FN) if TP+FN!=0 else None,
        'class 0': TN/(TN+FP) if TN+FP!=0 else None,
        'true num': TP + FN,
        'false num': TN + FP,
        'balanced': 0.5*(TP/(TP+FN)+TN/(TN+FP)) if TP+FN!=0 and TN+FP!=0 else None
    }

def save_exp(data, result, output):
    print(f'save results to {output}')
    init = (('dataset',[]),('doc', []), ('sum', []),('label', []), ('prompt', []), ('gen', []), ('res', []), ('true or false', []))
    save = OrderedDict(init)
    i=0
    for row in data:
        id_, dataset,doc, sum, label = str(i), row['dataset'],row['document'], row['claim'],row['label']
        prompt = result[id_]['prompt']
        gen = result[id_]['raw']
        res = result[id_]['pred']
        t_or_f = int(res == label)
        i+=1
        save['dataset'].append(dataset)
        save['doc'].append(doc)
        save['sum'].append(sum)
        save['label'].append(label)
        save['prompt'].append(prompt)
        save['gen'].append(gen)
        save['res'].append(res)
        save['true or false'].append(t_or_f)

    df = pd.DataFrame(data=save)
    df.to_csv(output)





def save_exp_aggrefact(data, result, output):
    print(f'save results to {output}')
    init = (('dataset',[]),('doc', []), ('sum', []),('label', []), ('prompt', []), ('gen', []), ('res', []), ('true or false', []))
    save = OrderedDict(init)
    i=0
    for i, row in data.iterrows():
        pdb.set_trace()
        id_, dataset,doc, sum, label = str(i), row['dataset'],row['doc'], row['summary'],row['label']

        prompt = result[id_]['prompt']
        gen = result[id_]['raw']
        res = result[id_]['pred']
        t_or_f = int(res == label)
        i+=1
        save['dataset'].append(dataset)
        save['doc'].append(doc)
        save['sum'].append(sum)
        save['label'].append(label)
        save['prompt'].append(prompt)
        save['gen'].append(gen)
        save['res'].append(res)
        save['true or false'].append(t_or_f)

    df = pd.DataFrame(data=save)
    df.to_csv(output)


@retry(wait=wait_random_exponential(min=8, max=50), stop=stop_after_attempt(6))
def req(prefix,model):
    request=openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model=model,
            messages=prefix,
            temperature=0,
            max_tokens=30
        )
    return request

def print_saveresult(data,data_name,result,method):
    if data_name=='xsumfaith' or data_name=='summeval' or data_name=='xsum-sota':
        print('ALL'+str(compute_accuracy_aggrefact(data, result)))
    else:
        print('ALL'+str(compute_accuracy(data, result)))
    time_=time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time()))
    if not os.path.exists('summac_res'):
        os.makedirs('summac_res') 
    output='summac_res/'+data_name+time_+'_'+str(len(data))+str(method)+'.csv'
    if data_name=='xsumfaith' or data_name=='summeval' or data_name=='xsum-sota':
        save_exp_aggrefact(data, result, output)
    else:
        save_exp(data, result, output)


def aggrefactrun(data,data_name,model,method):
    result={}
    for i,row in data.iterrows():
        _id=str(i)
        doc=' '.join(row[3].split( )[0:1024])
        #doc=row[3]
        res=1
        
        
        if method=='direct' or method=='2shotdirect':
            a="Document: "+doc+"\n\nQ: Can the following statement be inferred from the above document? Yes or No?\n"+ row[4]+"\n\nA:"
        elif method=='cot' or method=='2shotcot':
            a="\n\nDocument: "+doc+"\n\nQ: Can the following statement be inferred from the above document? Please answer with the following structure. 1. Try to find the supporting evidence from the document. 2. Answer Yes or No.\n"+ row[4]+"\n\nA: 1."
        elif method=='sbs' or method=='2shotsbs':
            a="Document: "+doc+"\n\n"
            sumsentence=sentence_seg(row[4])
            a+="Q: Can the following statements be inferred from the above document? Yes or No?\n"
            for j in range(len(sumsentence)):
                b=str(j+1)+". "+sumsentence[j]+"\n"
                a+=b
            a+="\nA: 1."

        generate,prefix=gen(a,data_name,model,method)
        print(generate)
        if method=='cot' or method=='2shotcot':
            res=max(0,res-('2. No' in generate or 'No.' in generate))
        else:
            res=max(0,res-('No' in generate))
            
        if res==row[6]==1:
            print("TP")
        elif res==row[6]==0:
            print("TN")
        elif res==1 and row[6]==0:
            print("FP")
        else:
            print('FN')
        result[_id] = {'pred': res, 'raw': generate, 'prompt': prefix}
    return result
    
if __name__ =='__main__':
    time_=time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(time.time()))
    if not os.path.exists('summac_res'):
        os.makedirs('summac_res')
    make_print_to_file(path='summac_res/')
    args=parse_args()
    openai.api_key=args.key
    data_name=args.data
    if data_name=='xsum-sota':
        data=pd.read_csv('ori_data/aggre_fact_sota.csv')
        data=data.loc[data['cut']=='test']
        data=data.loc[data['origin']=='xsum']
        data=data.loc[data['dataset'].isin(['CLIFF','Goyal21'])]
        result=aggrefactrun(data,data_name,args.model,args.method)
        print_saveresult(data,data_name,result,args.method)
    elif data_name=='summeval':
        data=pd.read_csv('ori_data/aggre_fact_final.csv')
        data=data.loc[data['cut']=='test']
        data=data.loc[data['dataset']=='SummEval']
        data=data.loc[data['model_name']!='LEAD3']
        print(data_name,len(data))
        result=aggrefactrun(data,data_name,args.model,args.method)
        print_saveresult(data,data_name,result,args.method)
    elif data_name=='xsumfaith':
        data=pd.read_csv('ori_data/aggre_fact_final.csv')
        data=data.loc[data['cut']=='test']
        data=data.loc[data['origin']=='xsum']
        data=data.loc[data['dataset']=='XSumFaith']
        data=data.loc[~data['model_name'].isin (['Gold'])]
        result=aggrefactrun(data,data_name,args.model,args.method)
        print_saveresult(data,data_name,result,args.method)   
    else:
        benchmark_test = SummaCBenchmark(benchmark_folder="summac_benchmark", cut="test")
        data=benchmark_test.get_dataset(data_name)
        result=run(data,data_name,args.model,args.method)
        print_saveresult(data,data_name,result,args.method)
