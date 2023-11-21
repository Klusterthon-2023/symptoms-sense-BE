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
                            {"role": "user", "content": "Does this message contain medical, sickness and illness information? If it doesn't, just return 'No':"},
                            {"role": "user", "content": f"{request}"},
                        ]
                    )
        
        res = completion.choices[0].message.content
        if res[:2] == 'No' and len(res)<=3:
            return res
        
        completion = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": f"{request}"},
                        ]
                    )
        return completion.choices[0].message.content