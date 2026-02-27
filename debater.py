# LLM-to-LLM Debater - two agents debate a topic (starter)
# pip install openai
from openai import OpenAI

print("\n### DON'T FORGET TO START LLAMA.CPP SERVER ###")

client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed")

# Load prompts from files
with open("_debate_rules.txt") as f:
    rules = f.read()
with open("_persona_affirmative.txt") as f:
    persona_aff = f.read()
with open("_persona_negative.txt") as f:
    persona_neg = f.read()

topic = "AI-generated art should be considered authentic creative expression."

def sanitize_for_routing(text: str) -> str:
    text = (text or "").strip()
    for marker in ["TURN 3", "TURN 4", "TURN 5", "Turn 3", "Turn 4", "Turn 5"]:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx].strip()
    return text

def sanitize_for_printing(text: str) -> str:
    text = (text or "").strip()
    for marker in ["IMPORTANT TASK", "ICE:", "TURN 1", "TURN 2", "TURN 3", "TURN 4", "TURN 5"]:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx].strip()
    return text

# TODO: Create two separate conversation histories
history_aff = [{"role": "system", "content": f"{rules}\n\n{persona_aff}\n\nTOPIC: {topic}"}]
history_neg = [{"role": "system", "content": f"{rules}\n\n{persona_neg}\n\nTOPIC: {topic}"}]


print(f"DEBATE TOPIC: {topic}\n")

# --- TURN 1: Affirmative opens ---
input("TURN 1: Affirmative opens, press ENTER...")
# TODO: Add user message to history_aff
# TODO: Call LLM with history_aff
# TODO: Get turn1 from response
# TODO: Add assistant message to history_aff
# TODO: Print turn1
history_aff.append({"role": "user", "content": "TURN 1 (Affirmative Constructive): Present ONLY your opening argument. Do not write future turns."})
response = client.chat.completions.create(model="local", messages=history_aff, temperature=0.4, max_tokens=500)
turn1 = response.choices[0].message.content
history_aff.append({"role": "assistant", "content": turn1})
print(f"\nAFFIRMATIVE:\n{sanitize_for_printing(turn1)}\n")

# TODO: Route - add turn1 to history_neg as "user"
history_neg.append({"role": "user", "content": f"Opponent said:\n{sanitize_for_routing(turn1)}"})

# --- TURN 2: Negative responds ---
input("TURN 2: Negative responds, press ENTER...")
# TODO: Call LLM with history_neg (no need to add user message, already routed)
# TODO: Get turn2, add to history_neg as assistant
# TODO: Print turn2
history_neg.append({"role": "user", "content": "TURN 2 ONLY (Negative Cross-Ex + Constructive): Ask 2-3 cross-ex questions about the Affirmative case, then present your counter-argument. Do not concede. STOP after Turn 2. Do not include any text like 'TURN 3/4/5'."})
response = client.chat.completions.create(model="local", messages=history_neg, temperature=0.4, max_tokens=500)
turn2 = response.choices[0].message.content
history_neg.append({"role": "assistant", "content": turn2})
print(f"\nNEGATIVE:\n{sanitize_for_printing(turn2)}\n")

# TODO: Route - add turn2 to history_aff as "user"
history_aff.append({"role": "user", "content": f"Opponent said:\n{sanitize_for_routing(turn2)}"})

# --- TURN 3: Affirmative rebuts ---
input("TURN 3: Affirmative rebuts, press ENTER...")
# TODO: Same pattern - call LLM, get response, add to history, print
history_aff.append({"role": "user", "content": "TURN 3 ONLY (Affirmative Cross-Ex + Rebuttal): Briefly answer the Negative’s cross-ex if needed, ask 2-3 cross-ex questions back, then rebut their main arguments. Do not concede. STOP after Turn 3. Do not include any text like 'TURN 4/5'."})
response = client.chat.completions.create(model="local", messages=history_aff, temperature=0.4, max_tokens=500)
turn3 = response.choices[0].message.content
history_aff.append({"role": "assistant", "content": turn3})
print(f"\nAFFIRMATIVE:\n{sanitize_for_printing(turn3)}\n")

# TODO: Route to negative
history_neg.append({"role": "user", "content": f"Opponent said:\n{sanitize_for_routing(turn3)}"})

# --- TURN 4: Negative rebuts ---
input("TURN 4: Negative rebuts, press ENTER...")
# TODO: Same pattern
history_neg.append({"role": "user", "content": "TURN 4 ONLY (Negative Rebuttal): Give your final rebuttal. No cross-ex questions. STOP after Turn 4. Do not include any text like 'TURN 5'."})
response = client.chat.completions.create(model="local", messages=history_neg, temperature=0.4, max_tokens=500)
turn4 = response.choices[0].message.content
history_neg.append({"role": "assistant", "content": turn4})
print(f"\nNEGATIVE:\n{sanitize_for_printing(turn4)}\n")

# TODO: Route to affirmative
history_aff.append({"role": "user", "content": f"Opponent said:\n{sanitize_for_routing(turn4)}"})

# --- TURN 5: Affirmative closing ---
input("TURN 5: Affirmative closing, press ENTER...")
# TODO: Same pattern
history_aff.append({"role": "user", "content": "Give your final rebuttal in under 200 words. End after your conclusion."})
response = client.chat.completions.create(model="local", messages=history_aff, temperature=0.4, max_tokens=450)
turn5 = response.choices[0].message.content
history_aff.append({"role": "assistant", "content": turn5})
print(f"\nAFFIRMATIVE:\n{sanitize_for_printing(turn5)}\n")

print("### DEBATE COMPLETE ###")

'''
Multi-agent pattern: Two LLMs "talk" to each other.

The key insight:
- Each agent has its own conversation history
- What is "assistant" output for Agent A becomes "user" input for Agent B
- This role flip is how agents communicate

history_aff: [system, user, assistant, user, assistant, ...]
history_neg: [system, user, assistant, user, assistant, ...]

When Affirmative speaks (assistant), that text goes to Negative as (user).
'''

# ============================================================
# STEP 6: See what happens with a single shared history.
#
# 1. Replace history_aff and history_neg with a single:
#      history = [{"role": "system", "content": rules}]
# 2. Use this one history for ALL turns
# 3. Watch how the LLM gets confused about which side it's on
#
# STEP 7: See sycophancy in action.
#
# 1. Remove "IMPORTANT: Never agree with your opponent" from personas
# 2. Run the debate and watch for phrases like:
#    - "You make a good point"
#    - "I agree with..."
#    - "That's a valid concern"
# 3. The agents may start agreeing instead of debating!
# ============================================================
