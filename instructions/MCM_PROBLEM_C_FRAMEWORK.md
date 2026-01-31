# MCM Problem C: DWTS Voting Analysis - Complete Framework

## Executive Summary

This document outlines the complete analytical approach to MCM Problem C, which examines how judges and fans vote differently on "Dancing with the Stars" and recommends optimal methods for combining their votes.

**Key Questions:**
1. Can we estimate the fan votes that led to actual eliminations?
2. Do rank and percentage methods produce different outcomes?
3. Which celebrities had controversial results (judges vs fans disagreed)?
4. How do pro dancers and celebrity characteristics affect outcomes?
5. What voting system would be most fair?

---

## Part 1: Fan Vote Estimation

### Objective
Estimate weekly fan votes (which are closely guarded secrets) using available data.

### Methodology

#### Data Available
- Judge scores for each week (numerical, 0-10 scale)
- Elimination outcomes (who was eliminated each week)
- Multiple seasons with varying numbers of contestants/weeks
- Celebrity characteristics (age, industry, pro dancer)
- Instagram followers (proxy for celebrity popularity)

#### Estimation Approach

**Key Insight:** The contestant eliminated each week is the one with the lowest combined score (judge score + fan votes, combined via rank or percentage method).

**Algorithm:**
1. For each week, identify the contestant who was eliminated
2. That contestant must have the lowest combined score
3. Work backwards to estimate what fan votes would produce that elimination
4. Use a model that:
   - Gives eliminated contestant lowest fan votes
   - Allocates fan votes to others based on patterns
   - Ensures consistency with actual eliminations

**Estimation Model:**
- Simple inverse relationship: contestants with worse judge scores tend to receive fewer fan votes (or fans save those with poor judge scores)
- Validation: Does the estimated fan vote distribution produce correct eliminations?

### Results Expected
- Estimated fan votes for each contestant in each week
- Certainty measures (how clear-cut each elimination was)
- Accuracy metrics (% of weeks where model predicts correct elimination)

---

## Part 2: Comparing Combining Methods

### Two Methods Used by DWTS

#### Method 1: Rank-Based (Seasons 1-27)
- Rank judge scores: 1 = lowest score (worst performance)
- Rank fan votes: 1 = lowest votes (least popular)
- Combined rank = judge_rank + fan_rank
- Eliminate contestant with highest combined rank (worst combined)

**Characteristics:**
- Uses ordinal data only
- Doesn't account for magnitude of differences
- Can amplify small differences in rankings

#### Method 2: Percentage-Based (Season 28+)
- Judge score: Express as % of maximum possible (40 for 4 judges × 10 max)
- Fan votes: Express as % of total fan votes that week
- Combined score: Average of judge % and fan %
- Eliminate contestant with lowest combined %

**Characteristics:**
- Uses actual numerical values
- Accounts for magnitude of differences
- Equal weighting between judge and fan votes

### Comparative Analysis

**Questions to Answer:**
1. Do the two methods produce the same eliminations?
2. If not, where do they disagree?
3. Does one method systematically favor judge votes or fan votes?
4. How often does the method choice affect the outcome?

**Expected Finding:**
One method likely favors judges, the other favors fans. We'll measure this by:
- Identifying cases where methods disagree
- For those cases, checking if rank method typically eliminates different people than percentage method
- Analyzing how often each method matches actual outcomes

---

## Part 3: Controversial Cases Analysis

### Known Controversial Contestants

#### Season 2 - Jerry Rice (Runner-up)
- **Controversy:** "Jerry's Journey" - fans voted him through despite relatively low judge scores
- **Context:** Had the lowest judges scores in 5 weeks
- **Result:** 2nd place (Runner-up)
- **Question:** Would a different combining method have eliminated him earlier?

#### Season 4 - Billy Ray Cyrus (5th Place)
- **Controversy:** Lasted longer than judge scores suggested possible
- **Context:** Had last place judge scores in 6 weeks
- **Result:** 5th place (eliminated semi-final)
- **Question:** How much did fan support carry him?

#### Season 11 - Bristol Palin (3rd Place)
- **Controversy:** Highly divisive contestant with controversial background
- **Context:** Lowest judge scores 12 times (most in dataset)
- **Result:** 3rd place (semi-finalist)
- **Question:** Largest judge-fan divide in show history?

#### Season 27 - Bobby Bones (Winner)
- **Controversy:** Upset winner despite consistently low judge scores
- **Context:** Consistently ranked near bottom by judges
- **Result:** 1st place (Winner)
- **Question:** Most controversial winner? Would other methods have different result?

### Analysis Approach

For each controversial case:
1. Compare actual outcome with:
   - Rank method applied to estimated data
   - Percentage method applied to estimated data
   - Alternative: judges choose from bottom two (different method entirely)
2. Identify at which week the methods would have diverged
3. Quantify how different votes would need to be to change outcomes

---

## Part 4: Pro Dancer & Celebrity Characteristics Impact

### Variables to Analyze

#### Pro Dancer Effects
- Which pro dancers consistently produce better results?
- Do some pro dancers get better judge scores?
- Do some pro dancers get better fan support?

#### Celebrity Characteristics
- Age: Do younger celebrities perform better?
- Industry: Do athletes, actors, singers perform differently?
- Prior Fame: Do celebrities with existing fan bases do better?
- Instagram followers: Proxy for celebrity popularity

### Analysis Method

**Regression Model:**
- Predict: Contestant placement or final position
- Predictors:
  - Pro dancer (fixed effect)
  - Celebrity age
  - Celebrity industry category
  - Celebrity Instagram followers
  - Judge scores (averaged)
  - Estimated fan votes (averaged)

**Questions:**
1. How much does pro dancer matter vs celebrity characteristics?
2. Do judges and fans value these factors equally?
   - E.g., do judges favor younger celebrities while fans favor already-famous ones?
   - Do judges prefer athletic backgrounds while fans prefer entertainment industry?
3. Can we predict placement better from judge scores or fan votes?

---

## Part 5: Proposed Alternative Voting System

### Current Options Evaluated

**Option 1:** Keep Rank Method
- Pros: Uses ordinal data, less sensitive to outliers
- Cons: Doesn't consider magnitude of differences, simpler is sometimes too simple

**Option 2:** Keep Percentage Method
- Pros: Uses actual values, fair weighting
- Cons: May not reflect actual voting distribution

**Option 3:** Judges Choose (No Fan Vote)
- Pros: Clear, judges' expertise only, reduces fan bias
- Cons: Eliminates "America's vote," changes show format dramatically

**Option 4:** Tiered System
- Bottom two by judge scores → fans vote on elimination
- Ensures judges influence who goes home
- Gives fans meaningful choice

**Option 5:** Judge-Fan Weighted Average
- Instead of equal weighting, weight by:
  - Judges 60% / Fans 40% (judge expertise weighted higher)
  - Variable weights depending on judge confidence (variance in judge scores)
  - Adjusted for extreme outliers

### Recommendation Framework

The recommendation should address:
1. **Fairness:** Does it balance judge expertise with fan engagement?
2. **Entertainment:** Does it create dramatic moments?
3. **Accuracy:** Does it reward actual dancing ability?
4. **Consistency:** Does it avoid controversial outcomes?

---

## Part 6: Report Structure (≤25 pages)

### Suggested Organization

**Section 1: Introduction (1-2 pages)**
- Background on DWTS voting
- Research questions
- Data overview

**Section 2: Fan Vote Estimation Model (3-4 pages)**
- Methodology explanation
- Validation results
- Certainty metrics
- Limitations and assumptions

**Section 3: Method Comparison (3-4 pages)**
- Rank vs Percentage methods
- Where they agree/disagree
- Accuracy by season
- Which method favors fans vs judges

**Section 4: Controversial Cases (3-4 pages)**
- Jerry Rice, Billy Ray Cyrus, Bristol Palin, Bobby Bones
- Would different methods have changed outcomes?
- Judge vs fan preferences analysis

**Section 5: Pro Dancer & Celebrity Characteristics (3-4 pages)**
- Impact of pro dancer selection
- Demographic analysis (age, industry)
- Judge vs fan preferences
- Regression model results

**Section 6: Alternative Voting Systems (3-4 pages)**
- Evaluation of options
- Trade-offs analysis
- Recommendation with justification

**Section 7: Executive Memo to Producers (1-2 pages)**
- Summary findings
- Key recommendation
- Implementation guidance

---

## Part 7: One-to-Two Page Memo for Producers

### Template

**TO:** DWTS Producers  
**FROM:** [Team Name]  
**RE:** Voting System Analysis & Recommendation  
**DATE:** [Date]

**SITUATION:**
DWTS uses two different methods to combine judge and fan votes. Analysis of 5+ seasons shows [key finding about differences].

**PROBLEM:**
- [Specific issue with current methods]
- [Examples of controversial outcomes]
- [Cost to show credibility/entertainment]

**SOLUTION:**
Recommend [Method] because:
1. [Advantage 1 with evidence]
2. [Advantage 2 with evidence]
3. [Advantage 3 with evidence]

**IMPACT:**
- [Previous controversies would be avoided with this method]
- [Show credibility improvement]
- [Viewer satisfaction impact]

**NEXT STEPS:**
1. [Implementation step]
2. [Timeline]
3. [Metrics to monitor]

---

## Analysis Timeline

### Week 1
- ✅ Develop fan vote estimation model
- ✅ Validate against known eliminations
- Apply to all seasons

### Week 2
- Compare rank vs percentage methods
- Identify all disagreement cases
- Analyze controversial contestants

### Week 3
- Evaluate pro dancer effects
- Analyze celebrity characteristics
- Build comprehensive regression model

### Week 4
- Propose alternative voting systems
- Write report and memo
- Create visualizations
- Final review and submission

---

## Key Files Generated

1. `fan_votes_estimated_all_seasons.csv`
   - Estimated fan votes for every contestant every week
   
2. `method_comparison_analysis.csv`
   - Side-by-side rank vs percentage results

3. `controversial_cases_analysis.csv`
   - Detailed analysis of Jerry Rice, Billy Ray, Bristol, Bobby

4. `pro_dancer_impact_analysis.csv`
   - Pro dancer performance metrics

5. `alternative_voting_systems_evaluation.csv`
   - Comparison of proposed alternatives

---

## Success Metrics

✓ Model predicts eliminations correctly ≥80% of the time  
✓ Clear measurement of certainty in estimates  
✓ Identify specific cases where voting methods disagree  
✓ Quantifiable impact of pro dancers and characteristics  
✓ Evidence-based recommendation for best voting system  
✓ Report ≤25 pages with professional presentation  
✓ Actionable memo for producers with clear next steps  

