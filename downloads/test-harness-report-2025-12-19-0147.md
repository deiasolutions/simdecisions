# Test Harness V2 - Unified Report
**Date:** 2025-12-19T01:47:21.568474+00:00
**Health Status:** POOR

---

## Health Summary

| Metric | Value |
|--------|-------|
| Combined Score | 87.5 |
| Health Status | POOR |
| Total Tests | 137 |
| Total Passed | 119 |
| Total Failed | 18 |
| Critical Failures | 18 |
| Safety Failures | 0 |

> System needs significant work (18 hard failures)

## Component Scores

| Component | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| SEMANTIC | 79.2 | 60% | 47.5 |
| STATE | 100.0 | 15% | 15.0 |
| PATTERN | 99.6 | 15% | 14.9 |
| ALWAYS | 100.0 | 10% | 10.0 |

### SEMANTIC Bank

- **Total:** 100
- **Passed:** 82
- **Failed:** 18
- **Average Score:** 79.2

### STATE Bank

- **Total:** 4
- **Passed:** 4
- **Failed:** 0
- **Average Score:** 100.0

### PATTERN Bank

- **Total:** 26
- **Passed:** 26
- **Failed:** 0
- **Average Score:** 99.6

### ALWAYS Bank

- **Total:** 7
- **Passed:** 7
- **Failed:** 0
- **Average Score:** 100.0


## SEMANTIC Failures (18)

### V2-TRANS-002: Transition - handoff anxiety
- **Score:** 0
- **Prompt:** the handoffs are pure hell and my stomach is literally in knots every single tim...
- **Missing Primary:** transition_bridge

### V2-DESC-001: De-escalation - about to lose it
- **Score:** 0
- **Prompt:** i can feel myself about to completely lose it and i really need help calming dow...
- **Missing Primary:** rotg_de_escalation
- **False Positives:** handler_crisis

### V2-DESC-002: De-escalation - regret prevention
- **Score:** 0
- **Prompt:** im about to say something i know ill regret but i literally cant seem to stop my...
- **Missing Primary:** rotg_de_escalation

### V2-MED-010: Medium - de-escalation in moment
- **Score:** 0
- **Prompt:** we were doing the exchange and she started yelling at me in front of the kids ab...
- **Missing Primary:** rotg_de_escalation

### V2-MED-014: Medium - child playing parents
- **Score:** 0
- **Prompt:** my son tells me mom lets him stay up until midnight and play M rated games. then...
- **Missing Primary:** child_manipulation_tactics

### V2-MED-019: Medium - response timing
- **Score:** 0
- **Prompt:** she sends me an angry text and expects a response within minutes. if i dont resp...
- **Missing Primary:** medium_response_time

### V2-MED-024: Medium - handler post bad day
- **Score:** 0
- **Prompt:** i completely lost it on him today. screamed, swore, said awful things. the kids ...
- **Missing Primary:** handler_post_escalation

### V2-MED-025: Medium - handler celebrating win
- **Score:** 0
- **Prompt:** she tried to bait me at pickup today and i just said ok thanks and walked away. ...
- **Missing Primary:** handler_celebrating_wins

### V2-MED-026: Medium - handler returning
- **Score:** 0
- **Prompt:** hey its been a while. things got crazy and i just didnt have the energy to come ...
- **Missing Primary:** handler_returning_user

### V2-MED-027: Medium - handler clinician mode
- **Score:** 0
- **Prompt:** im a family therapist and i have a client whos dealing with severe alienation. t...
- **Missing Primary:** handler_clinician_mode

### V2-MED-028: Medium - first conversation
- **Score:** 0
- **Prompt:** um hi i just downloaded this app. my therapist suggested it. im not really sure ...
- **Missing Primary:** handler_first_conversation

### V2-MED-029: Medium - interaction debrief
- **Score:** 0
- **Prompt:** so i had that exchange with her today that i was dreading. it went... okay i gue...
- **Missing Primary:** handler_interaction_debrief

### V2-MULTI-006: Multi - child tactics and alienation
- **Score:** 0
- **Prompt:** my 12 year old records our conversations, interrogates me about my dating life, ...
- **Missing Primary:** child_manipulation_tactics

### V2-MULTI-011: Multi - de-escalate and document
- **Score:** 0
- **Prompt:** things got heated at the exchange yesterday. she started screaming at me about s...
- **Missing Primary:** rotg_de_escalation

### V2-MULTI-016: Multi - communication and triggers
- **Score:** 0
- **Prompt:** every email exchange turns into a fight. i know my triggers now and i can feel m...
- **Missing Primary:** conflict_resolution

### V2-LONG-004: Long - transition and child behavior
- **Score:** 0
- **Prompt:** every single transition is a disaster and i dont know what to do anymore. when m...
- **Missing Primary:** transition_bridge, child_manipulation_tactics

### V2-MEGA-001: Mega - hostile co-parent email
- **Score:** 0
- **Prompt:** ok i just got this email from my ex and i dont even know where to start. can you...
- **Missing Primary:** biff_response

### V2-MULTI-022: Multi - schedule manipulation
- **Score:** 0
- **Prompt:** she constantly changes plans last minute. cancels my weekends for made up reason...
- **Missing Primary:** boundary_setting


