"""Layer/package decomposition for the editable overview renderer.

Coordinates are absolute; parent IDs encode real native containment in draw.io.
CODE is inspected source, SPEC is documented commerce, PROPOSED is in-review.
"""
from diagram_content import box, row, link, MONO


def leaf(parent, key, x, y, w, h, title, tag, lines, kind="backend"):
    value = box(key, x, y, w, h, title, tag, [row(s, MONO if mono else "sans") for s, mono in lines], kind)
    if parent:
        value["parent"] = parent
    return value


def group(key, x, y, w, h, title, tag, parent=None, kind="application"):
    value = dict(id=key, x=x, y=y, w=w, h=h, title=title, tag=tag, kind=kind)
    if parent:
        value["parent"] = parent
    return value


ARCHITECTURE = dict(
    slug="architecture-design",
    title="Backend layers & service boundaries",
    type="Architecture",
    eyebrow="E-COMMERCE / 01 / LOGICAL LAYERS + RUNTIME COLLABORATION",
    subtitle="One backend host, decomposed into real responsibilities. CODE = source present · SPEC = documented commerce · PROPOSED = in review.",
    desc="The backend contains Presentation, Application, Domain, Infrastructure and Shared responsibilities, with separate authoritative and proposed external data services.",
    containers=[
        group("a-backend",232,160,1008,856,"One ASP.NET Core backend","CODE · e-commerce-backend COMPONENT · ONE HOST",kind="system"),
        group("a-presentation",256,208,960,152,"Presentation · Ecommerce.Api","CODE", "a-backend"),
        group("a-application",256,384,752,272,"Application · use-case coordination","CODE + PROPOSED PORTS", "a-backend", "focal"),
        group("a-domain",256,680,752,152,"Domain · business rules & inner contracts","CODE + OWNER-DIRECTED DESIGN", "a-backend"),
        group("a-infrastructure",256,840,960,160,"Infrastructure · concrete adapters","CODE + PROPOSED ADAPTERS", "a-backend"),
        group("a-shared",1032,384,184,448,"Shared","CODE · SUPPORT", "a-backend"),
        group("a-services",1264,160,280,856,"Data & external services","SEPARATE AUTHORITY / FAILURE ROLES",kind="system"),
    ],
    nodes=[
        leaf(None,"a-client",40,208,168,144,"Client roles","SPEC · NO UI CODE",[("Customer / shop member",False),("Platform administrator",False),("HTTP + Stripe.js",False)],"input"),
        leaf("a-presentation","a-controller",272,256,288,88,"Controllers","CODE",[("AuthenController",True),("HTTP → Command / Query",False)]),
        leaf("a-presentation","a-contracts",592,256,288,88,"Contracts & HTTP results","CODE",[("AuthenRequests / ResultExtensions",True),("Result → status / ProblemDetails",False)]),
        leaf("a-presentation","a-program",912,256,288,88,"Composition & security","CODE · Program.cs",[("AddCqrs + AddInfrastructure",True),("JWT authentication / authorization",False)]),
        leaf("a-application","a-inputs",272,432,224,88,"Command / Query","CODE · INPUT RECORDS",[("4 commands + GetCurrentUserQuery",True),("Register / Login / reset / me",False)]),
        leaf("a-application","a-validator",520,432,224,88,"Validator","CODE · 4 COMMAND VALIDATORS",[("Domain value-object checks",False),("Invalid → Failure; skip handler",False)]),
        leaf("a-application","a-handler",768,432,224,88,"Handler","CODE · 5 USE CASES",[("Coordinate rules / ports / TX",False),("GetCurrentUser has no validator",False)]),
        leaf("a-application","a-mapping",272,548,224,92,"Mapping & responses","CODE",[("AuthenMappings",True),("Domain → response records",False),("Domain entities stay inside core",False)]),
        leaf("a-application","a-ports",520,548,472,92,"Application ports","CODE + PROPOSED",[("CODE: unit of work / hash / token / email",False),("PROPOSED: cache / rate / config snapshot ports",False),("PROPOSED: event / projection delivery contracts",False)]),
        leaf("a-domain","a-entities",272,728,172,96,"Entities","CODE",[("User / PasswordResetToken",True),("Register / sign-in / consume",False)]),
        leaf("a-domain","a-values",456,728,172,96,"Value objects","CODE",[("Username / EmailAddress",True),("PlainPassword / identity primitives",True)]),
        leaf("a-domain","a-repositories",640,728,172,96,"Repository contracts","CODE",[("IUser / IPassword / IToken",True),("No HTTP, SQL or provider SDK",False)]),
        leaf("a-domain","a-business",824,728,172,96,"Domain","PROPOSED · OWNER REQUEST",[("Reusable business rules",False),("e.g. tax calculation",False),("No I/O or use-case flow",False)],"optional"),
        leaf("a-infrastructure","a-security",272,888,220,96,"Security","CODE",[("PBKDF2 / JWT / FieldProtector",True),("Implements inner security ports",False)]),
        leaf("a-infrastructure","a-provider",508,888,220,96,"Email / payment","CODE + SPEC",[("CODE: LoggingEmailSender (dev)",True),("SPEC: Stripe intent / refund",False)]),
        leaf("a-infrastructure","a-data-adapters",744,888,220,96,"Data adapters","PROPOSED",[("Redis cache / rate adapters",False),("Mongo config / event adapters",False)],"optional"),
        leaf("a-infrastructure","a-persistence",980,888,220,96,"Persistence","CODE",[("Dapper / Npgsql / DbSession",True),("Repositories + UnitOfWork",True)]),
        leaf("a-shared","a-dispatcher",1048,432,152,152,"CQRS dispatcher","CODE",[("Messaging / Dispatcher",True),("Validate, then handle",False),("DI assembly scanning",False)]),
        leaf("a-shared","a-result",1048,608,152,112,"Results","CODE",[("Result / Error",True),("Expected failures",False),("Result.Failure errors",True)]),
        leaf("a-services","a-postgres",1280,208,248,104,"PostgreSQL","CODE ADAPTERS + SPEC",[("Business / account authority",False),("Order / payment / stock / budget",False),("SQL constraints, locks, transaction",False)],"store"),
        leaf("a-services","a-mongo",1280,328,248,144,"MongoDB","PROPOSED",[("Non-secret config source",False),("Audit / event / status projections",False),("Derived copies never settle money",False)],"optional"),
        leaf("a-services","a-cache",1280,488,248,112,"Redis · public cache","PROPOSED · REBUILDABLE",[("Public descriptors; live values SQL",False),("Cache-aside / after-commit invalidate",False),("Separate allkeys-lfu memory domain",True)],"optional"),
        leaf("a-services","a-rate",1280,616,248,112,"Redis · shared admission","PROPOSED · ISOLATED",[("Atomic token buckets; noeviction",True),("Quota 429 / protected outage 503",False),("Signed webhook bypasses user quota",False)],"optional"),
        leaf("a-services","a-stripe",1280,744,248,112,"Stripe","SPEC · EXTERNAL",[("PaymentIntent / whole refund",True),("Stripe.js keeps card data at provider",False),("Signed webhook is payment truth",False)],"optional"),
    ],
    edges=[
        link("a-client","a-controller",[(208,280),(272,280)],color="link"),
        link("a-controller","a-inputs",[(384,344),(384,432)]),
        link("a-dispatcher","a-validator",[(1120,584),(1120,596),(1020,596),(1020,536),(632,536),(632,520)]),
        link("a-dispatcher","a-handler",[(1048,480),(992,480)]),
        link("a-persistence","a-postgres",[(1200,936),(1248,936),(1248,264),(1280,264)]),
    ],
    notes=[
        (40,408,"Read the boundaries",12,"heading"),
        (40,436,"Containment = responsibility.",10,"body"),
        (40,456,"Arrows = selected runtime calls.",10,"body"),
        (40,476,"No compile-reference arrows.",10,"body"),
        (40,528,"CODE is Authen baseline.",10,"body"),
        (40,548,"Commerce handlers are SPEC.",10,"body"),
        (40,568,"No carrier, broker or gateway",10,"body"),
        (40,588,"is established by the sources.",10,"body"),
        (40,656,"DI selects implementations.",10,"body"),
        (40,676,"Layers are not separate services.",10,"body"),
        (40,736,"Expiry / 7-day completion:",10,"body"),
        (40,756,"SPEC; worker host unresolved.",10,"body"),
        (1280,900,"PROPOSED: SQL outbox → Mongo relay",10,"body"),
        (1280,920,"Business + intent commit in SQL.",10,"body"),
        (1280,940,"Replay uses stable ID + source version.",10,"body"),
        (1280,960,"No shared transaction; retention TBD.",10,"body"),
        (1280,980,"Worker hosting remains undecided.",10,"body"),
    ],
    source="CODE: e-commerce-backend@d8255183cba54d0c2b218607456b895a70df32f0 · Program.cs / Dispatcher.cs / DI | SPEC: commerce docs | PROPOSED: Redis / Mongo designs",
    legend=[("box","CODE responsibility"),("focal","Application coordination"),("store","PostgreSQL authority"),("optional","SPEC / PROPOSED; read tag"),("arrow","Selected runtime call"),("text","Containment = logical ownership")],
)


REPOSITORY = dict(
    slug="repository-architecture",
    title="Source packages & responsibility map",
    type="Nested",
    eyebrow="E-COMMERCE / 02 / PHYSICAL CODE OWNERSHIP",
    subtitle="Native folders → use-case files and role summaries. Five production projects, two test projects; direct REF lines account for all 9 + 5 references.",
    desc="The independently versioned backend Component Repository contains source projects, tests, shared build files and its own guides, with project references recorded as text.",
    containers=[
        group("r-root",40,160,1504,856,"e-commerce/repository/e-commerce-backend/","COMPONENT REPOSITORY · github.com/ittikornsopawan/e-commerce-backend · PIN d8255183cba54d0c2b218607456b895a70df32f0",kind="system"),
        group("r-src",64,208,1112,784,"src/","5 PRODUCTION .csproj", "r-root", "folder"),
        group("r-api",88,256,520,208,"Ecommerce.Api/","CODE · HTTP + COMPOSITION", "r-src"),
        group("r-app",632,256,520,352,"Ecommerce.Application/","CODE · FEATURE / USE CASE", "r-src", "focal"),
        group("r-feature",648,304,488,152,"Features/Authen/","CODE · ROLE SUMMARIES ACROSS USE-CASE FOLDERS", "r-app"),
        group("r-domain",88,488,520,272,"Ecommerce.Domain/","CODE + OWNER-DIRECTED DOMAIN/ PATH", "r-src"),
        group("r-infra",632,632,520,336,"Ecommerce.Infrastructure/","CODE + PROPOSED ADAPTERS", "r-src"),
        group("r-shared",88,784,520,184,"Ecommerce.Shared/","CODE · COMMON PRIMITIVES", "r-src"),
        group("r-tests",1200,208,320,384,"tests/","2 xUnit .csproj", "r-root", "folder"),
        group("r-domain-tests",1216,256,288,152,"Ecommerce.Domain.Tests/","CODE", "r-tests"),
        group("r-app-tests",1216,424,288,152,"Ecommerce.Application.Tests/","CODE", "r-tests"),
        group("r-build",1200,616,320,176,"Component root files","CODE · SOLUTION / SHARED BUILD", "r-root", "folder"),
        group("r-evidence",1200,816,320,176,"Component guides","CODE BASELINE · KNOWN SPEC GAPS", "r-root", "folder"),
    ],
    nodes=[
        leaf("r-api","r-http",104,304,232,144,"Controllers / Contracts","CODE",[("AuthenController / AuthenRequests",True),("Build command/query from HTTP",False),("REF: Application + Shared",True)]),
        leaf("r-api","r-composition",352,304,240,144,"Program / Extensions","CODE",[("DI / JWT / ResultExtensions",True),("REF: Infrastructure",True),("PROPOSED: quota middleware",False)]),
        leaf("r-feature","r-input",664,352,136,88,"Command / Query","CODE · FILE ROLES",[("4 cmds + 1 query",False),("Use-case files",False)]),
        leaf("r-feature","r-validators",824,352,136,88,"Validators","CODE · FILE ROLES",[("4 validators",False),("Commands; no /me",False)]),
        leaf("r-feature","r-handlers",984,352,136,88,"Handlers","CODE · FILE ROLES",[("5 handlers",False),("Use-case files",False)]),
        leaf("r-app","r-map",648,480,224,112,"Mapping / responses","CODE · Features/Authen/",[("Mapping/AuthenMappings",True),("Response records in use cases",False),("Domain → response records",False)]),
        leaf("r-app","r-abstractions",888,480,248,112,"Abstractions / Common","CODE + PROPOSED PORTS",[("UnitOfWork / hash / token / email",False),("REF: Domain + Shared",True),("PROPOSED: cache/rate/config/events",False)]),
        leaf("r-domain","r-entities",104,536,232,88,"Authen/Entities/","CODE",[("User / PasswordResetToken",True),("Common: Entity / IAggregateRoot",True)]),
        leaf("r-domain","r-value",352,536,240,88,"Authen/ValueObjects/","CODE",[("Username / EmailAddress",True),("PlainPassword / credentials",True)]),
        leaf("r-domain","r-business",104,640,232,112,"Authen/Domain/","PROPOSED · OWNER REQUEST",[("Reusable Authen business rules",False),("No implementation at pinned SHA",False)],"optional"),
        leaf("r-domain","r-repos",352,640,240,112,"Repositories / Common","CODE · Authen/Repositories/",[("IAuthenRepositories",True),("IUser / IPassword / IToken",True),("Result/Error; domain errors",False),("Duplicate key; REF: Shared",False)]),
        leaf("r-infra","r-persistence",648,680,224,112,"Persistence/","CODE",[("Authen: User / Password / Token",True),("DbSession / UnitOfWork",True),("Dapper / Npgsql",True)]),
        leaf("r-infra","r-security",888,680,248,112,"Security/","CODE",[("Pbkdf2PasswordHasher / TokenService",True),("FieldProtector",True),("JWT / opaque tokens / field crypto",False)]),
        leaf("r-infra","r-options",648,808,224,136,"Email/ · Options/ · DI","CODE",[("LoggingEmailSender is dev-only",False),("Database / Jwt / Security options",True),("REF: Application, Domain, Shared",True)]),
        leaf("r-infra","r-proposed",888,808,248,144,"Proposed source seams","PROPOSED · FILES ABSENT",[("Caching/ + RateLimiting/ (Redis)",True),("Configuration/ + Documents/ (Mongo)",True),("Client/options registration; relay TBD",False)],"optional"),
        leaf("r-shared","r-cqrs",104,832,232,112,"Cqrs/","CODE",[("Messaging / Dispatcher / registration",True),("Validators run before handler",False),("Assembly scanning; no broker",False)]),
        leaf("r-shared","r-results",352,832,240,112,"Results/","CODE",[("Result / Result<T> / Error",True),("Expected failure values",False),("REF: none",True)]),
        leaf("r-domain-tests","r-domain-suite",1232,304,256,88,"Authen model tests","CODE",[("EntityTests / ValueObjectTests",True),("REF: Domain + Shared (2)",True)]),
        leaf("r-app-tests","r-app-suite",1232,472,256,88,"Handler / dispatcher tests","CODE",[("AuthenHandlerTests / Fakes",True),("REF: Application, Domain, Shared (3)",True)]),
        leaf("r-build","r-settings",1216,664,288,112,"Build & entry documents","CODE",[("Ecommerce.sln / net10.0",True),("Directory.Build.props: warnings=errors",True),("README / project-structure; dotnet test",True)]),
        leaf("r-evidence","r-analysis",1216,864,288,112,"Backend guidance","COMPONENT-OWNED DOCS",[("README.md / project-structure.md",True),("code.md: legacy implementation gaps",True),("Showcase owns REPOS.md + specs",False)],"folder"),
    ],
    edges=[],
    notes=[],
    source="Manifest: e-commerce/REPOS.md | Component: https://github.com/ittikornsopawan/e-commerce-backend · PIN d8255183cba54d0c2b218607456b895a70df32f0 | 9 source + 5 test refs",
    legend=[("box","CODE source responsibility"),("focal","Application use-case package"),("optional","PROPOSED path; file absent"),("text","REF = direct project reference"),("text","9 production + 5 test references"),("text","Containers = paths; leaves = roles")],
)

CORE = [ARCHITECTURE, REPOSITORY]
