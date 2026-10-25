import requests


INSTRUCTION="You are an AI content moderator that classifies statements into the most appropriate category based on their content, tone, and intent. Choose the single best-fitting category from the available options."
def call(STATE):
    resp = requests.post(
        "http://localhost:11434/v1/systemone",
        json={
            "model": "tev1:0.8b",
            "state":STATE,
            "questions":{
                "category":{
                    "type":"choice",
                    "instructions":INSTRUCTION,
                    "criteria":{
                        "AI Larp":" Text that imitate AI-generated content or pretend to be written by an AI, often using artificial-sounding language, exaggerated politeness, or stereotypical AI behavior.",
                        "Pure ragebait":" Text that provoke anger, outrage, or frustration through inflammatory opinions, deliberately provocative statements, or controversial takes.",
                        "sigh, Interaction bait":" Text designed to encourage engagement through replies, likes, reposts, or other interactions, often using questions, challenges, or requests for audience participation",
                        "NPC dialogue":" Text that sound generic, repetitive, predictable, or scripted, resembling stereotypical video game NPC dialogue or phrases repeated without much originality.",
                    }


                }
            }
        }
    )
    resp.raise_for_status()
    return resp.json()["answers"]["category"]["choice"]
