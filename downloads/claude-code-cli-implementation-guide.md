# Claude Code CLI Implementation Guide for Autonomous Bot Runner

**Document:** Technical Implementation Specification
**Version:** 1.0
**Date:** 2025-10-23
**Target:** Agent BC and Development Team
**Purpose:** Full-featured Claude Code CLI subprocess integration

---

## 1. Executive Summary

### 1.1. Current State
The existing `claude_code_adapter.py` uses the Anthropic Messages API for basic Claude interactions. This provides chat-level responses but lacks the autonomous tool access required for real coding tasks.

### 1.2. Required Enhancement
Implement a true Claude Code CLI integration that spawns actual `claude code` subprocess sessions with full tool access including file operations (Read, Write, Edit), bash command execution, and multi-step autonomous workflows.

### 1.3. Expected Outcome
Bots will be able to delegate complete coding tasks to Claude Code CLI, which autonomously edits files, runs tests, executes commands, and tracks modifications - all while the bot orchestrates higher-level workflow.

---

## 2. Architecture Overview

### 2.1. Component Layers
The implementation consists of three primary layers working in coordination:

**2.1.1. Process Management Layer**
Handles subprocess lifecycle including spawning `claude code` processes, monitoring health, managing stdin/stdout/stderr streams, implementing timeout controls, and graceful shutdown procedures.

**2.1.2. Communication Layer**
Manages task submission through file-based or stdin-based interfaces, captures and buffers output streams, implements response parsing for tool invocations and results, and handles error conditions and recovery.

**2.1.3. Integration Layer**
Provides the bot-facing API with simple task submission and result retrieval, tracks file modifications across sessions, implements session state management, and coordinates with existing bot infrastructure.

### 2.2. Process Flow
When a bot needs to execute a coding task, it creates a ClaudeCodeCLIAdapter instance with the target working directory, calls start_session to spawn the subprocess, submits the task via send_task, monitors output for tool uses and completion signals, extracts modified files list and success status, and finally calls stop_session for cleanup.

---

## 3. Core Implementation

### 3.1. ClaudeCodeCLIAdapter Class Structure

```python
"""
Claude Code CLI subprocess adapter for autonomous bot integration.

This module provides process-based integration with the Claude Code CLI,
enabling bots to delegate complete coding tasks with full tool access.
"""

import subprocess
import threading
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class SessionState(Enum):
    """Claude Code session states."""
    UNINITIALIZED = "uninitialized"
    STARTING = "starting"
    READY = "ready"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class TaskResult:
    """Result from Claude Code task execution."""
    success: bool
    output: str
    files_modified: Set[Path]
    tool_uses: List[Dict[str, Any]]
    error: Optional[str]
    duration: float
    exit_code: Optional[int]


class ClaudeCodeCLIAdapter:
    """
    Claude Code CLI subprocess controller for autonomous coding tasks.

    Spawns and manages 'claude code' CLI processes with full tool access,
    enabling bots to delegate file operations, bash execution, and
    multi-step coding workflows.
    """

    def __init__(
        self,
        bot_id: str,
        work_dir: Path,
        claude_cli_path: str = "claude",
        timeout: int = 300,
        max_retries: int = 3
    ):
        """
        Initialize Claude Code CLI adapter.

        Args:
            bot_id: Unique identifier for the bot using this adapter
            work_dir: Working directory for Claude Code session
            claude_cli_path: Path to claude CLI binary (default: "claude" in PATH)
            timeout: Maximum seconds for task execution (default: 300)
            max_retries: Maximum retry attempts for failed tasks (default: 3)
        """
        self.bot_id = bot_id
        self.work_dir = Path(work_dir).resolve()
        self.claude_cli_path = claude_cli_path
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.process: Optional[subprocess.Popen] = None
        self.state = SessionState.UNINITIALIZED
        self.files_modified: Set[Path] = set()
        self.output_buffer: List[str] = []
        self.error_buffer: List[str] = []
        
        self._stdout_thread: Optional[threading.Thread] = None
        self._stderr_thread: Optional[threading.Thread] = None
        self._stop_threads = threading.Event()

    def start_session(self) -> bool:
        """
        Start Claude Code CLI subprocess session.

        Returns:
            True if session started successfully, False otherwise
        """
        if self.state not in [SessionState.UNINITIALIZED, SessionState.TERMINATED]:
            return False

        try:
            self.state = SessionState.STARTING
            
            # Verify working directory exists
            self.work_dir.mkdir(parents=True, exist_ok=True)
            
            # Spawn claude code process
            self.process = subprocess.Popen(
                [self.claude_cli_path, "code"],
                cwd=str(self.work_dir),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Start output capture threads
            self._start_output_threads()
            
            # Wait for ready signal (timeout after 10 seconds)
            ready = self._wait_for_ready(timeout=10)
            
            if ready:
                self.state = SessionState.READY
                return True
            else:
                self.stop_session()
                self.state = SessionState.ERROR
                return False
                
        except Exception as e:
            self.error_buffer.append(f"Failed to start session: {str(e)}")
            self.state = SessionState.ERROR
            return False

    def send_task(
        self,
        task_content: str,
        task_timeout: Optional[int] = None
    ) -> TaskResult:
        """
        Send task to Claude Code CLI and wait for completion.

        Args:
            task_content: Task description for Claude Code
            task_timeout: Override default timeout for this task

        Returns:
            TaskResult with execution details
        """
        if self.state != SessionState.READY:
            return TaskResult(
                success=False,
                output="",
                files_modified=set(),
                tool_uses=[],
                error="Session not ready",
                duration=0.0,
                exit_code=None
            )

        timeout = task_timeout or self.timeout
        start_time = time.time()
        
        try:
            self.state = SessionState.PROCESSING
            self.output_buffer.clear()
            
            # Send task via stdin
            self.process.stdin.write(task_content + "\n")
            self.process.stdin.flush()
            
            # Wait for completion or timeout
            completed = self._wait_for_completion(timeout)
            duration = time.time() - start_time
            
            if not completed:
                self.stop_session()
                return TaskResult(
                    success=False,
                    output="\n".join(self.output_buffer),
                    files_modified=self.files_modified.copy(),
                    tool_uses=[],
                    error=f"Task timeout after {timeout}s",
                    duration=duration,
                    exit_code=None
                )
            
            # Parse output for tool uses and results
            tool_uses = self._parse_tool_uses(self.output_buffer)
            files_modified = self._extract_modified_files(tool_uses)
            self.files_modified.update(files_modified)
            
            # Determine success
            success = self._check_success(self.output_buffer)
            error = None if success else self._extract_error(self.error_buffer)
            
            self.state = SessionState.READY
            
            return TaskResult(
                success=success,
                output="\n".join(self.output_buffer),
                files_modified=files_modified,
                tool_uses=tool_uses,
                error=error,
                duration=duration,
                exit_code=self.process.returncode if self.process.poll() is not None else None
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.state = SessionState.ERROR
            return TaskResult(
                success=False,
                output="\n".join(self.output_buffer),
                files_modified=set(),
                tool_uses=[],
                error=str(e),
                duration=duration,
                exit_code=None
            )

    def check_health(self) -> bool:
        """
        Check if subprocess is alive and responsive.

        Returns:
            True if healthy, False otherwise
        """
        if self.process is None:
            return False
            
        # Check if process is still running
        if self.process.poll() is not None:
            return False
            
        # Could add ping test here if needed
        return self.state in [SessionState.READY, SessionState.PROCESSING]

    def stop_session(self) -> None:
        """Kill subprocess gracefully (SIGTERM then SIGKILL if needed)."""
        if self.process is None:
            return
            
        try:
            # Signal threads to stop
            self._stop_threads.set()
            
            # Try graceful termination
            self.process.terminate()
            
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if not terminated
                self.process.kill()
                self.process.wait(timeout=2)
                
        except Exception as e:
            self.error_buffer.append(f"Error stopping session: {str(e)}")
        finally:
            self.process = None
            self.state = SessionState.TERMINATED
            
            # Wait for threads to finish
            if self._stdout_thread:
                self._stdout_thread.join(timeout=2)
            if self._stderr_thread:
                self._stderr_thread.join(timeout=2)

    def get_modified_files(self) -> Set[Path]:
        """
        Get set of all files modified during this session.

        Returns:
            Set of Path objects for modified files
        """
        return self.files_modified.copy()

    def reset_modified_files(self) -> None:
        """Clear the tracking of modified files."""
        self.files_modified.clear()

    # Private helper methods

    def _start_output_threads(self) -> None:
        """Start background threads for capturing stdout/stderr."""
        self._stop_threads.clear()
        
        self._stdout_thread = threading.Thread(
            target=self._capture_output,
            args=(self.process.stdout, self.output_buffer),
            daemon=True
        )
        self._stdout_thread.start()
        
        self._stderr_thread = threading.Thread(
            target=self._capture_output,
            args=(self.process.stderr, self.error_buffer),
            daemon=True
        )
        self._stderr_thread.start()

    def _capture_output(self, stream, buffer: List[str]) -> None:
        """Capture output stream to buffer (runs in background thread)."""
        try:
            while not self._stop_threads.is_set():
                line = stream.readline()
                if not line:
                    break
                buffer.append(line.rstrip())
        except Exception as e:
            buffer.append(f"Error capturing output: {str(e)}")

    def _wait_for_ready(self, timeout: int) -> bool:
        """Wait for Claude Code to signal ready state."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                return False
                
            # Look for ready indicators in output
            if any("ready" in line.lower() or "waiting for input" in line.lower() 
                   for line in self.output_buffer[-5:]):
                return True
                
            time.sleep(0.1)
            
        return False

    def _wait_for_completion(self, timeout: int) -> bool:
        """Wait for task completion signal."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                return True
                
            # Look for completion indicators
            recent_output = "\n".join(self.output_buffer[-10:])
            if any(indicator in recent_output for indicator in 
                   ["Task completed", "Done", "Finished", "Error:", "Failed"]):
                return True
                
            time.sleep(0.1)
            
        return False

    def _parse_tool_uses(self, output: List[str]) -> List[Dict[str, Any]]:
        """
        Parse tool invocations from Claude Code output.

        Returns:
            List of tool use dictionaries with name and parameters
        """
        tool_uses = []
        output_text = "\n".join(output)
        
        # Pattern for <invoke name="ToolName"> blocks
        invoke_pattern = r'<invoke name="([^"]+)">(.*?)</invoke>'
        
        for match in re.finditer(invoke_pattern, output_text, re.DOTALL):
            tool_name = match.group(1)
            tool_content = match.group(2)
            
            # Extract parameters
            params = {}
            param_pattern = r'<parameter name="([^"]+)">(.*?)</parameter>'
            
            for param_match in re.finditer(param_pattern, tool_content, re.DOTALL):
                param_name = param_match.group(1)
                param_value = param_match.group(2).strip()
                params[param_name] = param_value
            
            tool_uses.append({
                "name": tool_name,
                "parameters": params
            })
        
        return tool_uses

    def _extract_modified_files(self, tool_uses: List[Dict[str, Any]]) -> Set[Path]:
        """Extract file paths from Write and Edit tool uses."""
        modified = set()
        
        for tool in tool_uses:
            if tool["name"] in ["Write", "str_replace", "create_file"]:
                if "file_path" in tool["parameters"]:
                    file_path = Path(tool["parameters"]["file_path"])
                    if not file_path.is_absolute():
                        file_path = self.work_dir / file_path
                    modified.add(file_path)
                elif "path" in tool["parameters"]:
                    file_path = Path(tool["parameters"]["path"])
                    if not file_path.is_absolute():
                        file_path = self.work_dir / file_path
                    modified.add(file_path)
        
        return modified

    def _check_success(self, output: List[str]) -> bool:
        """Determine if task completed successfully."""
        output_text = "\n".join(output).lower()
        
        # Success indicators
        if any(indicator in output_text for indicator in 
               ["task completed", "successfully", "done"]):
            return True
            
        # Failure indicators
        if any(indicator in output_text for indicator in 
               ["error:", "failed", "exception", "traceback"]):
            return False
            
        # Default to success if no clear failure
        return True

    def _extract_error(self, error_buffer: List[str]) -> Optional[str]:
        """Extract error message from stderr buffer."""
        if not error_buffer:
            return None
            
        # Return last few error lines
        return "\n".join(error_buffer[-10:])
```

---

## 4. Integration with Bot Infrastructure

### 4.1. Bot Adapter Usage Pattern

```python
"""
Example bot implementation using ClaudeCodeCLIAdapter.
"""

class CodingBot:
    """Bot that delegates coding tasks to Claude Code CLI."""
    
    def __init__(self, bot_id: str, workspace: Path):
        self.bot_id = bot_id
        self.workspace = workspace
        self.adapter: Optional[ClaudeCodeCLIAdapter] = None
    
    def execute_coding_task(self, task_description: str) -> bool:
        """Execute a coding task using Claude Code CLI."""
        
        # Initialize adapter for this task
        self.adapter = ClaudeCodeCLIAdapter(
            bot_id=self.bot_id,
            work_dir=self.workspace,
            timeout=600  # 10 minutes
        )
        
        try:
            # Start Claude Code session
            if not self.adapter.start_session():
                print("Failed to start Claude Code session")
                return False
            
            # Send task
            result = self.adapter.send_task(task_description)
            
            # Process results
            if result.success:
                print(f"Task completed successfully in {result.duration:.2f}s")
                print(f"Modified files: {len(result.files_modified)}")
                for file_path in result.files_modified:
                    print(f"  - {file_path}")
                return True
            else:
                print(f"Task failed: {result.error}")
                return False
                
        finally:
            # Always cleanup
            if self.adapter:
                self.adapter.stop_session()
```

### 4.2. Multi-Bot Coordination

```python
"""
Coordinator for multiple bots using Claude Code CLI.
"""

class ClaudeCodeBotCoordinator:
    """Manages multiple bots with Claude Code CLI access."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.active_adapters: Dict[str, ClaudeCodeCLIAdapter] = {}
    
    def assign_task_to_bot(
        self,
        bot_id: str,
        task: str,
        bot_workspace: Optional[Path] = None
    ) -> TaskResult:
        """Assign coding task to specific bot."""
        
        workspace = bot_workspace or (self.workspace_root / bot_id)
        
        # Create or reuse adapter
        if bot_id not in self.active_adapters:
            adapter = ClaudeCodeCLIAdapter(
                bot_id=bot_id,
                work_dir=workspace
            )
            if not adapter.start_session():
                raise RuntimeError(f"Failed to start session for bot {bot_id}")
            self.active_adapters[bot_id] = adapter
        else:
            adapter = self.active_adapters[bot_id]
        
        # Execute task
        return adapter.send_task(task)
    
    def get_bot_modified_files(self, bot_id: str) -> Set[Path]:
        """Get files modified by specific bot."""
        if bot_id in self.active_adapters:
            return self.active_adapters[bot_id].get_modified_files()
        return set()
    
    def shutdown_all(self) -> None:
        """Shutdown all active Claude Code sessions."""
        for adapter in self.active_adapters.values():
            adapter.stop_session()
        self.active_adapters.clear()
```

---

## 5. Testing Strategy

### 5.1. Unit Tests

```python
"""
Unit tests for ClaudeCodeCLIAdapter.
"""

import pytest
from pathlib import Path
from claude_code_cli_adapter import ClaudeCodeCLIAdapter, SessionState


def test_adapter_initialization():
    """Test adapter initializes correctly."""
    adapter = ClaudeCodeCLIAdapter(
        bot_id="test-bot",
        work_dir=Path("/tmp/test")
    )
    assert adapter.bot_id == "test-bot"
    assert adapter.state == SessionState.UNINITIALIZED


def test_session_lifecycle(tmp_path):
    """Test starting and stopping session."""
    adapter = ClaudeCodeCLIAdapter(
        bot_id="test-bot",
        work_dir=tmp_path
    )
    
    # Start session
    started = adapter.start_session()
    assert started
    assert adapter.state == SessionState.READY
    assert adapter.check_health()
    
    # Stop session
    adapter.stop_session()
    assert adapter.state == SessionState.TERMINATED
    assert not adapter.check_health()


def test_simple_task_execution(tmp_path):
    """Test executing simple task."""
    adapter = ClaudeCodeCLIAdapter(
        bot_id="test-bot",
        work_dir=tmp_path
    )
    
    adapter.start_session()
    
    try:
        result = adapter.send_task(
            "Create a file called test.txt with the content 'Hello World'"
        )
        
        assert result.success
        assert len(result.files_modified) > 0
        assert (tmp_path / "test.txt").exists()
        
    finally:
        adapter.stop_session()


def test_task_timeout(tmp_path):
    """Test task timeout handling."""
    adapter = ClaudeCodeCLIAdapter(
        bot_id="test-bot",
        work_dir=tmp_path,
        timeout=1  # 1 second timeout
    )
    
    adapter.start_session()
    
    try:
        result = adapter.send_task(
            "Run an infinite loop"
        )
        
        assert not result.success
        assert "timeout" in result.error.lower()
        
    finally:
        adapter.stop_session()
```

### 5.2. Integration Tests

```python
"""
Integration tests with real Claude Code CLI.
"""

def test_real_coding_task(tmp_path):
    """Test real coding task with Claude Code."""
    
    # Create test project structure
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    
    adapter = ClaudeCodeCLIAdapter(
        bot_id="integration-test",
        work_dir=tmp_path
    )
    
    adapter.start_session()
    
    try:
        # Task: Create a simple Python module with tests
        task = """
        Create a Python module in src/calculator.py with add and multiply functions.
        Then create tests in tests/test_calculator.py using pytest.
        Run the tests to verify they pass.
        """
        
        result = adapter.send_task(task)
        
        assert result.success
        assert (tmp_path / "src" / "calculator.py").exists()
        assert (tmp_path / "tests" / "test_calculator.py").exists()
        
        # Check tool uses
        tool_names = [tool["name"] for tool in result.tool_uses]
        assert "create_file" in tool_names or "Write" in tool_names
        assert "bash_tool" in tool_names  # Should have run pytest
        
    finally:
        adapter.stop_session()
```

---

## 6. Error Handling and Recovery

### 6.1. Error Categories

**6.1.1. Process Errors**
Handle subprocess spawn failures, unexpected process termination, communication pipe failures, and zombie process cleanup.

**6.1.2. Timeout Errors**
Implement task execution timeouts, session startup timeouts, graceful termination timeouts, and force-kill as last resort.

**6.1.3. Parsing Errors**
Handle malformed tool use XML, missing parameters, unexpected output format, and fallback to raw output on parse failure.

**6.1.4. File System Errors**
Manage working directory access issues, file permission problems, disk space exhaustion, and path resolution errors.

### 6.2. Recovery Strategies

```python
class RobustClaudeCodeAdapter(ClaudeCodeCLIAdapter):
    """Enhanced adapter with automatic recovery."""
    
    def send_task_with_retry(
        self,
        task_content: str,
        max_retries: int = 3
    ) -> TaskResult:
        """Send task with automatic retry on failure."""
        
        for attempt in range(max_retries):
            try:
                # Check health before attempting
                if not self.check_health():
                    self.stop_session()
                    if not self.start_session():
                        continue
                
                result = self.send_task(task_content)
                
                if result.success:
                    return result
                    
                # If failure wasn't due to crash, don't retry
                if result.exit_code is None or result.exit_code == 0:
                    return result
                    
                # Process crashed, try restarting
                self.stop_session()
                time.sleep(1)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                self.stop_session()
                time.sleep(1)
        
        return TaskResult(
            success=False,
            output="",
            files_modified=set(),
            tool_uses=[],
            error=f"Failed after {max_retries} attempts",
            duration=0.0,
            exit_code=None
        )
```

---

## 7. Performance Optimization

### 7.1. Session Reuse
Keep Claude Code sessions alive between tasks instead of creating new sessions for each task. This reduces startup overhead and maintains context across related tasks.

### 7.2. Parallel Execution
Run multiple Claude Code sessions in parallel for independent tasks, coordinate through the BotCoordinator, and implement resource limits to prevent overwhelming the system.

### 7.3. Output Buffering
Use efficient buffering strategies for capturing output, implement ring buffers for long-running tasks to limit memory usage, and parse incrementally rather than waiting for completion.

---

## 8. Security Considerations

### 8.1. Working Directory Isolation
Each bot session operates in isolated working directory, implement path validation to prevent directory traversal, and use read-only mounts where appropriate.

### 8.2. Resource Limits
Set CPU and memory limits per process, implement task timeout enforcement, and limit concurrent sessions per bot.

### 8.3. Command Validation
Validate claude CLI path before execution, prevent arbitrary command injection, and sanitize task inputs.

---

## 9. Deployment Checklist

### 9.1. Prerequisites
- [ ] Claude CLI installed and in PATH
- [ ] API key configured in environment
- [ ] Python 3.13+ environment
- [ ] Required permissions for subprocess spawning

### 9.2. Configuration
- [ ] Set appropriate timeout values
- [ ] Configure workspace directory structure
- [ ] Set up logging infrastructure
- [ ] Define retry policies

### 9.3. Testing
- [ ] Run unit tests
- [ ] Execute integration tests with real CLI
- [ ] Verify error handling
- [ ] Test timeout mechanisms
- [ ] Validate file tracking

### 9.4. Monitoring
- [ ] Track session success/failure rates
- [ ] Monitor average task duration
- [ ] Log resource usage
- [ ] Alert on repeated failures

---

## 10. Future Enhancements

### 10.1. Streaming Output
Implement real-time output streaming instead of buffering, enable progress monitoring for long tasks, and provide intermediate status updates to bots.

### 10.2. Task Cancellation
Add ability to cancel running tasks mid-execution, implement graceful cleanup on cancellation, and support task priority queuing.

### 10.3. Advanced Parsing
Improve tool use extraction with better XML parsing, track token usage from Claude Code output, and extract structured results for common task patterns.

### 10.4. Session Pooling
Maintain pool of warm Claude Code sessions, implement session allocation strategy, and optimize for task affinity.

---

## Conclusion

This implementation provides a robust foundation for integrating Claude Code CLI into your autonomous bot runner system. The process-based approach gives bots full access to Claude Code's autonomous capabilities while maintaining proper isolation, error handling, and resource management.

The key benefits are true autonomous coding with file operations and bash execution, clean separation between bot orchestration and Claude Code execution, comprehensive error handling and recovery, detailed tracking of file modifications, and flexible integration with existing bot infrastructure.

Start with the core ClaudeCodeCLIAdapter implementation, add thorough testing at each layer, and progressively enhance with recovery mechanisms and optimizations as operational experience grows.
