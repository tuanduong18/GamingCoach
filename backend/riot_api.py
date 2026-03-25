import os
from riotwatcher import LolWatcher, RiotWatcher, ApiError
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")
if not api_key:
    raise ValueError("RIOT_API_KEY environment variable is missing")

lol_watcher = LolWatcher(api_key)
riot_watcher = RiotWatcher(api_key)

def get_summoner_data(game_name: str, tag_line: str, region: str = "na1", gameType: str = "ALL"):
    """
    Fetches the summoner's PUUID and comprehensive stats.
    The RIOT ID is structured as gameName#tagLine.
    Note: 'americas', 'europe', 'asia', 'esports' are the routing regions for account-v1.
    """
    try:
        # 1. Get PUUID by Riot ID
        # Route mapping: 'na1', 'br1', 'la1', 'la2' -> 'americas'
        # Let's map typical server regions to their routing values for account v1.
        account_routing = "americas"
        match_routing = "americas"
        region_lower = region.lower()
        if region_lower in ["euw1", "eun1", "tr1", "ru"]:
            account_routing = "europe"
            match_routing = "europe"
        elif region_lower in ["kr", "jp1"]:
            account_routing = "asia"
            match_routing = "asia"
        elif region_lower in ["sg2", "ph2", "tw2", "vn2", "th2", "oc1"]:
            account_routing = "asia"
            match_routing = "sea"

        account = riot_watcher.account.by_riot_id(account_routing, game_name, tag_line)
        puuid = account['puuid']
        
        # 2. Get Summoner details by PUUID (for summonerId, profileIconId, etc)
        # We need the platform routing value for this (e.g. 'na1', 'kr', 'euw1')
        summoner = lol_watcher.summoner.by_puuid(region, puuid)
        
        # 3. Get recent match IDs
        kwargs = {"count": 40}
        if gameType == "RANKED":
            kwargs["type"] = "ranked"
        elif gameType == "UNRANKED_SR":
            kwargs["type"] = "normal"
        elif gameType == "ARAM":
            kwargs["queue"] = 450
        elif gameType == "AAA_ARAM":
            kwargs["queue"] = 720
            
        match_ids = lol_watcher.match.matchlist_by_puuid(match_routing, puuid, **kwargs)
        
        # 4. Get Match Details
        matches = []
        for match_id in match_ids:
            if len(matches) >= 20:
                break
                
            match_detail = lol_watcher.match.by_id(match_routing, match_id)
            info = match_detail['info']
            queue_id = info.get('queueId')
            game_mode = info.get('gameMode')
            
            display_mode = game_mode
            if queue_id == 420:
                display_mode = "Ranked Solo/Duo"
            elif queue_id == 440:
                display_mode = "Ranked Flex"
            elif queue_id in [400, 430, 490]:
                display_mode = "Unranked SR"
            elif queue_id == 450:
                display_mode = "ARAM"
            elif queue_id == 720:
                display_mode = "AAA ARAM"
            elif queue_id == 1900 or queue_id == 900:
                display_mode = "URF"
            elif queue_id == 1700:
                display_mode = "Arena"
            
            if gameType == "UNRANKED_SR" and queue_id not in [400, 430, 490]:
                continue
            if gameType == "EVENT" and queue_id in [420, 440, 400, 430, 490, 450]:
                continue
                
            # Find our player in the match
            my_participant = None
            for participant in info['participants']:
                if participant.get('puuid') == puuid:
                    my_participant = participant
                    break
                    
            if my_participant:
                role = my_participant.get("teamPosition")
                raw_role = my_participant.get("teamPosition") # keep raw for opp matching
                if role == "UTILITY":
                    role = "Support"
                    
                cs = my_participant.get("totalMinionsKilled", 0) + my_participant.get("neutralMinionsKilled", 0)
                duration_mins = info['gameDuration'] / 60.0
                cs_per_min = round(cs / duration_mins, 1) if duration_mins > 0 else 0
                
                wards_placed = my_participant.get("wardsPlaced", 0)
                vision_score = my_participant.get("visionScore", 0)
                
                challenges = my_participant.get("challenges", {})
                dmg_pct = round(challenges.get("teamDamagePercentage", 0) * 100, 1)
                kp = round(challenges.get("killParticipation", 0) * 100, 1)
                
                dmg = my_participant.get("totalDamageDealtToChampions", 0)
                gold = my_participant.get("goldEarned", 1)
                dmg_per_gold = round(dmg / gold, 2) if gold > 0 else 0
                
                gold_diff_15 = 0
                gold_diff_over_time = []
                try:
                    if display_mode in ["Ranked Solo/Duo", "Ranked Flex", "Unranked SR"]:
                        timeline = lol_watcher.match.timeline_by_match(match_routing, match_id)
                        frames = timeline['info']['frames']
                        my_p_id = str(my_participant['participantId'])
                        
                        opp_p_id = None
                        for p in info['participants']:
                            if p['teamPosition'] == raw_role and p['teamId'] != my_participant['teamId']:
                                opp_p_id = str(p['participantId'])
                                break
                                
                        if opp_p_id:
                            for idx, f in enumerate(frames):
                                pf = f['participantFrames']
                                if my_p_id in pf and opp_p_id in pf:
                                    diff = pf[my_p_id]['totalGold'] - pf[opp_p_id]['totalGold']
                                    gold_diff_over_time.append({"minute": idx, "goldDiff": diff})
                                    if idx == 15:
                                        gold_diff_15 = diff
                        elif len(frames) > 15:
                            frame_15 = frames[15]['participantFrames']
                            if my_p_id in frame_15:
                                my_gold = frame_15[my_p_id]['totalGold']
                except Exception as e:
                    print(f"Timeline error: {e}")
                    
                matches.append({
                    "matchId": match_id,
                    "gameMode": display_mode,
                    "gameDuration": info['gameDuration'],
                    "championName": my_participant.get("championName"),
                    "kills": my_participant.get("kills", 0),
                    "deaths": my_participant.get("deaths", 0),
                    "assists": my_participant.get("assists", 0),
                    "win": my_participant.get("win"),
                    "totalMinionsKilled": my_participant.get("totalMinionsKilled", 0),
                    "neutralMinionsKilled": my_participant.get("neutralMinionsKilled", 0),
                    "csPerMin": cs_per_min,
                    "visionScore": vision_score,
                    "wardsPlaced": wards_placed,
                    "goldDiff15": gold_diff_15,
                    "goldDiffOverTime": gold_diff_over_time,
                    "damagePct": dmg_pct,
                    "killParticipation": kp,
                    "damagePerGold": dmg_per_gold,
                    "role": role,
                    "detailed_analysis_metrics": my_participant if display_mode in ["Ranked Solo/Duo", "Ranked Flex"] else None
                })
        
        return {
            "account": account,
            "summoner": summoner,
            "recent_matches": matches
        }
    except ApiError as err:
        print(f"Riot API Error: {err}")
        return None
