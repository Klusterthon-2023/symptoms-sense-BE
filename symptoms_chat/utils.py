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
        
        completion = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "assistant", "content": "If the following question does contain any medical, symptoms or general wellbeing/wellness related word, respond with a 'No'. If it does, then respond normally with my possible diagnosis and possible medication. And whether I need to visit a doctor:"},
                            {"role": "user", "content": f"{request}"},
                        ]
                    )
        
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