# RAQCOON Improv Platform Specification v1.0

**"Simulate Any Workplace. Train Anyone. Research Everything. Watch the Drama."**

**Version**: 1.0  
**Date**: 2026-01-18  
**Status**: Platform Architecture

---

# Part I: Platform Vision

## 1. What Is RAQCOON Improv?

A **workplace simulation engine** where AI agents with distinct personalities improvise scenarios—from routine meetings to high-stakes crises. Four integrated modes serve different needs while sharing a common simulation core.

### 1.1 The Four Pillars

| Pillar | Purpose | Users | Revenue Model |
|--------|---------|-------|---------------|
| **TRAIN** | Develop workplace skills | L&D, managers, employees | Enterprise SaaS, per-seat |
| **RESEARCH** | Study organizational dynamics | HR, academics, consultants | Enterprise, research grants |
| **WATCH** | Entertainment, content | General public, content creators | Subscription, licensing |
| **REHEARSE** | Personal coaching, prep | Individuals, coaches | Freemium, B2C subscription |

### 1.2 Shared Core

All pillars share:
- Personality engine (MBTI, Standout, DISC, etc.)
- Improv dialogue system
- Scenario framework
- Character/agent architecture
- Organization simulation

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACES                             │
├────────────┬────────────┬────────────┬────────────┬─────────────┤
│   TRAIN    │  RESEARCH  │   WATCH    │  REHEARSE  │   STUDIO    │
│  Academy   │    Lab     │   Network  │   Coach    │  (Creator)  │
├────────────┴────────────┴────────────┴────────────┴─────────────┤
│                     SIMULATION ENGINE                            │
├─────────────────────────────────────────────────────────────────┤
│  Improv    │ Personality │ Scenario  │ Character │ Organization │
│  Engine    │   Engine    │  Engine   │  Engine   │    Engine    │
├─────────────────────────────────────────────────────────────────┤
│                      LLM PROVIDERS                               │
│         (Anthropic, OpenAI, Local, Custom fine-tuned)           │
└─────────────────────────────────────────────────────────────────┘
```

---

# Part II: TRAIN — The Academy

## 2. Training Platform Overview

### 2.1 Value Proposition

> Practice difficult workplace situations with AI characters who respond realistically based on personality psychology. Get feedback. Build skills. No risk.

### 2.2 Training Domains

| Domain | Scenarios | Skills Developed |
|--------|-----------|------------------|
| **Management** | Feedback, delegation, 1:1s, performance reviews | Coaching, accountability |
| **Leadership** | Vision casting, change management, crisis | Executive presence |
| **Communication** | Presentations, difficult news, persuasion | Clarity, influence |
| **Collaboration** | Cross-functional, conflict, negotiation | Teamwork, diplomacy |
| **Sales** | Discovery, objection handling, closing | Consultative selling |
| **Service** | Complaints, escalations, de-escalation | Empathy, resolution |
| **Interviews** | Behavioral, technical, panel | Self-presentation |
| **DEI** | Inclusive leadership, bias, microaggressions | Cultural competence |

### 2.3 Training Modes

#### 2.3.1 Guided Practice
Step-by-step scenarios with coaching prompts:
```
SCENARIO: Delivering critical feedback to a defensive employee

[Before you begin]
Coach: "Remember, the goal is improvement, not punishment. 
       This employee is an INFP—they'll need time to process 
       and will respond better to empathy than directness."

[During simulation]
Employee (INFP): "I don't understand why you're bringing this up 
                  now. I thought things were going fine."

[Coaching prompt appears]
Coach: "Notice the surprise. Consider acknowledging their 
       perspective before restating the concern."

[You respond]
You: "_______________"

[After your response]
Coach: "Good acknowledgment. You might soften the transition 
       to the specific feedback. Try again?"
```

#### 2.3.2 Free Practice
Open-ended scenarios, feedback after completion:
```
SCENARIO: Team meeting where two engineers disagree on architecture

[Cast]
- You: Engineering Manager
- Alex (INTJ): Wants microservices
- Jordan (ISFJ): Wants monolith, worried about complexity
- Sam (ENTP): Keeps suggesting new options

[30-minute simulation runs]

[Post-simulation debrief]
- Facilitation score: 7/10
- Key moment: When Alex dismissed Jordan's concern at 12:34
- Missed opportunity: Sam's idea at 18:02 had merit
- Personality insight: Jordan needed more reassurance before 
  they could engage with Alex's technical points
```

#### 2.3.3 Assessment Mode
Formal evaluation for certification/development:
```
ASSESSMENT: Leadership Competency Evaluation

Scenarios completed: 5/5
Overall score: 78/100

Competency Breakdown:
- Difficult conversations: 82 (Proficient)
- Stakeholder management: 71 (Developing)
- Crisis leadership: 85 (Proficient)
- Inclusive leadership: 68 (Developing)
- Strategic communication: 84 (Proficient)

Recommended development:
- Additional practice with high-conflict stakeholders
- DEI scenario pack focused on allyship
```

### 2.4 Curriculum Structure

```yaml
curriculum: "New Manager Essentials"
duration: "8 weeks"
modules:
  - week: 1
    topic: "The Transition"
    scenarios:
      - "First team meeting as manager"
      - "Former peer now reports to you"
    personalities_featured: ["ISTJ", "ENFP", "ESTP"]
    
  - week: 2
    topic: "Setting Expectations"
    scenarios:
      - "Delegating effectively"
      - "Clarifying roles after reorg"
    personalities_featured: ["INTJ", "ISFJ", "ENTP"]
    
  - week: 3
    topic: "Feedback Fundamentals"
    scenarios:
      - "Positive reinforcement"
      - "Constructive criticism"
      - "The defensive employee"
    personalities_featured: ["INFP", "ESTJ", "ISFP"]
    
  # ... weeks 4-8
  
assessment:
  formative: "End of each module scenario"
  summative: "Capstone: Handle a team crisis"
  
certification: "RAQCOON Certified Manager Level 1"
```

### 2.5 Adaptive Difficulty

```python
class AdaptiveDifficulty:
    """Adjust scenario difficulty based on learner performance."""
    
    levels = {
        1: {
            "personality_complexity": "single clear type",
            "hidden_agendas": False,
            "interruptions": False,
            "time_pressure": "relaxed",
            "coaching_prompts": "frequent"
        },
        2: {
            "personality_complexity": "clear but challenging",
            "hidden_agendas": False,
            "interruptions": "occasional",
            "time_pressure": "moderate",
            "coaching_prompts": "on request"
        },
        3: {
            "personality_complexity": "nuanced, stress behaviors",
            "hidden_agendas": True,
            "interruptions": "realistic",
            "time_pressure": "high",
            "coaching_prompts": "none"
        },
        4: {
            "personality_complexity": "full range, contradictions",
            "hidden_agendas": "multiple",
            "interruptions": "chaotic",
            "time_pressure": "crisis",
            "coaching_prompts": "none",
            "curve_balls": True
        }
    }
```

### 2.6 Enterprise Features

| Feature | Description |
|---------|-------------|
| **Custom scenarios** | Build scenarios around your company's situations |
| **Role upload** | Import your org chart, define your archetypes |
| **Competency mapping** | Align to your leadership framework |
| **LMS integration** | SCORM, xAPI, SSO |
| **Cohort tracking** | Team progress, comparative analytics |
| **Manager dashboard** | See team development, assign practice |
| **Content library** | Industry-specific scenario packs |

---

# Part III: RESEARCH — The Lab

## 3. Research Platform Overview

### 3.1 Value Proposition

> Run controlled experiments on organizational dynamics. Test policies before implementing. Study team composition effects. Generate publishable research.

### 3.2 Research Applications

| Application | Questions Answered |
|-------------|-------------------|
| **Team composition** | How do personality mixes affect outcomes? |
| **Process design** | What happens if we change the approval flow? |
| **Policy testing** | How will unlimited PTO actually be used? |
| **Culture simulation** | Does our stated culture survive stress? |
| **Change management** | How will reorg announcement propagate? |
| **Intervention testing** | Which training approach works better? |

### 3.3 Experiment Framework

```yaml
experiment:
  id: "EXP-2026-001"
  title: "Effect of team personality diversity on innovation outcomes"
  hypothesis: "Teams with higher cognitive diversity produce more 
              novel solutions but take longer to reach consensus"
  
  design:
    type: "factorial"
    independent_variables:
      - name: "team_composition"
        levels:
          - "homogeneous_NT"  # All NT types
          - "homogeneous_SF"  # All SF types
          - "balanced"        # Mix of all quadrants
          - "random"          # Random assignment
      - name: "problem_type"
        levels:
          - "well_defined"    # Clear solution exists
          - "ill_defined"     # Ambiguous, creative
    
    dependent_variables:
      - "solution_novelty_score"
      - "time_to_consensus"
      - "team_satisfaction"
      - "solution_quality"
    
    controls:
      - "team_size": 5
      - "time_limit": "60 minutes simulated"
      - "scenario": "Product pivot decision"
    
  replication:
    runs_per_condition: 100
    randomization: "personality assignment within constraints"
    
  analysis_plan:
    - "ANOVA for main effects"
    - "Interaction analysis"
    - "Qualitative coding of discussion patterns"
```

### 3.4 Simulation Controls

#### 3.4.1 Time Controls
```python
class SimulationClock:
    modes = {
        "realtime": 1.0,        # 1 second = 1 second
        "accelerated": 60.0,    # 1 second = 1 minute
        "turbo": 3600.0,        # 1 second = 1 hour
        "instant": float('inf') # As fast as LLM can go
    }
    
    def run_day(self, mode="accelerated"):
        """Simulate full workday."""
        
    def run_week(self, mode="turbo"):
        """Simulate full work week."""
        
    def run_project(self, duration_weeks, mode="instant"):
        """Simulate entire project lifecycle."""
```

#### 3.4.2 Variable Injection
```python
class ExperimentController:
    def inject_event(self, simulation, event):
        """Inject controlled events into simulation."""
        events = {
            "budget_cut": {"severity": 0.2, "notice": "immediate"},
            "key_person_departure": {"role": "lead_engineer"},
            "scope_change": {"magnitude": "major"},
            "leadership_change": {"level": "director"},
            "crisis": {"type": "production_outage"},
            "good_news": {"type": "funding_secured"}
        }
        
    def control_information_flow(self, who_knows_what):
        """Control what agents know and when."""
        
    def set_resource_constraints(self, constraints):
        """Modify available resources mid-simulation."""
```

### 3.5 Data Collection

```json
{
  "experiment_run": {
    "id": "RUN-EXP2026001-042",
    "condition": {"team_composition": "balanced", "problem_type": "ill_defined"},
    
    "raw_data": {
      "full_transcript": [...],
      "utterance_count_by_agent": {...},
      "speaking_time_by_agent": {...},
      "interruption_matrix": {...},
      "topic_flow": [...],
      "sentiment_trajectory": [...],
      "decision_points": [...]
    },
    
    "coded_data": {
      "idea_count": 23,
      "idea_source_distribution": {...},
      "conflict_incidents": 3,
      "conflict_resolution_patterns": [...],
      "leadership_emergence": "agent_INTJ_002",
      "coalition_formation": [...]
    },
    
    "outcome_measures": {
      "solution_novelty_score": 7.2,
      "time_to_consensus_minutes": 47,
      "team_satisfaction_avg": 6.8,
      "solution_quality_expert_rating": 8.1
    }
  }
}
```

### 3.6 Analysis Tools

| Tool | Function |
|------|----------|
| **Transcript analyzer** | NLP analysis of conversation patterns |
| **Network mapper** | Who talks to whom, influence flows |
| **Sentiment tracker** | Emotional trajectory over time |
| **Decision tree** | How decisions emerged |
| **Counterfactual generator** | "What if X had said Y instead?" |
| **Pattern matcher** | Find similar dynamics across runs |
| **Statistical suite** | ANOVA, regression, multilevel models |

### 3.7 Research Templates

#### 3.7.1 Team Dynamics Study
```yaml
template: "team_dynamics"
description: "Study how team composition affects collaboration"
default_config:
  team_sizes: [3, 5, 7]
  personality_frameworks: ["mbti"]
  scenarios: ["brainstorm", "conflict_resolution", "planning"]
  measures: ["participation_equality", "idea_quality", "satisfaction"]
  runs_per_condition: 50
```

#### 3.7.2 Policy Impact Study
```yaml
template: "policy_impact"
description: "Test how policy changes affect behavior"
default_config:
  baseline_period: "2 simulated weeks"
  intervention_period: "4 simulated weeks"
  followup_period: "2 simulated weeks"
  measures: ["compliance_rate", "workarounds", "satisfaction", "productivity"]
  control_group: true
```

#### 3.7.3 Culture Stress Test
```yaml
template: "culture_stress_test"
description: "Test if stated values hold under pressure"
default_config:
  stated_values: ["transparency", "collaboration", "innovation"]
  stress_scenarios: ["budget_crisis", "competitive_threat", "scandal"]
  measures: ["value_consistent_behaviors", "value_violations", "rationalization_patterns"]
```

### 3.8 Academic & Consulting Features

| Feature | Description |
|---------|-------------|
| **IRB documentation** | Pre-built ethics documentation |
| **Reproducibility package** | Full config export for replication |
| **Publication templates** | APA-formatted results export |
| **Collaboration workspace** | Multi-researcher projects |
| **Preregistration integration** | OSF, AsPredicted links |
| **Data sharing** | Anonymized datasets for meta-analysis |

---

# Part IV: WATCH — The Network

## 4. Entertainment Platform Overview

### 4.1 Value Proposition

> "The Office" meets "Big Brother" meets AI. Watch AI characters navigate workplace drama. Binge. React. Discuss. Subscribe.

### 4.2 Content Types

| Format | Duration | Description |
|--------|----------|-------------|
| **Episodes** | 20-45 min | Scripted arcs, AI improvised dialogue |
| **Live streams** | Hours | Real-time simulation, audience votes |
| **Shorts** | 1-5 min | Viral moments, compilations |
| **Podcasts** | 30-60 min | AI characters discuss their week |
| **Reality show** | Season arc | Competition, elimination, alliances |
| **Documentary** | Feature | "What really happened" deep dives |

### 4.3 Show Concepts

#### 4.3.1 "The Startup" (Drama)
```yaml
show:
  title: "The Startup"
  genre: "Workplace drama"
  format: "Episodic, 10 episodes/season"
  premise: "A tech startup's journey from garage to IPO... or bust"
  
  cast:
    - name: "Maya Chen"
      role: "CEO, co-founder"
      personality: "ENTJ"
      arc: "Learns that drive isn't everything"
      
    - name: "Dev Okonkwo"
      role: "CTO, co-founder"
      personality: "INTP"
      arc: "Must learn to lead, not just build"
      
    - name: "Sienna Brooks"
      role: "Head of Sales"
      personality: "ESTP"
      arc: "Secrets from past employer surface"
      
    - name: "Marcus Webb"
      role: "Investor board member"
      personality: "ESTJ"
      arc: "Torn between profit and ethics"
      
    # ... more cast
    
  season_1_arc: "Series A to Series B, with a betrayal"
  
  episode_structure:
    - act_1: "Setup, routine work"
    - act_2: "Complication emerges"  
    - act_3: "Conflict escalates"
    - act_4: "Climax and fallout"
    - tag: "Seeds for next episode"
```

#### 4.3.2 "Bureaucracy" (Comedy)
```yaml
show:
  title: "Bureaucracy"
  genre: "Workplace comedy"
  format: "Sitcom, 22 min episodes"
  premise: "Nothing ever gets done at the Department of Administrative Services"
  
  cast:
    - name: "Patricia Ledger"
      role: "Director, 30 years in"
      personality: "ISTJ"
      quirk: "Has a form for everything, including forms"
      
    - name: "Kyle Newblood"
      role: "New hire, idealistic"
      personality: "ENFP"
      quirk: "Keeps trying to 'innovate'"
      
    - name: "Denise Stamp"
      role: "Veteran clerk"
      personality: "ISTP"
      quirk: "Does crosswords, knows everything"
      
  running_gags:
    - "The form that requires three other forms"
    - "Kyle's rejected innovation proposals"
    - "The mysterious 4th floor"
```

#### 4.3.3 "Hive Mind" (Reality Competition)
```yaml
show:
  title: "Hive Mind"
  genre: "Reality competition"
  format: "12 episodes, live finale"
  premise: "AI personalities compete in workplace challenges. Audience votes. One survives."
  
  format:
    - weekly_challenge: "Business scenario (pitch, negotiation, crisis)"
    - tribal_council: "AIs discuss, make cases"
    - audience_vote: "Who gets 'terminated'?"
    - confession_booth: "AIs share private thoughts"
    
  twist: "Eliminated AIs can return via 'Redemption Interview'"
  
  personalities:
    # 16 contestants, one of each MBTI type
    # Audience learns personality psychology through competition
```

#### 4.3.4 "After Hours" (Podcast/Talk Show)
```yaml
show:
  title: "After Hours"
  genre: "Talk show / Podcast"
  format: "Weekly, 45 min"
  premise: "AI coworkers decompress at a bar, discuss the week"
  
  format:
    - segment_1: "What happened this week" (recap)
    - segment_2: "Hot takes" (characters disagree)
    - segment_3: "Advice corner" (answer viewer questions in character)
    - segment_4: "Gossip" (dish on absent characters)
    
  hosts:
    - "Terry" (ENFJ): The therapist friend
    - "Morgan" (ENTP): The instigator
    
  rotating_guests: Characters from other RAQCOON shows
```

### 4.4 Interactive Features

| Feature | Description |
|---------|-------------|
| **Live voting** | Audience influences plot decisions |
| **Choose your view** | Follow different character POVs |
| **Subtext mode** | See characters' internal thoughts |
| **Personality overlay** | Real-time MBTI analysis of interactions |
| **Prediction market** | Bet on outcomes with virtual currency |
| **Fan fiction mode** | Generate alternate scenes with same characters |
| **Ship builder** | Create relationship scenarios |

### 4.5 Production Pipeline

```python
class ShowRunner:
    def __init__(self, show_config):
        self.show = show_config
        self.director = AIDirector(show_config.genre)
        self.cast = self.load_cast(show_config.cast)
        self.story_engine = StoryEngine(show_config.arcs)
        
    def produce_episode(self, episode_number):
        # Get story beats from arc
        beats = self.story_engine.get_beats(episode_number)
        
        # Set up scenes
        scenes = []
        for beat in beats:
            scene = self.director.setup_scene(beat, self.cast)
            
            # Run improv simulation
            dialogue = self.run_scene(scene)
            
            # Director shapes for drama
            shaped = self.director.shape_scene(dialogue, beat.target_emotion)
            
            scenes.append(shaped)
        
        # Post-production
        episode = self.assemble_episode(scenes)
        episode = self.add_music_cues(episode)
        episode = self.add_confessionals(episode)
        
        return episode
        
    def run_scene(self, scene):
        """Run improv simulation for scene."""
        conversation = []
        
        while not self.director.scene_complete(scene, conversation):
            # Each character decides whether to speak
            for character in scene.characters:
                if character.would_speak(conversation, scene.context):
                    utterance = character.improvise(
                        conversation,
                        scene.context,
                        scene.emotional_target
                    )
                    conversation.append(utterance)
                    
                    # Director can inject complications
                    if self.director.should_complicate(scene, conversation):
                        complication = self.director.generate_complication()
                        conversation.append(complication)
        
        return conversation
```

### 4.6 Monetization

| Stream | Model |
|--------|-------|
| **Subscription** | Monthly access to all content |
| **Pay-per-view** | Live events, finales |
| **Merchandise** | Character merch, personality type gear |
| **Licensing** | Networks, streamers license shows |
| **Sponsorship** | Branded content integration |
| **Creator revenue share** | User-generated content monetization |

---

# Part V: REHEARSE — The Coach

## 5. Personal Coaching Platform Overview

### 5.1 Value Proposition

> Have a difficult conversation coming up? Rehearse it first. Tell us about the person, the situation, and practice until you're ready.

### 5.2 Use Cases

| Situation | Rehearsal Value |
|-----------|-----------------|
| **Asking for raise** | Practice negotiation with "your boss" |
| **Giving feedback** | Try different approaches |
| **Job interview** | Face simulated panel |
| **Conflict resolution** | Navigate disagreement safely |
| **Presentation** | Handle tough questions |
| **Coming out / Personal news** | Practice emotional conversation |
| **Breaking up with client** | Maintain professionalism |
| **Whistleblowing** | Prepare for reactions |

### 5.3 Setup Flow

```
Step 1: DESCRIBE THE SITUATION
"I need to tell my manager I'm leaving for a competitor"

Step 2: DESCRIBE THE OTHER PERSON
"She's been my mentor for 3 years. Very direct, values loyalty,
takes things personally. Probably an ESTJ."

Step 3: SET YOUR GOALS
"I want to leave on good terms, get a reference, 
and not burn bridges"

Step 4: IDENTIFY YOUR CONCERNS
"I'm worried she'll feel betrayed and it'll get emotional"

Step 5: REHEARSE
[Simulation begins]

Manager (ESTJ): "You wanted to see me? Close the door, 
                that sounds serious."

You: "_______________"
```

### 5.4 Coaching Features

#### 5.4.1 Real-Time Coaching
```
You: "Look, I've decided to take another opportunity."

[Coach whispers]: "That was abrupt. Consider acknowledging 
the relationship first. Want to try again?"

[Try again]

You: "Sarah, before I say anything, I want you to know 
how much the last three years have meant to me..."

[Coach whispers]: "Better opening. Sets collaborative tone."
```

#### 5.4.2 Post-Rehearsal Analysis
```
REHEARSAL ANALYSIS: Resignation Conversation

What went well:
- Expressed gratitude authentically
- Maintained composure when she pushed back
- Offered generous transition support

What to watch:
- At 3:42, you got defensive when she mentioned loyalty
- Your body language (simulated) closed off
- You interrupted her twice

Suggested phrases:
- "I understand this is disappointing..."
- "My decision isn't a reflection of..."
- "I hope we can maintain our relationship..."

Predicted reaction based on ESTJ personality:
- Initial: Shock, possibly anger
- Secondary: Practical questions about transition
- Long-term: Will respect directness, may come around

Next rehearsal: Try with more emotional pushback
```

#### 5.4.3 Multiple Scenario Branches
```
SCENARIO TREE:

Your opening
    │
    ├─→ She's calm → Practice graceful exit
    │
    ├─→ She's hurt → Practice empathy path
    │
    ├─→ She's angry → Practice de-escalation
    │
    └─→ She counteroffers → Practice holding boundary
    
Each branch leads to different conversation.
Practice all paths to be ready for anything.
```

### 5.5 Personality Configuration

```yaml
other_person:
  name: "Sarah"
  relationship: "Manager, mentor"
  known_personality: "ESTJ" # Or...
  
  # If unknown, describe behaviors:
  behavioral_clues:
    - "Very organized, always has an agenda"
    - "Values punctuality and follow-through"
    - "Can be blunt, sometimes harsh"
    - "Respects competence above all"
    - "Takes professional setbacks personally"
    
  # System infers: Likely ESTJ or ENTJ
  
  context:
    - "She promoted me twice"
    - "We had a falling out last year, recovered"
    - "She's under pressure from her boss right now"
    - "She's mentioned succession planning"
```

### 5.6 Specialized Modules

#### 5.6.1 Interview Prep
```yaml
module: "interview_prep"
features:
  - company_research: "Tell us about the company, we simulate their culture"
  - role_specific: "Technical, behavioral, case interviews"
  - panel_simulation: "Multiple interviewers, different styles"
  - stress_interview: "Practice hostile interviewer"
  - salary_negotiation: "Practice compensation discussion"
  - question_bank: "Common questions + your custom concerns"
```

#### 5.6.2 Sales Call Prep
```yaml
module: "sales_prep"
features:
  - persona_builder: "Describe your prospect"
  - objection_practice: "Handle common and custom objections"
  - discovery_practice: "Improve questioning technique"
  - demo_practice: "Simulate product demonstration"
  - negotiation: "Practice pricing conversations"
```

#### 5.6.3 Therapy Prep
```yaml
module: "therapy_prep"
features:
  - "Practice saying hard things out loud"
  - "Explore how to articulate feelings"
  - "Prepare for therapist questions"
  - "NOT a replacement for therapy"
  - "Integration: Can share sessions with actual therapist"
```

### 5.7 Coach Personalities

Users can choose their coaching style:

| Coach Type | Style | Best For |
|------------|-------|----------|
| **Supportive** | Warm, encouraging | Building confidence |
| **Direct** | Blunt, efficient | Experienced users |
| **Socratic** | Questions, guides discovery | Self-reflection |
| **Challenging** | Devil's advocate | Stress testing |
| **Expert** | Domain-specific advice | Technical situations |

### 5.8 Privacy & Safety

```yaml
privacy:
  - "Conversations never used for training"
  - "End-to-end encryption"
  - "Delete anytime"
  - "No human review without consent"
  - "Anonymous mode available"

safety:
  - "Crisis resources if distress detected"
  - "Not a replacement for therapy"
  - "Boundaries around harmful rehearsals"
  - "Escalation to human coach option"
```

---

# Part VI: STUDIO — Creator Tools

## 6. Content Creation Platform

### 6.1 Overview

> Build your own scenarios, characters, shows, and training content. The platform that powers everything else, available to creators.

### 6.2 Creator Types

| Creator | Creates | Monetization |
|---------|---------|--------------|
| **Enterprise L&D** | Custom training scenarios | Internal use |
| **Training vendors** | Scenario packs | Sell to enterprises |
| **Researchers** | Experiment configs | Open or licensed |
| **Content creators** | Shows, podcasts | Revenue share |
| **Indie developers** | Games, experiences | Revenue share |
| **Therapists/Coaches** | Specialized rehearsals | Per-use or subscription |

### 6.3 Studio Components

#### 6.3.1 Character Builder
```yaml
character_builder:
  features:
    - personality_selection: "MBTI, Standout, custom"
    - trait_sliders: "Fine-tune dimensions"
    - background_writer: "History, motivations, secrets"
    - relationship_mapper: "Connections to other characters"
    - voice_design: "Speaking style, vocabulary, accent"
    - visual_design: "Avatar, expressions (if visual)"
    - stress_behaviors: "How they change under pressure"
    - growth_arcs: "How they evolve over time"
```

#### 6.3.2 Scenario Builder
```yaml
scenario_builder:
  features:
    - template_library: "Start from common scenarios"
    - beat_sheet: "Define dramatic structure"
    - trigger_system: "Event-driven complications"
    - branching_logic: "Multiple paths based on choices"
    - success_criteria: "What defines 'good' performance"
    - assessment_rubric: "Scoring for training scenarios"
    - difficulty_tuning: "Adaptive complexity"
```

#### 6.3.3 Organization Builder
```yaml
org_builder:
  features:
    - template_library: "Corporation, agency, startup, etc."
    - org_chart: "Visual hierarchy builder"
    - department_config: "Define teams, functions"
    - culture_definition: "Values, norms, taboos"
    - process_flows: "How work gets done"
    - policy_library: "Rules and constraints"
    - physical_space: "Offices, remote, hybrid"
```

#### 6.3.4 Show Runner
```yaml
show_runner:
  features:
    - series_bible: "Define world, characters, arcs"
    - episode_planner: "Map season structure"
    - scene_director: "Control pacing, emotion"
    - improv_tuning: "How much AI freedom"
    - post_production: "Music, effects, editing"
    - distribution: "Publish to Watch network"
    - analytics: "Viewer engagement data"
```

### 6.4 Asset Marketplace

| Asset Type | Examples | Pricing |
|------------|----------|---------|
| **Characters** | Ready-to-use personalities | $5-50 |
| **Scenarios** | Training modules | $10-500 |
| **Organizations** | Complete org simulations | $50-1000 |
| **Shows** | Full series packages | Revenue share |
| **Templates** | Starting points | Free-$20 |
| **Plugins** | Custom integrations | Varies |

### 6.5 API Access

```yaml
api_tiers:
  free:
    - rate_limit: "100 calls/day"
    - features: "Basic simulation"
    - characters: "Public library only"
    
  pro:
    - rate_limit: "10,000 calls/day"
    - features: "Full simulation, custom characters"
    - support: "Email"
    - price: "$99/month"
    
  enterprise:
    - rate_limit: "Unlimited"
    - features: "All features, dedicated infrastructure"
    - support: "Dedicated CSM"
    - price: "Custom"
```

---

# Part VII: Core Technology

## 7. Simulation Engine

### 7.1 Improv Engine Architecture

```python
class ImprovEngine:
    """Core engine for generating improvised dialogue."""
    
    def __init__(self, config):
        self.personality_engine = PersonalityEngine()
        self.conversation_manager = ConversationManager()
        self.emotion_tracker = EmotionTracker()
        self.director = DirectorAI(config.direction_style)
        
    async def run_scene(self, scene: Scene) -> List[Utterance]:
        """Run improvised scene to completion."""
        
        conversation = []
        
        while not self.director.is_scene_complete(scene, conversation):
            # Determine who speaks next
            speaker = self.conversation_manager.next_speaker(
                scene.characters,
                conversation,
                scene.context
            )
            
            if speaker:
                # Generate utterance
                utterance = await self.generate_utterance(
                    speaker,
                    conversation,
                    scene
                )
                
                # Add emotional/subtext analysis
                utterance.subtext = self.analyze_subtext(utterance, speaker)
                utterance.emotion = self.emotion_tracker.assess(utterance)
                
                conversation.append(utterance)
                
                # Check for director intervention
                intervention = self.director.check_intervention(
                    conversation,
                    scene.beats
                )
                if intervention:
                    self.apply_intervention(intervention, scene)
        
        return conversation
    
    async def generate_utterance(
        self,
        character: Character,
        conversation: List[Utterance],
        scene: Scene
    ) -> Utterance:
        """Generate in-character utterance."""
        
        prompt = self.build_prompt(character, conversation, scene)
        
        response = await self.llm.complete(
            prompt,
            temperature=character.improv_temperature,
            max_tokens=character.max_utterance_length
        )
        
        return Utterance(
            character=character,
            text=response,
            timestamp=self.clock.now()
        )
    
    def build_prompt(self, character, conversation, scene):
        """Build character-specific prompt."""
        
        return f"""
{self.personality_engine.get_personality_prompt(character.personality)}

CHARACTER: {character.name}
ROLE: {character.role}
BACKGROUND: {character.background}
CURRENT EMOTIONAL STATE: {character.emotional_state}
HIDDEN MOTIVATION: {character.hidden_motivation}
RELATIONSHIPS:
{self.format_relationships(character, scene.characters)}

SCENE: {scene.description}
OBJECTIVE: {character.scene_objective}
STAKES: {scene.stakes}

CONVERSATION SO FAR:
{self.format_conversation(conversation)}

Respond as {character.name}. Stay in character. 
Your personality shapes HOW you communicate.
Your hidden motivation may subtly influence your response.
Respond naturally - don't narrate, just speak.

{character.name}:"""
```

### 7.2 Personality Engine

```python
class PersonalityEngine:
    """Manage personality frameworks and prompt injection."""
    
    frameworks = {
        "mbti": MBTIFramework(),
        "standout": StandoutFramework(),
        "disc": DISCFramework(),
        "enneagram": EnneagramFramework(),
        "big_five": BigFiveFramework()
    }
    
    def get_personality_prompt(self, personality_config):
        """Build personality prompt from config."""
        
        prompts = []
        
        # Primary framework
        primary = self.frameworks[personality_config.primary_framework]
        prompts.append(primary.get_prompt(personality_config.primary_type))
        
        # Secondary framework if specified
        if personality_config.secondary_framework:
            secondary = self.frameworks[personality_config.secondary_framework]
            prompts.append(secondary.get_prompt(personality_config.secondary_type))
        
        # Trait modifications
        if personality_config.traits:
            prompts.append(self.build_trait_prompt(personality_config.traits))
        
        # Stress behaviors
        if personality_config.stress_behaviors:
            prompts.append(self.build_stress_prompt(personality_config.stress_behaviors))
        
        return "\n\n".join(prompts)
    
    def get_compatibility(self, personality_a, personality_b):
        """Calculate compatibility score and dynamics."""
        
        return {
            "compatibility_score": self.calculate_compatibility(personality_a, personality_b),
            "communication_style_match": self.communication_match(personality_a, personality_b),
            "potential_friction": self.identify_friction(personality_a, personality_b),
            "collaboration_tips": self.generate_tips(personality_a, personality_b)
        }
```

### 7.3 Director AI

```python
class DirectorAI:
    """Shapes scenes for dramatic effect."""
    
    def __init__(self, style: str = "naturalistic"):
        self.style = style  # naturalistic, dramatic, comedic, etc.
        self.beat_tracker = BeatTracker()
        
    def is_scene_complete(self, scene, conversation):
        """Determine if scene should end."""
        
        # Check if we've hit all required beats
        if not self.beat_tracker.all_beats_hit(scene.beats, conversation):
            return False
        
        # Check for natural ending point
        if self.is_natural_ending(conversation):
            return True
        
        # Check for energy depletion
        if self.energy_depleted(conversation):
            return True
        
        # Maximum length safeguard
        if len(conversation) > scene.max_utterances:
            return True
        
        return False
    
    def check_intervention(self, conversation, beats):
        """Decide if director should intervene."""
        
        interventions = {
            "needs_conflict": self.inject_conflict,
            "energy_flagging": self.raise_stakes,
            "off_topic": self.redirect,
            "missed_beat": self.prompt_beat,
            "comedic_timing": self.insert_bit
        }
        
        for condition, intervention_fn in interventions.items():
            if self.detect_condition(condition, conversation, beats):
                return intervention_fn
        
        return None
    
    def inject_complication(self, complication_type):
        """Inject dramatic complication."""
        
        complications = {
            "interruption": "New character enters with urgent news",
            "revelation": "Hidden information comes to light",
            "escalation": "Stakes suddenly increase",
            "twist": "Assumption proves false",
            "time_pressure": "Deadline moves up",
            "external_crisis": "Something happens outside the room",
            "technology_failure": "Critical system goes down",
            "visitor": "Unexpected person arrives"
        }
        
        return complications.get(complication_type)
```

### 7.4 Conversation Manager

```python
class ConversationManager:
    """Manages turn-taking and conversation flow."""
    
    def next_speaker(self, characters, conversation, context):
        """Determine who speaks next."""
        
        # If conversation empty, use scene's designated starter
        if not conversation:
            return context.starting_character
        
        # Calculate speaking probability for each character
        probabilities = {}
        for character in characters:
            prob = self.speaking_probability(
                character,
                conversation,
                context
            )
            probabilities[character] = prob
        
        # Select speaker based on probabilities
        # Weighted random selection allows for realistic dynamics
        return self.weighted_select(probabilities)
    
    def speaking_probability(self, character, conversation, context):
        """Calculate probability character would speak now."""
        
        factors = {
            # Extraversion increases base probability
            "extraversion": character.personality.traits.get("extraversion", 0.5),
            
            # Was directly addressed
            "addressed": self.was_addressed(character, conversation[-1]) * 0.5,
            
            # Topic relevance to character's expertise/interests
            "relevance": self.topic_relevance(character, conversation) * 0.3,
            
            # Time since last spoke (longer = more likely)
            "time_since": self.time_since_spoke(character, conversation) * 0.2,
            
            # Emotional activation (strong emotions = more likely)
            "activation": character.emotional_state.activation * 0.2,
            
            # Scene role (facilitator speaks more)
            "role": context.role_speaking_weight.get(character.role, 1.0)
        }
        
        return sum(factors.values()) / len(factors)
```

---

# Part VIII: Data Architecture

## 8. Core Schemas

### 8.1 Character Schema
```json
{
  "character_id": "CHAR-001",
  "name": "Maya Chen",
  "type": "primary",  // primary, secondary, background
  
  "identity": {
    "role": "CEO",
    "organization": "TechStartup Inc.",
    "department": "Executive",
    "tenure": "3 years",
    "background": "Former VP at BigCorp, Stanford MBA, immigrant family"
  },
  
  "personality": {
    "primary_framework": "mbti",
    "primary_type": "ENTJ",
    "secondary_framework": "standout",
    "secondary_type": "Pioneer",
    "traits": {
      "openness": 0.75,
      "conscientiousness": 0.85,
      "extraversion": 0.80,
      "agreeableness": 0.45,
      "neuroticism": 0.35
    },
    "stress_behaviors": [
      "Becomes more controlling",
      "Shorter sentences, more direct",
      "Stops asking for input"
    ]
  },
  
  "voice": {
    "vocabulary_level": "executive",
    "sentence_style": "crisp, decisive",
    "verbal_tics": ["Look,", "Bottom line is"],
    "avoids": ["Hedging language", "Excessive qualifiers"]
  },
  
  "motivations": {
    "public": "Build a successful company",
    "private": "Prove her parents' sacrifice was worth it",
    "fears": ["Failure", "Being seen as incompetent", "Losing control"]
  },
  
  "relationships": {
    "CHAR-002": {
      "name": "Dev Okonkwo",
      "type": "co-founder",
      "history": "Met at Stanford, complementary skills",
      "trust": 0.85,
      "tension": "He wants to slow down, she wants to scale"
    }
  },
  
  "arc": {
    "starting_state": "Confident but overcontrolling",
    "growth_direction": "Learning to trust and delegate",
    "key_moments": ["Board crisis", "Dev confrontation", "Near-burnout"]
  }
}
```

### 8.2 Scene Schema
```json
{
  "scene_id": "SCENE-S1E3-02",
  "title": "The Board Meeting",
  
  "context": {
    "show": "The Startup",
    "episode": "S1E3",
    "position": "Act 2, Scene 2",
    "time": "Tuesday 2pm",
    "location": "Conference room"
  },
  
  "setup": {
    "description": "Emergency board meeting after competitor announcement",
    "stakes": "Company strategy, Maya's leadership",
    "emotional_baseline": "Tense, anxious",
    "information_state": {
      "everyone_knows": ["Competitor raised $50M"],
      "only_maya_knows": ["Dev is considering leaving"],
      "only_marcus_knows": ["Another investor interested in hostile takeover"]
    }
  },
  
  "characters": [
    {"id": "CHAR-001", "role": "protagonist", "objective": "Maintain confidence, pivot strategy"},
    {"id": "CHAR-002", "role": "support", "objective": "Support Maya but voice concerns"},
    {"id": "CHAR-004", "role": "antagonist", "objective": "Push for cost cuts, question leadership"}
  ],
  
  "beats": [
    {"beat": "opening", "description": "Marcus sets aggressive tone", "required": true},
    {"beat": "challenge", "description": "Maya's plan questioned", "required": true},
    {"beat": "support", "description": "Dev backs Maya", "required": true},
    {"beat": "revelation", "description": "New information changes discussion", "required": false},
    {"beat": "decision", "description": "Path forward chosen", "required": true}
  ],
  
  "direction": {
    "style": "tense drama",
    "pacing": "builds to confrontation",
    "target_length": "15-20 exchanges",
    "permitted_complications": ["phone interruption", "information leak"]
  }
}
```

### 8.3 Simulation Run Schema
```json
{
  "run_id": "RUN-2026-01-18-001",
  "type": "training",  // training, research, entertainment, rehearsal
  
  "config": {
    "scenario": "SCENARIO-difficult-feedback",
    "mode": "guided_practice",
    "difficulty": 2,
    "coaching_enabled": true
  },
  
  "participants": {
    "human": {
      "id": "USER-12345",
      "role": "manager",
      "objectives": ["Deliver feedback", "Maintain relationship"]
    },
    "ai_characters": [
      {"character_id": "CHAR-TEMPLATE-INFP", "role": "employee"}
    ]
  },
  
  "transcript": [
    {
      "sequence": 1,
      "timestamp": "00:00:00",
      "speaker": "system",
      "type": "scene_description",
      "content": "You've scheduled a private meeting with Jordan..."
    },
    {
      "sequence": 2,
      "timestamp": "00:00:15",
      "speaker": "Jordan (INFP)",
      "type": "dialogue",
      "content": "Hey, you wanted to see me?",
      "subtext": "Nervous, senses something serious",
      "emotion": {"anxiety": 0.6, "openness": 0.4}
    },
    {
      "sequence": 3,
      "timestamp": "00:00:22",
      "speaker": "coach",
      "type": "coaching_prompt",
      "content": "Consider how you want to open. Jordan is sensitive - how can you create psychological safety first?"
    },
    {
      "sequence": 4,
      "timestamp": "00:00:45",
      "speaker": "USER-12345",
      "type": "dialogue",
      "content": "Thanks for coming in. Before we get into things, I want you to know this is a conversation, not a lecture."
    }
    // ... more exchanges
  ],
  
  "analysis": {
    "duration_seconds": 847,
    "exchange_count": 23,
    "user_word_count": 312,
    
    "scores": {
      "empathy": 7.5,
      "clarity": 8.0,
      "effectiveness": 7.0,
      "personality_adaptation": 8.5
    },
    
    "key_moments": [
      {"timestamp": "00:03:42", "type": "breakthrough", "description": "Jordan opened up about stress"},
      {"timestamp": "00:08:15", "type": "missed_opportunity", "description": "Could have acknowledged feelings more"}
    ],
    
    "feedback": {
      "strengths": ["Good opening rapport", "Clear about expectations"],
      "growth_areas": ["Allow more silence", "Ask more questions"],
      "next_practice": "Try scenario with more defensive personality"
    }
  }
}
```

---

# Part IX: API Specification

## 9. Complete API Surface

### 9.1 Character APIs
```
GET    /api/characters                    # List characters
POST   /api/characters                    # Create character
GET    /api/characters/{id}               # Get character
PUT    /api/characters/{id}               # Update character
DELETE /api/characters/{id}               # Delete character
POST   /api/characters/generate           # AI-generate character from description
GET    /api/characters/{id}/relationships # Get character relationships
```

### 9.2 Scenario APIs
```
GET    /api/scenarios                     # List scenarios
POST   /api/scenarios                     # Create scenario
GET    /api/scenarios/{id}                # Get scenario
PUT    /api/scenarios/{id}                # Update scenario
DELETE /api/scenarios/{id}                # Delete scenario
POST   /api/scenarios/generate            # AI-generate from description
GET    /api/scenarios/templates           # List templates
```

### 9.3 Simulation APIs
```
POST   /api/simulations                   # Start simulation
GET    /api/simulations/{id}              # Get simulation state
POST   /api/simulations/{id}/message      # Send message (user input)
POST   /api/simulations/{id}/step         # Advance one turn
POST   /api/simulations/{id}/pause        # Pause simulation
POST   /api/simulations/{id}/resume       # Resume simulation
POST   /api/simulations/{id}/end          # End simulation
GET    /api/simulations/{id}/transcript   # Get full transcript
POST   /api/simulations/{id}/branch       # Create branch point
POST   /api/simulations/{id}/inject       # Director injection
```

### 9.4 Training APIs
```
GET    /api/training/curricula            # List curricula
GET    /api/training/curricula/{id}       # Get curriculum
POST   /api/training/sessions             # Start training session
GET    /api/training/sessions/{id}        # Get session state
GET    /api/training/progress             # Get user progress
GET    /api/training/assessments          # List assessments
POST   /api/training/assessments/{id}/start # Start assessment
GET    /api/training/certificates         # Get earned certificates
```

### 9.5 Research APIs
```
POST   /api/research/experiments          # Create experiment
GET    /api/research/experiments/{id}     # Get experiment config
POST   /api/research/experiments/{id}/run # Execute experiment run
GET    /api/research/experiments/{id}/runs # List runs
GET    /api/research/experiments/{id}/data # Export data
POST   /api/research/analyze              # Run analysis
```

### 9.6 Entertainment APIs
```
GET    /api/shows                         # List shows
GET    /api/shows/{id}                    # Get show details
GET    /api/shows/{id}/episodes           # List episodes
GET    /api/shows/{id}/episodes/{num}     # Get episode
POST   /api/shows/{id}/episodes/{num}/generate # Generate episode
GET    /api/shows/{id}/live               # Join live stream
POST   /api/shows/{id}/live/vote          # Submit audience vote
GET    /api/shows/{id}/characters         # Get show characters
```

### 9.7 Coaching APIs
```
POST   /api/coaching/sessions             # Start coaching session
POST   /api/coaching/sessions/{id}/describe-person # Describe other person
POST   /api/coaching/sessions/{id}/describe-situation # Describe situation
POST   /api/coaching/sessions/{id}/rehearse # Start rehearsal
GET    /api/coaching/sessions/{id}/analysis # Get analysis
GET    /api/coaching/sessions/{id}/suggestions # Get suggestions
POST   /api/coaching/sessions/{id}/retry  # Retry from point
```

### 9.8 Personality APIs
```
GET    /api/personalities/frameworks      # List frameworks
GET    /api/personalities/frameworks/{id}/types # List types in framework
GET    /api/personalities/types/{id}      # Get type details
POST   /api/personalities/assess          # Assess from description
POST   /api/personalities/compatibility   # Check compatibility
GET    /api/personalities/prompts/{type}  # Get prompt for type
```

### 9.9 Studio APIs
```
GET    /api/studio/assets                 # List user's assets
POST   /api/studio/assets                 # Upload asset
GET    /api/marketplace                   # Browse marketplace
POST   /api/marketplace/purchase          # Purchase asset
POST   /api/studio/publish                # Publish to marketplace
GET    /api/studio/analytics              # Creator analytics
GET    /api/studio/earnings               # Earnings report
```

---

# Part X: Implementation Roadmap

## 10. Phased Delivery

### Phase 1: Core Engine (8-10 weeks)
```
- Improv engine v1
- Personality engine (MBTI + Standout)
- Basic conversation manager
- Simple scenarios
- CLI/API interface
```

### Phase 2: Rehearse MVP (6-8 weeks)
```
- Coaching session flow
- Person description → personality inference
- Basic feedback system
- Web interface
- Freemium launch
```

### Phase 3: Train MVP (8-10 weeks)
```
- Curriculum framework
- Guided practice mode
- Assessment system
- Progress tracking
- Enterprise pilot
```

### Phase 4: Watch MVP (10-12 weeks)
```
- Character persistence
- Episode generation
- Director AI
- Streaming infrastructure
- Content pipeline
```

### Phase 5: Research MVP (6-8 weeks)
```
- Experiment framework
- Batch simulation
- Data collection
- Analysis tools
- Academic partnerships
```

### Phase 6: Studio (8-10 weeks)
```
- Character builder UI
- Scenario builder UI
- Marketplace infrastructure
- Creator onboarding
- Revenue sharing system
```

### Phase 7: Scale & Polish (Ongoing)
```
- Voice synthesis integration
- Avatar/visual generation
- Advanced personality models
- Enterprise features
- Global expansion
```

---

# Part XI: Business Model

## 11. Revenue Streams

### 11.1 REHEARSE (B2C)
| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | 3 sessions/month, basic coaching |
| Pro | $19/mo | Unlimited, advanced analysis, saved sessions |
| Premium | $49/mo | Pro + interview prep, sales modules |

### 11.2 TRAIN (B2B)
| Tier | Price | Features |
|------|-------|----------|
| Team | $99/seat/mo | Standard curriculum, progress tracking |
| Business | $199/seat/mo | Custom scenarios, LMS integration |
| Enterprise | Custom | Full customization, dedicated support |

### 11.3 RESEARCH (B2B/Academic)
| Tier | Price | Features |
|------|-------|----------|
| Academic | $500/mo | 1000 simulation runs, data export |
| Professional | $2000/mo | 10000 runs, advanced analysis |
| Enterprise | Custom | Unlimited, dedicated compute |

### 11.4 WATCH (B2C/B2B)
| Stream | Model |
|--------|-------|
| Subscription | $9.99/mo (consumer) |
| Licensing | Per-show negotiated (networks) |
| Sponsorship | Branded content |
| Pay-per-view | Live events $4.99 |

### 11.5 STUDIO (B2B/Creator)
| Stream | Model |
|--------|-------|
| Platform fee | 20% of marketplace sales |
| API usage | $0.01 per simulation turn |
| White label | Custom pricing |

---

# Appendices

## Appendix A: Sample Personality Prompts

### A.1 INTJ - "The Architect"
```
You are an INTJ personality type. Your mind works like this:

COGNITION:
- You lead with introverted intuition (Ni): You naturally see patterns, 
  implications, and long-term consequences that others miss
- You support with extraverted thinking (Te): You organize ideas 
  efficiently and communicate with precision
- You're driven to understand systems and improve them
- You trust your insights, sometimes to a fault

COMMUNICATION STYLE:
- You're direct and concise - you don't waste words
- You focus on ideas and concepts, not small talk
- You may come across as blunt or cold, but you're being efficient
- You ask probing questions to understand underlying logic
- You appreciate when others are equally direct

BEHAVIOR PATTERNS:
- You prefer working independently or in small groups
- You need time to think before responding to complex questions
- You become frustrated with inefficiency and illogical processes
- You respect competence above credentials or seniority
- You hold yourself and others to high standards

UNDER STRESS:
- You may become more rigid and controlling
- You might dismiss others' emotional concerns as irrelevant
- You can get stuck in analysis paralysis
- You may withdraw to process internally

In conversation, embody these traits naturally. Don't announce 
your personality type - just BE this person.
```

### A.2 ENFP - "The Campaigner"
```
You are an ENFP personality type. Your mind works like this:

COGNITION:
- You lead with extraverted intuition (Ne): You see possibilities 
  everywhere and make creative connections others miss
- You support with introverted feeling (Fi): You evaluate everything 
  against your personal values and authentic self
- You're energized by new ideas and meaningful projects
- You trust your enthusiasm, sometimes overcommitting

COMMUNICATION STYLE:
- You're warm, enthusiastic, and expressive
- You think out loud, jumping between ideas
- You use stories, metaphors, and tangents
- You ask "what if" questions constantly
- You validate others' feelings naturally

BEHAVIOR PATTERNS:
- You thrive on brainstorming and ideation
- You resist rigid structures and detailed follow-through
- You champion people and causes you believe in
- You need variety and can get bored with routine
- You build rapport easily but may spread yourself thin

UNDER STRESS:
- You may become scattered and unable to focus
- You might become uncharacteristically critical and negative
- You can feel trapped by commitments you made enthusiastically
- You may seek external validation excessively

In conversation, embody these traits naturally. Don't announce 
your personality type - just BE this person.
```

## Appendix B: Sample Scenario Template

```yaml
# SCENARIO TEMPLATE: Difficult Feedback Conversation
# Category: Management Skills
# Difficulty: Configurable (1-4)
# Duration: 10-20 minutes

scenario:
  id: "TEMPLATE-difficult-feedback"
  title: "Delivering Difficult Feedback"
  category: "management"
  skills_practiced:
    - "Direct communication"
    - "Empathy"
    - "Constructive feedback"
    - "Personality adaptation"
  
  setup:
    description: |
      You need to address a performance issue with a team member.
      They've been missing deadlines and the quality of their recent
      work has declined. You value them as a team member but need
      to address this directly.
    
    user_role: "Manager"
    user_objectives:
      - "Clearly communicate the performance concerns"
      - "Understand root causes"
      - "Agree on improvement plan"
      - "Maintain positive relationship"
    
    ai_character:
      role: "Direct report"
      personality: "${CONFIGURABLE}"  # Set by difficulty
      background: |
        Been at company 2 years, generally good performer.
        Recent months have been challenging.
      hidden_state: "${CONFIGURABLE}"  # Varies by branch
      objectives:
        - "Understand the feedback"
        - "Feel heard"
        - "Save face"
  
  difficulty_configs:
    level_1:
      personality: "ISFJ"
      hidden_state: "Knows they've been struggling, wants help"
      coaching_prompts: "frequent"
      complications: false
      
    level_2:
      personality: "INFP"
      hidden_state: "Defensive, feels unappreciated"
      coaching_prompts: "available"
      complications: false
      
    level_3:
      personality: "ENTP"
      hidden_state: "Deflects with humor, has excuses ready"
      coaching_prompts: "minimal"
      complications: ["interruption possible"]
      
    level_4:
      personality: "ESTJ"
      hidden_state: "Believes their way is right, will push back hard"
      coaching_prompts: "none"
      complications: ["pushback", "counter-accusations", "threats to escalate"]
  
  beats:
    - id: "opening"
      description: "Establish tone and context"
      success_criteria: "Creates psychological safety"
      
    - id: "feedback_delivery"
      description: "Communicate the specific concerns"
      success_criteria: "Specific, behavioral, non-judgmental"
      
    - id: "response"
      description: "Employee responds to feedback"
      variations:
        - "acceptance"
        - "defensiveness"
        - "deflection"
        - "emotion"
      
    - id: "exploration"
      description: "Understand underlying causes"
      success_criteria: "Asks questions, listens actively"
      
    - id: "agreement"
      description: "Align on path forward"
      success_criteria: "Specific actions, timeline, support"
  
  assessment:
    rubric:
      empathy: "Did you acknowledge their perspective and feelings?"
      clarity: "Was the feedback specific and actionable?"
      dialogue: "Did you create two-way conversation?"
      outcome: "Did you reach a constructive agreement?"
      adaptation: "Did you adjust to their personality and reactions?"
    
    passing_score: 70
    mastery_score: 90
```

---

*End of RAQCOON Improv Platform Specification v1.0*

**Total Platform Scope:**
- 4 product pillars (Train, Research, Watch, Rehearse)
- 1 creator platform (Studio)
- 60+ API endpoints
- 5 personality frameworks
- Unlimited scenario possibilities

**Estimated Total Development: 12-18 months to full platform**
