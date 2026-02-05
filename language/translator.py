from lark import Lark, Transformer, exceptions
from backend.app.llm_clients import LLMClient
import asyncio
import re

# Grammar for the English-like Script Language
script_grammar = r"""
    ?start: command

    command: create_task | list_tasks | assign_task | get_task | send_message

    create_task: "CREATE" "TASK" "with" "title" ESCAPED_STRING ("and" "description" ESCAPED_STRING)? -> create_task
    list_tasks: "LIST" "TASKS" ("with" "status" ESCAPED_STRING)? -> list_tasks
    assign_task: "ASSIGN" "TASK" ESCAPED_STRING "to" "AGENT" ESCAPED_STRING -> assign_task
    get_task: "GET" "TASK" ESCAPED_STRING -> get_task
    send_message: "SEND" "MESSAGE" ESCAPED_STRING "to" "CHANNEL" ESCAPED_STRING -> send_message

    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""

class ScriptToHiveTransformer(Transformer):
    def ESCAPED_STRING(self, s):
        # Remove quotes
        return s[1:-1]

    def create_task(self, items):
        title = items[4]
        desc = items[7] if len(items) > 7 else None
        
        if desc:
            return f'SORTU ZEREGINA "{title}" izenburuarekin eta "{desc}" deskribapenarekin'
        else:
            return f'SORTU ZEREGINA "{title}" izenburuarekin'
            
    def list_tasks(self, items):
        if len(items) > 2:
            status = items[4]
            return f'ZERRENDATU ZEREGINAK "{status}" egoerarekin'
        else:
            return 'ZERRENDATU ZEREGINAK'

    def assign_task(self, items):
        task_id = items[2]
        agent_id = items[5]
        return f'ESLEITU ZEREGINA "{task_id}" "{agent_id}" eragileari'

    def get_task(self, items):
        task_id = items[2]
        return f'LORTU ZEREGINA "{task_id}"'
        
    def send_message(self, items):
        message = items[2]
        channel = items[5]
        return f'BIDALI MEZUA "{message}" "{channel}" kanalari'


# Initialize parser and transformer
script_parser = Lark(script_grammar, start='command', parser='lalr', case_sensitive=False)
hive_transformer = ScriptToHiveTransformer()
llm_client = LLMClient() # Initialize LLM client for fallback

async def async_translate_script_to_hive_code(script: str, context: str = None) -> str:
    """
    Translates a Script Language string into a Hive Code string using a Lark parser,
    with an LLM fallback for ambiguous inputs.
    """
    try:
        # Fast Path: Rule-based parsing
        tree = script_parser.parse(script)
        hive_code = hive_transformer.transform(tree)
        return hive_code
    except exceptions.UnexpectedInput as e:
        # Fallback Path: LLM-based translation or clarification
        print(f"Lark parser failed for '{script}'. Falling back to LLM. Error: {e}")
        llm_response = await llm_client.translate_or_clarify(script, context=context)
        
        # Attempt to extract Hive Code from LLM response
        # This regex looks for common Hive Code verbs at the start of a line
        hive_code_match = re.search(r'^(SORTU|ZERRENDATU|ESLEITU|LORTU|BIDALI)\s+.*', llm_response, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if hive_code_match:
            return hive_code_match.group(0).strip()
        elif "clarify" in llm_response.lower() or "ambiguous" in llm_response.lower() or "more information" in llm_response.lower():
            raise ValueError(f"LLM requires clarification: {llm_response}")
        else:
            raise ValueError(f"LLM could not translate and did not ask for clarification: {llm_response}")

def translate_script_to_hive_code(script: str, context: str = None) -> str:
    """Synchronous wrapper for the async translation function."""
    return asyncio.run(async_translate_script_to_hive_code(script, context))


# Example Usage
if __name__ == "__main__":
    scripts_to_test = [
        'CREATE TASK with title "Review ADR-010" and description "A new language spec"',
        'CREATE TASK with title "A simple task"',
        'LIST TASKS with status "pending"',
        'LIST TASKS',
        'ASSIGN TASK "task-123" to AGENT "BEE-001"',
        'GET TASK "task-456"',
        'SEND MESSAGE "Hello World" to CHANNEL "general"',
        'create a new task about the project scope', # Ambiguous for Lark, should go to LLM
        'list all the pending items please', # Ambiguous for Lark, should go to LLM
    ]

    for script_input in scripts_to_test:
        try:
            hive_code_output = translate_script_to_hive_code(script_input)
            print(f'Script: "{script_input}"\nHive Code: {hive_code_output}\n')
        except ValueError as e:
            print(f'Failed to translate script: "{script_input}"')
            print(f'Error: {e}\n')
        except Exception as e:
            print(f'An unexpected error occurred for script: "{script_input}"')
            print(f'Error: {e}\n')
