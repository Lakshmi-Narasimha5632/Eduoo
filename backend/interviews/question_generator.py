"""Adaptive multi-turn interview question generator synthesizing Agent Persona, Round Type, Role, and Performance History."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from .ai import InterviewAIService


class InterviewQuestionGenerator:
    """Multi-dimensional question generator matching Agent Persona, Round Type, and Target Role."""

    # Role Category Mapping
    @staticmethod
    def match_role_category(role: str) -> str:
        r = (role or "").lower()
        if any(w in r for w in ["front", "ui", "ux", "react", "vue", "angular", "web dev", "css", "html"]):
            return "frontend"
        if any(w in r for w in ["back", "python", "django", "node", "java", "golang", "go dev", "api", "flask", "fastapi", "spring"]):
            return "backend"
        if any(w in r for w in ["ai", "machine learning", "ml", "data sci", "deep learning", "nlp", "llm", "vision", "dataset", "analytics"]):
            return "data_ai"
        if any(w in r for w in ["devops", "cloud", "sre", "infra", "kubernetes", "docker", "aws", "azure", "gcp", "terraform", "platform"]):
            return "devops_cloud"
        if any(w in r for w in ["security", "cyber", "infosec", "soc", "penetration", "threat", "auth"]):
            return "security"
        if any(w in r for w in ["mobile", "ios", "android", "flutter", "react native", "swift", "kotlin"]):
            return "mobile"
        if any(w in r for w in ["product", "qa", "test", "sdet", "manager", "lead", "director"]):
            return "management"
        return "fullstack"

    # =========================================================================
    # 1. QUESTION 1 OPENERS: Tailored by (Agent, Round Type, Role Category)
    # =========================================================================
    AGENT_ROLE_OPENERS: Dict[str, Dict[str, Dict[str, List[str]]]] = {
        "alex_architect": {
            "technical": {
                "frontend": [
                    "Alex Chen here from Google. Welcome to the technical systems round. For a {role}, browser runtime performance is systems engineering. Walk me through how you diagnose and eliminate severe Interaction to Next Paint (INP) bottlenecks or JavaScript main-thread lockups caused by bloated DOM trees and un-batched microtasks.",
                    "Alex Chen here. In high-traffic client applications, offline state resilience is critical. As a {role}, how do you architect an offline-first storage and synchronization layer using Service Workers and IndexedDB that guarantees data integrity across intermittent cellular disconnects?",
                ],
                "backend": [
                    "Alex Chen here. Welcome to the technical systems round. At Google scale, we prioritize memory layouts, network I/O bounds, and thread safety. For your work as a {role}, explain how you diagnose and eliminate database connection pool exhaustion and lock contention under high-concurrency writes.",
                    "Alex Chen here. Let's discuss resilient API design. As a {role}, how do you implement idempotency keys, exponential backoff, and distributed circuit breakers across microservices to prevent cascading network failures?",
                ],
                "data_ai": [
                    "Alex Chen here. In large-scale ML systems, data ingestion latency is often the primary bottleneck. For your role as a {role}, how do you architect a high-throughput feature store pipeline that delivers sub-10ms point-in-time features to live inference models without memory leaks?",
                    "Alex Chen here. Let's examine distributed model serving. As a {role}, how do you manage GPU memory allocation, dynamic request batching, and horizontal autoscaling under unpredictable inference spikes?",
                ],
                "devops_cloud": [
                    "Alex Chen here. Welcome to the technical systems round. At Google scale, infrastructure resilience is paramount. As a {role}, walk me through how you configure Kubernetes pod disruption budgets, horizontal pod autoscalers, and multi-region traffic failover to survive total availability zone outages.",
                    "Alex Chen here. Let's talk about infrastructure reliability. As a {role}, how do you design zero-downtime progressive rollouts (Canary or Blue-Green) with automated health metric verification and instantaneous rollbacks?",
                ],
                "security": [
                    "Alex Chen here. In zero-trust distributed architectures, every boundary must be verified. For your {role} work, explain how you enforce mutual TLS (mTLS) across microservices, dynamic secret rotation, and protection against Server-Side Request Forgery (SSRF).",
                ],
                "mobile": [
                    "Alex Chen here. Mobile systems must operate under strict battery, CPU, and thermal constraints. For your role as a {role}, how do you design an efficient background sync scheduler that avoids holding radio wakelocks while managing SQLite concurrent write transactions?",
                ],
                "fullstack": [
                    "Alex Chen here. Welcome to the technical systems round. In full-stack systems, we evaluate end-to-end data flow. As a {role}, walk me through how you design caching across browser, CDN, reverse proxy, and distributed database to achieve sub-50ms p99 response times while avoiding stale-cache anomalies.",
                ],
            },
            "coding": {
                "default": [
                    "Hello, I am Alex Chen. In coding rounds, I evaluate systems awareness—cache friendliness, memory allocation overhead, and thread safety. For your {role} interview, describe an algorithmic design where you must process a continuous high-velocity data stream under a strict 64MB memory ceiling.",
                    "Alex Chen here. Let's examine algorithmic concurrency. As a {role}, how would you implement a thread-safe in-memory cache with reader-writer locks and probabilistic early expiration (XFetch) to prevent thundering herd spikes?",
                ],
            },
            "system_design": {
                "default": [
                    "Welcome. I am Alex Chen, Staff Systems Architect at Google. In system design, we look for engineers who master horizontal partitioning, fault domains, and datacenter partitions. For your work as a {role}, walk me through the high-level architecture of a system you designed or maintained that handled high concurrency or mission-critical traffic.",
                    "Alex Chen here. Let's design a globally distributed event ingestion engine processing 500,000 events/sec. As a {role}, how do you handle message ordering, cross-region replication lag, and exactly-once delivery guarantees?",
                ],
            },
            "behavioral": {
                "default": [
                    "Alex Chen here. Technical leadership requires making hard trade-offs when business deadlines clash with architectural integrity. As a {role}, tell me about a time you had to push back against a technical shortcut that would have caused critical architectural debt or production instability.",
                    "Alex Chen here. At Google scale, managing large-scale outages tests leadership. Tell me about the most severe production incident you owned as a {role}. Walk me through your triage, mitigation, and how you conducted the blameless post-mortem.",
                ],
            },
            "resume": {
                "default": [
                    "Alex Chen here. Looking at your resume for {role}, I want to dive into the core architecture of your most impactful project. What were the exact throughput requirements, data storage choices, and single points of failure you had to engineer around?",
                ],
            },
            "mixed": {
                "default": [
                    "Welcome. I am Alex Chen, Staff Systems Architect at Google. Today we will evaluate your systems thinking, architectural trade-offs, and technical judgment as a {role}. To kick off, walk me through a recent engineering challenge where you designed for high availability and low latency.",
                ],
            },
        },
        "sophia_algorithms": {
            "coding": {
                "frontend": [
                    "Hello, candidate. I am Dr. Sophia Lin from DeepMind. In frontend engineering, algorithmic efficiency directly governs frame rendering. Explain the asymptotic time complexity of Virtual DOM tree diffing. How do key heuristics reduce an O(n^3) tree edit-distance problem down to O(n), and what edge cases break this heuristic?",
                    "Dr. Sophia Lin here. When implementing client-side autocomplete or search-as-you-type over 50,000 items in a {role} application, how do you construct a Trie or Prefix Tree with memoized sub-results that guarantees sub-5ms query response without excessive memory bloat?",
                ],
                "backend": [
                    "Hello, candidate. I am Dr. Sophia Lin from DeepMind. In algorithmic interviews, I look for formal problem decomposition, clear invariant proofs, and asymptotic optimality. For your role as a {role}, explain how you implement a sliding-window rate limiter with strictly O(1) space and time overhead.",
                    "Dr. Sophia Lin here. Consider dependency resolution in backend build systems. As a {role}, explain how you detect cyclic dependencies using Kahn's topological sort algorithm versus Tarjan's strongly connected components algorithm, detailing their time-space invariants.",
                ],
                "data_ai": [
                    "Hello. I am Dr. Sophia Lin from DeepMind. In machine learning systems, algorithmic complexity determines scale. For a {role}, walk me through the mathematical formulation and asymptotic complexity of the standard Transformer attention mechanism O(n^2), and how FlashAttention or sparse attention optimize memory locality.",
                    "Dr. Sophia Lin here. In high-dimensional vector search, exact nearest neighbors scale as O(d * n). For your {role} work, explain the invariant properties and graph traversal complexity of Hierarchical Navigable Small World (HNSW) indexing.",
                ],
                "devops_cloud": [
                    "Dr. Sophia Lin here from DeepMind. Distributed orchestration relies on graph algorithms. For your {role} assessment, explain how Kubernetes pod scheduling models the multi-dimensional bin-packing problem, and the asymptotic trade-offs of greedy heuristics versus optimal integer linear programming.",
                    "Dr. Sophia Lin here. In distributed consensus, how do consistent hashing rings maintain minimal key remapping invariants when nodes dynamically join or fail? Prove the bound on remapped keys.",
                ],
                "default": [
                    "Hello, candidate. I am Dr. Sophia Lin from DeepMind. In algorithmic interviews, I look for formal problem decomposition, clear invariant proofs, and asymptotic optimality. For your role as {role}, walk me through your approach to analyzing worst-case vs amortized complexities, and a complex algorithm you have implemented.",
                    "Dr. Sophia Lin here. Explain how you formulate dynamic programming state transitions and prove optimal substructure and overlapping subproblems for a multi-constraint optimization problem in {role}.",
                ],
            },
            "technical": {
                "frontend": [
                    "Dr. Sophia Lin here. Beyond UI libraries, deep client engineering requires mastering memory locality and browser event loop microtasks. For your {role} work, walk me through how layout thrashing and forced synchronous reflow occur algorithmically in the browser render tree.",
                ],
                "backend": [
                    "Dr. Sophia Lin here. Beyond high-level frameworks, deep software engineering requires mastering memory locality, cache lines, and data structure internals. For your {role} work, walk me through how you choose between pointer-based structures vs contiguous memory layouts under high-frequency access.",
                ],
                "default": [
                    "Dr. Sophia Lin here from DeepMind. In this technical round, we explore computational foundations. For your role as a {role}, explain how database index structures (B+ Trees vs LSM Trees) trade write amplification against read latency using formal asymptotic bounds.",
                ],
            },
            "system_design": {
                "default": [
                    "Dr. Sophia Lin here. In distributed systems, consensus algorithms depend on formal state invariants like Raft or Paxos. In the context of {role}, how do consistent hashing rings handle dynamic node membership without data loss or cascading rebalances?",
                ],
            },
            "behavioral": {
                "default": [
                    "Dr. Sophia Lin here. Algorithmic rigor requires discipline when diagnosing elusive, non-deterministic bugs or race conditions. Tell me about a time as a {role} where intuition failed and you used structured scientific hypothesis testing to isolate an algorithmic bug.",
                ],
            },
            "resume": {
                "default": [
                    "Dr. Sophia Lin here. Walk me through the most algorithmically challenging feature on your resume as a {role}. What were the exact space and time complexities, and what algorithmic trade-offs did you evaluate?",
                ],
            },
            "mixed": {
                "default": [
                    "Hello. I am Dr. Sophia Lin from DeepMind. We will explore your algorithmic depth, data structure design, and mathematical problem solving for {role}. To begin, describe an algorithmic optimization you implemented that dramatically reduced time or space consumption.",
                ],
            },
        },
        "marcus_director": {
            "behavioral": {
                "frontend": [
                    "Marcus Vance here. Welcome to the leadership and culture round. As a Bar Raiser at Stripe, I evaluate genuine ownership and how you deliver measurable business impact. As a {role}, tell me about a high-stakes project where you had to push back on unrealistic product feature requests to safeguard user experience and accessibility.",
                    "Marcus Vance here. In frontend teams, disagreements over architecture or design system adoption can paralyze shipping velocity. Tell me about a time as a {role} where you aligned conflicting stakeholders and drove consensus on a contentious technical decision.",
                ],
                "backend": [
                    "Marcus Vance here. Welcome to the leadership round. As a Bar Raiser at Stripe, I look beyond technical jargon to evaluate accountability under pressure. Tell me about a critical production outage or data integrity failure you personally managed as a {role}. Walk me through your triage, stakeholder communication, and post-mortem.",
                    "Marcus Vance here. Technical leadership means making hard calls on tech debt versus feature velocity. As a {role}, describe a time you had to persuade business stakeholders to allocate significant engineering bandwidth toward refactoring legacy backend services.",
                ],
                "devops_cloud": [
                    "Marcus Vance here. In infrastructure and cloud engineering, reliability is the bedrock of business trust. Tell me about a high-stakes cloud migration or major infrastructure upgrade you led as a {role} where any mistake would have resulted in immediate customer downtime.",
                    "Marcus Vance here. Tell me about a situation as a {role} where developer velocity clashed with cloud security or compliance standards. How did you partner with development teams without becoming a bottleneck?",
                ],
                "data_ai": [
                    "Marcus Vance here. In AI and data science, moving from research prototypes to revenue-generating production services is tough. Tell me about a time as a {role} where an ML model failed to deliver the expected business impact in production, and how you pivoted.",
                ],
                "default": [
                    "Marcus Vance here. Welcome to the leadership and culture round. As a Bar Raiser at Stripe, I look beyond technical jargon to evaluate genuine ownership, stakeholder alignment, and how you deliver measurable business impact. As a {role}, tell me about a high-stakes project where you had to navigate conflicting priorities between engineering and product leadership.",
                    "Marcus Vance here. Tell me about a time you had a fundamental technical disagreement with another senior engineer or manager. How did you disagree and commit without damaging team trust?",
                ],
            },
            "technical": {
                "default": [
                    "Marcus Vance here. In this round, we evaluate how you make pragmatic technical compromises when engineering ideals clash with business deadlines. As a {role}, describe a time you had to choose between building custom infrastructure vs using a managed SaaS service, and how you justified that decision to leadership.",
                    "Marcus Vance here. Walk me through your mental framework for evaluating Total Cost of Ownership (TCO) when architecting a major software system for {role}.",
                ],
            },
            "system_design": {
                "default": [
                    "Marcus Vance here. System design is as much about operational simplicity, cost, and developer velocity as raw scale. As a {role}, how do you evaluate total cost of ownership (TCO) and team maintainability when architecting a major platform service?",
                ],
            },
            "coding": {
                "default": [
                    "Marcus Vance here. When evaluating code, I look for clean craftsmanship, testability, and defensive programming that any engineer can easily maintain. As a {role}, how do you structure your code, error boundaries, and tests to ensure long-term maintainability?",
                ],
            },
            "resume": {
                "default": [
                    "Marcus Vance here. Walk me through the project on your resume you are most proud of as a {role}. What was YOUR personal contribution, what measurable KPI did it move, and what would you do differently if building it again today?",
                ],
            },
            "mixed": {
                "default": [
                    "Marcus Vance here. As a Bar Raiser at Stripe, I focus on candidate ownership, technical decision-making, and leadership impact. For your {role} evaluation, start by telling me about a challenging technical initiative you drove from ambiguity to production delivery.",
                ],
            },
        },
        "elena_fullstack": {
            "technical": {
                "frontend": [
                    "Hi! Elena Rostova here from Vercel! For your role as a {role}, let's dive into modern rendering paradigms. Walk me through the exact execution lifecycle differences between React Server Components (RSC), Client Hydration, and Static Site Generation (SSG). In what scenarios would Server Components actually degrade user experience?",
                    "Elena Rostova here from Vercel. We look for full-stack excellence where frontend responsiveness meets resilient backend data models. In this {role} round, tell me how you architect the communication boundary between client state and server APIs to ensure sub-100ms interactions.",
                ],
                "backend": [
                    "Hi! Elena Rostova here from Vercel. For a {role}, modern backend architecture often requires Edge middleware and Backend-for-Frontend (BFF) patterns. How do you design an edge API layer that performs authentication, session validation, and geo-routing with under 10ms cold start latency?",
                    "Elena Rostova here. Let's discuss real-time data delivery for {role}. Compare Server-Sent Events (SSE) versus WebSockets for streaming live updates to thousands of concurrent browser sessions across unreliable mobile networks.",
                ],
                "data_ai": [
                    "Elena Rostova here from Vercel! When integrating AI and LLMs into modern web apps, streaming user interfaces are essential. For your {role} work, how do you handle streaming chunked token responses over HTTP to a reactive UI while supporting smooth auto-scrolling, Markdown parsing, and syntax highlighting without dropping frames?",
                ],
                "devops_cloud": [
                    "Elena Rostova here from Vercel. In modern web deployment pipelines, Edge caching rules like stale-while-revalidate (SWR) and instant cache purges are critical. As a {role}, how do you architect global CDN caching headers so dynamic content updates instantly without cache-stampede storms on your origin servers?",
                ],
                "default": [
                    "Hi! Elena Rostova here from Vercel. We look for full-stack excellence where frontend responsiveness meets resilient backend data models. In this {role} round, tell me how you architect the communication boundary between client state and server APIs to ensure sub-100ms interactions.",
                ],
            },
            "coding": {
                "frontend": [
                    "Elena Rostova here from Vercel. In modern full-stack systems, algorithmic performance on the client is critical to prevent UI frame drops. For your {role} assessment, how do you implement a virtualized list component capable of rendering 100,000 dynamic items at 60 frames per second?",
                ],
                "default": [
                    "Elena Rostova here. In modern full-stack systems, algorithmic performance on the client is critical to prevent UI frame drops. For your {role} assessment, how do you optimize deep object diffing, memoization, or client-side searching over tens of thousands of items without blocking the main thread?",
                ],
            },
            "system_design": {
                "default": [
                    "Elena Rostova here. Let's discuss modern web architecture—Edge computing, Server-Side Rendering (SSR) vs Incremental Static Regeneration (ISR), and global CDN caching. As a {role}, how would you architect a globally distributed application that delivers instant page loads with live real-time updates?",
                ],
            },
            "behavioral": {
                "default": [
                    "Elena Rostova here. Delivering delightful products requires empathy for both end-users and developer experience. Tell me about a time as a {role} where you advocated for user experience or accessibility when the team wanted to ship a quick, unpolished feature.",
                ],
            },
            "resume": {
                "default": [
                    "Elena Rostova here. I would love to explore the user-facing application on your resume for {role}. Walk me through the architecture: from the UI state machines down to database indexing and API response payloads.",
                ],
            },
            "mixed": {
                "default": [
                    "Hi! Elena Rostova from Vercel. Today we will explore your full-stack engineering, performance optimizations, and user experience craftsmanship for {role}. To kick off, describe a complex feature you shipped and how you balanced client fluidity with backend resilience.",
                ],
            },
        },
    }

    # =========================================================================
    # 2. QUESTION 2+ QUESTION BANKS (Categorized by Round Type & Role)
    # =========================================================================
    QUESTIONS_BY_ROUND: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
        "system_design": {
            "all": [
                {
                    "question": "How do you design a resilient multi-datacenter data ingestion pipeline that guarantees zero data loss during network partitions?",
                    "category": "system_design",
                    "difficulty": "advanced",
                    "expected_answer": "Decoupled message brokers (Kafka/Pulsar), local disk buffers, idempotent consumer offsets, write-ahead logging, and multi-region asynchronous replication with failover circuit breakers.",
                },
                {
                    "question": "When designing database sharding for high-growth workloads, how do you choose a shard key to avoid hot partitions, and how do you execute cross-shard aggregations?",
                    "category": "system_design",
                    "difficulty": "advanced",
                    "expected_answer": "Consistent hashing with virtual nodes, composite shard keys (tenant_id + hash), scatter-gather queries with map-reduce aggregations, or maintaining materialized views in secondary storage.",
                },
                {
                    "question": "How would you design a distributed rate limiter that operates across dozens of microservice nodes with sub-millisecond overhead?",
                    "category": "system_design",
                    "difficulty": "intermediate",
                    "expected_answer": "Token bucket or sliding window logs implemented with Redis Lua scripts, or local in-memory token buckets synchronized asynchronously via batch gossip protocols.",
                },
                {
                    "question": "Explain how you implement distributed locking in high-throughput systems, and how you guard against split-brain, clock drift, and GC pause expirations.",
                    "category": "system_design",
                    "difficulty": "advanced",
                    "expected_answer": "Consensus-backed leases in etcd/ZooKeeper with fencing tokens to prevent zombie processes from committing state mutations after lease expiration.",
                },
                {
                    "question": "Walk me through how you mitigate cache stampedes (thundering herd) and cache penetration under sudden 50x read traffic spikes.",
                    "category": "system_design",
                    "difficulty": "intermediate",
                    "expected_answer": "Mutex locking on cache miss (singleflight), probabilistic early expiration (XFetch), Bloom filters for non-existent keys, and stale-while-revalidate background warmers.",
                },
            ],
        },
        "coding": {
            "all": [
                {
                    "question": "Given a continuous data stream, design an algorithm to find the maximum in a sliding window of size K in O(n) total time. Detail your monotonic invariant.",
                    "category": "coding",
                    "difficulty": "advanced",
                    "expected_answer": "Maintain a double-ended queue (deque) storing indices. Invariant: elements in deque are strictly monotonically decreasing. Evict indices outside window from front, pop smaller elements from back.",
                },
                {
                    "question": "Explain the state-space formulation and transition equations for a multidimensional dynamic programming problem (such as edit distance or knapsack with capacity and item limits).",
                    "category": "coding",
                    "difficulty": "advanced",
                    "expected_answer": "Define DP state dp[i][w], establish recurrence relation dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight[i]] + val[i]), base cases, and optimize memory to O(w) using 1D rolling array.",
                },
                {
                    "question": "How do you implement an in-memory LRU Cache with strictly O(1) average time complexity for both get and put operations? Detail internal pointer mechanics.",
                    "category": "coding",
                    "difficulty": "intermediate",
                    "expected_answer": "Hash map mapping keys to doubly linked list nodes. Node contains key and val. On access/update, splice node and move to head. On eviction, remove tail node and delete key from map.",
                },
                {
                    "question": "Walk through the binary search invariant on an answer space (e.g. allocating tasks across K workers to minimize max load). How do you prove termination and avoid off-by-one errors?",
                    "category": "coding",
                    "difficulty": "intermediate",
                    "expected_answer": "Define search range [low, high]. Invariant: feasible(ans) is monotonic. In loop while low < high, mid = low + (high - low) // 2. If feasible(mid), high = mid; else low = mid + 1. Returns low.",
                },
                {
                    "question": "Compare graph cycle detection in directed graphs vs undirected graphs. When would you choose Kahn's topological sort over Tarjan's strongly connected components algorithm?",
                    "category": "coding",
                    "difficulty": "advanced",
                    "expected_answer": "Undirected uses DFS with parent check or Disjoint Set Union (Union-Find). Directed uses 3-color DFS or in-degree tracking (Kahn's). Tarjan's is preferred when full component condensation is required.",
                },
            ],
        },
        "behavioral": {
            "all": [
                {
                    "question": "Describe a high-stakes project in your career where deliverables were falling behind schedule. What decisive actions did you take to re-scope, realign stakeholders, and deliver?",
                    "category": "behavioral",
                    "difficulty": "intermediate",
                    "expected_answer": "STAR framework: Situation context, Task objective, Actions taken (ruthless re-scoping, transparent stakeholder communication, unblocking team), and quantifiable Outcome.",
                },
                {
                    "question": "Tell me about a critical production outage or data integrity failure you managed. Walk me through your triage, mitigation, and how you conducted a blameless post-mortem.",
                    "category": "behavioral",
                    "difficulty": "advanced",
                    "expected_answer": "Immediate incident containment, role separation (incident commander vs communications), blameless post-mortem identifying systemic root causes, and tracking action items to prevent recurrence.",
                },
                {
                    "question": "Describe a time you had a fundamental technical disagreement with another senior engineer or engineering manager. How did you disagree and commit without damaging team trust?",
                    "category": "behavioral",
                    "difficulty": "intermediate",
                    "expected_answer": "Focused on shared business goals, separated ego from architecture, gathered objective benchmark data/prototypes, and fully committed to the chosen path once decided.",
                },
                {
                    "question": "How do you manage technical debt within a fast-moving organization where product management constantly prioritizes new feature requests?",
                    "category": "behavioral",
                    "difficulty": "intermediate",
                    "expected_answer": "Quantifies tech debt in business terms (e.g. developer velocity slowdown, incident rate, latency impact), and negotiates a dedicated 15-20% capacity allocation or tech debt sprints.",
                },
                {
                    "question": "Give an example of an engineering standard, code review practice, or testing culture you introduced that tangibly improved your team's software quality.",
                    "category": "behavioral",
                    "difficulty": "intermediate",
                    "expected_answer": "Introduced automated linting/CI gates, architecture decision records (ADRs), or PR review checklists, leading to lower rollback rates and faster onboarding.",
                },
            ],
        },
        "technical": {
            "frontend": [
                {
                    "question": "How do you architect the boundary between server cache (like TanStack Query or SWR) and client UI state (Zustand/Context) to avoid hydration mismatches and stale state races?",
                    "category": "technical",
                    "difficulty": "intermediate",
                    "expected_answer": "Treating server state strictly as an asynchronous cache with stale-while-revalidate invalidation, keeping client UI state ephemeral, and avoiding duplicating server data into local component state.",
                },
                {
                    "question": "Walk me through how you diagnose and optimize Core Web Vitals—specifically Interaction to Next Paint (INP) and Largest Contentful Paint (LCP)—on a complex single-page application.",
                    "category": "technical",
                    "difficulty": "advanced",
                    "expected_answer": "For INP: breaking long tasks with scheduler.yield/requestIdleCallback, debouncing handlers, and using React 18 startTransition. For LCP: image preloading, server-side rendering critical HTML, and deferring non-critical JS.",
                },
                {
                    "question": "What are the engineering trade-offs between Server-Side Rendering (SSR), Static Site Generation (SSG), and React Server Components (RSC)? When would you avoid RSC?",
                    "category": "technical",
                    "difficulty": "intermediate",
                    "expected_answer": "RSC minimizes client JS bundle and enables direct backend data access without client waterfalls, but increases mental model complexity and is unneeded for purely client-side interactive canvases or offline apps.",
                },
                {
                    "question": "Describe how you implement optimistic UI updates for complex mutations (like drag-and-drop kanban cards or batch actions) while gracefully rolling back on server validation errors.",
                    "category": "technical",
                    "difficulty": "intermediate",
                    "expected_answer": "Snapshot current UI state before mutation, apply immediate local cache update, dispatch network request, and if rejected, rollback to snapshot and show an actionable toast notification.",
                },
            ],
            "backend": [
                {
                    "question": "Explain how database transaction isolation levels (Read Committed, Repeatable Read, Serializable) behave under high write contention, and how you resolve deadlocks.",
                    "category": "technical",
                    "difficulty": "advanced",
                    "expected_answer": "MVCC snapshot isolation, dirty reads vs phantom reads, row-level locks, lock ordering conventions, and optimistic concurrency control with version checks.",
                },
                {
                    "question": "How do you design a high-throughput message consumer that guarantees at-least-once processing without suffering from poison pills or consumer group rebalance storms?",
                    "category": "technical",
                    "difficulty": "advanced",
                    "expected_answer": "Manual offset commits after database transaction commit, dead-letter queues (DLQ) with exponential backoff retries, static consumer group membership to avoid stop-the-world rebalances.",
                },
                {
                    "question": "Explain why array-based contiguous data structures dramatically outperform pointer-heavy node structures (like linked lists or trees) in high-throughput CPU benchmarks.",
                    "category": "technical",
                    "difficulty": "advanced",
                    "expected_answer": "Spatial locality of reference, CPU cache line prefetching (L1/L2/L3 caches), eliminating cache misses, and avoiding pointer indirection and memory fragmentation.",
                },
            ],
            "data_ai": [
                {
                    "question": "Explain how you prevent data leakage when engineering features across time-series or tabular machine learning datasets.",
                    "category": "technical",
                    "difficulty": "advanced",
                    "expected_answer": "Strictly fit scalers and transformers only on training folds using pipeline objects; enforce expanding-window or rolling-window splits for time series.",
                },
                {
                    "question": "How do you design a low-latency Retrieval-Augmented Generation (RAG) pipeline with hybrid search (dense embeddings + sparse BM25) and re-ranking?",
                    "category": "technical",
                    "difficulty": "advanced",
                    "expected_answer": "Two-stage retrieval: fast approximate nearest neighbors (HNSW) combined with BM25 via reciprocal rank fusion (RRF), followed by a cross-encoder re-ranker on top 50 candidates.",
                },
                {
                    "question": "What strategies do you use to detect and mitigate model drift and concept drift in production ML inference services?",
                    "category": "technical",
                    "difficulty": "intermediate",
                    "expected_answer": "Kolmogorov-Smirnov statistical tests, Population Stability Index (PSI), monitoring prediction distribution entropy, and triggering automated retraining workflows.",
                },
            ],
            "devops_cloud": [
                {
                    "question": "How do you architect a zero-downtime progressive deployment strategy (Canary or Blue-Green) across a distributed Kubernetes cluster?",
                    "category": "technical",
                    "difficulty": "advanced",
                    "expected_answer": "Service mesh (Istio/Linkerd) or Argo Rollouts traffic splitting, automated metric analysis (error rate, p99 latency), and automated rollback triggers on threshold breach.",
                },
                {
                    "question": "Describe how you secure infrastructure-as-code (Terraform) pipelines, manage secret rotation, and enforce least-privilege IAM policies.",
                    "category": "technical",
                    "difficulty": "intermediate",
                    "expected_answer": "Static policy as code (OPA/Checkov), HashiCorp Vault dynamic ephemeral credentials, OIDC-based cloud federation in CI, and separating state files with remote locking.",
                },
            ],
            "security": [
                {
                    "question": "How do you defend a modern API architecture against Insecure Direct Object References (IDOR), JWT replay attacks, and SSRF?",
                    "category": "technical",
                    "difficulty": "advanced",
                    "expected_answer": "Object-level authorization verification (checks user tenant on every fetch), short-lived JWTs with token rotation, and strict egress allowlisting with metadata service IP blocking.",
                },
            ],
            "all": [
                {
                    "question": "When evaluating whether to build custom infrastructure internally vs adopting a third-party managed service/SaaS, what framework do you use to evaluate total cost of ownership (TCO)?",
                    "category": "technical",
                    "difficulty": "advanced",
                    "expected_answer": "Calculates direct SaaS licensing vs ongoing engineering maintenance, on-call burden, security/compliance risks, vendor lock-in, and core competency alignment.",
                },
                {
                    "question": "How do you design a resilient real-time live synchronization feature? Compare WebSockets vs Server-Sent Events (SSE) across mobile network reconnects and battery usage.",
                    "category": "technical",
                    "difficulty": "advanced",
                    "expected_answer": "SSE is lightweight and HTTP-native for unidirectional streams with automatic reconnects. WebSockets support bidirectional low-latency duplexing but require heartbeat pings and custom reconnect backoff.",
                },
            ],
        },
    }

    # =========================================================================
    # 3. QUESTION GENERATION LOGIC
    # =========================================================================
    @classmethod
    def get_opener(cls, agent_persona: str, interview_type: str, role: str, session_seed: int = 0) -> str:
        """Generate a personalized, agent-distinct, role-aware Question 1 opener."""
        persona = agent_persona or "alex_architect"
        agent_dict = cls.AGENT_ROLE_OPENERS.get(persona, cls.AGENT_ROLE_OPENERS["alex_architect"])

        norm_type = (interview_type or "technical").lower().replace("-", "_")
        if norm_type not in agent_dict:
            norm_type = "mixed" if "mix" in norm_type else "technical"

        type_dict = agent_dict.get(norm_type, agent_dict.get("technical", {}))

        role_cat = cls.match_role_category(role)
        # Select best candidate list
        candidates = type_dict.get(role_cat) or type_dict.get("default") or []

        # If not found, try fallback to technical for that role or default
        if not candidates:
            tech_dict = agent_dict.get("technical", {})
            candidates = tech_dict.get(role_cat) or tech_dict.get("default") or []

        if not candidates:
            # Ultimate safety fallback
            candidates = [
                f"Welcome to your {interview_type} mock interview for {role}. Walk me through an architectural challenge you solved recently."
            ]

        # Rotate based on session seed
        idx = session_seed % len(candidates)
        template = candidates[idx]
        return template.format(role=role.strip() or "Software Developer")

    @classmethod
    def generate_question(
        cls,
        interview,
        order: int,
        previous_qa: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        """Generate dynamic, distinctive question based on Agent Persona, Round Type, Role, and Order."""
        role = (interview.target_role or "Software Developer").strip()
        int_type = (interview.interview_type or "technical").lower().replace("-", "_")
        difficulty = interview.difficulty or "intermediate"
        agent_persona = getattr(interview, "agent_persona", "alex_architect") or "alex_architect"
        agent_strictness = getattr(interview, "agent_strictness", "balanced") or "balanced"
        agent_details = getattr(interview, "agent_details", {}) or {}
        agent_name = agent_details.get("name", "Alex Chen")
        agent_company = agent_details.get("company", "Google")
        agent_style = agent_details.get("style", "Rigorous Architecture")

        interview_id = getattr(interview, "id", None) or 1
        role_hash = int(hashlib.md5(f"{role}_{agent_persona}_{int_type}".encode("utf-8")).hexdigest()[:6], 16)
        session_seed = interview_id * 101 + role_hash

        # Adapt difficulty based on performance
        next_diff = difficulty
        if previous_qa and len(previous_qa) > 0:
            last_score = previous_qa[-1].get("score", 75)
            if last_score >= 85:
                next_diff = "advanced"
            elif last_score < 60:
                next_diff = "beginner"

        # ---------------------------------------------------------------------
        # Question 1: Distinctive Agent-Grounded Icebreaker & Problem
        # ---------------------------------------------------------------------
        if order == 1:
            opener_text = cls.get_opener(agent_persona, int_type, role, session_seed=session_seed)
            return {
                "question": opener_text,
                "category": int_type if int_type in ["coding", "system_design", "behavioral"] else "technical",
                "difficulty": "beginner" if difficulty == "beginner" else "intermediate",
                "expected_answer": (
                    f"Structured, concise response for {agent_name} covering relevant technical foundations, "
                    f"system tradeoffs, and concrete outcomes in {role}."
                ),
            }

        # ---------------------------------------------------------------------
        # Live AI Generation (if available and valid)
        # ---------------------------------------------------------------------
        if InterviewAIService.is_live_ai_available():
            total_target = getattr(interview, "num_questions", 5) or 5
            prompt = f"""
            You are {agent_name}, {agent_style} at {agent_company}.
            Candidate Role: {role}
            Round Type: {int_type}
            Strictness Level: {agent_strictness}
            Question #{order} of {total_target}
            Target Difficulty: {next_diff}
            Previous QA History: {previous_qa or 'None'}

            Generate question #{order} in YOUR distinct voice ({agent_name} at {agent_company}).
            Do NOT ask a generic introduction. Ask ONE highly specific, practical, in-depth {int_type} question tailored to a {role}.
            Return JSON with keys: "question", "category", "difficulty", "expected_answer".
            """
            system_prompt = (
                f"You are {agent_name}, an elite interviewer at {agent_company}. "
                f"Embody your signature style ({agent_style}). Speak directly to the candidate."
            )
            try:
                ai_data = InterviewAIService.generate_json(prompt, system_prompt)
                if ai_data and ai_data.get("question"):
                    return {
                        "question": ai_data["question"],
                        "category": ai_data.get("category", int_type),
                        "difficulty": ai_data.get("difficulty", next_diff),
                        "expected_answer": ai_data.get(
                            "expected_answer",
                            f"Comprehensive explanation demonstrating practical {role} mastery for {agent_name}.",
                        ),
                    }
            except Exception:
                pass

        # ---------------------------------------------------------------------
        # Multi-Dimensional Question Bank Fallback (Agent, Round Type, Role)
        # ---------------------------------------------------------------------
        role_cat = cls.match_role_category(role)

        # For mixed rounds, alternate across round types systematically
        effective_round = int_type
        if int_type == "mixed":
            mixed_sequence = ["technical", "coding", "system_design", "behavioral", "technical"]
            effective_round = mixed_sequence[(order - 1) % len(mixed_sequence)]

        # Collect relevant questions for the effective round
        round_pool = cls.QUESTIONS_BY_ROUND.get(effective_round, cls.QUESTIONS_BY_ROUND["technical"])
        available_questions: List[Dict[str, Any]] = []

        if role_cat in round_pool:
            available_questions.extend(round_pool[role_cat])
        if "all" in round_pool:
            available_questions.extend(round_pool["all"])

        # Fallback if specific pool is dry
        if not available_questions:
            tech_pool = cls.QUESTIONS_BY_ROUND["technical"]
            available_questions = tech_pool.get(role_cat, tech_pool.get("all", []))

        # Filter out questions already asked in this session
        asked_texts = {q.get("question", "").strip() for q in (previous_qa or [])}
        fresh_questions = [q for q in available_questions if q.get("question", "").strip() not in asked_texts]
        if not fresh_questions:
            fresh_questions = available_questions

        # Deterministic rotation based on session ID, order, and role hash
        rotation_idx = (session_seed + order * 23) % len(fresh_questions)
        selected_q = fresh_questions[rotation_idx]

        q_text = selected_q["question"]
        if "{role}" in q_text:
            q_text = q_text.format(role=role)

        # Prepend agent voice flair for subtle individuality
        agent_prefix = ""
        if order == 2 and agent_persona == "sophia_algorithms":
            agent_prefix = "Dr. Sophia Lin here: Let's analyze algorithmic depth. "
        elif order == 2 and agent_persona == "alex_architect":
            agent_prefix = "Alex Chen here: Diving into system constraints. "
        elif order == 2 and agent_persona == "marcus_director":
            agent_prefix = "Marcus Vance here: Let's examine execution trade-offs. "
        elif order == 2 and agent_persona == "elena_fullstack":
            agent_prefix = "Elena Rostova here: Exploring end-to-end architecture. "

        final_question_text = f"{agent_prefix}{q_text}" if agent_prefix and not q_text.startswith(agent_name.split()[0]) else q_text

        return {
            "question": final_question_text,
            "category": selected_q.get("category", effective_round),
            "difficulty": selected_q.get("difficulty", next_diff),
            "expected_answer": selected_q.get(
                "expected_answer",
                f"Structured explanation demonstrating practical knowledge for {agent_name} in {role}.",
            ),
        }
