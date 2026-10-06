from pathlib import Path
import shutil
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer


NOTES_DIR = Path(__file__).parent / "notes"

# Original study summaries; product-specific behavior can vary by version.
SUBJECTS = [
    ("Python_Notes.pdf", "Python Programming", [
        ("1. Foundations", [
            "Python is a high-level, dynamically typed language. Names refer to objects; assignment binds a name rather than copying an object. Indentation defines code blocks. The common CPython implementation compiles source to bytecode and executes it on a virtual machine.",
            "Built-in types include int, float, bool, str, list, tuple, dict, set, and None. Lists and dictionaries are mutable; strings and tuples are immutable. A shallow copy duplicates the outer collection but can still share nested objects.",
        ]),
        ("2. Control Flow and Functions", [
            "Use if/elif/else for branching, for to iterate over iterables, and while for condition-based repetition. break exits a loop; continue advances it. Functions use def and return values. Arguments may be positional or keyword-based, and type hints document intended types without default runtime enforcement.",
            "Default arguments are evaluated once when a function is defined, so avoid mutable defaults. Closures retain access to enclosing variables. Generators use yield to produce values lazily and can process large inputs without materializing all results.",
            "code: def add_tag(tag, tags=None):\n    if tags is None:\n        tags = []\n    tags.append(tag)\n    return tags",
        ]),
        ("3. Collections and OOP", [
            "A list is an ordered mutable sequence; a tuple is ordered and immutable; a set contains unique hashable values; a dict maps unique hashable keys to values. Use enumerate for indexes, zip for parallel iteration, and comprehensions for clear transformations.",
            "A class defines state and behavior; an instance is an object made from it. __init__ initializes instances. Inheritance models an is-a relationship; composition combines collaborating objects. Prefer small cohesive classes and explicit ownership of mutable state.",
        ]),
        ("4. Files, Errors, Testing", [
            "Use with to manage files and other resources; specify text encodings. pathlib handles paths, while json and csv handle common data formats. Catch only exceptions you can address, and preserve useful error context.",
            "Write focused tests for normal behavior, edge cases, and failures. unittest is built in; pytest is widely used. Avoid eval on untrusted data, protect credentials, validate external input, and keep dependencies maintained.",
        ]),
        ("5. Common Questions", [
            "List versus tuple: lists can be changed; tuples cannot. is checks object identity, while == compares values. Use is None for a None check. A generator is an iterator that yields values on demand. A virtual environment isolates project dependencies.",
        ]),
    ]),
    ("Java_Notes.pdf", "Java Programming", [
        ("1. Platform and Types", [
            "Java source is compiled by javac into bytecode; a Java Virtual Machine (JVM) executes it and may use just-in-time compilation. A JDK provides development tools and runtime components, with packaging varying by vendor. Java is statically typed; primitive types hold values, while reference types refer to objects.",
            "Packages organize names and APIs. Build tools such as Maven and Gradle manage dependencies, builds, and tests. A conventional program entry point is public static void main(String[] args).", 
        ]),
        ("2. Classes and Interfaces", [
            "A class defines fields, constructors, and methods. Encapsulation protects invariants; interfaces define contracts; inheritance specializes an is-a relationship. Prefer composition when it better represents collaboration. Use private fields and expose deliberate public methods.",
            "Overloading uses the same method name with different parameters; overriding supplies a subtype implementation. Use @Override. static members belong to the class; final can prevent reassignment, overriding, or inheritance depending on its use.",
        ]),
        ("3. Generics and Collections", [
            "Generics provide compile-time type safety. List stores an ordered sequence, Set stores unique values, and Map associates keys with values. ArrayList is a common resizable list; HashMap offers expected constant-time lookup under typical hashing assumptions, but does not promise iteration order.",
            "Choose collections by ordering, uniqueness, and lookup needs. Wildcard bounds such as ? extends T and ? super T express safe producer and consumer use. Streams process values with operations such as filter and map; terminal operations trigger evaluation.",
        ]),
        ("4. Errors and Concurrency", [
            "Checked exceptions must be caught or declared; unchecked exceptions extend RuntimeException. Catch specific failures. Try-with-resources closes AutoCloseable resources. ExecutorService manages task execution; protect shared mutable state with synchronization, locks, atomics, or concurrent collections.",
            "Common questions: the JVM executes bytecode while a JDK supplies development tools; encapsulation protects an object's state; an interface lets multiple types satisfy one contract. Strong typing does not prevent injection or authorization bugs: use parameterized SQL and least privilege.",
        ]),
    ]),
    ("C_Programming_Notes.pdf", "C Programming", [
        ("1. Compilation and Types", [
            "C is a compiled procedural language used in systems and embedded software. A toolchain preprocesses, compiles, and links translation units. Header files declare interfaces; source files define them. main is the conventional entry point. Compiler flags and the selected C standard affect available features.",
            "Types include integers, floating-point values, arrays, structures, unions, enums, and pointers. Integer widths can vary by platform; stdint.h defines fixed-width integer types. Use size_t for sizes and indexes, and check conversions, bounds, and overflow.",
        ]),
        ("2. Arrays, Pointers, Strings", [
            "An array stores contiguous elements. In many expressions it converts to a pointer to its first element, but an array is not itself a pointer. Pointer arithmetic is valid only within an array and one position past its end. C passes arguments by value; pass a pointer to allow a function to modify a caller's object.",
            "A C string is a character array terminated by '\\0'; storage must include the terminator. Validate buffer lengths. Undefined behavior, such as out-of-bounds access or signed overflow, means the language imposes no requirements on the result.",
            "code: int sum(const int *v, size_t n) {\n    int total = 0;\n    for (size_t i = 0; i < n; ++i) total += v[i];\n    return total;\n}",
        ]),
        ("3. Memory and Files", [
            "Automatic local objects typically have block lifetime; static objects last for the program duration. malloc allocates dynamic storage and free releases it. Check allocation results and prevent leaks, double frees, and use-after-free. Guard against overflow in count * sizeof(element).",
            "Use FILE functions such as fopen, fgets, and fclose and check their return values. Use compiler warnings, sanitizers, and static analysis. Do not use untrusted text as a printf format string; validate all external lengths and inputs.",
        ]),
        ("4. Common Questions", [
            "A pointer stores an address and enables indirect access. Stack and heap describe common storage strategies, but are not a complete language guarantee. A memory leak is allocated storage that can no longer be released by the program. const can prevent modification through a particular pointer or reference.",
        ]),
    ]),
    ("Cpp_Programming_Notes.pdf", "C++ Programming", [
        ("1. Modern C++", [
            "C++ is a compiled, multi-paradigm language. Select an explicit project standard such as C++17 or C++20. Prefer standard-library facilities: std::string for text, std::vector for dynamic sequences, and algorithms for common operations.",
            "A reference is an alias that must bind to an object; a pointer can be reseated and can represent no object. Use const references for large read-only inputs. Classes combine data and operations; constructors establish invariants and destructors release owned resources.",
        ]),
        ("2. RAII and Ownership", [
            "RAII ties resource lifetime to object lifetime, so destructors release resources even during exception unwinding. Use std::unique_ptr for exclusive ownership; use std::shared_ptr only when shared lifetime is needed. Raw pointers and references are usually non-owning views.",
            "The Rule of Zero favors composing types that already manage resources. If a type directly owns a resource, define copy and move behavior consistently. A moved-from object remains valid, but its value is usually unspecified.",
        ]),
        ("3. Templates and Containers", [
            "Templates enable generic functions and types. vector suits contiguous dynamic sequences, map gives ordered key lookup, unordered_map gives hash-based lookup, and set stores unique values. Choose by required operations and complexity; iterator invalidation rules vary by container.",
            "Algorithms such as sort, find, and transform operate on iterator ranges. Exceptions communicate failures that cannot be handled locally; throw by value and catch by const reference. A data race on unsynchronized shared memory is undefined behavior.",
            "code: std::vector<int> scores{82, 95, 71};\nstd::sort(scores.begin(), scores.end());\nauto high = std::find_if(scores.begin(), scores.end(),\n    [](int score) { return score >= 90; });",
        ]),
        ("4. Common Questions", [
            "RAII means resource acquisition is tied to initialization and deterministic destruction. A pointer may be null and reseated; a reference aliases an initialized object. Prefer smart pointers for ownership, compiler warnings and sanitizers for checks, and clear lifetime contracts in APIs.",
        ]),
    ]),
    ("Machine_Learning_Notes.pdf", "Machine Learning", [
        ("1. Problem and Workflow", [
            "Machine learning fits a model from data to make predictions or discover structure. Features are inputs; a label or target is the value supervised learning predicts. Define the user decision and cost of mistakes before choosing a model.",
            "Workflow: define a metric, inspect and clean data, split data, establish a baseline, train and tune on training/validation data, evaluate once on held-out test data, deploy, then monitor. Never let test data influence preprocessing or model selection: this is data leakage.",
        ]),
        ("2. Learning Types and Models", [
            "Supervised learning uses labeled examples. Classification predicts categories; regression predicts numeric values. Unsupervised learning finds structure without labels, such as clusters. Reinforcement learning learns actions from rewards and requires careful evaluation and safety constraints.",
            "Models include linear/logistic regression, decision trees, random forests, gradient-boosted trees, support vector machines, clustering, and neural networks. Complexity is not automatically better; compare against a simple baseline.",
        ]),
        ("3. Generalization and Metrics", [
            "Overfitting models training details that do not generalize; underfitting fails to capture useful patterns. Use representative data, regularization, validation, and simpler models when appropriate. Use time-ordered splits for time prediction and group-aware splits for correlated samples.",
            "Accuracy can mislead on imbalanced data. Precision measures correctness among predicted positives; recall measures how many true positives were found; F1 balances them. MAE and RMSE evaluate regression errors. Choose metrics based on actual error costs.",
        ]),
        ("4. Deployment and Common Questions", [
            "A deployed model needs versioned data and artifacts, monitoring, latency controls, security, and rollback plans. Track input drift and model quality as labels arrive. Review privacy, consent, bias, subgroup performance, and human oversight for high-impact decisions.",
            "Classification predicts a category; regression predicts a number. Cross-validation evaluates multiple partitions. A baseline catches pipeline mistakes and shows whether added complexity provides useful improvement. Fit transformations only on training data, then apply the fitted pipeline to other splits.",
        ]),
    ]),
    ("DSA_Notes.pdf", "Data Structures and Algorithms", [
        ("1. Complexity", [
            "Time complexity describes how operation counts grow with input size n; space complexity describes memory. Big O is an asymptotic upper bound, Omega a lower bound, and Theta a tight bound. Common growth rates include O(1), O(log n), O(n), O(n log n), O(n^2), and O(2^n).",
            "Analyze dominant terms and state assumptions. Best, average, and worst cases may differ. Dynamic-array append is amortized O(1), although a resize can take O(n). Measure real performance when constant factors and memory matter.",
        ]),
        ("2. Linear, Hash, and Tree Structures", [
            "Arrays provide O(1) indexed access; middle insertion usually shifts O(n) values. Linked-list insertion is O(1) when the node is known, but finding a position is O(n). Stacks are LIFO; queues are FIFO; deques support both ends.",
            "Hash-table lookup is expected O(1) with suitable hashing and load factor, but worst-case O(n). Balanced search trees support ordered operations in O(log n). A heap gives O(1) access to the highest-priority item and O(log n) insertion/removal.",
        ]),
        ("3. Searching and Sorting", [
            "Linear search takes O(n). Binary search takes O(log n) on sorted random-access data; maintain a precise interval invariant. Merge sort is stable O(n log n) and uses extra memory; heapsort is O(n log n); quicksort is typically O(n log n) but can be O(n^2); insertion sort suits small or nearly sorted input.",
            "Stability preserves the input order of equal-key items. In-place algorithms use limited extra storage. Choose based on constraints and required guarantees, not only the headline complexity.",
        ]),
        ("4. Graphs and Problem Solving", [
            "Graphs contain vertices and edges. Adjacency lists use O(V+E) space; matrices use O(V^2). BFS finds shortest paths in unweighted graphs in O(V+E). DFS helps find components and cycles. Dijkstra requires nonnegative edge weights; Bellman-Ford can handle negative edges.",
            "Dynamic programming stores overlapping subproblem results. Greedy algorithms need a proof that local choices produce a global solution. Clarify constraints, edge cases, invariants, data structures, and complexity before coding; test empty, duplicate, and boundary inputs.",
        ]),
    ]),
    ("Cybersecurity_Notes.pdf", "Cybersecurity Fundamentals", [
        ("1. Principles and Risk", [
            "The CIA triad is confidentiality, integrity, and availability. A threat could cause harm; a vulnerability is a weakness; risk combines likelihood and impact; a control reduces risk. Threat modeling identifies assets, trust boundaries, attack paths, and mitigations.",
            "Defense in depth uses complementary controls. Least privilege limits access; secure defaults reduce exposure; separation of duties distributes sensitive authority. Security is an ongoing process, not a product guarantee.",
        ]),
        ("2. Identity and Data", [
            "Authentication verifies identity; authorization grants actions. MFA combines independent factors. Encrypt data in transit with correctly configured TLS and protect stored data and keys. Hashing is one-way; password storage requires a slow salted scheme such as Argon2, scrypt, or bcrypt, not a fast general-purpose hash.",
            "Segment networks, patch exposed services, disable unused accounts and ports, protect secrets, and log security events without recording passwords or tokens. Replication is not a substitute for an independent tested backup.",
        ]),
        ("3. Application and Incident Security", [
            "Use parameterized queries to prevent SQL injection. Context-aware output encoding and safe templating reduce XSS. Protect state-changing requests against CSRF where applicable. Validate server-side input, enforce authorization on every protected operation, and keep dependencies current.",
            "Incident response commonly includes preparation, detection, containment, eradication, recovery, and lessons learned. Preserve evidence, document actions, follow escalation procedures, and communicate through approved channels. Test only systems you own or have explicit permission to assess.",
        ]),
        ("4. Common Questions and Habits", [
            "Encryption is reversible with the appropriate key; hashing is designed to be one-way. Phishing deceives people into revealing information or taking unsafe actions. A zero-day describes a vulnerability unknown to or not yet fixed by a responsible vendor, depending on context.",
            "Use unique passwords with a password manager, enable MFA, verify unexpected requests independently, update software, and report suspected incidents. Security testing without permission is not acceptable.",
        ]),
    ]),
    ("Mobile_Application_Development_Notes.pdf", "Mobile Application Development", [
        ("1. Platforms and Architecture", [
            "Android and iOS have distinct SDKs, lifecycle rules, UI conventions, permissions, and distribution. Native development uses each platform's primary tools; cross-platform frameworks share code but still need native integration. Choose based on audience, device features, team skills, performance, and maintenance.",
            "Separate presentation, business/domain logic, and data access. Keep rendering apart from business rules so behavior can be tested. Verify current platform requirements and store policies before release.",
        ]),
        ("2. Lifecycle, UI, Accessibility", [
            "Apps can move to background, be suspended, or be recreated after process death. Persist important state instead of assuming a process lives forever. Handle rotation, low memory, navigation, and interruptions.",
            "Adapt to screen size, text scaling, safe areas, and input methods. Accessibility requires semantic labels, contrast, logical focus, screen-reader support, and usable touch targets. Test using platform accessibility tools and real devices.",
        ]),
        ("3. Network, Storage, and Privacy", [
            "Network operations are asynchronous and may time out or fail. Use TLS and bounded timeouts. Retry carefully; non-idempotent operations need an idempotency strategy. Provide meaningful offline, loading, and error states.",
            "Store only necessary data. Use platform secure storage for credentials and keys, request permissions only when needed, and gracefully handle denial or revocation. Define consent, retention, deletion, and synchronization conflict behavior.",
        ]),
        ("4. Testing and Common Questions", [
            "Unit tests cover logic, integration tests cover boundaries, and UI tests exercise flows. Test multiple devices, OS versions, offline conditions, slow networks, and denied permissions. Profile startup, memory, battery, networking, and rendering before optimizing.",
            "Native apps directly use platform APIs; cross-platform apps share more code but may need platform-specific refinement. Keep network work off the UI thread. Deep links are input and must not bypass authorization. Offline-first design keeps useful local behavior and defines synchronization rules.",
        ]),
    ]),
    ("JavaScript_Notes.pdf", "JavaScript Programming", [
        ("1. Language Fundamentals", [
            "JavaScript runs in browsers and server runtimes such as Node.js. let and const are block-scoped; prefer const unless rebinding is required. Primitives include string, number, boolean, undefined, symbol, bigint, and null; objects, arrays, and functions are references.",
            "Use === and !== to avoid most coercive equality surprises. Empty arrays and objects are truthy. == converts types. Closures retain access to lexical variables; arrow functions capture this from the surrounding scope.",
        ]),
        ("2. Objects and Asynchronous Code", [
            "Objects store properties; arrays are ordered collections. Destructuring extracts values; spread syntax makes shallow copies, so nested objects may remain shared. Modules use import and export to state dependencies.",
            "Promises represent future completion. async functions return Promises; await pauses that function, not the entire runtime. Handle rejection with try/catch. Promise.all suits independent tasks that must all succeed; AbortController can cancel fetch requests.",
            "code: async function load(url) {\n    const response = await fetch(url);\n    if (!response.ok) throw new Error(String(response.status));\n    return response.json();\n}",
        ]),
        ("3. Browser APIs and Security", [
            "The DOM represents the page. Use querySelector and event listeners to interact with it. Prefer textContent for plain text; assigning untrusted input to innerHTML can cause cross-site scripting. Validate data on the server even when the browser checks it.",
            "Do not place API secrets in browser code. Web storage is accessible to same-origin scripts; cookies support controls such as HttpOnly, Secure, and SameSite. Use tests, linting, clear module boundaries, and explicit handling of asynchronous failures.",
        ]),
        ("4. Common Questions", [
            "null is an explicit empty value; undefined often means absent or unassigned. A closure is a function plus access to its lexical environment. Event bubbling propagates an event from its target through ancestors. await unwraps a Promise result or throws its rejection in an async function.",
        ]),
    ]),
    ("Web_Development_Notes.pdf", "Web Development: HTML, CSS, and HTTP", [
        ("1. Web and HTTP", [
            "A browser resolves a URL, sends an HTTP request, and renders the response. DNS resolves names; HTTPS uses TLS to protect HTTP. Requests contain methods, headers, and optional bodies; responses contain status codes, headers, and optional content.",
            "GET retrieves data and should not change server state; POST processes or creates; PUT replaces; PATCH partially updates; DELETE removes. Common statuses include 200, 201, 400, 401, 403, 404, and 500. APIs define contracts between clients and services.",
        ]),
        ("2. Semantic HTML and Accessibility", [
            "HTML describes document structure. Use semantic elements, logical headings, associated form labels, and buttons for actions. Provide meaningful alternative text for useful images; decorative images can use empty alt text. Keyboard users need visible focus and logical navigation.",
            "Use native HTML accessibility before ARIA. Forms should describe errors, identify required fields, and announce important status changes. Do not use color alone to convey meaning.",
        ]),
        ("3. CSS and Performance", [
            "CSS styling follows cascade, specificity, inheritance, and source order. The box model contains content, padding, border, and margin; border-box includes padding and border in declared dimensions. Flexbox handles one-dimensional layouts; Grid handles two-dimensional layouts.",
            "Responsive design adapts to viewport and user preferences. Test narrow and wide screens, contrast, text scaling, and reduced motion. Browsers parse HTML and CSS, compute layout, paint, and composite; measure before optimizing assets or scripts.",
        ]),
        ("4. Security and Common Questions", [
            "Same-origin policy restricts cross-origin access; CORS lets servers selectively authorize browser access and is not authentication. Prevent XSS with context-aware output encoding, protect state-changing requests against CSRF, use secure cookies, and authorize on the server.",
            "Authentication verifies identity; authorization checks allowed actions. Responsive design adapts usable content to devices and settings. REST is an architectural style commonly applied to resource-oriented web APIs; implementations vary in how completely they follow its constraints.",
        ]),
    ]),
    ("Operating_Systems_Notes.pdf", "Operating Systems", [
        ("1. Kernel and Processes", [
            "An operating system manages hardware and provides processes, virtual memory, files, and device access. The kernel handles privileged operations; applications request services through system calls. Interrupts notify the processor of events; context switches change the running execution state.",
            "A process is a running program with an address space and resources. A thread is an execution path inside a process; threads share process memory. Processes provide stronger isolation but inter-process communication adds cost.",
        ]),
        ("2. Scheduling and Synchronization", [
            "Schedulers select ready tasks. FCFS is simple; shortest-job-first can reduce average waiting under assumptions; round robin provides time slices; priority scheduling can starve low-priority work unless mitigated. I/O-blocked tasks wait for events and are not ready to run.",
            "Race conditions depend on timing. Mutexes protect critical sections; semaphores count permits; condition variables wait for predicates. Deadlock requires mutual exclusion, hold-and-wait, no preemption, and circular wait. Systems prevent, avoid, detect, or recover from it.",
        ]),
        ("3. Memory and Filesystems", [
            "Virtual memory gives a process an address space mapped to physical memory. Paging divides memory into pages and frames; a page fault triggers OS handling. A TLB caches translations. Thrashing occurs when excessive paging prevents useful work.",
            "Filesystems organize persistent files and metadata. Journaling can improve crash consistency but is not a backup. Use permissions and isolation to protect data; test backup restoration.",
        ]),
        ("4. Common Questions", [
            "A system call is a controlled request from user mode to the kernel. Virtual memory supports isolation and flexible memory management. A page fault can mean a page must be loaded or access permissions checked. A process has its own address space; threads commonly share one.",
        ]),
    ]),
    ("Computer_Networks_Notes.pdf", "Computer Networks", [
        ("1. Layers and Addressing", [
            "The OSI model describes physical, data-link, network, transport, session, presentation, and application layers. The Internet suite is commonly described as link, internet, transport, and application. Encapsulation adds headers as data moves through layers.",
            "Ethernet and Wi-Fi carry local frames; IP routes packets. IPv4 addresses are 32 bits; IPv6 addresses are 128 bits. CIDR prefixes such as /24 identify network bits. Routers forward between networks; a default gateway handles unmatched routes.",
        ]),
        ("2. Transport and Services", [
            "TCP provides reliable, ordered byte streams with retransmission, flow control, and congestion control; it does not preserve application message boundaries. UDP sends datagrams without built-in delivery or ordering guarantees.",
            "DNS resolves names into records such as A and AAAA and may cache answers according to TTL. DHCP can assign network configuration. ARP maps IPv4 local-network addresses to link-layer addresses; IPv6 uses Neighbor Discovery.",
        ]),
        ("3. Web Security and Troubleshooting", [
            "HTTP has methods, status codes, headers, and optional bodies. TLS authenticates a server and encrypts communication when correctly configured; HTTPS is HTTP over TLS. A port identifies a transport endpoint. Firewalls filter traffic but do not replace secure applications.",
            "Troubleshoot from local interface and link, to IP and route, DNS, transport connectivity, TLS, then application response and logs. Expose only required services and never ignore certificate warnings without understanding the cause.",
        ]),
        ("4. Common Questions", [
            "TCP is a reliable ordered byte stream; UDP is datagram-based without built-in reliability. DNS maps names to records. A subnet prefix specifies the network portion of an IP address. NAT translates addresses at network boundaries but is not itself a firewall or security guarantee.",
        ]),
    ]),
    ("Software_Engineering_Notes.pdf", "Software Engineering", [
        ("1. Requirements and Lifecycle", [
            "Software engineering uses disciplined practices to build and maintain software. Lifecycle activities include discovery, requirements, design, implementation, testing, deployment, and maintenance; teams revisit them as they learn.",
            "Functional requirements describe behavior; nonfunctional requirements describe qualities such as performance, security, availability, accessibility, and maintainability. Acceptance criteria make outcomes testable. Clarify edge cases and failure behavior early.",
        ]),
        ("2. Design and Implementation", [
            "Architecture defines components, responsibilities, and communication. High cohesion and low coupling support change. Common styles include layered, client-server, event-driven, and services; each adds trade-offs. Prefer the simplest design that meets requirements.",
            "Readable code uses clear names, focused functions, explicit errors, and tests. Version control records changes; coherent commits and reviews improve traceability. Continuous integration runs repeatable checks such as builds, tests, and linting.",
        ]),
        ("3. Testing and Delivery", [
            "Unit tests cover small units; integration tests cover boundaries; end-to-end tests cover user flows. Test expected cases, boundaries, invalid input, and recovery. Static analysis, security review, accessibility, and load tests complement automated tests.",
            "Agile emphasizes iterative delivery and feedback. Scrum and Kanban are frameworks, not goals. Technical debt is future cost caused by shortcuts or constraints; track its impact and plan. Safe releases need traceability, monitoring, and rollback.",
        ]),
        ("4. Common Questions", [
            "Verification asks whether the product meets specified requirements; validation asks whether it solves the user's actual problem. Requirements align stakeholders and guide design and tests. Code review should focus on correctness, security, clarity, and maintainability.",
        ]),
    ]),
    ("Cloud_Computing_Notes.pdf", "Cloud Computing", [
        ("1. Concepts and Service Models", [
            "Cloud computing provides on-demand network access to configurable resources with self-service provisioning, elasticity, pooling, and measured usage. It does not automatically mean cheaper, more secure, or more reliable.",
            "IaaS provides infrastructure; PaaS manages more of the platform; SaaS delivers an application. Serverless abstracts server management, not the existence of servers. Public, private, hybrid, and multicloud deployments differ in control, skills, and operations.",
        ]),
        ("2. Infrastructure and Responsibility", [
            "A region is a geographic deployment area; availability zones are isolated locations where offered. Compute includes virtual machines, containers, managed platforms, and functions. Object, block, and file storage have different access semantics.",
            "Cloud security is shared: providers secure parts of the service while customers remain responsible for areas such as identity, data, configuration, and applications. Use least privilege, MFA, protected secrets, encryption, logging, and tested backups.",
        ]),
        ("3. Reliability, Observability, and Cost", [
            "Design for failure using health checks, timeouts, bounded retries with jitter, redundancy where justified, and graceful degradation. Unbounded retries can amplify outages. Define service objectives and recovery goals.",
            "Metrics, logs, and traces help explain behavior. Monitor user-facing latency, errors, and availability. Cost includes compute, storage, requests, data transfer, licensing, and support; tag resources, set budgets, and review idle capacity.",
        ]),
        ("4. Common Questions", [
            "Scalability is the ability to handle growth; elasticity adjusts capacity as demand changes. A container packages an application process and dependencies but is not automatically a VM or complete security boundary. Replication copies data; sharding partitions it.",
        ]),
    ]),
]


def page_footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D5DEE5"))
    canvas.line(0.68 * inch, 0.52 * inch, letter[0] - 0.68 * inch, 0.52 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5A6B78"))
    canvas.drawString(0.68 * inch, 0.34 * inch, "CampusGPT Technical Notes")
    canvas.drawRightString(letter[0] - 0.68 * inch, 0.34 * inch, f"Page {document.page}")
    canvas.restoreState()


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="NotesTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=29, textColor=colors.HexColor("#17324D"), alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle(name="NotesSubtitle", parent=styles["Normal"], fontSize=10.5, leading=15, textColor=colors.HexColor("#46596B"), alignment=TA_CENTER, spaceAfter=18))
    styles.add(ParagraphStyle(name="NotesSection", parent=styles["Heading1"], fontSize=15, leading=19, textColor=colors.HexColor("#176B66"), spaceBefore=10, spaceAfter=6, keepWithNext=True))
    styles.add(ParagraphStyle(name="NotesBody", parent=styles["BodyText"], fontSize=9, leading=12.5, spaceAfter=6))
    styles.add(ParagraphStyle(name="NotesCode", fontName="Courier", fontSize=7.5, leading=9.5, leftIndent=8, rightIndent=8, borderColor=colors.HexColor("#D5DEE5"), borderWidth=0.5, borderPadding=7, backColor=colors.HexColor("#F3F6F8"), spaceBefore=3, spaceAfter=8))
    return styles


def create_pdf(filename, title, sections, styles):
    output = NOTES_DIR / filename
    document = SimpleDocTemplate(str(output), pagesize=letter, rightMargin=0.68 * inch, leftMargin=0.68 * inch, topMargin=0.72 * inch, bottomMargin=0.68 * inch, title=f"{title} Notes", author="CampusGPT Study Notes")
    story = [Spacer(1, 1.2 * inch), Paragraph(escape(title), styles["NotesTitle"]), Paragraph("A practical study reference with foundational concepts, examples, and common review questions.", styles["NotesSubtitle"]), PageBreak()]
    for section_title, entries in sections:
        story.append(Paragraph(escape(section_title), styles["NotesSection"]))
        for entry in entries:
            if entry.startswith("code: "):
                story.append(Preformatted(entry[6:], styles["NotesCode"]))
            else:
                story.append(Paragraph(escape(entry), styles["NotesBody"]))
    document.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return output


def main():
    NOTES_DIR.mkdir(exist_ok=True)
    styles = build_styles()
    for filename, title, sections in SUBJECTS:
        output = create_pdf(filename, title, sections, styles)
        print(f"Created {output.relative_to(Path(__file__).parent)}")
    dbms_pdf = Path(__file__).parent / "DBMS_Notes.pdf"
    shutil.copy2(dbms_pdf, NOTES_DIR / dbms_pdf.name)
    print(f"Copied DBMS_Notes.pdf to {NOTES_DIR.name}/")


if __name__ == "__main__":
    main()