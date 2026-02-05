# Advanced Query Router Technical Guide

This technical guide provides an in-depth explanation of how the Advanced Query Router component works in the DEIA project. It covers the routing mechanism, complexity scoring, capability matching, confidence thresholds, and configuration options.

## Routing Mechanism

The Advanced Query Router is responsible for routing user queries to the appropriate agent based on the query's complexity and the agent's capabilities. The routing process involves the following steps:

1. **Query Complexity Scoring**: The router analyzes the query and assigns a complexity score based on factors such as word count, technical terms, ambiguity indicators, multi-step indicators, and code/system keywords. The complexity score ranges from 1 to 10, with higher scores indicating more complex queries.

2. **Capability Matching**: The router compares the query against the capabilities of each available agent. It calculates a match score for each agent based on the overlap between the query keywords and the agent's capabilities. The match score ranges from 0 to 1, with higher scores indicating a better match.

3. **Confidence Threshold**: The router determines the confidence level of the routing decision based on the highest match score achieved. If the highest match score exceeds a predefined confidence threshold (default: 0.7), the query is considered to have a high-confidence match. If the match score is below the threshold, the router may choose a fallback agent or route the query to a default agent.

4. **Routing Decision**: The router selects the agent with the highest match score as the primary agent for handling the query. If the primary agent's match score is below the confidence threshold, the router may assign a fallback agent to assist with the query. The routing decision also includes an estimated duration for the query based on its complexity.

## Complexity Scoring Algorithm

The complexity scoring algorithm takes into account various factors to determine the complexity of a query. The factors and their weights are as follows:

- Word count: The number of words in the query divided by 10.
- Technical terms: The count of technical terms (identified by uppercase letters) multiplied by 2.
- Ambiguity indicators: The count of ambiguity indicators (e.g., "or," "versus") multiplied by 3.
- Multi-step indicators: The count of multi-step indicators (e.g., "then," "next") multiplied by 2.
- Code/system keywords: The count of code or system-related keywords multiplied by 3.

The weighted scores are summed up to obtain the final complexity score, which is then capped at a maximum value of 10.

## Capability Matching

The capability matching process involves comparing the query keywords against the predefined capabilities of each agent. The router maintains a mapping of agent IDs to their respective capabilities.

To determine the match score, the router follows these steps:

1. Tokenize the query into individual words.
2. For each agent, calculate the overlap between the query words and the agent's capabilities.
3. Divide the overlap count by the total number of capabilities for the agent to obtain the match score.

The agent with the highest match score is considered the best match for the query.

## Confidence Thresholds

The confidence threshold determines the minimum match score required for a query to be considered a high-confidence match. The default confidence threshold is set to 0.7, but it can be adjusted based on the specific requirements of the project.

If the highest match score exceeds the confidence threshold, the query is routed to the primary agent with high confidence. If the match score is below the threshold, the router may assign a fallback agent or route the query to a default agent.

## Configuration Options

The Advanced Query Router provides the following configuration options:

- `confidence_threshold`: The minimum match score required for a high-confidence match (default: 0.7).
- `default_agent`: The ID of the default agent to route queries to when no suitable agent is found.
- `fallback_agent`: The ID of the fallback agent to assist with queries when the primary agent's match score is below the confidence threshold.

These configuration options can be modified based on the project's needs and the available agents.

## Error Handling

The Advanced Query Router includes error handling mechanisms to gracefully handle scenarios such as:

- No agents available: If no agents are provided during initialization, the router will route all queries to the default agent.
- No matching agents: If no agents match the query's keywords, the router will route the query to the default agent.
- Invalid configuration: If the provided configuration options are invalid (e.g., non-existent agent IDs), the router will raise an exception with an appropriate error message.

## Logging and Monitoring

The Advanced Query Router incorporates logging and monitoring capabilities to track the routing process and identify potential issues. The following information is logged:

- Query received: The received query and its timestamp.
- Complexity score: The calculated complexity score for the query.
- Capability matching: The match scores for each agent.
- Routing decision: The selected primary agent, fallback agent (if applicable), and the estimated duration.
- Errors and exceptions: Any errors or exceptions encountered during the routing process.

The logs can be used for debugging, performance analysis, and monitoring the system's health.

## Conclusion

The Advanced Query Router plays a crucial role in efficiently routing user queries to the appropriate agents based on query complexity and agent capabilities. By leveraging complexity scoring, capability matching, and confidence thresholds, the router ensures that queries are handled by the most suitable agents, improving the overall system's performance and user experience.

This technical guide provides a comprehensive understanding of the Advanced Query Router's inner workings, configuration options, error handling, and logging capabilities. It serves as a reference for developers and system administrators working with the DEIA project.
