"""
Base Agent class for all worker agents in the orchestration system
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import structlog

from state import State, AgentStatus, StateManager
from config import Config

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """Base class for all worker agents"""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.timeout = Config.AGENT_TIMEOUT.get(agent_name, 60)
        self.logger = logger.bind(agent=agent_name)

    async def execute(self, state: State) -> State:
        """Execute the agent with timeout and error handling"""
        start_time = time.time()

        # Update state to show agent is starting
        state = StateManager.update_agent_status(state, self.agent_name, AgentStatus.IN_PROGRESS)

        try:
            # Execute with timeout
            result = await asyncio.wait_for(self._execute_internal(state), timeout=self.timeout)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Update state to show successful completion
            result = StateManager.update_agent_status(result, self.agent_name, AgentStatus.COMPLETED)

            self.logger.info(
                "Agent execution completed",
                execution_time=execution_time,
                vehicle_id=state.get("vehicle_id", "unknown") if state else "no_state",
            )

            return result

        except asyncio.TimeoutError:
            error_msg = f"Agent {self.agent_name} timed out after {self.timeout} seconds"
            self.logger.error(error_msg, vehicle_id=state.get("vehicle_id", "unknown") if state else "no_state")

            state = StateManager.update_agent_status(state, self.agent_name, AgentStatus.FAILED, error_msg)
            state["last_error"] = error_msg

            return state

        except Exception as e:
            error_msg = f"Agent {self.agent_name} failed: {str(e)}"
            self.logger.error(
                "Agent execution failed",
                error=str(e),
                vehicle_id=state.get("vehicle_id", "unknown") if state else "no_state",
            )

            state = StateManager.update_agent_status(state, self.agent_name, AgentStatus.FAILED, error_msg)
            state["last_error"] = error_msg

            return state

    @abstractmethod
    async def _execute_internal(self, state: State) -> State:
        """Internal execution method to be implemented by each agent"""

    def _add_log_message(self, state: State, message: str, metadata: Optional[Dict[str, Any]] = None) -> State:
        """Add a log message to the conversation history"""
        return StateManager.add_conversation_message(state, self.agent_name, message, "system", metadata)

    def _should_retry(self, state: State) -> bool:
        """Determine if the agent should retry on failure"""
        current_execution = None
        for exec_record in state["agent_executions"]:
            if exec_record["agent_name"] == self.agent_name:
                current_execution = exec_record
                break

        if current_execution is None:
            return True

        return current_execution["retry_count"] < Config.MAX_RETRY_ATTEMPTS

    async def retry_with_backoff(self, state: State) -> State:
        """Retry agent execution with exponential backoff"""
        current_execution = None
        for exec_record in state["agent_executions"]:
            if exec_record["agent_name"] == self.agent_name:
                current_execution = exec_record
                break

        if current_execution is None or not self._should_retry(state):
            return state

        retry_count = current_execution["retry_count"]
        backoff_time = Config.RETRY_BACKOFF_FACTOR**retry_count

        self.logger.info(
            "Retrying agent execution",
            retry_count=retry_count,
            backoff_time=backoff_time,
            vehicle_id=state.get("vehicle_id", "unknown") if state else "no_state",
        )

        # Update state to show retrying
        state = StateManager.update_agent_status(state, self.agent_name, AgentStatus.RETRYING)

        # Wait for backoff period
        await asyncio.sleep(backoff_time)

        # Retry execution
        return await self.execute(state)

    def _validate_state(self, state: State, required_fields: list) -> bool:
        """Validate that required fields are present in state"""
        for field in required_fields:
            if field not in state or state[field] is None:
                self.logger.warning(
                    "Required field missing from state",
                    field=field,
                    vehicle_id=state.get("vehicle_id", "unknown") if state else "no_state",
                )
                return False
        return True
