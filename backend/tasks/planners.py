"""Adaptive daily study task planner for Eduoo.

Generates dynamic, date-sequenced study plans that evolve day-by-day across
DSA coding challenges, practical target-role engineering, interview readiness,
and technical system design reading.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional
from django.utils import timezone

from platforms.models import ConnectedPlatform, LeetCodeCatalogProblem
from .models import DailyTask, DailyTaskPlan

# Comprehensive rotating pool of algorithmic & database coding challenges
CODING_CURRICULUM = [
    {
        "title": "Two Sum",
        "topic": "Arrays & Hash Maps",
        "difficulty": "Easy",
        "problem_url": "https://leetcode.com/problems/two-sum/",
        "focus": "One-pass hash table lookup with O(n) time and O(n) space.",
    },
    {
        "title": "Valid Anagram",
        "topic": "Strings & Frequency Maps",
        "difficulty": "Easy",
        "problem_url": "https://leetcode.com/problems/valid-anagram/",
        "focus": "Character count array hashing and boundary case checks.",
    },
    {
        "title": "Valid Parentheses",
        "topic": "Stacks & LIFO Processing",
        "difficulty": "Easy",
        "problem_url": "https://leetcode.com/problems/valid-parentheses/",
        "focus": "Bracket matching using stack state and empty-stack verification.",
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "topic": "Sliding Window & Hash Sets",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
        "focus": "Dynamic sliding window with pointer expansion and contraction.",
    },
    {
        "title": "Add Two Numbers",
        "topic": "Linked Lists & Digit Carry",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/add-two-numbers/",
        "focus": "List node pointer manipulation and carry value propagation.",
    },
    {
        "title": "Coin Change",
        "topic": "Dynamic Programming & Tabulation",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/coin-change/",
        "focus": "Bottom-up dynamic programming with optimal substructure.",
    },
    {
        "title": "Search in Rotated Sorted Array",
        "topic": "Binary Search & Array Partitions",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/search-in-rotated-sorted-array/",
        "focus": "Modified binary search finding sorted half in O(log n) time.",
    },
    {
        "title": "Department Highest Salary",
        "topic": "SQL Window Functions & Aggregation",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/department-highest-salary/",
        "focus": "Window functions (DENSE_RANK), CTEs, and JOIN performance.",
    },
    {
        "title": "Subsets (Power Set Generation)",
        "topic": "Recursion & Backtracking",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/subsets/",
        "focus": "Decision tree branching and clean state backtrack cleanup.",
    },
    {
        "title": "Climbing Stairs",
        "topic": "Dynamic Programming & Fibonacci",
        "difficulty": "Easy",
        "problem_url": "https://leetcode.com/problems/climbing-stairs/",
        "focus": "Space-optimized DP with constant O(1) auxiliary memory.",
    },
    {
        "title": "Maximum Subarray (Kadane's Algorithm)",
        "topic": "Arrays & Greedy Optimization",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/maximum-subarray/",
        "focus": "Linear O(n) scan tracking contiguous subarray maximum.",
    },
    {
        "title": "Binary Tree Level Order Traversal",
        "topic": "Trees & BFS Breadth-First Search",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/binary-tree-level-order-traversal/",
        "focus": "Queue-driven level-by-level traversal with size boundaries.",
    },
    {
        "title": "Merge Intervals",
        "topic": "Interval Scheduling & Sorting",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/merge-intervals/",
        "focus": "Start-coordinate sorting followed by linear interval consolidation.",
    },
    {
        "title": "Kth Largest Element in an Array",
        "topic": "Heaps & QuickSelect",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/kth-largest-element-in-an-array/",
        "focus": "Min-heap of size K vs O(n) average QuickSelect partitioning.",
    },
    {
        "title": "Trapping Rain Water",
        "topic": "Two Pointers & Monotonic Stacks",
        "difficulty": "Hard",
        "problem_url": "https://leetcode.com/problems/trapping-rain-water/",
        "focus": "Dual inward-moving height pointers tracking trapped water volumes.",
    },
    {
        "title": "Course Schedule (Topological Sort)",
        "topic": "Graphs & Dependency Cycles",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/course-schedule/",
        "focus": "Kahn's algorithm using in-degree arrays to detect DAG cycles.",
    },
    {
        "title": "Top K Frequent Elements",
        "topic": "Hash Maps & Bucket Sort",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/top-k-frequent-elements/",
        "focus": "Frequency mapping with linear bucket sort in O(n) time.",
    },
    {
        "title": "Invert Binary Tree",
        "topic": "Binary Trees & Recursion",
        "difficulty": "Easy",
        "problem_url": "https://leetcode.com/problems/invert-binary-tree/",
        "focus": "Recursive child pointer swap with base termination.",
    },
    {
        "title": "Median of Two Sorted Arrays",
        "topic": "Binary Search & Divide and Conquer",
        "difficulty": "Hard",
        "problem_url": "https://leetcode.com/problems/median-of-two-sorted-arrays/",
        "focus": "Binary search on partition indices with logarithmic O(log(min(m, n))) complexity.",
    },
    {
        "title": "Valid Palindrome",
        "topic": "Two Pointers & String Sanitation",
        "difficulty": "Easy",
        "problem_url": "https://leetcode.com/problems/valid-palindrome/",
        "focus": "Inward converging pointers ignoring non-alphanumeric characters.",
    },
    {
        "title": "Product of Array Except Self",
        "topic": "Arrays & Prefix Accumulation",
        "difficulty": "Medium",
        "problem_url": "https://leetcode.com/problems/product-of-array-except-self/",
        "focus": "Left prefix and right suffix product accumulation without division.",
    },
]

# Role-specific rotating practical engineering milestones (14 unique days per track)
ROLE_PROJECT_CURRICULUM = {
    "full_stack": [
        {
            "title": "Database Schema & Migration Scaffolding",
            "description": "Design normalized relational schemas, define foreign key constraints, and write atomic migrations.",
            "topic": "Database Architecture",
        },
        {
            "title": "JWT Auth & Session Security Hardening",
            "description": "Implement access and refresh token rotation with HTTP-only cookies and bcrypt password hashing.",
            "topic": "Authentication & Security",
        },
        {
            "title": "REST API CRUD & Query Filtering",
            "description": "Build high-throughput CRUD endpoints with pagination, search query filtering, and standardized error envelopes.",
            "topic": "Backend APIs",
        },
        {
            "title": "Database Query Optimization & Indexing",
            "description": "Analyze slow queries with EXPLAIN ANALYZE, add composite indexes, and eliminate N+1 ORM queries.",
            "topic": "Database Performance",
        },
        {
            "title": "Frontend State Management & Optimistic UI",
            "description": "Implement modular state management in React, handling optimistic updates and graceful error fallbacks.",
            "topic": "Frontend Engineering",
        },
        {
            "title": "Background Job Queue Integration",
            "description": "Setup async task queue workers (Celery/BullMQ with Redis) for asynchronous email dispatch and report generation.",
            "topic": "Async Architecture",
        },
        {
            "title": "Automated Testing & Coverage Benchmark",
            "description": "Write comprehensive unit and integration test suites achieving 80%+ coverage across business critical flows.",
            "topic": "Quality Assurance",
        },
        {
            "title": "In-Memory Caching Implementation",
            "description": "Implement Redis cache-aside pattern with TTL invalidation for frequently read endpoint payloads.",
            "topic": "Caching & Latency",
        },
        {
            "title": "Docker Multi-Stage Containerization",
            "description": "Write multi-stage Dockerfiles optimizing image size, configure docker-compose services, and setup local dev parity.",
            "topic": "DevOps & Containers",
        },
        {
            "title": "Real-Time Event Streaming (WebSockets/SSE)",
            "description": "Implement bidirectional WebSocket or SSE communication for live notifications and status updates.",
            "topic": "Real-Time Systems",
        },
        {
            "title": "API Rate Limiting & Input Sanitization",
            "description": "Configure sliding-window rate limiters, strict CORS policies, and schema validation to mitigate DDoS and injection.",
            "topic": "Security & Resilience",
        },
        {
            "title": "Third-Party Service Integration (S3/Stripe)",
            "description": "Integrate cloud storage (presigned S3 upload URLs) or webhook verification for external payment/auth providers.",
            "topic": "Cloud Integrations",
        },
        {
            "title": "Observability: Structured Logging & Telemetry",
            "description": "Setup structured JSON request logging, healthcheck endpoint probes (/health/), and latency tracking.",
            "topic": "Observability",
        },
        {
            "title": "CI/CD Pipeline & Cloud Deployment",
            "description": "Create automated GitHub Actions workflows for linting, testing, and continuous deployment to cloud environments.",
            "topic": "CI/CD Automation",
        },
    ],
    "data_science": [
        {
            "title": "Automated Data Ingestion & Cleansing",
            "description": "Ingest multi-source tabular datasets, handle missing values, and validate schema integrity using Pandas.",
            "topic": "Data Preprocessing",
        },
        {
            "title": "Exploratory Data Analysis (EDA) & Outliers",
            "description": "Generate correlation heatmaps, feature distributions, and detect anomalies using IQR and Z-scores.",
            "topic": "Exploratory Analysis",
        },
        {
            "title": "Feature Engineering & Scaling Pipelines",
            "description": "Build Scikit-Learn transformers for one-hot encoding, target encoding, and RobustScaler pipelines.",
            "topic": "Feature Engineering",
        },
        {
            "title": "Baseline Machine Learning Classification",
            "description": "Train baseline Logistic Regression and Random Forest models; evaluate ROC-AUC, Precision, and Recall.",
            "topic": "Predictive Modeling",
        },
        {
            "title": "Hyperparameter Optimization & Cross-Validation",
            "description": "Implement Stratified 5-Fold Cross-Validation and Bayesian optimization for model hyperparameter search.",
            "topic": "Model Tuning",
        },
        {
            "title": "Deep Learning Pipeline with PyTorch",
            "description": "Build a PyTorch neural network with custom layers, AdamW optimizer, and learning rate schedulers.",
            "topic": "Deep Learning",
        },
        {
            "title": "Model Explainability with SHAP & LIME",
            "description": "Calculate SHAP values and feature importance scores to explain individual model predictions to stakeholders.",
            "topic": "Explainable AI",
        },
        {
            "title": "Model Serialization & Inference API",
            "description": "Export trained model weights to ONNX/Joblib format and expose sub-50ms inference via FastAPI.",
            "topic": "Model Deployment",
        },
        {
            "title": "LLM & Retrieval-Augmented Generation (RAG)",
            "description": "Generate text embeddings, store in vector databases, and build context-augmented retrieval pipelines.",
            "topic": "Generative AI & LLMs",
        },
        {
            "title": "A/B Testing & Statistical Hypothesis Testing",
            "description": "Compute required sample sizes, power calculations, and two-sample t-tests to evaluate feature lift.",
            "topic": "Experimentation",
        },
        {
            "title": "Interactive Analytics Dashboard Building",
            "description": "Build interactive visualization dashboards using Streamlit, Plotly, or PowerBI to present business KPIs.",
            "topic": "Data Visualization",
        },
        {
            "title": "Automated ETL Pipeline & Validation",
            "description": "Build scheduled batch ETL scripts with Great Expectations data quality assertions and error alerts.",
            "topic": "Data Engineering",
        },
        {
            "title": "Model Drift & Telemetry Monitoring",
            "description": "Implement statistical drift detection (KS-test, PSI) to monitor data drift and performance decay in production.",
            "topic": "MLOps",
        },
        {
            "title": "Data Science Portfolio & Research Summary",
            "description": "Document methodology, data visualizations, and business conclusions in an executive GitHub README.",
            "topic": "Portfolio Showcase",
        },
    ],
}

# 14 unique daily interview readiness topics
INTERVIEW_CURRICULUM = [
    {
        "title": "Behavioral: 2-Minute Elevator Pitch",
        "description": "Refine and record your 'Tell me about yourself' story using the Present-Past-Future narrative framework.",
        "topic": "STAR Behavioral",
    },
    {
        "title": "Architecture: SQL vs NoSQL Trade-Offs",
        "description": "Practice explaining ACID transaction guarantees vs horizontal partitioning and eventual consistency.",
        "topic": "System Architecture",
    },
    {
        "title": "Behavioral: Resolving Technical Disagreements",
        "description": "Formulate a STAR response describing a technical disagreement with a teammate and how you resolved it constructively.",
        "topic": "Teamwork & Culture",
    },
    {
        "title": "System Design: High-Throughput URL Shortener",
        "description": "Design a Bitly-scale service handling 10,000 req/sec: hashing algorithms, base62 encoding, and Redis caching.",
        "topic": "System Design Round",
    },
    {
        "title": "Behavioral: Production Bug & Outage Defense",
        "description": "Structure a compelling STAR story describing a critical bug or production incident you diagnosed under pressure.",
        "topic": "Incident Response",
    },
    {
        "title": "Core Concepts: Memory Management & Event Loop",
        "description": "Explain how garbage collection, heap/stack allocations, and asynchronous event loops function under the hood.",
        "topic": "Language Internals",
    },
    {
        "title": "Live Simulation: AI Mock Interview Round",
        "description": "Complete 1 full AI Mock Interview session in Eduoo's Career Platform with voice or text responses.",
        "topic": "Interview Simulation",
    },
    {
        "title": "Behavioral: Rapid Learning on Tight Deadlines",
        "description": "Prepare a STAR example of having to master an unfamiliar tool, framework, or cloud technology on short notice.",
        "topic": "Adaptability",
    },
    {
        "title": "System Design: Real-Time Notification System",
        "description": "Architect a distributed notification engine supporting WebSockets, push alerts, email queues, and user rate limits.",
        "topic": "System Design Round",
    },
    {
        "title": "Architecture: Database Indexing Internals",
        "description": "Explain B-Trees vs Hash indexes, composite index column ordering rules, and write amplification overhead.",
        "topic": "Data Architecture",
    },
    {
        "title": "Behavioral: Failed Project & Lessons Learned",
        "description": "Prepare an honest, growth-oriented STAR response detailing a project that missed a deadline or failed, and key learnings.",
        "topic": "Growth Mindset",
    },
    {
        "title": "System Design: Distributed Rate Limiter",
        "description": "Design an API rate limiter: compare Token Bucket, Leaky Bucket, and Sliding Window Log algorithms in Redis.",
        "topic": "Distributed Systems",
    },
    {
        "title": "Behavioral: Technical Debt vs Fast Delivery",
        "description": "Practice answering: 'How do you balance engineering excellence and refactoring against urgent business deadlines?'",
        "topic": "Engineering Leadership",
    },
    {
        "title": "Portfolio Defense: Architecture Walkthrough",
        "description": "Practice presenting your main portfolio project: defend technology stack choices, bottlenecks, and future scaling.",
        "topic": "Project Defense",
    },
]

# 14 unique technical reading & system design deep-dives
READING_CURRICULUM = [
    {
        "title": "Read: How In-Memory Caching Works: Redis Internals & Eviction",
        "description": "Study Redis single-threaded event loop, memory structures, RDB/AOF persistence, and LRU eviction policies.",
        "topic": "System Design",
    },
    {
        "title": "Read: The Anatomy of a Relational Query Plan",
        "description": "Study how SQL query optimizers parse syntax, choose between Index Scans and Seq Scans, and execute Hash Joins.",
        "topic": "Database Internals",
    },
    {
        "title": "Read: Designing Scalable REST & GraphQL APIs",
        "description": "Study idempotency keys, cursor-based pagination, API versioning strategies, and GraphQL N+1 data loader patterns.",
        "topic": "API Design",
    },
    {
        "title": "Read: Understanding the CAP Theorem in Production",
        "description": "Analyze real-world trade-offs between Consistency and Availability in distributed systems during network partitions.",
        "topic": "Distributed Systems",
    },
    {
        "title": "Read: Message Queues Compared: Kafka, RabbitMQ, and SQS",
        "description": "Compare distributed log append brokers (Kafka) vs AMQP message brokers (RabbitMQ) for event-driven architectures.",
        "topic": "Message Brokers",
    },
    {
        "title": "Read: Web Frontend Performance & Core Web Vitals",
        "description": "Study Critical Rendering Path, Largest Contentful Paint (LCP), code splitting, and browser caching optimizations.",
        "topic": "Web Performance",
    },
    {
        "title": "Read Engineering Blogs: How Uber Scaled Its Dispatch System",
        "description": "Read case studies on geospatial indexing (H3 grid), distributed state management, and real-time ride matching.",
        "topic": "Engineering Case Study",
    },
    {
        "title": "Read: Microservices Communication: gRPC vs Event-Driven Pub/Sub",
        "description": "Analyze protocol buffer serialization efficiency, multiplexing in HTTP/2, and asynchronous event choreographies.",
        "topic": "Microservices",
    },
    {
        "title": "Read: Modern Web Security & OWASP Top 10 Defenses",
        "description": "Review defenses against SQL injection, Cross-Site Scripting (XSS), CSRF token validation, and Broken Object Level Auth.",
        "topic": "Application Security",
    },
    {
        "title": "Read: Database Sharding & Horizontal Partitioning",
        "description": "Study hash-based vs range-based sharding keys, rebalancing protocols, and distributed query coordination.",
        "topic": "Database Scaling",
    },
    {
        "title": "Read: Concurrency Models: Asyncio vs Threads vs Goroutines",
        "description": "Deep-dive into cooperative multitasking, OS thread scheduling overhead, and green thread runtimes.",
        "topic": "Concurrency",
    },
    {
        "title": "Read: Distributed Observability & OpenTelemetry",
        "description": "Understand structured spans, trace propagation across network boundaries, and Service Level Objectives (SLOs).",
        "topic": "Observability",
    },
    {
        "title": "Read: Designing Distributed Rate Limiters & Throttling",
        "description": "Study Token Bucket vs Leaky Bucket algorithms, Redis atomic Lua scripts, and client retry backoff strategies.",
        "topic": "Resilience Patterns",
    },
    {
        "title": "Read Engineering Blogs: Netflix Multi-Region Active-Active Deployments",
        "description": "Explore how Netflix routes live traffic across AWS regions with Cassandra data replication and zero downtime failover.",
        "topic": "High Availability",
    },
]

# 7 rotating language practice drills for connected Duolingo users
LANGUAGE_CURRICULUM = [
    {
        "title": "Complete 2 Duolingo lessons: Daily Vocabulary Expansion",
        "description": "Learn 10+ new words and practice pronunciation to keep your foreign language streak alive.",
        "topic": "Foreign Languages",
    },
    {
        "title": "Complete 2 Duolingo lessons: Grammar & Sentence Formation",
        "description": "Focus on verb conjugations, tense structures, and sentence ordering drills.",
        "topic": "Foreign Languages",
    },
    {
        "title": "Complete 2 Duolingo lessons: Listening Comprehension Drills",
        "description": "Practice audio-only listening exercises without subtitles to train conversational ear recognition.",
        "topic": "Foreign Languages",
    },
    {
        "title": "Complete 2 Duolingo lessons: Mistake Review & Spaced Repetition",
        "description": "Visit your Duolingo review hub to replay missed questions and reinforce weak word memories.",
        "topic": "Foreign Languages",
    },
    {
        "title": "Complete 2 Duolingo lessons: Speed Challenges & Timed Recall",
        "description": "Complete timed practice challenges to test rapid vocabulary retrieval under time pressure.",
        "topic": "Foreign Languages",
    },
    {
        "title": "Complete 2 Duolingo lessons: Contextual Story Mode",
        "description": "Read and listen to a continuous interactive narrative to build contextual sentence comprehension.",
        "topic": "Foreign Languages",
    },
    {
        "title": "Complete 2 Duolingo lessons: Weekly Checkpoint Milestone",
        "description": "Finish unit review checkpoint questions to cement this week's linguistic progress.",
        "topic": "Foreign Languages",
    },
]


class AdaptiveDailyTaskPlanner:
    @staticmethod
    def get_or_create_plan(user, target_date: date | None = None) -> DailyTaskPlan:
        plan_date = target_date or timezone.now().date()
        plan, _ = DailyTaskPlan.objects.get_or_create(user=user, date=plan_date)
        return plan

    @staticmethod
    def generate_for_user(user, target_date: date | None = None, variation: int = 0) -> DailyTaskPlan:
        """Generates dynamic daily tasks that change day-by-day based on calendar date and role."""
        plan = AdaptiveDailyTaskPlanner.get_or_create_plan(user, target_date)
        if plan.tasks.exists():
            return plan

        plan_date = plan.date
        day_ordinal = plan_date.toordinal()

        # Deterministic but ever-changing seed combining date ordinal, user id, and optional variation
        seed = day_ordinal + (user.id * 11) + variation

        daily_study_hours = float(user.daily_study_hours or 0)
        minutes_budget = int(daily_study_hours * 60)
        if minutes_budget <= 0:
            minutes_budget = 90

        role = user.target_role or "Full Stack Developer"
        role_lower = role.lower()
        is_ds_track = any(k in role_lower for k in ["data", "ai", "machine learning", "ml", "analyst", "scientist"])

        # Check connected platforms
        has_leetcode = ConnectedPlatform.objects.filter(user=user, platform="leetcode", connected=True).exists()
        has_github = ConnectedPlatform.objects.filter(user=user, platform="github", connected=True).exists()
        has_duolingo = ConnectedPlatform.objects.filter(user=user, platform="duolingo", connected=True).exists()

        tasks_data = []

        # -------------------------------------------------------------
        # 1. DSA & Coding Task: Rotates day by day
        # -------------------------------------------------------------
        # Merge catalog database problems if available, otherwise use CODING_CURRICULUM
        db_problems = list(LeetCodeCatalogProblem.objects.all())
        coding_pool = list(CODING_CURRICULUM)
        if db_problems:
            # Map DB problems to curriculum format
            for db_p in db_problems:
                coding_pool.append({
                    "title": db_p.title,
                    "topic": ", ".join(db_p.topics) if isinstance(db_p.topics, list) else "Data Structures",
                    "difficulty": db_p.difficulty,
                    "problem_url": db_p.problem_url or f"https://leetcode.com/problems/{db_p.slug}/",
                    "focus": f"Master optimal time and space complexity for {role} interviews.",
                })

        problem_idx = seed % len(coding_pool)
        selected_problem = coding_pool[problem_idx]

        if minutes_budget >= 120:
            time_alloc = 45
            problem_diff = "Hard" if has_leetcode else "Medium"
        elif minutes_budget >= 60:
            time_alloc = 35
            problem_diff = selected_problem.get("difficulty") or "Medium"
        else:
            time_alloc = 25
            problem_diff = "Easy"

        tasks_data.append({
            "task_type": "leetcode",
            "title": f"Solve a {problem_diff} DSA problem: {selected_problem['title']}",
            "description": f"Topic: {selected_problem['topic']}. Focus: {selected_problem.get('focus', 'Optimal complexity')}",
            "topic": selected_problem.get("topic", "Data Structures & Algorithms"),
            "difficulty": problem_diff.lower(),
            "estimated_minutes": time_alloc,
            "priority": "high",
            "problem_url": selected_problem.get("problem_url") or "http://localhost:5173/interviews?tab=skill_assessment",
        })

        # -------------------------------------------------------------
        # 2. Target Role Practical Project Task: Rotates day by day
        # -------------------------------------------------------------
        project_pool = ROLE_PROJECT_CURRICULUM["data_science"] if is_ds_track else ROLE_PROJECT_CURRICULUM["full_stack"]
        project_idx = (seed + 3) % len(project_pool)
        selected_project = project_pool[project_idx]
        github_time = min(35, max(15, int(minutes_budget * 0.28)))

        tasks_data.append({
            "task_type": "github",
            "title": f"Project Milestone: {selected_project['title']}",
            "description": f"{selected_project['description']} Commit clean changes to your repository to strengthen your {role} portfolio.",
            "topic": f"{role}: {selected_project['topic']}",
            "difficulty": "medium",
            "estimated_minutes": github_time,
            "priority": "high" if has_github else "medium",
            "problem_url": "http://localhost:5173/resume",
        })

        # -------------------------------------------------------------
        # 3. Interview Readiness Task: Rotates day by day
        # -------------------------------------------------------------
        interview_idx = (seed + 7) % len(INTERVIEW_CURRICULUM)
        selected_interview = INTERVIEW_CURRICULUM[interview_idx]
        interview_time = min(25, max(15, int(minutes_budget * 0.20)))

        tasks_data.append({
            "task_type": "interview",
            "title": f"Interview Practice: {selected_interview['title']}",
            "description": f"{selected_interview['description']} Tailored to hiring standards for {role}.",
            "topic": selected_interview["topic"],
            "difficulty": "medium",
            "estimated_minutes": interview_time,
            "priority": "high",
            "problem_url": "http://localhost:5173/interviews?tab=job_interviews",
        })

        # -------------------------------------------------------------
        # 4. Technical Reading or Language Learning: Rotates day by day
        # -------------------------------------------------------------
        lang_time = min(20, max(10, int(minutes_budget * 0.15)))
        if has_duolingo:
            lang_idx = seed % len(LANGUAGE_CURRICULUM)
            selected_lang = LANGUAGE_CURRICULUM[lang_idx]
            tasks_data.append({
                "task_type": "language",
                "title": selected_lang["title"],
                "description": selected_lang["description"],
                "topic": selected_lang["topic"],
                "difficulty": "easy",
                "estimated_minutes": lang_time,
                "priority": "medium",
            })
        else:
            reading_idx = (seed + 11) % len(READING_CURRICULUM)
            selected_reading = READING_CURRICULUM[reading_idx]
            tasks_data.append({
                "task_type": "general",
                "title": selected_reading["title"],
                "description": selected_reading["description"],
                "topic": selected_reading["topic"],
                "difficulty": "medium",
                "estimated_minutes": lang_time,
                "priority": "medium",
                "problem_url": "http://localhost:5173/interviews?tab=communication",
            })

        # Persist tasks to plan
        total_minutes = 0
        for td in tasks_data:
            task = DailyTask.objects.create(plan=plan, **td)
            total_minutes += task.estimated_minutes

        plan.total_minutes = total_minutes
        plan.status = "planned"
        plan.save(update_fields=["total_minutes", "status", "updated_at"])
        return plan

    @staticmethod
    def complete_task(task: DailyTask) -> DailyTask:
        if task.status == "completed":
            return task

        task.status = "completed"
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at"])

        plan = task.plan
        plan.completed_minutes = sum(item.estimated_minutes for item in plan.tasks.filter(status="completed"))
        if plan.completed_minutes >= plan.total_minutes:
            plan.status = "completed"
        else:
            plan.status = "in_progress"
        plan.save(update_fields=["completed_minutes", "status", "updated_at"])

        # Update StudyProgress without double counting
        try:
            from progress.models import StudyProgress
            study_progress, _ = StudyProgress.objects.get_or_create(user=plan.user, date=plan.date)
            completed_tasks_count = plan.tasks.filter(status="completed").count()
            study_progress.tasks_completed = completed_tasks_count
            study_progress.study_minutes = plan.completed_minutes
            study_progress.save(update_fields=["tasks_completed", "study_minutes", "updated_at"])
        except Exception:
            pass

        return task
