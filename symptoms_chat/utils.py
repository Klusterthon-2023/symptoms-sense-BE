# guidance_app.utils

import os
from django.conf import settings
from openai import OpenAI
from django.conf import settings

class GPTQuery:
    
    def __init__(self) -> None:
        key = settings.CHAT_GPT_KEY
        if key:
            self.client = OpenAI(api_key=key)
            
    def get_response(self, request) -> None|str:
        
        if not self.client:
            return
               
        return self.completion(request)
            
    def completion(self, request):
        completion = self.client.chat.completions.create(
                            model="ft:gpt-3.5-turbo-0613:personal::8OFaUXrw",
                            messages=[
                                {"role": "system", "content": "If the following question does contain any medical, symptoms or general wellbeing/wellness related word, respond with a typical response for a question you can't answer such as \"I'm sorry, but I can't assist with that.\", unless it's based on a previous medical request or medical response. If it does, then respond normally with fully-detailed explanation under the following but not limited to headings, as applicable: 'causes', 'diagnosis', 'medication', 'preventive measures', 'If/when to visit a doctor'. Also, don't forget that all requests will be in English. You might need to detect the language first."},
                                {"role": "user", "content": f"{request}"},
                            ]
                        )
        
        return completion.choices[0].message.content
            
    def transcribe(self, audio) -> str|None:
        if not self.client:
            return
        
        audio_file= open(os.path.join(settings.MEDIA_ROOT, audio), "rb")
        transcript = self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
            )

        return self.completion(transcript.text)
        