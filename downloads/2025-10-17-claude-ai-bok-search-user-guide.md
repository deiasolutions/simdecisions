# Enhanced BOK Search User Guide

The Enhanced BOK Search component provides advanced search capabilities for the Body of Knowledge (BOK) in the DEIA project. This user guide will walk you through the features and usage of the Enhanced BOK Search.

## Features

1. **Semantic Search**: The Enhanced BOK Search uses TF-IDF vectorization to perform semantic search on the BOK index. It retrieves the most relevant patterns based on the similarity of the query to the pattern content.

2. **Fuzzy Search**: The component also supports fuzzy search, which allows you to find patterns even if there are minor typos or variations in the query. It uses the `rapidfuzz` library to calculate the similarity ratio between the query and the pattern titles.

3. **Related Patterns**: You can find patterns related to a specific pattern using the `find_related` method. It uses cosine similarity to identify patterns with similar content.

## Usage

### Importing the Enhanced BOK Search

To use the Enhanced BOK Search in your Python code, import the `EnhancedBOKSearch` class from the `enhanced_bok_search` module:

```python
from enhanced_bok_search import EnhancedBOKSearch
```

### Initializing the Enhanced BOK Search

Create an instance of the `EnhancedBOKSearch` class by providing the path to the BOK index JSON file:

```python
bok_search = EnhancedBOKSearch(index_path="path/to/bok_index.json")
```

### Performing a Semantic Search

To perform a semantic search on the BOK, use the `search` method and provide the query string:

```python
query = "python list comprehension"
results = bok_search.search(query, top_k=5)
```

The `search` method returns a list of `SearchResult` objects, containing the top `k` most relevant patterns based on the query.

### Performing a Fuzzy Search

To perform a fuzzy search on the BOK, use the `fuzzy_search` method and provide the query string:

```python
query = "pythn list comprhensin"
results = bok_search.fuzzy_search(query, threshold=0.8)
```

The `fuzzy_search` method returns a list of `SearchResult` objects that match the query with a similarity ratio above the specified threshold.

### Finding Related Patterns

To find patterns related to a specific pattern, use the `find_related` method and provide the pattern ID:

```python
pattern_id = "123"
related_patterns = bok_search.find_related(pattern_id, top_k=3)
```

The `find_related` method returns a list of pattern IDs that are most similar to the specified pattern based on cosine similarity.

## Examples

Here are a few examples of how to use the Enhanced BOK Search:

1. Searching for patterns related to "python list comprehension":
   ```python
   query = "python list comprehension"
   results = bok_search.search(query)
   for result in results:
       print(result.title)
   ```

2. Performing a fuzzy search for "pythn list comprhensin":
   ```python
   query = "pythn list comprhensin"
   results = bok_search.fuzzy_search(query)
   for result in results:
       print(result.title)
   ```

3. Finding patterns related to a specific pattern:
   ```python
   pattern_id = "123"
   related_patterns = bok_search.find_related(pattern_id)
   for pattern_id in related_patterns:
       print(pattern_id)
   ```

## Troubleshooting

- If the Enhanced BOK Search is not returning any results, ensure that the BOK index JSON file path is correct and the file exists.

- If the fuzzy search is not matching the expected patterns, adjust the similarity threshold to a lower value (e.g., 0.7) to allow for more variations in the query.

- If the `find_related` method is not returning relevant patterns, check if the specified pattern ID exists in the BOK index.

For any other issues or questions, please refer to the documentation or contact the development team.

