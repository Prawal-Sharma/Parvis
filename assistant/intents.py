"""
Pi-Jarvis Intent System - Phase 7
Extensible intent classification and handling system with built-in intents for:
- Timer management
- Weather information
- Time queries  
- Translation services
"""

import asyncio
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import json

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Supported intent types."""
    TIMER = "timer"
    WEATHER = "weather" 
    TIME = "time"
    TRANSLATION = "translation"
    GENERAL_CHAT = "general_chat"
    VISION = "vision"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent processing."""
    intent_type: IntentType
    confidence: float
    response_text: str
    success: bool = True
    error_message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class Intent(ABC):
    """Base class for all intent handlers."""
    
    def __init__(self, intent_type: IntentType):
        self.intent_type = intent_type
        self.keywords = self._get_keywords()
        self.patterns = self._get_patterns()
    
    @abstractmethod
    def _get_keywords(self) -> List[str]:
        """Return keywords that trigger this intent."""
        pass
    
    @abstractmethod
    def _get_patterns(self) -> List[str]:
        """Return regex patterns that match this intent."""
        pass
    
    @abstractmethod
    async def handle(self, user_text: str, context: Optional[Dict] = None) -> IntentResult:
        """Handle the intent and return a response."""
        pass
    
    def matches(self, user_text: str) -> float:
        """Calculate confidence score for this intent (0.0-1.0)."""
        text_lower = user_text.lower()
        score = 0.0
        
        # Check keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in text_lower)
        if keyword_matches > 0:
            score += min(keyword_matches * 0.3, 0.7)
        
        # Check patterns
        for pattern in self.patterns:
            if re.search(pattern, text_lower):
                score += 0.5
                break
        
        return min(score, 1.0)


class TimerIntent(Intent):
    """Handle timer-related requests."""
    
    def __init__(self):
        super().__init__(IntentType.TIMER)
        self.active_timers: Dict[str, Dict] = {}
    
    def _get_keywords(self) -> List[str]:
        return [
            "timer", "alarm", "remind", "set timer", "start timer",
            "minute", "second", "hour", "countdown", "wake me up"
        ]
    
    def _get_patterns(self) -> List[str]:
        return [
            r"set (?:a )?timer (?:for )?(\d+) ?(minute|second|hour)s?",
            r"(?:start|begin) (?:a )?(\d+) ?(minute|second|hour) timer",
            r"remind me in (\d+) ?(minute|second|hour)s?",
            r"timer (?:for )?(\d+) ?(minute|second|hour)s?",
            r"wake me (?:up )?in (\d+) ?(minute|second|hour)s?"
        ]
    
    async def handle(self, user_text: str, context: Optional[Dict] = None) -> IntentResult:
        """Handle timer requests."""
        text_lower = user_text.lower()
        
        try:
            # Parse timer duration
            duration_seconds = self._parse_duration(text_lower)
            if duration_seconds is None:
                return IntentResult(
                    intent_type=self.intent_type,
                    confidence=0.8,
                    response_text="I couldn't understand the timer duration. Please say something like 'set a timer for 5 minutes'.",
                    success=False
                )
            
            # Create timer
            timer_id = f"timer_{int(time.time())}"
            end_time = datetime.now() + timedelta(seconds=duration_seconds)
            
            self.active_timers[timer_id] = {
                "duration": duration_seconds,
                "end_time": end_time,
                "description": self._format_duration(duration_seconds)
            }
            
            # Format response
            duration_text = self._format_duration(duration_seconds)
            response = f"Timer set for {duration_text}. I'll let you know when it's done!"
            
            # Schedule timer completion (non-blocking for testing)
            asyncio.create_task(self._timer_completion(timer_id, duration_seconds))
            
            return IntentResult(
                intent_type=self.intent_type,
                confidence=0.9,
                response_text=response,
                data={"timer_id": timer_id, "duration": duration_seconds}
            )
            
        except Exception as e:
            logger.error(f"Timer intent error: {e}")
            return IntentResult(
                intent_type=self.intent_type,
                confidence=0.8,
                response_text="Sorry, I had trouble setting the timer. Please try again.",
                success=False,
                error_message=str(e)
            )
    
    def _parse_duration(self, text: str) -> Optional[int]:
        """Parse duration from text and return seconds."""
        for pattern in self.patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    amount = int(match.group(1))
                    unit = match.group(2)
                    
                    if unit.startswith("second"):
                        return amount
                    elif unit.startswith("minute"):
                        return amount * 60
                    elif unit.startswith("hour"):
                        return amount * 3600
                except (ValueError, IndexError):
                    continue
        
        # Try simple number extraction
        numbers = re.findall(r'\d+', text)
        if numbers:
            amount = int(numbers[0])
            if "hour" in text:
                return amount * 3600
            elif "second" in text:
                return amount
            else:  # Default to minutes
                return amount * 60
        
        return None
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration for display."""
        if seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''}"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''}"
    
    async def _timer_completion(self, timer_id: str, duration: int):
        """Handle timer completion."""
        await asyncio.sleep(duration)
        if timer_id in self.active_timers:
            timer = self.active_timers[timer_id]
            logger.info(f"🔔 Timer completed: {timer['description']}")
            # In testing mode, just log completion
            del self.active_timers[timer_id]


class WeatherIntent(Intent):
    """Handle weather-related requests."""
    
    def __init__(self):
        super().__init__(IntentType.WEATHER)
    
    def _get_keywords(self) -> List[str]:
        return [
            "weather", "temperature", "rain", "sunny", "cloudy", "forecast",
            "hot", "cold", "warm", "cool", "humid", "windy", "storm"
        ]
    
    def _get_patterns(self) -> List[str]:
        return [
            r"what'?s the weather",
            r"how'?s the weather",
            r"weather (?:forecast|report|today|tomorrow)",
            r"is it (?:raining|sunny|cloudy|hot|cold)",
            r"temperature (?:today|outside|now)"
        ]
    
    async def handle(self, user_text: str, context: Optional[Dict] = None) -> IntentResult:
        """Handle weather requests."""
        try:
            # Since this is an offline assistant, we provide a helpful explanation
            response = ("I'm an offline assistant and don't have access to current weather data. "
                       "For weather information, I recommend checking your phone's weather app "
                       "or asking a connected assistant like Siri or Google Assistant.")
            
            return IntentResult(
                intent_type=self.intent_type,
                confidence=0.9,
                response_text=response,
                data={"offline_response": True}
            )
            
        except Exception as e:
            logger.error(f"Weather intent error: {e}")
            return IntentResult(
                intent_type=self.intent_type,
                confidence=0.8,
                response_text="Sorry, I had trouble with your weather request.",
                success=False,
                error_message=str(e)
            )


class TimeIntent(Intent):
    """Handle time-related requests."""
    
    def __init__(self):
        super().__init__(IntentType.TIME)
    
    def _get_keywords(self) -> List[str]:
        return [
            "time", "clock", "hour", "date", "today", "now",
            "what time", "current time", "o'clock"
        ]
    
    def _get_patterns(self) -> List[str]:
        return [
            r"what time is it",
            r"what'?s the time",
            r"current time",
            r"what'?s today'?s date",
            r"what date is it",
            r"tell me the time"
        ]
    
    async def handle(self, user_text: str, context: Optional[Dict] = None) -> IntentResult:
        """Handle time requests."""
        try:
            now = datetime.now()
            text_lower = user_text.lower()
            
            if "date" in text_lower:
                response = now.strftime("Today is %A, %B %d, %Y")
            else:
                response = now.strftime("It's currently %I:%M %p")
            
            return IntentResult(
                intent_type=self.intent_type,
                confidence=0.9,
                response_text=response,
                data={"timestamp": now.isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Time intent error: {e}")
            return IntentResult(
                intent_type=self.intent_type,
                confidence=0.8,
                response_text="Sorry, I had trouble getting the current time.",
                success=False,
                error_message=str(e)
            )


class TranslationIntent(Intent):
    """Handle translation requests."""
    
    def __init__(self):
        super().__init__(IntentType.TRANSLATION)
        # Simple word translations for demonstration
        self.translations = {
            "hello": {"spanish": "hola", "french": "bonjour", "german": "hallo"},
            "goodbye": {"spanish": "adiós", "french": "au revoir", "german": "auf wiedersehen"},
            "thank you": {"spanish": "gracias", "french": "merci", "german": "danke"},
            "please": {"spanish": "por favor", "french": "s'il vous plaît", "german": "bitte"},
            "yes": {"spanish": "sí", "french": "oui", "german": "ja"},
            "no": {"spanish": "no", "french": "non", "german": "nein"},
            "water": {"spanish": "agua", "french": "eau", "german": "wasser"},
            "food": {"spanish": "comida", "french": "nourriture", "german": "essen"},
            "house": {"spanish": "casa", "french": "maison", "german": "haus"},
            "good": {"spanish": "bueno", "french": "bon", "german": "gut"}
        }
    
    def _get_keywords(self) -> List[str]:
        return [
            "translate", "translation", "spanish", "french", "german",
            "how do you say", "in spanish", "in french", "in german"
        ]
    
    def _get_patterns(self) -> List[str]:
        return [
            r"translate (.+?) (?:to|into) (spanish|french|german)",
            r"how do you say (.+?) in (spanish|french|german)",
            r"what is (.+?) in (spanish|french|german)",
            r"(.+?) in (spanish|french|german)"
        ]
    
    async def handle(self, user_text: str, context: Optional[Dict] = None) -> IntentResult:
        """Handle translation requests."""
        try:
            text_lower = user_text.lower()
            
            # Extract text to translate and target language
            word_to_translate = None
            target_language = None
            
            for pattern in self.patterns:
                match = re.search(pattern, text_lower)
                if match:
                    word_to_translate = match.group(1).strip()
                    target_language = match.group(2).strip()
                    break
            
            if not word_to_translate or not target_language:
                return IntentResult(
                    intent_type=self.intent_type,
                    confidence=0.8,
                    response_text="I couldn't understand what you want to translate. Try asking 'How do you say hello in Spanish?'",
                    success=False
                )
            
            # Look up translation
            if word_to_translate in self.translations:
                if target_language in self.translations[word_to_translate]:
                    translation = self.translations[word_to_translate][target_language]
                    response = f"'{word_to_translate}' in {target_language} is '{translation}'"
                else:
                    response = f"I don't know how to say '{word_to_translate}' in {target_language}. I can translate to Spanish, French, or German."
            else:
                available_words = ", ".join(self.translations.keys())
                response = f"I don't know how to translate '{word_to_translate}'. I can translate these words: {available_words}"
            
            return IntentResult(
                intent_type=self.intent_type,
                confidence=0.9,
                response_text=response,
                data={"word": word_to_translate, "language": target_language}
            )
            
        except Exception as e:
            logger.error(f"Translation intent error: {e}")
            return IntentResult(
                intent_type=self.intent_type,
                confidence=0.8,
                response_text="Sorry, I had trouble with the translation.",
                success=False,
                error_message=str(e)
            )


class IntentManager:
    """Main intent classification and routing system."""
    
    def __init__(self):
        """Initialize the intent manager with all available intents."""
        self.intents: List[Intent] = [
            TimerIntent(),
            WeatherIntent(),
            TimeIntent(),
            TranslationIntent(),
        ]
        self.intent_stats = {intent.intent_type: {"count": 0, "success": 0} for intent in self.intents}
        logger.info(f"Intent manager initialized with {len(self.intents)} intent handlers")
    
    async def classify_and_handle(self, user_text: str, context: Optional[Dict] = None) -> IntentResult:
        """Classify user input and handle with appropriate intent."""
        if not user_text or not user_text.strip():
            return IntentResult(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                response_text="I didn't hear anything. Could you please repeat that?",
                success=False
            )
        
        # Check for vision requests first (delegate to existing vision system)
        if self._is_vision_request(user_text):
            return IntentResult(
                intent_type=IntentType.VISION,
                confidence=0.9,
                response_text="Vision request detected - delegating to vision system",
                data={"delegate_to_vision": True}
            )
        
        # Find best matching intent
        best_intent = None
        best_confidence = 0.0
        
        for intent in self.intents:
            confidence = intent.matches(user_text)
            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent
        
        # Handle the intent
        if best_intent and best_confidence > 0.3:  # Minimum confidence threshold
            logger.info(f"Intent classified: {best_intent.intent_type.value} (confidence: {best_confidence:.2f})")
            
            # Update stats
            self.intent_stats[best_intent.intent_type]["count"] += 1
            
            try:
                result = await best_intent.handle(user_text, context)
                if result.success:
                    self.intent_stats[best_intent.intent_type]["success"] += 1
                return result
            except Exception as e:
                logger.error(f"Intent handling error: {e}")
                return IntentResult(
                    intent_type=best_intent.intent_type,
                    confidence=best_confidence,
                    response_text="Sorry, I had trouble processing your request.",
                    success=False,
                    error_message=str(e)
                )
        else:
            # No confident match found - fall back to general chat
            logger.info(f"No confident intent match for: '{user_text}' (best: {best_confidence:.2f})")
            return IntentResult(
                intent_type=IntentType.GENERAL_CHAT,
                confidence=0.5,
                response_text="Let me think about that.",
                data={"delegate_to_llm": True}
            )
    
    def _is_vision_request(self, text: str) -> bool:
        """Check if user input is requesting vision functionality."""
        if not text:
            return False
            
        text_lower = text.lower()
        vision_keywords = [
            "what do you see", "what can you see", "describe what you see",
            "look around", "tell me what you see", "what's in front", 
            "describe the scene", "what's there", "look at", "vision",
            "camera", "image", "picture", "see anything"
        ]
        
        return any(keyword in text_lower for keyword in vision_keywords)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get intent usage statistics."""
        total_requests = sum(stats["count"] for stats in self.intent_stats.values())
        return {
            "total_requests": total_requests,
            "intent_counts": {intent.value: stats["count"] for intent, stats in self.intent_stats.items()},
            "success_rates": {
                intent.value: (stats["success"] / stats["count"] * 100) if stats["count"] > 0 else 0
                for intent, stats in self.intent_stats.items()
            }
        }
    
    def list_capabilities(self) -> List[Dict[str, Any]]:
        """List all available intent capabilities."""
        capabilities = []
        for intent in self.intents:
            capabilities.append({
                "intent_type": intent.intent_type.value,
                "keywords": intent.keywords,
                "examples": self._get_intent_examples(intent.intent_type)
            })
        return capabilities
    
    def _get_intent_examples(self, intent_type: IntentType) -> List[str]:
        """Get example phrases for each intent."""
        examples = {
            IntentType.TIMER: [
                "Set a timer for 5 minutes",
                "Start a 30 second timer",
                "Remind me in 2 hours"
            ],
            IntentType.WEATHER: [
                "What's the weather like?",
                "Is it raining outside?",
                "How's the temperature today?"
            ],
            IntentType.TIME: [
                "What time is it?",
                "What's today's date?",
                "Tell me the current time"
            ],
            IntentType.TRANSLATION: [
                "How do you say hello in Spanish?",
                "Translate water to French",
                "What is goodbye in German?"
            ],
            IntentType.VISION: [
                "What do you see?",
                "Look around and describe the scene",
                "What's in front of you?"
            ],
            IntentType.GENERAL_CHAT: [
                "Hello, how are you?",
                "What can you help me with?",
                "Tell me about yourself"
            ]
        }
        return examples.get(intent_type, [])


# Global intent manager instance
intent_manager = IntentManager()