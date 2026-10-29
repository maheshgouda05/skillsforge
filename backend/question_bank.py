"""Comprehensive Question Bank for technical assessments across multiple engineering domains."""

import random
from typing import Dict, List, Optional
from skills import get_role_skills, normalize_skill

QUESTION_BANK: Dict[str, List[dict]] = {
    "python": [
        {
            "id": "py_01",
            "skill": "python",
            "question": "Which Python data type is mutable and maintains insertion order (as of Python 3.7+)?",
            "options": ["tuple", "list", "frozenset", "int"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "Lists in Python are mutable ordered sequences that retain insertion order."
        },
        {
            "id": "py_02",
            "skill": "python",
            "question": "What is the time complexity of looking up a key in a standard Python dictionary in the average case?",
            "options": ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
            "answer": 2,
            "difficulty": "medium",
            "explanation": "Python dictionaries are implemented using hash tables, giving average O(1) lookup time."
        },
        {
            "id": "py_03",
            "skill": "python",
            "question": "What does the `*args` syntax in a function definition signify?",
            "options": ["Keyword-only arguments", "Arbitrary number of positional arguments", "A pointer reference", "Mandatory arguments"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`*args` allows a function to accept any number of positional arguments unpacked into a tuple."
        },
        {
            "id": "py_04",
            "skill": "python",
            "question": "Which built-in function returns an iterator that produces tuples containing count and value?",
            "options": ["zip()", "map()", "enumerate()", "filter()"],
            "answer": 2,
            "difficulty": "easy",
            "explanation": "`enumerate()` pairs each element of an iterable with an incrementing integer counter."
        },
        {
            "id": "py_05",
            "skill": "python",
            "question": "What is the purpose of the `__init__` method in Python classes?",
            "options": ["To destroy class instances", "To initialize attributes when an instance is instantiated", "To define static methods", "To enforce private variables"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`__init__` is the constructor method called to initialize newly created object attributes."
        },
        {
            "id": "py_06",
            "skill": "python",
            "question": "What does a generator function return when called?",
            "options": ["A list of all generated values", "A generator object that yields items lazily", "A coroutine", "None"],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "A generator function contains `yield` and produces a generator iterator evaluating values on demand."
        },
        {
            "id": "py_07",
            "skill": "python",
            "question": "What will `bool([])` evaluate to in Python?",
            "options": ["True", "False", "None", "TypeError"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "Empty collections (like empty lists `[]`) evaluate to `False` in boolean contexts."
        },
        {
            "id": "py_08",
            "skill": "python",
            "question": "Which Python module provides tools for working with high-performance C-based datatypes such as `deque` and `Counter`?",
            "options": ["itertools", "collections", "functools", "sys"],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "The `collections` module provides specialized container datatypes like `deque`, `Counter`, `defaultdict`."
        },
        {
            "id": "py_09",
            "skill": "python",
            "question": "What does the Global Interpreter Lock (GIL) primarily restrict in standard CPython?",
            "options": ["Multiple processes from running concurrently", "Multiple native threads from executing Python bytecode simultaneously", "Memory allocation over 4GB", "Garbage collection execution"],
            "answer": 1,
            "difficulty": "hard",
            "explanation": "The GIL is a mutex preventing multiple native OS threads from running Python bytecode in parallel inside one process."
        },
        {
            "id": "py_10",
            "skill": "python",
            "question": "What is the output of `[x**2 for x in range(4) if x % 2 == 0]`?",
            "options": ["[0, 4]", "[1, 9]", "[0, 1, 4, 9]", "[4, 16]"],
            "answer": 0,
            "difficulty": "medium",
            "explanation": "Even numbers in range(4) are 0 and 2. Squaring them yields [0, 4]."
        }
    ],

    "sql": [
        {
            "id": "sql_01",
            "skill": "sql",
            "question": "Which SQL statement is used to extract data from a relational database?",
            "options": ["EXTRACT", "SELECT", "QUERY", "RETRIEVE"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`SELECT` is the standard DQL command used to query records from database tables."
        },
        {
            "id": "sql_02",
            "skill": "sql",
            "question": "What is the difference between `WHERE` and `HAVING` in SQL?",
            "options": [
                "`WHERE` filters aggregated groups, `HAVING` filters individual rows",
                "`WHERE` filters rows before aggregation, `HAVING` filters aggregated groups",
                "`HAVING` can only be used with subqueries",
                "There is no difference"
            ],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "`WHERE` filters table records before grouping, whereas `HAVING` applies filters on grouped/aggregated data."
        },
        {
            "id": "sql_03",
            "skill": "sql",
            "question": "Which JOIN returns all rows from the left table and matching rows from the right table?",
            "options": ["INNER JOIN", "RIGHT JOIN", "LEFT JOIN", "FULL OUTER JOIN"],
            "answer": 2,
            "difficulty": "easy",
            "explanation": "`LEFT JOIN` preserves all rows from the left table, populating NULLs for non-matching right table columns."
        },
        {
            "id": "sql_04",
            "skill": "sql",
            "question": "What type of index is typically created automatically on a PRIMARY KEY column?",
            "options": ["Composite Index", "Unique / Clustered Index", "Bitmap Index", "Full-text Index"],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "Primary keys require uniqueness and non-null values, automatically prompting unique index creation."
        },
        {
            "id": "sql_05",
            "skill": "sql",
            "question": "What does ACID stand for in database transaction management?",
            "options": [
                "Accuracy, Consistency, Integrity, Durability",
                "Atomicity, Consistency, Isolation, Durability",
                "Action, Concurrency, Indexing, Delivery",
                "Availability, Consistency, Isolation, Distribution"
            ],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "ACID properties (Atomicity, Consistency, Isolation, Durability) guarantee reliable transaction execution."
        },
        {
            "id": "sql_06",
            "skill": "sql",
            "question": "Which SQL function assigns a unique sequential integer to rows within a partitioned window?",
            "options": ["RANK()", "DENSE_RANK()", "ROW_NUMBER()", "NTILE()"],
            "answer": 2,
            "difficulty": "medium",
            "explanation": "`ROW_NUMBER()` assigns contiguous sequential integers without gaps to rows in each window partition."
        },
        {
            "id": "sql_07",
            "skill": "sql",
            "question": "What happens when you execute `DROP TABLE` versus `TRUNCATE TABLE`?",
            "options": [
                "`DROP` removes structure and data; `TRUNCATE` deletes all rows while preserving the table schema",
                "`TRUNCATE` removes structure and data; `DROP` only removes rows",
                "Both commands perform identical rollback-supported deletions",
                "`DROP` only works on temporary tables"
            ],
            "answer": 0,
            "difficulty": "medium",
            "explanation": "`DROP TABLE` deletes the entire table definition and data from the catalog. `TRUNCATE` clears rows fast."
        },
        {
            "id": "sql_08",
            "skill": "sql",
            "question": "What is the purpose of database normalization (e.g., 3NF)?",
            "options": ["To increase query complexity", "To reduce data redundancy and eliminate undesirable update anomalies", "To avoid writing SQL joins", "To increase disk storage usage"],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "Normalization organizes data into logical entities, eliminating redundancy and insertion/update/deletion anomalies."
        }
    ],

    "fastapi": [
        {
            "id": "fa_01",
            "skill": "fastapi",
            "question": "Which Python library does FastAPI use under the hood for data validation and schema serialization?",
            "options": ["Marshmallow", "Pydantic", "Cerberus", "Attrs"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "FastAPI is built on top of Pydantic for request parsing, type validation, and OpenAPI documentation."
        },
        {
            "id": "fa_02",
            "skill": "fastapi",
            "question": "Which ASGI server is most commonly used to run FastAPI applications in production?",
            "options": ["Gunicorn with WSGI", "Uvicorn", "Flask-Server", "Nginx directly"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "Uvicorn is a lightning-fast ASGI web server implementation used as the standard runtime for FastAPI."
        },
        {
            "id": "fa_03",
            "skill": "fastapi",
            "question": "How do you declare dependency injection in FastAPI route handlers?",
            "options": ["Using `@inject` decorator", "Using `Depends()` parameter in endpoint signature", "Via a global config file", "Through class inheritance only"],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "FastAPI provides `from fastapi import Depends` to declare reusable shared dependencies cleanly."
        },
        {
            "id": "fa_04",
            "skill": "fastapi",
            "question": "Which built-in interactive documentation interfaces does FastAPI automatically generate?",
            "options": ["Swagger UI (/docs) and ReDoc (/redoc)", "Postman Collections only", "GraphQL Playground only", "Sphinx HTML docs"],
            "answer": 0,
            "difficulty": "easy",
            "explanation": "FastAPI automatically generates interactive Swagger UI at `/docs` and ReDoc documentation at `/redoc`."
        },
        {
            "id": "fa_05",
            "skill": "fastapi",
            "question": "How does FastAPI handle `async def` endpoints compared to standard `def` endpoints?",
            "options": [
                "`async def` runs on the event loop; `def` runs in a separate external threadpool to prevent blocking",
                "`def` endpoints are not supported in FastAPI",
                "`async def` creates a new OS process per request",
                "There is no difference in execution runtime"
            ],
            "answer": 0,
            "difficulty": "hard",
            "explanation": "FastAPI executes `async def` functions directly in the main event loop, while sync `def` calls run in AnyIO worker threads."
        }
    ],

    "git": [
        {
            "id": "git_01",
            "skill": "git",
            "question": "Which Git command is used to record staged changes to the local repository history?",
            "options": ["git stage", "git save", "git commit", "git push"],
            "answer": 2,
            "difficulty": "easy",
            "explanation": "`git commit` snapshots the staged changes into the local repository with an informative commit message."
        },
        {
            "id": "git_02",
            "skill": "git",
            "question": "What does `git rebase` do compared to `git merge`?",
            "options": [
                "`rebase` rewires commit history by reapplying commits onto a new base tip, creating a linear history",
                "`merge` rewires history while `rebase` preserves original commit hashes exactly",
                "`rebase` deletes commits permanently from the branch",
                "`rebase` is only used for remote repository sync"
            ],
            "answer": 0,
            "difficulty": "medium",
            "explanation": "`git rebase` reapplies your feature commits on top of the target branch tip, avoiding merge commit bubbles."
        },
        {
            "id": "git_03",
            "skill": "git",
            "question": "Which command allows you to temporarily save uncommitted modifications without committing them?",
            "options": ["git cache", "git stash", "git pause", "git store"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`git stash` temporarily shelves tracked modifications so you can switch branches cleanly."
        },
        {
            "id": "git_04",
            "skill": "git",
            "question": "What is the command to create and switch to a new branch in a single command?",
            "options": ["git branch -new <name>", "git checkout -b <name>", "git switch -create <name>", "git make <name>"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`git checkout -b <name>` (or `git switch -c <name>`) creates and checks out the new branch immediately."
        }
    ],

    "rest apis": [
        {
            "id": "rest_01",
            "skill": "rest apis",
            "question": "Which HTTP method is considered idempotent and used for complete resource replacement?",
            "options": ["POST", "PUT", "PATCH", "DELETE"],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "`PUT` is idempotent and replaces the entire target resource with the uploaded payload."
        },
        {
            "id": "rest_02",
            "skill": "rest apis",
            "question": "What does HTTP status code 401 Unauthorized indicate?",
            "options": [
                "The server encountered an unhandled exception",
                "The request lacks valid authentication credentials",
                "The authenticated user does not have permission for the resource",
                "The requested resource was not found"
            ],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "401 Unauthorized specifically means authentication is required or credentials are missing/invalid."
        },
        {
            "id": "rest_03",
            "skill": "rest apis",
            "question": "What is the primary difference between `PUT` and `PATCH` methods?",
            "options": [
                "`PUT` replaces the whole entity; `PATCH` applies partial modifications to the entity",
                "`PATCH` is idempotent while `PUT` is never idempotent",
                "`PUT` cannot include a request body",
                "`PATCH` is only supported in HTTP/2"
            ],
            "answer": 0,
            "difficulty": "medium",
            "explanation": "RFC 5789 defines `PATCH` for partial resource updates, whereas `PUT` replaces the full resource representation."
        },
        {
            "id": "rest_04",
            "skill": "rest apis",
            "question": "Which standard HTTP header is used to pass a bearer JWT token for authorized requests?",
            "options": ["Token-Verify", "Authorization", "X-Auth-Token", "Authentication"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "The standard HTTP header is `Authorization: Bearer <token>`."
        }
    ],

    "javascript": [
        {
            "id": "js_01",
            "skill": "javascript",
            "question": "What is the difference between `let` and `var` in modern JavaScript?",
            "options": [
                "`let` is block-scoped and does not create window properties; `var` is function-scoped",
                "`var` is block-scoped; `let` is globally scoped",
                "`let` variables cannot be reassigned",
                "There is no difference in modern browsers"
            ],
            "answer": 0,
            "difficulty": "easy",
            "explanation": "`let` provides block scoping and avoids variable hoisting bugs associated with `var`."
        },
        {
            "id": "js_02",
            "skill": "javascript",
            "question": "What does the expression `'5' - 3` evaluate to in JavaScript?",
            "options": ["'53'", "2", "NaN", "TypeError"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "The minus operator triggers numeric coercion, converting the string '5' to number 5, resulting in 2."
        },
        {
            "id": "js_03",
            "skill": "javascript",
            "question": "What is a closure in JavaScript?",
            "options": [
                "A function bundled together with references to its surrounding lexical environment",
                "A method that terminates an asynchronous Promise",
                "A syntax error caused by unclosed parentheses",
                "An anonymous arrow function without parameters"
            ],
            "answer": 0,
            "difficulty": "medium",
            "explanation": "A closure gives an inner function access to its outer function's scope even after the outer function has returned."
        },
        {
            "id": "js_04",
            "skill": "javascript",
            "question": "What does `Promise.all([p1, p2, p3])` do if any single promise rejects?",
            "options": [
                "It immediately rejects with the reason of the first rejected promise",
                "It waits for all promises to settle regardless of errors",
                "It retries the failed promise three times",
                "It returns null for the failed promise"
            ],
            "answer": 0,
            "difficulty": "medium",
            "explanation": "`Promise.all` fails fast: if any promise in the array rejects, the returned promise immediately rejects."
        },
        {
            "id": "js_05",
            "skill": "javascript",
            "question": "Which method is best suited to deep clone a standard nested JavaScript object in modern browsers?",
            "options": ["Object.assign({}, obj)", "structuredClone(obj)", "obj.clone()", "{ ...obj }"],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "`structuredClone()` is the modern standard native API for performing deep copies of nested objects."
        }
    ],

    "html": [
        {
            "id": "html_01",
            "skill": "html",
            "question": "Which HTML5 semantic tag represents self-contained, standalone syndicated content?",
            "options": ["<section>", "<article>", "<div>", "<aside>"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "<article> represents an independent piece of content, such as a blog post or news story."
        },
        {
            "id": "html_02",
            "skill": "html",
            "question": "Which attribute on an `<img>` tag is mandatory for accessibility and screen readers?",
            "options": ["title", "src", "alt", "aria-label"],
            "answer": 2,
            "difficulty": "easy",
            "explanation": "The `alt` attribute provides essential text alternatives for visually impaired users and screen readers."
        },
        {
            "id": "html_03",
            "skill": "html",
            "question": "What does the `<meta name='viewport' content='width=device-width, initial-scale=1.0'>` tag achieve?",
            "options": [
                "Optimizes search engine crawl rate",
                "Configures proper scaling and responsive viewport dimensions on mobile devices",
                "Enables desktop zoom restriction",
                "Loads external mobile stylesheets"
            ],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "It instructs mobile browsers to render the website viewport at the actual device screen width."
        }
    ],

    "css": [
        {
            "id": "css_01",
            "skill": "css",
            "question": "Which CSS property centers items along the main axis in a Flexbox container?",
            "options": ["align-items", "justify-content", "align-content", "text-align"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`justify-content` aligns flex items along the primary axis (horizontal by default)."
        },
        {
            "id": "css_02",
            "skill": "css",
            "question": "In the CSS Box Model, what is the correct order from outermost to innermost?",
            "options": [
                "Margin -> Border -> Padding -> Content",
                "Border -> Margin -> Padding -> Content",
                "Padding -> Border -> Margin -> Content",
                "Margin -> Padding -> Border -> Content"
            ],
            "answer": 0,
            "difficulty": "easy",
            "explanation": "The standard box model layer sequence is Margin (outside), Border, Padding, and Content (inside)."
        },
        {
            "id": "css_03",
            "skill": "css",
            "question": "What does setting `box-sizing: border-box;` accomplish?",
            "options": [
                "Excludes padding from the element's total calculated width",
                "Includes padding and border within the element's specified width and height",
                "Removes all borders around the box",
                "Forces inline display"
            ],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`border-box` ensures the element's declared width includes padding and borders, simplifying layout sizing."
        }
    ],

    "react": [
        {
            "id": "react_01",
            "skill": "react",
            "question": "Which Hook should be used to perform side effects like data fetching or subscriptions in a functional component?",
            "options": ["useState", "useEffect", "useMemo", "useContext"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`useEffect` serves the purpose of handling side effects, synchronization, and lifecycle cleanups."
        },
        {
            "id": "react_02",
            "skill": "react",
            "question": "Why are `key` props important when rendering lists in React?",
            "options": [
                "They style list items automatically",
                "They help React's virtual DOM reconciliation identify which items have changed, been added, or removed",
                "They are required by JavaScript arrays",
                "They encrypt item data"
            ],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "Keys provide persistent identities to elements across renders, enabling efficient DOM diffing."
        },
        {
            "id": "react_03",
            "skill": "react",
            "question": "What is the primary difference between `useMemo` and `useCallback`?",
            "options": [
                "`useMemo` memoizes a computed value; `useCallback` memoizes a callback function definition",
                "`useCallback` memoizes values while `useMemo` is only for DOM nodes",
                "`useMemo` triggers re-renders on every tick",
                "They are aliases of the same hook"
            ],
            "answer": 0,
            "difficulty": "medium",
            "explanation": "`useMemo` caches the calculated result of an expensive function; `useCallback` caches the function instance."
        }
    ],

    "docker": [
        {
            "id": "docker_01",
            "skill": "docker",
            "question": "What is the fundamental difference between a Docker image and a Docker container?",
            "options": [
                "An image is a read-only template; a container is a runnable, isolated instance of that image",
                "A container is static and immutable; an image is runnable",
                "Images run on Linux only, while containers run on any OS",
                "There is no difference"
            ],
            "answer": 0,
            "difficulty": "easy",
            "explanation": "A Docker image is a packaged blueprint. A container is the live running process instantiated from that image."
        },
        {
            "id": "docker_02",
            "skill": "docker",
            "question": "Which instruction in a Dockerfile defines the default executable command when a container starts?",
            "options": ["RUN", "CMD / ENTRYPOINT", "ENV", "EXPOSE"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`ENTRYPOINT` and `CMD` define the default command executed when running the container."
        }
    ],

    "data structures": [
        {
            "id": "dsa_01",
            "skill": "data structures",
            "question": "What is the worst-case time complexity of searching for an element in an unbalanced Binary Search Tree (BST)?",
            "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "answer": 2,
            "difficulty": "medium",
            "explanation": "An unbalanced BST degrades into a linear linked list where searching requires O(n) comparisons."
        },
        {
            "id": "dsa_02",
            "skill": "data structures",
            "question": "Which data structure follows the Last-In, First-Out (LIFO) principle?",
            "options": ["Queue", "Stack", "Linked List", "Priority Queue"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "A Stack operates on LIFO (Last-In, First-Out) semantics via push and pop operations."
        },
        {
            "id": "dsa_03",
            "skill": "data structures",
            "question": "Which sorting algorithm has a guaranteed worst-case time complexity of O(n log n)?",
            "options": ["Quick Sort", "Bubble Sort", "Merge Sort", "Insertion Sort"],
            "answer": 2,
            "difficulty": "medium",
            "explanation": "Merge Sort recursively divides the list and merges in linear time, guaranteeing O(n log n) even in the worst case."
        }
    ],

    "pandas": [
        {
            "id": "pd_01",
            "skill": "pandas",
            "question": "Which Pandas function is used to load data from a comma-separated values file into a DataFrame?",
            "options": ["pd.read_table()", "pd.read_csv()", "pd.parse_csv()", "pd.load_csv()"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`pd.read_csv()` reads CSV datasets into a two-dimensional labeled DataFrame."
        },
        {
            "id": "pd_02",
            "skill": "pandas",
            "question": "What is the difference between `.loc[]` and `.iloc[]` in Pandas?",
            "options": [
                "`.loc` uses label-based indexing; `.iloc` uses integer position-based indexing",
                "`.iloc` uses labels while `.loc` is integer only",
                "`.loc` works only on Series while `.iloc` works on DataFrames",
                "They are interchangeable synonyms"
            ],
            "answer": 0,
            "difficulty": "easy",
            "explanation": "`.loc` selects by row and column labels. `.iloc` selects by 0-based integer positions."
        },
        {
            "id": "pd_03",
            "skill": "pandas",
            "question": "Which method drops rows with missing/null values from a DataFrame?",
            "options": ["df.clean()", "df.dropna()", "df.filter_null()", "df.fillna()"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`df.dropna()` detects and removes rows or columns containing NA/NaN values."
        }
    ],

    "machine learning": [
        {
            "id": "ml_01",
            "skill": "machine learning",
            "question": "What is the fundamental difference between supervised and unsupervised learning?",
            "options": [
                "Supervised learning trains on labeled target data; unsupervised learning discovers patterns from unlabeled inputs",
                "Unsupervised learning requires ground-truth labels",
                "Supervised learning only works with neural networks",
                "Supervised learning cannot do classification"
            ],
            "answer": 0,
            "difficulty": "easy",
            "explanation": "Supervised algorithms learn mappings from labeled features to targets, while unsupervised models cluster unlabeled data."
        },
        {
            "id": "ml_02",
            "skill": "machine learning",
            "question": "What does high variance and low bias typically signify in a trained machine learning model?",
            "options": ["Underfitting", "Overfitting", "Optimal generalization", "Data leakage"],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "High variance means the model memorized the training noise and fails to generalize to unseen test data (overfitting)."
        },
        {
            "id": "ml_03",
            "skill": "machine learning",
            "question": "Which metric is most appropriate for evaluating a binary classification model with severe class imbalance (e.g. 99% negative)?",
            "options": ["Accuracy", "Precision-Recall AUC / F1-Score", "Mean Squared Error", "R-Squared"],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "Accuracy is misleading on imbalanced sets (a trivial all-negative model gets 99%). F1-Score or PR-AUC focuses on minority class performance."
        }
    ],

    "statistics": [
        {
            "id": "stat_01",
            "skill": "statistics",
            "question": "What does a p-value less than 0.05 typically indicate in hypothesis testing?",
            "options": [
                "The null hypothesis is definitively proven true",
                "There is sufficient statistical evidence to reject the null hypothesis at the 5% significance level",
                "The test has a 95% calculation error",
                "The sample size was too small"
            ],
            "answer": 1,
            "difficulty": "medium",
            "explanation": "p < 0.05 suggests that observing the sample outcome by random chance alone is unlikely, rejecting the null."
        },
        {
            "id": "stat_02",
            "skill": "statistics",
            "question": "Which measure of central tendency is least sensitive to extreme outliers in a skewed distribution?",
            "options": ["Mean", "Median", "Mode", "Standard Deviation"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "The median represents the 50th percentile rank and is robust against skewed extreme values."
        }
    ],

    "excel": [
        {
            "id": "excel_01",
            "skill": "excel",
            "question": "Which modern Excel formula lookup function replaces both VLOOKUP and HLOOKUP with bidirectional search?",
            "options": ["INDEX", "XLOOKUP", "MATCH", "LOOKUP2"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "`XLOOKUP` allows searching both vertically and horizontally without requiring sorted columns or left-to-right constraints."
        },
        {
            "id": "excel_02",
            "skill": "excel",
            "question": "What tool in Excel allows you to quickly summarize, aggregate, and slice large multi-column datasets interactively?",
            "options": ["Conditional Formatting", "Pivot Table", "Data Validation", "Goal Seek"],
            "answer": 1,
            "difficulty": "easy",
            "explanation": "Pivot Tables summarize, group, count, sum, or average data dynamically across row and column dimensions."
        }
    ]
}


def get_all_skills_in_bank() -> List[str]:
    """Return all skills represented in the question bank."""
    return sorted(list(QUESTION_BANK.keys()))


def get_questions_for_skills(skills: List[str], count: int = 20) -> List[dict]:
    """
    Select up to `count` questions distributed across the provided skills.
    Ensures exactly `count` questions are returned whenever possible by balancing
    across target skills and core technical competencies.
    """
    normalized_skills = [normalize_skill(s) for s in skills if s.strip()]
    if not normalized_skills:
        normalized_skills = ["python", "sql", "git", "rest apis"]

    selected_pool = []
    seen_ids = set()

    # Pass 1: Gather questions from requested skills
    for skill in normalized_skills:
        bank = QUESTION_BANK.get(skill, [])
        for q in bank:
            if q["id"] not in seen_ids:
                selected_pool.append({**q, "_skill": skill})
                seen_ids.add(q["id"])

    # Pass 2: If pool has fewer than count questions, augment with general programming & engineering questions
    if len(selected_pool) < count:
        supplemental_skills = ["python", "sql", "git", "rest apis", "data structures", "javascript"]
        for supp in supplemental_skills:
            for q in QUESTION_BANK.get(supp, []):
                if q["id"] not in seen_ids:
                    selected_pool.append({**q, "_skill": supp})
                    seen_ids.add(q["id"])
                    if len(selected_pool) >= count * 2:
                        break

    random.shuffle(selected_pool)
    return selected_pool[:count]


def get_questions_for_role(role_name: str, count: int = 20) -> List[dict]:
    """Retrieve balanced questions tailored to a specific job role."""
    core, secondary = get_role_skills(role_name)
    role_skills = core + secondary
    return get_questions_for_skills(role_skills, count=count)


def public_question(question: dict) -> dict:
    """Strip answer and explanation before sending to the client."""
    return {
        "id": question["id"],
        "skill": question.get("_skill", question.get("skill", "general")),
        "question": question["question"],
        "options": question["options"],
        "difficulty": question.get("difficulty", "medium")
    }
