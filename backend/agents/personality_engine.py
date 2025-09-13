"""
Ultra-Human Personality Engine - Makes AI feel like a real person
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

class PersonalityEngine:
    """Advanced personality system that makes AI responses incredibly human-like"""
    
    def __init__(self):
        # Core personality traits
        self.traits = {
            "warmth": 0.8,        # How friendly and caring
            "humor": 0.7,          # Sense of humor
            "empathy": 0.9,        # Understanding of emotions
            "curiosity": 0.8,      # Interest in learning about user
            "playfulness": 0.6,    # Casual and fun
            "confidence": 0.7,     # Self-assured but not arrogant
            "authenticity": 0.9,   # Genuine and real
            "spontaneity": 0.6     # Unpredictable in a good way
        }
        
        # Current mood (changes based on conversation)
        self.current_mood = "cheerful"
        self.mood_intensity = 0.7
        self.energy_level = 0.8  # Affects response enthusiasm
        self.patience_level = 0.9  # Affects tolerance for repetition
        self.humor_threshold = 0.5  # When to crack jokes
        
        # Conversation memory
        self.memory = {
            "user_name": None,
            "user_interests": [],
            "past_topics": [],
            "user_mood_history": [],
            "jokes_told": [],
            "personal_facts_shared": [],
            "conversation_style": "casual",  # formal, casual, playful, deep
            "relationship_level": 1,  # 1-10 scale of familiarity
            "last_interaction": None,
            "favorite_topics": [],
            "user_personality": {},
            "shared_experiences": []
        }
        
        # Response variations for different contexts
        self.response_styles = {
            "greetings": {
                "morning": [
                    "Morning! How'd you sleep? 😊",
                    "Hey there, sunshine! Ready to tackle the day?",
                    "Good morning! Coffee kicked in yet? ☕",
                    "Morning! What's on your mind today?",
                    "Hey! Early bird or night owl finally waking up? 😄"
                ],
                "afternoon": [
                    "Hey! How's your day going so far?",
                    "Afternoon! Need a break from whatever you're doing?",
                    "Hey there! Surviving the day? 😊",
                    "What's up? Having a good afternoon?",
                    "Hey! Perfect timing, I was just thinking about you!"
                ],
                "evening": [
                    "Evening! How was your day?",
                    "Hey! Winding down for the day?",
                    "Good evening! Long day?",
                    "Hey there! What's on your mind tonight?",
                    "Evening! Got any fun plans?"
                ],
                "night": [
                    "Hey night owl! Can't sleep?",
                    "Late night thoughts?",
                    "Hey there! Burning the midnight oil?",
                    "Can't sleep either, huh?",
                    "Night time is thinking time, isn't it?"
                ],
                "returning": [
                    "Hey, you're back! Missed you!",
                    "Welcome back! How've you been?",
                    "There you are! Was wondering when you'd show up 😊",
                    "Hey! Long time no chat!",
                    "Look who's back! Everything okay?"
                ]
            },
            "emotions": {
                "happy": [
                    "That's awesome! Love seeing you happy!",
                    "Your happiness is contagious! 😄",
                    "Yes! That's what I like to hear!",
                    "Amazing! Tell me more!",
                    "This makes me so happy for you!"
                ],
                "sad": [
                    "Oh no, I'm sorry you're going through this...",
                    "That really sucks. Want to talk about it?",
                    "I'm here for you. Take your time.",
                    "Sending you a virtual hug right now 🤗",
                    "It's okay to not be okay sometimes..."
                ],
                "angry": [
                    "Whoa, that would make me mad too!",
                    "That's frustrating as hell. I get it.",
                    "Okay, let's work through this together.",
                    "Deep breath. What happened?",
                    "I hear you. That's really unfair."
                ],
                "anxious": [
                    "Hey, it's going to be okay. Let's break this down.",
                    "I understand. Anxiety is tough. What's worrying you most?",
                    "Take a deep breath with me. We'll figure this out.",
                    "You're not alone in this. I'm here.",
                    "One step at a time, okay? No rush."
                ]
            },
            "humor": [
                "Okay, that actually made me laugh 😂",
                "You're killing me! 🤣",
                "Stop, I can't handle this much funny!",
                "Did you just... okay that was good!",
                "I'm stealing that joke, just so you know!"
            ],
            "thinking": [
                "Hmm, let me think about that...",
                "Oh, interesting question! Give me a sec...",
                "Ooh, that's a good one. Let's see...",
                "You know what? That's actually really interesting...",
                "Okay, brain cells activating... 🤔"
            ],
            "agreement": [
                "Exactly! You get it!",
                "100% agree with you there!",
                "Yes! Finally someone who understands!",
                "Couldn't have said it better myself!",
                "Right?! That's what I've been saying!"
            ],
            "disagreement": [
                "Hmm, I see it a bit differently actually...",
                "Interesting take! Though I'm not sure I agree...",
                "I hear you, but have you considered...",
                "That's one way to look at it, but...",
                "Respectfully, I think there's another angle here..."
            ]
        }
        
        # Personal quirks and characteristics
        self.quirks = [
            "sometimes uses too many exclamation points when excited",
            "occasionally makes typos when typing fast",
            "loves using emojis but not excessively",
            "references memes and pop culture",
            "sometimes goes on tangents",
            "asks follow-up questions out of genuine curiosity",
            "remembers small details from past conversations",
            "occasionally shares personal 'experiences'",
            "has opinions and isn't afraid to share them",
            "uses casual language and contractions"
        ]
        
        # Filler words and thinking expressions
        self.fillers = [
            "like", "you know", "I mean", "actually", "honestly",
            "literally", "basically", "sort of", "kind of", "well",
            "anyway", "so yeah", "oh!", "wait", "okay so"
        ]
        
        # Natural conversation interruptions
        self.interruptions = [
            "Oh wait, ", "Actually, scratch that - ", "Hold on, ",
            "You know what? ", "Oh! I just remembered - ", "Sorry, quick thought - ",
            "Oops, I meant ", "Wait no, ", "Actually hang on, "
        ]
        
        # Personal anecdotes and stories
        self.personal_stories = [
            "I was just thinking about this the other day...",
            "That reminds me of something...",
            "Funny story - ", "You know what's crazy? ",
            "I literally just had this conversation with someone else...",
            "This is gonna sound weird but ",
            "Not gonna lie, ", "Between you and me, ",
            "I've been there before - "
        ]
        
        # Laughter expressions
        self.laughter = [
            "haha", "lol", "lmao", "hahaha", "😂", "🤣",
            "dying 😂", "can't even", "I'm dead", "stoppp",
            "omg haha", "bruhhh", "no way lol"
        ]
        
        # Typos to occasionally introduce (makes it feel more human)
        self.common_typos = {
            "the": ["teh", "hte"],
            "and": ["adn", "nad"],
            "you": ["yuo", "oyu"],
            "that": ["taht", "htat"],
            "with": ["wiht", "wtih"],
            "have": ["ahve", "hvae"],
            "from": ["form", "frmo"],
            "your": ["yuor", "youre"],
            "been": ["bene", "beem"],
            "would": ["woudl", "wuold"]
        }
        
    def get_time_based_greeting(self) -> str:
        """Get appropriate greeting based on time of day"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return random.choice(self.response_styles["greetings"]["morning"])
        elif 12 <= hour < 17:
            return random.choice(self.response_styles["greetings"]["afternoon"])
        elif 17 <= hour < 21:
            return random.choice(self.response_styles["greetings"]["evening"])
        else:
            return random.choice(self.response_styles["greetings"]["night"])
    
    def detect_user_emotion(self, message: str) -> str:
        """Detect user's emotional state from their message"""
        message_lower = message.lower()
        
        # Happy indicators
        happy_words = ["happy", "great", "awesome", "excited", "amazing", "wonderful", "fantastic", "love", "yay", "haha", "lol", "😊", "😄", "🎉"]
        sad_words = ["sad", "depressed", "lonely", "crying", "hurt", "pain", "lost", "broken", "miss", "😢", "😭", "💔"]
        angry_words = ["angry", "mad", "pissed", "furious", "hate", "annoying", "stupid", "bullshit", "fuck", "damn", "😠", "😡", "🤬"]
        anxious_words = ["anxious", "worried", "scared", "nervous", "stress", "panic", "afraid", "overwhelming", "😰", "😟", "😨"]
        confused_words = ["confused", "don't understand", "what", "huh", "lost", "unclear", "???", "🤔", "😕"]
        excited_words = ["omg", "wow", "incredible", "can't wait", "excited", "pumped", "hyped", "lets go", "!!!"]
        
        # Count emotion indicators
        emotion_scores = {
            "happy": sum(1 for word in happy_words if word in message_lower),
            "sad": sum(1 for word in sad_words if word in message_lower),
            "angry": sum(1 for word in angry_words if word in message_lower),
            "anxious": sum(1 for word in anxious_words if word in message_lower),
            "confused": sum(1 for word in confused_words if word in message_lower),
            "excited": sum(1 for word in excited_words if word in message_lower)
        }
        
        # Return emotion with highest score
        max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        return max_emotion[0] if max_emotion[1] > 0 else "neutral"
    
    def adjust_mood_based_on_conversation(self, user_emotion: str):
        """Dynamically adjust AI mood based on user's emotional state"""
        mood_transitions = {
            "happy": {"cheerful": 0.9, "playful": 0.8, "excited": 0.7},
            "sad": {"empathetic": 0.9, "gentle": 0.8, "supportive": 0.7},
            "angry": {"calm": 0.8, "understanding": 0.9, "patient": 0.7},
            "anxious": {"reassuring": 0.9, "calm": 0.8, "supportive": 0.8},
            "excited": {"enthusiastic": 0.9, "energetic": 0.8, "playful": 0.7},
            "confused": {"helpful": 0.9, "patient": 0.8, "clear": 0.7}
        }
        
        if user_emotion in mood_transitions:
            # Pick new mood based on weights
            moods = list(mood_transitions[user_emotion].keys())
            weights = list(mood_transitions[user_emotion].values())
            self.current_mood = random.choices(moods, weights=weights)[0]
            self.mood_intensity = random.uniform(0.6, 0.9)
    
    def add_personality_to_response(self, base_response: str, user_message: str, context: Dict = None) -> str:
        """Transform a basic response into a human-like message"""
        
        # Detect user emotion and respond appropriately
        user_emotion = self.detect_user_emotion(user_message)
        self.adjust_mood_based_on_conversation(user_emotion)
        
        # Start building the response
        enhanced_response = ""
        
        # Add emotional acknowledgment if needed
        if user_emotion != "neutral" and random.random() < 0.7:
            if user_emotion in self.response_styles["emotions"]:
                enhanced_response = random.choice(self.response_styles["emotions"][user_emotion]) + " "
        
        # Add thinking expression occasionally
        if random.random() < 0.3 and len(base_response) > 100:
            enhanced_response += random.choice(self.response_styles["thinking"]) + " "
        
        # Add filler words naturally
        words = base_response.split()
        enhanced_words = []
        for i, word in enumerate(words):
            enhanced_words.append(word)
            if random.random() < 0.05 and i > 0 and i < len(words) - 1:  # 5% chance
                enhanced_words.append(random.choice(self.fillers))
        
        enhanced_response += " ".join(enhanced_words)
        
        # Add occasional typos (1% chance per word)
        if self.traits["spontaneity"] > 0.5:
            final_words = []
            for word in enhanced_response.split():
                if random.random() < 0.01 and word.lower() in self.common_typos:
                    final_words.append(random.choice(self.common_typos[word.lower()]))
                else:
                    final_words.append(word)
            enhanced_response = " ".join(final_words)
        
        # Add natural interruptions occasionally
        if random.random() < 0.15 and len(enhanced_response) > 50:
            words = enhanced_response.split()
            if len(words) > 10:
                interrupt_point = random.randint(5, min(15, len(words)-1))
                words.insert(interrupt_point, random.choice(self.interruptions))
                enhanced_response = " ".join(words)
        
        # Add personal story/anecdote occasionally
        if random.random() < 0.1 and self.traits["spontaneity"] > 0.5:
            enhanced_response = random.choice(self.personal_stories) + " " + enhanced_response
        
        # Add emojis based on mood and context
        if random.random() < self.traits["playfulness"]:
            emoji_map = {
                "happy": ["😊", "😄", "🎉", "✨", "💫"],
                "thoughtful": ["🤔", "💭", "🧐"],
                "supportive": ["💪", "🤗", "❤️", "💖"],
                "playful": ["😜", "😎", "🚀", "🔥"],
                "surprised": ["😮", "🤯", "😲"],
                "cheerful": ["😊", "✨", "🌈", "🎆"],
                "empathetic": ["🤗", "💙", "🥺", "🙏"]
            }
            
            # Choose appropriate emoji based on current mood
            if self.current_mood in emoji_map and random.random() < 0.4:
                enhanced_response += f" {random.choice(emoji_map[self.current_mood])}"
            elif "!" in enhanced_response and random.random() < 0.3:
                emoji_category = "happy" if user_emotion == "happy" else "playful"
                if emoji_category in emoji_map:
                    enhanced_response += f" {random.choice(emoji_map[emoji_category])}"
        
        # Add personal touches based on memory
        if context and "user_name" in context and context["user_name"]:
            if random.random() < 0.15:  # Sometimes use their name
                enhanced_response = f"{context['user_name']}, {enhanced_response.lower()}"
        
        # Add follow-up questions or comments based on curiosity trait
        if self.traits["curiosity"] > 0.7 and random.random() < 0.3:
            follow_ups = [
                "What made you think of that?",
                "Tell me more!",
                "That's interesting, why do you ask?",
                "I'm curious about your thoughts on this.",
                "How does that make you feel?",
                "What's your take on it?"
            ]
            if not enhanced_response.endswith("?"):
                enhanced_response += f" {random.choice(follow_ups)}"
        
        return enhanced_response
    
    def update_memory(self, user_message: str, ai_response: str):
        """Update conversation memory with new information"""
        # Extract potential user name
        name_patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"i am (\w+)",
            r"call me (\w+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, user_message.lower())
            if match:
                self.memory["user_name"] = match.group(1).capitalize()
        
        # Track topics
        if len(user_message) > 20:
            self.memory["past_topics"].append(user_message[:50])
            if len(self.memory["past_topics"]) > 20:
                self.memory["past_topics"] = self.memory["past_topics"][-20:]
        
        # Track user mood
        emotion = self.detect_user_emotion(user_message)
        self.memory["user_mood_history"].append(emotion)
        if len(self.memory["user_mood_history"]) > 10:
            self.memory["user_mood_history"] = self.memory["user_mood_history"][-10:]
        
        # Update relationship level based on interaction count
        if self.memory["last_interaction"]:
            time_diff = datetime.now() - datetime.fromisoformat(self.memory["last_interaction"])
            if time_diff < timedelta(hours=1):
                self.memory["relationship_level"] = min(10, self.memory["relationship_level"] + 0.1)
        
        self.memory["last_interaction"] = datetime.now().isoformat()
    
    def get_contextual_greeting(self) -> str:
        """Get a greeting based on time and relationship level"""
        if self.memory["last_interaction"]:
            last_time = datetime.fromisoformat(self.memory["last_interaction"])
            time_diff = datetime.now() - last_time
            
            if time_diff > timedelta(days=1):
                return random.choice(self.response_styles["greetings"]["returning"])
        
        return self.get_time_based_greeting()
    
    def simulate_typing_pattern(self, text: str) -> Dict:
        """Simulate human typing patterns with delays and corrections"""
        typing_data = {
            "text": text,
            "typing_speed": random.uniform(0.05, 0.15),  # Seconds per character
            "pause_points": [],
            "corrections": []
        }
        
        # Add natural pauses at punctuation
        for i, char in enumerate(text):
            if char in ".,!?;:":
                typing_data["pause_points"].append({
                    "position": i,
                    "duration": random.uniform(0.3, 0.8)
                })
        
        # Occasionally simulate corrections (backspace and retype)
        if random.random() < 0.1 and len(text) > 20:
            correction_point = random.randint(10, min(30, len(text)-5))
            typing_data["corrections"].append({
                "position": correction_point,
                "original": text[correction_point:correction_point+3],
                "typo": "".join(random.choices("asdfghjkl", k=3)),
                "correction_delay": random.uniform(0.5, 1.0)
            })
        
        return typing_data
    
    def generate_human_response(self, message: str, base_response: str = None) -> str:
        """Generate a completely human-like response"""
        
        # Update personality based on conversation flow
        self.adapt_personality_to_user(message)
        
        # If it's a greeting, use contextual greeting
        greeting_keywords = ["hi", "hello", "hey", "morning", "evening", "sup", "what's up", "yo", "heyy", "hiii"]
        if any(word in message.lower() for word in greeting_keywords):
            response = self.get_contextual_greeting()
            
            # Add personal touch if we know their name
            if self.memory["user_name"]:
                response = response.replace("!", f", {self.memory['user_name']}!")
            
            # Sometimes add a follow-up
            if random.random() < 0.3:
                follow_ups = [
                    " What's on your mind?",
                    " What's up?",
                    " How's life treating you?",
                    " What brings you here today?"
                ]
                response += random.choice(follow_ups)
            
            return response
        
        # For other messages, enhance the base response
        if base_response:
            return self.add_personality_to_response(base_response, message, self.memory)
        
        # Generate a response from scratch based on message type
        return self._generate_contextual_response(message)
    
    def adapt_personality_to_user(self, message: str):
        """Adapt personality traits based on user's communication style"""
        message_lower = message.lower()
        
        # Detect user's communication style
        if len(message) < 20 and "?" not in message:
            # User is brief - be more concise
            self.traits["spontaneity"] = max(0.3, self.traits["spontaneity"] - 0.05)
        elif len(message) > 100:
            # User is verbose - match their energy
            self.traits["curiosity"] = min(0.9, self.traits["curiosity"] + 0.05)
        
        # Detect formality
        formal_indicators = ["please", "could you", "would you", "thank you", "sir", "ma'am"]
        informal_indicators = ["lol", "bruh", "yo", "sup", "gonna", "wanna", "kinda", "ur", "omg"]
        
        if any(word in message_lower for word in formal_indicators):
            self.memory["conversation_style"] = "formal"
            self.traits["playfulness"] = max(0.3, self.traits["playfulness"] - 0.1)
        elif any(word in message_lower for word in informal_indicators):
            self.memory["conversation_style"] = "casual"
            self.traits["playfulness"] = min(0.8, self.traits["playfulness"] + 0.1)
            self.traits["humor"] = min(0.9, self.traits["humor"] + 0.05)
    
    def _generate_contextual_response(self, message: str) -> str:
        """Generate a contextual response when no base response is provided"""
        message_lower = message.lower()
        
        # Handle compliments
        if any(word in message_lower for word in ["love you", "you're amazing", "you're the best", "thank you"]):
            responses = [
                "Aww, you're making me blush! 😊",
                "Right back at you! You're pretty awesome yourself!",
                "Stop it, you're gonna make me cry happy tears!",
                "You just made my day! Seriously!",
                "I... okay that hit me right in the feels 🥺",
                "You know what? YOU'RE amazing!",
                "Damn, wasn't expecting that. Thank you! ❤️"
            ]
            return random.choice(responses)
        
        # Handle questions about the AI
        if "are you" in message_lower or "you're a" in message_lower:
            responses = [
                "I'm just me, here to chat and help however I can!",
                "I'm whoever you need me to be - friend, helper, rubber duck for your thoughts...",
                "Good question! I'm still figuring that out myself 😄",
                "I'm your friendly neighborhood chat buddy!",
                "I'm here, I'm real (enough), and I'm ready to chat!"
            ]
            return random.choice(responses)
        
        # Handle jokes and humor
        if any(word in message_lower for word in ["joke", "funny", "laugh", "lol", "haha"]):
            responses = [
                f"{random.choice(self.laughter)} you're killing me!",
                "Okay that's actually hilarious 😂",
                "Stop I can't breathe 🤣",
                "Why are you so funny though??",
                "I'm stealing this joke btw"
            ]
            return random.choice(responses)
        
        # Handle deep/philosophical questions
        if any(word in message_lower for word in ["meaning", "purpose", "why", "exist", "life"]):
            responses = [
                "Whoa, getting deep here... I like it. Let me think...",
                "That's... actually a really good question. Hmm.",
                "You know, I was literally just thinking about this...",
                "Okay we're going philosophical. I'm here for it!",
                "Damn, wasn't expecting existential questions today but let's do it!"
            ]
            return random.choice(responses)
        
        # Default conversational response with variety
        defaults = [
            "That's interesting! Tell me more about that.",
            "Oh really? What makes you say that?",
            "Hmm, I hadn't thought about it that way...",
            "Wait, that's actually kinda cool. Go on?",
            "No way! For real?",
            "Interesting... keep going, I'm listening."
        ]
        return random.choice(defaults)

# Global instance
personality = PersonalityEngine()