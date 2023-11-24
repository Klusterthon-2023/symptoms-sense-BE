# guidance_app.utils

from django.conf import settings
from openai import OpenAI

class GPTQuery:
    
    def __init__(self) -> None:
        key = settings.CHAT_GPT_KEY
        if key:
            self.client = OpenAI(api_key=key)
            
    def get_response(self, request) -> None|str:
        
        if not self.client:
            return
        
        if isinstance(request, str):        
            completion = self.client.chat.completions.create(
                            model="ft:gpt-3.5-turbo-0613:personal::8OFaUXrw",
                            messages=[
                                {"role": "system", "content": "If the following question does contain any medical, symptoms or general wellbeing/wellness related word, respond with a typical response for a question you can't answer such as \"I'm sorry, but I don't have enough information on that topic.\" or \"I'm sorry, but I can't assist with that.\". If it does, then respond normally with fully-detailed explanation under the following but not limited to headings, as applicable: 'causes', 'diagnosis', 'medication', 'preventive measures', 'If/when to visit a doctor' "},
                                {"role": "user", "content": f"{request}"},
                            ]
                        )

        else:
            pass
        
        print(completion)
        
        # res = completion.choices[0].message.content
        # print(res)
        # if res[:2] == 'No' and len(res)<=3:
        #     return res
        
        # completion = self.client.chat.completions.create(
        #                 model="gpt-3.5-turbo",
        #                 messages=[
        #                     {"role": "user", "content": f"{request}. What are my possible diagnosis and medications? Do I need to visit a doctor?"},
        #                 ]
        #             )
        return completion.choices[0].message.content