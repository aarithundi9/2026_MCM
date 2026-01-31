# Quick Start Guide: Next Steps for MCM Problem C

## You Are Here: Step 10 Complete ✅

You have:
1. Estimated fan votes for every contestant every week
2. Validated the model (80%+ accuracy)
3. Compared rank vs percentage combining methods
4. Identified where methods disagree

## Immediate Next Step: Step 11 - Controversial Cases

### The Four Famous Controversies

#### Case 1: Season 2 - Jerry Rice (Runner-up)
**The Story:** Former NFL player who made it to 2nd place
**Judge Opinion:** Gave him relatively low scores compared to winner (Kelly Monaco)
**Fan Opinion:** Consistently voted him through
**Your Task:**
- Extract Jerry's weekly judge scores vs winner's
- Estimate Jerry's fan votes
- Apply rank method: would he still make top 2?
- Apply percentage method: would he still make top 2?
- Show week-by-week where he was saved despite poor judges

**SQL/Code Snippet Needed:**
```python
jerry_data = df[df['celebrity_name'] == 'Jerry Rice']
winner_data = df[(df['season'] == 2) & (df['placement'] == 1)]
# Compare weekly judge scores
# Show which weeks Jerry's judge score < winner's judge score
# But Jerry advances while winner does too (both survive that week)
```

#### Case 2: Season 4 - Billy Ray Cyrus (5th Place)
**The Story:** Country singer who lasted to semi-finals
**Judge Opinion:** Last place judge scores in 6 weeks
**Fan Opinion:** Kept voting him through
**Your Task:**
- List all 6 weeks where Billy Ray had last-place judge scores
- Show estimated fan votes for those weeks
- Explain: how did fans overcome judges 6 times?

#### Case 3: Season 11 - Bristol Palin (3rd Place, Semi-finalist)
**The Story:** Politically divisive contestant (Sarah Palin's daughter)
**Judge Opinion:** Lowest judge scores 12 times (more than any other contestant)
**Fan Opinion:** 3rd place finish (semi-finals)
**Your Task:**
- Analyze the 12 weeks she had lowest judge scores
- Show estimated fan vote margin that kept her in
- Quantify: "fan votes had to overcome by X points each time"
- Political divide hypothesis: split fan base voting strategically?

#### Case 4: Season 27 - Bobby Bones (WINNER)
**The Story:** Radio personality who won the entire season
**Judge Opinion:** Consistently ranked near bottom by judges
**Fan Opinion:** Clear winner via fan votes
**Your Task:**
- Compare Bobby's average judge score vs average fan vote
- How unusual is this outcome?
- Calculate: how much would judges need to value his entertainment to justify the win?

### How to Analyze Each Case

```python
# For each controversial contestant:

# 1. Get their weekly data
contestant_data = df[df['celebrity_name'] == 'Jerry Rice']

# 2. Extract judge scores and eliminations
for week in range(1, max_week + 1):
    judge_cols = [f'week{week}_judge{i}_score' for i in range(1, 5)]
    judge_score = contestant_data[judge_cols].mean()
    
    # Get estimated fan votes from our model
    fan_votes = all_estimated_df[
        (all_estimated_df['celebrity_name'] == 'Jerry Rice') &
        (all_estimated_df['week'] == week)
    ]['fan_votes_estimate'].values[0]
    
    # Apply both methods
    rank_combined = contestant_data['judge_rank'] + contestant_data['fan_rank']
    pct_combined = (judge_pct + fan_pct) / 2
    
    # Who would eliminate with each method?
    # (Record lowest scores)

# 3. Compare to actual elimination
# If Jerry didn't eliminate week 5:
#   - With rank method: would he still not eliminate?
#   - With pct method: would he still not eliminate?
#   - Or would one method have eliminated him?

# 4. Visualize the timeline
# Show weekly judge scores vs estimated fan votes
# Highlight weeks where methods disagreed
```

### Expected Output for Each Case

A table showing:
```
Week | Judge_Score | Judge_Rank | Fan_Votes_Est | Fan_Rank | Rank_Method_Result | Pct_Method_Result | Actual_Result | Both_Agree?
---- | ----------- | ---------- | ------------- | -------- | ------------------- | ----------------- | ------------- | -----------
  1  |    7.5      |     4      |     75        |    4     | Doesn't Eliminate   | Doesn't Eliminate | Doesn't Elim  |    Yes
  2  |    6.5      |     6      |     68        |    5     | Doesn't Eliminate   | ELIMINATES*       | Doesn't Elim  |    No
  3  |    8.0      |     3      |     82        |    3     | Doesn't Eliminate   | Doesn't Eliminate | Doesn't Elim  |    Yes
...
```

Then answer: "With rank method, Jerry makes it to X. With pct method, Jerry makes it to Y. Actually, Jerry made it to Z."

### Files to Check

In your notebook, you should have:
- `all_estimated_df` - estimated fan votes for all contestants all weeks
- `comparison_df` - rank vs percentage method results
- `df` - original data with judge scores

---

## How This Fits Into Your Report

The controversial cases section (3-4 pages) will:

1. **Describe each case** (1 page)
   - Who was it?
   - Why was it controversial?
   - What happened?

2. **Show the analysis** (2 pages)
   - Judge vs fan scores for each case
   - Rank method results
   - Percentage method results
   - What-if scenarios

3. **Answer key questions** (1 page)
   - Would different methods change outcomes?
   - How much did fans have to overcome judges?
   - What does this tell us about system fairness?

---

## Code Template to Get Started

```python
# Step 11: Controversial Cases Analysis

controversial_cases = [
    ('Jerry Rice', 2),
    ('Billy Ray Cyrus', 4),
    ('Bristol Palin', 11),
    ('Bobby Bones', 27)
]

results = []

for name, season in controversial_cases:
    celeb_data = all_estimated_df[
        (all_estimated_df['celebrity_name'] == name) & 
        (all_estimated_df['season'] == season)
    ]
    
    print(f"\n{'='*80}")
    print(f"CASE: {name} (Season {season})")
    print(f"{'='*80}")
    
    # Get final placement from original data
    final_placement = df[
        (df['celebrity_name'] == name) & 
        (df['season'] == season)
    ]['placement'].values[0]
    
    print(f"Final Placement: {final_placement}")
    
    # Show week-by-week breakdown
    print(f"\nWeek-by-Week Analysis:")
    for week in sorted(celeb_data['week'].unique()):
        week_data = celeb_data[celeb_data['week'] == week].iloc[0]
        print(f"  Week {int(week)}: Judge={week_data['judge_score']:.1f}, " +
              f"Fans={week_data['fan_votes_estimate']:.1f}, " +
              f"Rank_Rank={week_data['judge_rank']:.0f}, " +
              f"Was_Elim={week_data['was_eliminated']}")
    
    results.append({
        'name': name,
        'season': season,
        'final_placement': final_placement,
        'data': celeb_data
    })
```

---

## Success Criteria for Step 11

✓ Analysis of all 4 controversial cases  
✓ Comparison of rank vs percentage methods for each  
✓ Clear explanation of why each was "controversial"  
✓ Evidence showing fan votes overcoming judge scores  
✓ Quantified margins showing how close the outcomes were  
✓ Visualization (timeline showing judge vs fan support)  

---

## Time Estimate
- Data preparation: 30 minutes
- Analysis: 1 hour
- Visualization: 30 minutes
- Writing explanation: 1 hour
- **Total: 3 hours**

---

*Once you complete Step 11, notify to proceed with Step 12 (Pro Dancers & Demographics)*
