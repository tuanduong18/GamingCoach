import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is missing")

# Initialize the genai client
client = genai.Client(api_key=api_key)

def generate_coaching_advice(summoner_name: str, match_data: list, game_type: str = "ALL") -> str:
    """
    Takes the recent match data and uses Gemini to generate coaching advice.
    """
    if not match_data:
        return "No recent match data available to analyze."

    # Construct the prompt context
    mode_text = f"{game_type.lower()} " if game_type != "ALL" else ""
    prompt = f"Act as a professional League of Legends coach. Analyze the recent {len(match_data)} {mode_text}matches for player {summoner_name} and provide constructive, detailed coaching advice.\n\n"
    
    prompt += "### Recent Matches Data:\n"
    for i, match in enumerate(match_data, 1):
        win_status = "Victory" if match.get("win") else "Defeat"
        kda = f"{match.get('kills')}/{match.get('deaths')}/{match.get('assists')}"
        mode = match.get('gameMode')
        
        prompt += f"\n--- Match {i} ({mode}): {match.get('championName')} ({match.get('role')}) - {win_status} ---\n"
        if mode in ["ARAM", "AAA ARAM"]:
            dmg_pct = match.get('damagePct', 0)
            kp = match.get('killParticipation', 0)
            dmg_gold = match.get('damagePerGold', 0)
            prompt += f"KDA: {kda} | Dmg Share: {dmg_pct}% | Kill Part: {kp}% | Dmg/Gold: {dmg_gold}\n"
        elif "Ranked" in mode:
            cs_min = match.get('csPerMin', 0)
            gold_diff = match.get('goldDiff15', 0)
            prompt += f"KDA: {kda} | CS/Min: {cs_min} | Gold Diff @ 15m: {gold_diff}\n"
            details = match.get("detailed_analysis_metrics", {})
            if details:
                challenges = details.get('challenges', {})
                prompt += f"Damage Dealt to Champs: {details.get('totalDamageDealtToChampions', 0)} | Damage Taken: {details.get('totalDamageTaken', 0)}\n"
                prompt += f"Objective Damage (Turrets, Dragons): {details.get('damageDealtToObjectives', 0)} | Turret Damage: {details.get('damageDealtToTurrets', 0)}\n"
                prompt += f"Vision Details: Base score {details.get('visionScore', 0)}, Wards Placed {details.get('wardsPlaced', 0)}, Wards Killed {details.get('wardsKilled', 0)}, Control Wards {details.get('visionWardsBoughtInGame', 0)}\n"
                prompt += f"Laning Phase: Solo Kills {challenges.get('soloKills', 0)}, Lane Adv % {round(challenges.get('laningPhaseGoldExpAdvantage', 0)*100, 1)}%, CS Adv @15 {challenges.get('maxCsAdvantageOnLaneOpponent', 0)}\n"
                prompt += f"Fights & Map: Kill Part {round(challenges.get('killParticipation', 0)*100, 1)}%, Dmg Share {round(challenges.get('teamDamagePercentage', 0)*100, 1)}%, Skirmishes Won {challenges.get('skirmishClashWon', 0)}\n"
                prompt += f"Misc: CC Time {details.get('timeCCingOthers', 0)}s, First Blood {details.get('firstBloodKill', False)}\n"
        else:
            cs_min = match.get('csPerMin', 0)
            gold_diff = match.get('goldDiff15', 0)
            vs = match.get('visionScore', 0)
            wards = match.get('wardsPlaced', 0)
            prompt += f"KDA: {kda} | CS/Min: {cs_min} | Gold Diff @ 15m: {gold_diff} | Vision: {vs} (Wards: {wards})\n"

    prompt += "\n### Coaching Request:\n"
    prompt += "Your name is Duong. Start your response by introducing yourself as Duong.\n"
    if game_type in ["ARAM", "AAA_ARAM"]:
        prompt += "- Analyze their playstyle based on the ARAM metrics provided: Damage Percentage, Kill Participation, and Damage-to-Gold ratio.\n"
        prompt += "- Keep your analysis exceptionally SHORT, concise, and straight to the point.\n"
        prompt += "- Do NOT provide specific mechanics for the exact champion. Focus purely on general archetype performance (e.g., 'As a Mage in ARAM, your damage share is low...', 'As a Tank, your KP is high...').\n"
        prompt += "- Highlight their strengths and one critical area to improve based strongly on the KDA, Damage%, KP%, and Dmg/Gold data.\n\n"
    elif game_type == "RANKED":
        prompt += "- You have been provided with an EXHAUSTIVE, rich dataset of Ranked match metrics (including objective damage, laning phase advantages, skirmishes, CC time, and granular vision control).\n"
        prompt += "- Perform a DEEP, INSIGHTFUL analysis of their playstyle based on their champion archetype (e.g., Mage, Brawler, Support, ADC, Jungler, Assassin).\n"
        prompt += "- Expand your analysis length significantly to provide longer, highly actionable insights. Break down what they are doing correctly and incorrectly in the laning phase vs. teamfights vs. map macro.\n"
        prompt += "- Find hidden patterns in the advanced stats (e.g., 'Your CS/min is fine, but your Lane Adv % is hugely negative, meaning you bleed pressure early...').\n\n"
    else:
        prompt += "- Condense the data to identify their general playstyle based on the champion archetype (e.g., Mage, Brawler, Support, ADC, Jungler, Assassin).\n"
        prompt += "- Keep your analysis exceptionally SHORT, concise, and straight to the point.\n"
        prompt += "- Do NOT provide specific mechanics for the exact champion. Focus purely on general archetype performance principles (e.g., 'As a Mage, your CS/min is low and you fall behind in gold early...').\n"
        prompt += "- Highlight their strengths and one critical area to improve based strongly on the KDA, CS/min, gold diff, and vision data provided.\n\n"
    prompt += "Format your response in Markdown, using bold text for emphasis."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return f"Sorry, I encountered an error while analyzing your stats: {e}"
