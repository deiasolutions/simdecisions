# Integrating Session Logger

This guide provides instructions on how to integrate the Session Logger component into the DEIA project.

## Dependencies
The Session Logger component does not have any additional dependencies beyond the standard Python libraries.

## Integration Steps
1. Copy the `session_logger.py` file to the `src/deia/logging/` directory.
   ```
   cp session_logger.py src/deia/logging/
   ```

2. Update the `DEIAAgent` class in `src/deia/agents/deia_agent.py` to initialize and use the `SessionLogger` class:
   ```python
   from deia.logging.session_logger import SessionLogger

   class DEIAAgent:
       def __init__(self, agent_id: str):
           self.session_logger = SessionLogger(agent_id)

       def log_task_start(self, task_name: str, metadata: dict = None):
           self.session_logger.log_task_start(task_name, metadata)

       def log_task_complete(self, task_name: str, duration_ms: int, metadata: dict = None):
           self.session_logger.log_task_complete(task_name, duration_ms, metadata)

       # Add other logging methods as needed
   ```

3. Integrate the session logging into the relevant parts of the DEIA project:
   - In the query handling process:
     ```python
     def handle_query(self, query: str) -> str:
         self.log_task_start("Handle Query", {"query": query})
         # Process the query
         # ...
         self.log_task_complete("Handle Query", duration_ms, {"response": response})
         return response
     ```

   - In the file processing logic:
     ```python
     def process_file(self, file_path: str):
         self.log_file_read(file_path)
         # Process the file
         # ...
         self.log_file_write(output_path, size_bytes, lines)
     ```

   - In the tool invocation code:
     ```python
     def invoke_tool(self, tool_name: str, params: dict):
         self.log_tool_call(tool_name, params, duration_ms)
         # Invoke the tool
         # ...
     ```

4. Configure the session log storage:
   - Create a directory for storing session logs, e.g., `logs/sessions/`.
   - Update the `save_session` method in the `SessionLogger` class to use the appropriate directory:
     ```python
     def save_session(self, output_dir: str = "logs/sessions"):
         # ...
     ```

5. Test the integration by running the DEIA project and verifying that session logs are being generated and stored correctly.

## Configuration
The Session Logger component uses the following default configuration:
- Session log storage directory: `logs/sessions/`

You can modify the storage directory by updating the `save_session` method in the `SessionLogger` class.

## Common Issues
- **Issue:** Session logs not being generated
  **Solution:** Ensure that the session logging methods (`log_task_start`, `log_task_complete`, etc.) are being called correctly in the appropriate places within the DEIA project.

- **Issue:** Session logs not being saved
  **Solution:** Verify that the `save_session` method is being called at the end of each session and that the specified output directory exists and has write permissions.

If you encounter any other issues during the integration process, please refer to the troubleshooting guide or reach out to the development team for assistance.

