# Automatic Parallelization Project

This project is a small multi-agent system that discovers traversal algorithms (BFS/DFS/A*) in Python code, analyzes them, picks a safe parallelization approach, rewrites the code, executes both sequential and parallel variants, and reports correctness and speedup. It uses only the Python 3.10+ standard library.

## How it Works (Pipeline Flow)
1) **Discovery (A2 + T1)**
	- Agent: `CodeDiscoveryAgent` (A2)
	- Tool: `CodebaseScanner` (T1)
	- Scans the target directory for top-level functions. Uses simple AST heuristics to classify BFS (deque/popleft), DFS (append/pop or recursion), and A* (heapq).

2) **Analysis (A3 + T2/T3/T4)**
	- Agent: `ProgramAnalysisAgent` (A3)
	- Tools: `ASTParser` (T2), `DependencyAnalyzer` (T3), `TraversalDetector` (T4)
	- Parses each candidate, checks for explicit `global` declarations, and tags whether it is safe to parallelize (very conservative heuristics).

3) **Strategy Selection (A4 + T5/T6)**
	- Agent: `ParallelizationStrategyAgent` (A4)
	- Tools: `ParallelizationKnowledgeBase` (T5), `StrategySelector` (T6)
	- Chooses a strategy per traversal: threads for BFS/DFS, processes for A*, or sequential if unsafe.

4) **Transformation (A5 + T7)**
	- Agent: `CodeTransformationAgent` (A5)
	- Tool: `CodeRewriter` (T7)
	- Emits a new file in `outputs/` prefixed with `parallel_`. Adds a generated function named `parallel_<original>` implementing a simple threaded BFS/DFS or delegating for A*.

5) **Execution & Validation (A6 + T8/T9/T10)**
	- Agent: `ExecutionValidationAgent` (A6)
	- Tools: `ExecutionSandbox` (T8), `CorrectnessValidator` (T9), `ProfilerTool` (T10)
	- Loads the transformed module, runs the original function and the parallel variant, compares outputs for equality, and reports timing and speedup.

## Directory Layout
- `main.py` — entry point orchestrating the full pipeline.
- `agents/` — multi-agent components: coordinator, discovery, analysis, strategy, transformation, execution & validation.
- `tools/` — helper tools: scanner, AST parser, dependency analysis, traversal detection, knowledge base, strategy selector, code rewriter, execution sandbox, validator, profiler.
- `core/models.py` — shared data classes for pipeline context and artifacts.
- `examples/` — sample traversals: `bfs_example.py`, `dfs_example.py`.
- `outputs/` — generated transformed files (created at runtime).

## Running the Pipeline
```bash
python main.py --target ./examples --output ./outputs
```

What happens:
- Discovers traversal functions under `--target`.
- Analyzes safety and picks a strategy.
- Writes transformed files to `--output` (e.g., `parallel_bfs_example.py`).
- Executes original vs generated functions and prints metrics.

## Configuration Flags
- `--target PATH`    Directory to scan (default: `examples`).
- `--output PATH`    Directory to write transformed files (default: `outputs`).
- `--max-workers N`  Max workers for execution (default: 4).
- `--processes`      Use processes instead of threads (execution step only).
- `--timeout SEC`    Optional per-run timeout.

## Notes and Caveats
- Heuristics are intentionally simple: explicit `global` flags a function as unsafe; attribute access is not currently treated as shared state.
- Generated parallel BFS/DFS are illustrative and thread-based; A* delegates to the original function for correctness.
- Only standard library is used; no external dependencies.

## Extending
- Add new traversal detectors in `tools/traversal_detector.py`.
- Add richer dependency checks in `tools/dependency_analyzer.py`.
- Swap or improve strategies in `tools/strategy_selector.py` and `tools/knowledge_base.py`.
- Enhance rewrites in `tools/code_rewriter.py` to emit more sophisticated parallel code.
