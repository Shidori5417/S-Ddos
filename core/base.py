"""
Base classes for the FsocietyDDoS framework
"""

import time
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class AttackStatus(Enum):
    """Attack status enumeration"""
    IDLE = "idle"
    PREPARING = "preparing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AttackResult:
    """Attack result data structure"""
    success: bool
    requests_sent: int
    requests_failed: int
    duration: float
    avg_response_time: float
    error_message: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class BaseAttack(ABC):
    """Base class for all attack types"""
    
    def __init__(self, target: str, **kwargs):
        self.target = target
        self.status = AttackStatus.IDLE
        self.start_time = None
        self.end_time = None
        self.requests_sent = 0
        self.requests_failed = 0
        self.response_times = []
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
        # Attack parameters
        self.duration = kwargs.get('duration', 60)
        self.concurrency = kwargs.get('concurrency', 50)
        self.verbose = kwargs.get('verbose', False)
        
    @abstractmethod
    def prepare(self) -> bool:
        """Prepare the attack (validate target, setup resources, etc.)"""
        pass
    
    @abstractmethod
    def execute(self) -> AttackResult:
        """Execute the attack"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup resources after attack"""
        pass
    
    def start(self) -> AttackResult:
        """Start the attack sequence"""
        try:
            self.status = AttackStatus.PREPARING
            if not self.prepare():
                self.status = AttackStatus.FAILED
                return AttackResult(
                    success=False,
                    requests_sent=0,
                    requests_failed=0,
                    duration=0,
                    avg_response_time=0,
                    error_message="Attack preparation failed"
                )
            
            self.status = AttackStatus.RUNNING
            self.start_time = time.time()
            
            result = self.execute()
            
            self.end_time = time.time()
            self.status = AttackStatus.COMPLETED if result.success else AttackStatus.FAILED
            
            return result
            
        except Exception as e:
            self.status = AttackStatus.FAILED
            return AttackResult(
                success=False,
                requests_sent=self.requests_sent,
                requests_failed=self.requests_failed,
                duration=time.time() - (self.start_time or time.time()),
                avg_response_time=0,
                error_message=str(e)
            )
        finally:
            self.cleanup()
    
    def stop(self):
        """Stop the attack"""
        self._stop_event.set()
        self.status = AttackStatus.STOPPED
    
    def pause(self):
        """Pause the attack"""
        self._pause_event.set()
        self.status = AttackStatus.PAUSED
    
    def resume(self):
        """Resume the attack"""
        self._pause_event.clear()
        self.status = AttackStatus.RUNNING
    
    def is_stopped(self) -> bool:
        """Check if attack should stop"""
        return self._stop_event.is_set()
    
    def is_paused(self) -> bool:
        """Check if attack is paused"""
        return self._pause_event.is_set()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current attack statistics"""
        current_time = time.time()
        duration = current_time - (self.start_time or current_time)
        
        return {
            'status': self.status.value,
            'target': self.target,
            'duration': duration,
            'requests_sent': self.requests_sent,
            'requests_failed': self.requests_failed,
            'success_rate': (self.requests_sent - self.requests_failed) / max(self.requests_sent, 1) * 100,
            'avg_response_time': sum(self.response_times) / max(len(self.response_times), 1),
            'requests_per_second': self.requests_sent / max(duration, 1)
        }


class AttackManager:
    """Manager for coordinating multiple attacks"""
    
    def __init__(self):
        self.attacks = {}
        self.active_attacks = []
    
    def register_attack(self, attack_id: str, attack: BaseAttack):
        """Register an attack instance"""
        self.attacks[attack_id] = attack
    
    def start_attack(self, attack_id: str) -> AttackResult:
        """Start a registered attack"""
        if attack_id not in self.attacks:
            raise ValueError(f"Attack {attack_id} not found")
        
        attack = self.attacks[attack_id]
        self.active_attacks.append(attack_id)
        
        try:
            result = attack.start()
            return result
        finally:
            if attack_id in self.active_attacks:
                self.active_attacks.remove(attack_id)
    
    def stop_attack(self, attack_id: str):
        """Stop a running attack"""
        if attack_id in self.attacks:
            self.attacks[attack_id].stop()
    
    def stop_all_attacks(self):
        """Stop all running attacks"""
        for attack_id in self.active_attacks[:]:
            self.stop_attack(attack_id)
    
    def get_attack_status(self, attack_id: str) -> Dict[str, Any]:
        """Get status of a specific attack"""
        if attack_id not in self.attacks:
            return {'error': 'Attack not found'}
        
        return self.attacks[attack_id].get_statistics()
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all attacks"""
        return {
            attack_id: attack.get_statistics()
            for attack_id, attack in self.attacks.items()
        }