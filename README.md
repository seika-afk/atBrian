atBrian : X/Twitter Bot that replies with local  Jev model

## About
- Classifies Text into 4 categories
  - AI Larp
  - Interaction bait
  - Rage bait
  - NPC Dialogue
 
Uses `Tev 0.8b` model from ollama and runs on port `11434`

## How To use This to create your own brian

1. Use ollama and pull model using `ollama pull tev1:0.8b`
2. serve ollama : `ollama serve`
3. Clone repo and run `uv sync`
4. Get your api from `https://www.twitterapis.com/`
5. Fill these env variables :
```
TWITTERAPIS_KEY
X_AUTH_TOKEN
X_AUTH_TOKEN
```
6. Run Register File to register yourself
7. Set the usertag 
8. Then run Tag_waiting.py
9. Tag that account and see the reply


### Note
You can vary classification and replies in `jev_call.py` file 
