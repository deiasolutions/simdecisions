# Session Logger User Guide

The Session Logger is a powerful tool for tracking and analyzing agent activities, task durations, file operations, and tool usage within the DEIA project. This user guide will walk you through the usage of the Session Logger, including how to integrate it into your agent's workflow, analyze sessions, and interpret the logged data.

## Integrating Session Logging

To integrate session logging into your agent's workflow, follow these steps:

1. Import the `SessionLogger` class from the `session_logger` module:
   ```python
   from session_logger import SessionLogger
   ```

2. Initialize a `SessionLogger` instance with your agent's ID:
   ```python
   session_logger = SessionLogger(agent_id="your_agent_id")
   ```

3. Throughout your agent's code, add logging statements for relevant events:
   - Log task start and completion:
     ```python
     session_logger.log_task_start("task_name", metadata={"key": "value"})
     # Perform the task
     session_logger.log_task_complete("task_name", duration_ms=1000)
     ```
   
   - Log file read and write operations:
     ```python
     session_logger.log_file_read("file_path", size_bytes=1024)
     # Read the file
     session_logger.log_file_write("file_path", size_bytes=2048, lines=100)
     # Write to the file
     ```
   
   - Log tool and function calls:
     ```python
     session_logger.log_tool_call("tool_name", params={"param1": "value1"}, duration_ms=500)
     # Call the tool or function
     ```

4. At the end of your agent's execution or at appropriate checkpoints, save the session log:
   ```python
   session_logger.save_session(output_dir="path/to/logs")
   ```

By adding these logging statements throughout your agent's code, you can capture valuable information about the agent's activities, task durations, file operations, and tool usage.

## Analyzing Sessions

To analyze a session and gain insights into your agent's performance, you can use the `analyze_session` method provided by the `SessionLogger` class. Here's how to use it:

```python
session_logger = SessionLogger(agent_id="your_agent_id")
analysis = session_logger.analyze_session("path/to/session_log.jsonl")
```

The `analyze_session` method takes the path to a saved session log file (in JSONL format) and returns a `SessionAnalysis` object containing various metrics and statistics.

The `SessionAnalysis` object provides the following information:
- `task_breakdown`: A dictionary mapping task names to their total duration in milliseconds.
- `bottlenecks`: A list of task names that took a significant portion of the total session duration.
- `velocity_metrics`: A dictionary containing velocity metrics such as tasks completed per hour, files read/written per hour, and tool calls per hour.
- `file_operation_stats`: A dictionary showing the count of file read and write operations.

You can access these attributes to gain insights into your agent's performance and identify areas for improvement.

## Interpreting Logged Data

The session log files are stored in JSONL format, where each line represents a logged event. The logged events can be of the following types:
- `TaskEvent`: Represents the start or completion of a task.
- `FileEvent`: Represents a file read or write operation.
- `ToolEvent`: Represents a tool or function call.

Each logged event contains relevant information such as the event type, timestamp, task name, file path, tool name, and associated metadata.

When analyzing the logged data, you can look for patterns, identify bottlenecks, and calculate metrics based on the event data. For example, you can:
- Calculate the total duration of each task by subtracting the task start time from the task complete time.
- Identify tasks that took a significant portion of the total session duration and consider them as potential bottlenecks.
- Compute velocity metrics by dividing the count of tasks completed, files read/written, or tool calls by the total session duration in hours.
- Analyze the file operation stats to understand the I/O behavior of your agent.

By interpreting the logged data, you can gain valuable insights into your agent's performance, identify areas for optimization, and make data-driven decisions to improve its efficiency and effectiveness.

## Best Practices

Here are some best practices to keep in mind when using the Session Logger:

1. Be consistent in logging events: Ensure that you log relevant events consistently throughout your agent's code to capture a complete picture of its activities.

2. Use meaningful task and event names: Choose descriptive and meaningful names for tasks and events to make the logged data more understandable and easier to analyze.

3. Provide relevant metadata: Include relevant metadata when logging events to provide additional context and information for analysis.

4. Save session logs regularly: Save session logs at appropriate intervals or checkpoints to prevent data loss and ensure a comprehensive record of your agent's activities.

5. Analyze sessions periodically: Regularly analyze session logs to identify trends, bottlenecks, and areas for improvement in your agent's performance.

6. Use session analysis to optimize performance: Leverage the insights gained from session analysis to optimize your agent's code, reduce bottlenecks, and improve overall efficiency.

By following these best practices, you can effectively utilize the Session Logger to monitor and optimize your agent's performance in the DEIA project.

## Conclusion

The Session Logger is a valuable tool for tracking and analyzing agent activities, task durations, file operations, and tool usage within the DEIA project. By integrating session logging into your agent's workflow and leveraging the session analysis capabilities, you can gain deep insights into your agent's performance, identify bottlenecks, and make data-driven decisions to optimize its efficiency and effectiveness.

This user guide provides a comprehensive overview of how to use the Session Logger, analyze sessions, interpret logged data, and follow best practices for effective session logging and analysis. By utilizing the Session Logger, you can continuously monitor and improve your agent's performance in the DEIA project.
