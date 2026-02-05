# Integrating Enhanced BOK Search

This guide provides instructions on how to integrate the Enhanced BOK Search component into the DEIA project.

## Dependencies
To use the Enhanced BOK Search component, make sure to install the following dependencies:
- `rapidfuzz` library: Used for fuzzy string matching
  ```
  pip install rapidfuzz
  ```
- Update `pyproject.toml` to include `rapidfuzz` in the dependencies section:
  ```toml
  [tool.poetry.dependencies]
  python = "^3.9"
  rapidfuzz = "^2.0.0"
  ```

## Integration Steps
1. Copy the `enhanced_bok_search.py` file to the `src/deia/services/` directory.
   ```
   cp enhanced_bok_search.py src/deia/services/
   ```

2. Update the `DEIAContextLoader` class in `src/deia/context/deia_context_loader.py` to use the `EnhancedBOKSearch` class:
   ```python
   from deia.services.enhanced_bok_search import EnhancedBOKSearch

   class DEIAContextLoader:
       def __init__(self, index_path: str):
           self.bok_search = EnhancedBOKSearch(index_path)

       def search_bok(self, query: str, top_k: int = 5) -> List[SearchResult]:
           return self.bok_search.search(query, top_k)

       def fuzzy_search_bok(self, query: str, threshold: float = 0.8) -> List[SearchResult]:
           return self.bok_search.fuzzy_search(query, threshold)
   ```

3. Update the `DEIAAgent` class in `src/deia/agents/deia_agent.py` to use the new BOK search methods:
   ```python
   from deia.context.deia_context_loader import DEIAContextLoader

   class DEIAAgent:
       def __init__(self, context_loader: DEIAContextLoader):
           self.context_loader = context_loader

       def search_bok(self, query: str, top_k: int = 5) -> List[SearchResult]:
           return self.context_loader.search_bok(query, top_k)

       def fuzzy_search_bok(self, query: str, threshold: float = 0.8) -> List[SearchResult]:
           return self.context_loader.fuzzy_search_bok(query, threshold)
   ```

4. Test the integration by running the following commands:
   ```python
   from deia.agents.deia_agent import DEIAAgent
   from deia.context.deia_context_loader import DEIAContextLoader

   context_loader = DEIAContextLoader(index_path="path/to/bok_index.json")
   agent = DEIAAgent(context_loader)

   results = agent.search_bok("python list comprehension")
   print(results)

   fuzzy_results = agent.fuzzy_search_bok("pyhton list comprension")
   print(fuzzy_results)
   ```

## Configuration
The Enhanced BOK Search component uses the following default configuration:
- Index path: The path to the BOK index JSON file (default: `"path/to/bok_index.json"`)
- TF-IDF parameters:
  - `min_df`: Ignore terms that have a document frequency strictly lower than the given threshold (default: `1`)
  - `max_df`: Ignore terms that have a document frequency strictly higher than the given threshold (default: `1.0`)

You can modify these parameters by updating the `EnhancedBOKSearch` constructor call in the `DEIAContextLoader` class:
```python
self.bok_search = EnhancedBOKSearch(index_path, min_df=2, max_df=0.9)
```

## Common Issues
- **Issue:** `rapidfuzz` library not found
  **Solution:** Make sure to install the `rapidfuzz` library and update the `pyproject.toml` file with the correct dependency.

- **Issue:** BOK index file not found
  **Solution:** Ensure that the `index_path` parameter points to the correct location of the BOK index JSON file.

If you encounter any other issues during the integration process, please refer to the troubleshooting guide or reach out to the development team for assistance.

