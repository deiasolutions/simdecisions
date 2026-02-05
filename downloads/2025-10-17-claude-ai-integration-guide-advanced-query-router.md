# Integrating Advanced Query Router

This guide provides instructions on how to integrate the Advanced Query Router component into the DEIA project.

## Dependencies
The Advanced Query Router component does not have any additional dependencies beyond the standard Python libraries.

## Integration Steps
1. Copy the `query_router_advanced.py` file to the `src/deia/routing/` directory.
   ```
   cp query_router_advanced.py src/deia/routing/
   ```

2. Update the `DEIAAgent` class in `src/deia/agents/deia_agent.py` to use the `AdvancedQueryRouter` class:
   ```python
   from deia.routing.query_router_advanced import AdvancedQueryRouter

   class DEIAAgent:
       def __init__(self, agents: List[Agent]):
           self.query_router = AdvancedQueryRouter(agents)

       def route_query(self, query: str) -> RoutingDecision:
           return self.query_router.route_with_confidence(query, self.query_router.agents)
   ```

3. Update the `DEIAQueryHandler` class in `src/deia/query_handler/deia_query_handler.py` to use the `DEIAAgent` for query routing:
   ```python
   from deia.agents.deia_agent import DEIAAgent

   class DEIAQueryHandler:
       def __init__(self, agents: List[Agent]):
           self.agent = DEIAAgent(agents)

       def handle_query(self, query: str) -> str:
           routing_decision = self.agent.route_query(query)
           # Process the query based on the routing decision
           # ...
           return response
   ```

4. Test the integration by running the following commands:
   ```python
   from deia.agents.deia_agent import Agent
   from deia.query_handler.deia_query_handler import DEIAQueryHandler

   agents = [
       Agent("ClaudeCode", ["python", "debugging", "algorithms"]),
       Agent("ClaudeDialog", ["conversation", "writing", "proofreading"]),
       # Add more agents as needed
   ]

   query_handler = DEIAQueryHandler(agents)

   query = "How do I optimize a Python script for performance?"
   response = query_handler.handle_query(query)
   print(response)
   ```

## Configuration
The Advanced Query Router component does not require any additional configuration.

## Common Issues
- **Issue:** Agents not properly initialized
  **Solution:** Ensure that the `agents` list is populated with the correct `Agent` instances, specifying their IDs and capabilities.

- **Issue:** Query routing not working as expected
  **Solution:** Verify that the agent capabilities are accurately defined and match the expected query types. Review the routing logic in the `AdvancedQueryRouter` class to ensure it aligns with your requirements.

If you encounter any other issues during the integration process, please refer to the troubleshooting guide or reach out to the development team for assistance.

