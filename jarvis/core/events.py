"""
================================================================================
                    JARVIS EVENT BUS & DISPATCH ENGINE
================================================================================
Enterprise publish-subscribe message broker with typed events, asynchronous
priority queues, listener filters, metrics tracking, and thread-safe dispatch.
================================================================================
"""

import time
import queue
import threading
import traceback
from enum import Enum, auto
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field


class Priority(Enum):
    LOW = 10
    NORMAL = 20
    HIGH = 30
    CRITICAL = 40


class EventType(Enum):
    # Audio & Voice Events
    AUDIO_RECORDING_START   = "audio.recording.start"
    AUDIO_RECORDING_STOP    = "audio.recording.stop"
    AUDIO_RMS_UPDATE        = "audio.rms.update"
    AUDIO_VAD_STATE         = "audio.vad.state"

    # Speech-to-Text Events
    STT_LISTENING           = "stt.listening"
    STT_PROCESSING          = "stt.processing"
    STT_RESULT              = "stt.result"
    STT_TIMEOUT             = "stt.timeout"
    STT_UNCLEAR             = "stt.unclear"
    STT_ERROR               = "stt.error"

    # Speaker Authentication Events
    AUTH_CHECK_START        = "auth.check.start"
    AUTH_SUCCESS            = "auth.success"
    AUTH_REJECTED           = "auth.rejected"
    AUTH_ENROLL_SAMPLE      = "auth.enroll.sample"
    AUTH_ENROLL_COMPLETE    = "auth.enroll.complete"

    # Natural Language & Brain
    COMMAND_RECEIVED        = "brain.command.received"
    INTENT_MATCHED          = "brain.intent.matched"
    LLM_STREAM_CHUNK        = "brain.llm.chunk"
    LLM_COMPLETED           = "brain.llm.completed"
    PROACTIVE_TALK          = "brain.proactive.talk"

    # Text-to-Speech Events
    TTS_SPEAK_REQUEST       = "tts.speak.request"
    TTS_START               = "tts.start"
    TTS_FINISH              = "tts.finish"
    TTS_INTERRUPT           = "tts.interrupt"

    # System & Telemetry Events
    HARDWARE_METRICS        = "system.hardware.metrics"
    SYSTEM_ALERT            = "system.alert"
    NOTIFICATION_SHOW       = "system.notification.show"
    APP_LAUNCHED            = "system.app.launched"

    # UI & Terminal Events
    UI_LOG_MESSAGE          = "ui.log.message"
    UI_THEME_CHANGED        = "ui.theme.changed"
    UI_STATUS_UPDATE        = "ui.status.update"
    CORE_SHUTDOWN           = "core.shutdown"


@dataclass(order=True)
class Event:
    """Represents a discrete typed event in the JARVIS architecture."""
    priority: int = field(init=False)
    priority_level: Priority = field(default=Priority.NORMAL, compare=False)
    event_type: EventType = field(default=EventType.UI_LOG_MESSAGE, compare=False)
    data: Dict[str, Any] = field(default_factory=dict, compare=False)
    timestamp: float = field(default_factory=time.time, compare=False)
    source: str = field(default="system", compare=False)

    def __post_init__(self):
        # Invert priority so higher numerical Priority pops first from PriorityQueue
        self.priority = -self.priority_level.value


class EventBus:
    """Central singleton asynchronous message bus."""
    
    _instance: Optional["EventBus"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "EventBus":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._wildcard_subscribers: List[Callable[[Event], None]] = []
        self._queue: queue.PriorityQueue[Event] = queue.PriorityQueue()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._events_dispatched = 0
        self._start_worker()
        self._initialized = True

    def _start_worker(self) -> None:
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._process_queue,
            name="JarvisEventBusWorker",
            daemon=True
        )
        self._worker_thread.start()

    def _process_queue(self) -> None:
        """Background dispatcher thread consuming prioritized events."""
        while self._running:
            try:
                event = self._queue.get(timeout=0.1)
                self._dispatch_event(event)
                self._queue.task_done()
                self._events_dispatched += 1
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[EventBus] Dispatch error: {e}\n{traceback.format_exc()}")

    def _dispatch_event(self, event: Event) -> None:
        """Dispatch event to registered handlers."""
        # Type-specific handlers
        handlers: List[Callable[[Event], None]] = []
        with self._lock:
            if event.event_type in self._subscribers:
                handlers.extend(self._subscribers[event.event_type])
            handlers.extend(self._wildcard_subscribers)

        for handler in handlers:
            try:
                handler(event)
            except Exception as err:
                print(f"[EventBus] Handler {handler.__name__} raised error on {event.event_type}: {err}")

    def publish(
        self,
        event_type: EventType,
        data: Optional[Dict[str, Any]] = None,
        priority: Priority = Priority.NORMAL,
        source: str = "system",
        sync: bool = False
    ) -> None:
        """Publish an event to the bus."""
        event = Event(
            priority_level=priority,
            event_type=event_type,
            data=data or {},
            source=source
        )
        if sync:
            self._dispatch_event(event)
        else:
            self._queue.put(event)

    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Subscribe a callable to a specific event type."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: Callable[[Event], None]) -> None:
        """Subscribe to all events across the entire bus."""
        with self._lock:
            if handler not in self._wildcard_subscribers:
                self._wildcard_subscribers.append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Unsubscribe a handler from an event type."""
        with self._lock:
            if event_type in self._subscribers and handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)

    def get_stats(self) -> Dict[str, Any]:
        """Telemetry on the bus state."""
        return {
            "queue_size": self._queue.qsize(),
            "events_dispatched": self._events_dispatched,
            "registered_types": len(self._subscribers),
            "wildcard_handlers": len(self._wildcard_subscribers)
        }

    def shutdown(self) -> None:
        """Gracefully stop event bus dispatch."""
        self._running = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)


def get_event_bus() -> EventBus:
    """Helper singleton accessor for EventBus."""
    return EventBus()
