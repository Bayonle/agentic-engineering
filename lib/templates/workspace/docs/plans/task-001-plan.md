# Technical Implementation Plan: JWT Authentication for TodoApi

**Task ID:** task-001
**Priority:** P1
**Architect:** architect
**Created:** 2026-02-02
**Status:** Ready for Approval

---

## Executive Summary

This plan implements JWT-based authentication for TodoApi using ASP.NET Core Identity. The good news: infrastructure is already in place (Identity, JWT Bearer, DbContext configured). We only need to build the authentication endpoints and supporting services.

**Approach:** RESTful API controllers with service layer for JWT token generation
**Complexity:** Medium (3-4 implementation tasks)
**Timeline:** 4-6 hours implementation + 2-3 hours testing
**Risk Level:** Low (using battle-tested ASP.NET Core Identity)

---

## 1. Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client                               │
│  (Postman, Frontend, Mobile App)                             │
└───────────────┬──────────────────────────────────────────────┘
                │
                │ HTTP/HTTPS
                ▼
┌─────────────────────────────────────────────────────────────┐
│              ASP.NET Core Middleware Pipeline                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. HTTPS Redirection                                │   │
│  │  2. Authentication (JWT Bearer)                       │   │
│  │  3. Authorization                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────┬──────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                    AuthController                            │
│  ┌────────────────────┐  ┌────────────────────┐             │
│  │  POST /api/auth/   │  │  POST /api/auth/   │             │
│  │      register      │  │      login         │             │
│  └────────┬───────────┘  └────────┬───────────┘             │
└───────────┼──────────────────────┼─────────────────────────┘
            │                      │
            ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      IAuthService                            │
│  ┌────────────────────────────────────────────────────┐     │
│  │  - RegisterUserAsync(email, password)              │     │
│  │  - LoginUserAsync(email, password)                 │     │
│  │  - GenerateJwtToken(user)                          │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────┬──────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│               ASP.NET Core Identity                          │
│  ┌────────────────────────────────────────────────────┐     │
│  │  UserManager<IdentityUser>                         │     │
│  │  SignInManager<IdentityUser>                       │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────┬──────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│            ApplicationDbContext (EF Core)                    │
│  ┌────────────────────────────────────────────────────┐     │
│  │  AspNetUsers                                       │     │
│  │  AspNetRoles                                       │     │
│  │  AspNetUserRoles                                   │     │
│  │  ... (other Identity tables)                       │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────┬──────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                   SQLite Database                            │
│                    (todoapi.db)                              │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**AuthController** - HTTP layer
- Receives and validates HTTP requests
- Maps DTOs to service calls
- Returns appropriate HTTP status codes
- Handles request-level errors

**IAuthService / AuthService** - Business logic layer
- Orchestrates registration and login workflows
- Generates JWT tokens
- Interacts with Identity UserManager and SignInManager
- Implements security logic

**DTOs (Data Transfer Objects)** - Contract layer
- Define request/response shapes
- Apply validation attributes
- Shield internal models from external APIs

**Identity** - Data access layer
- User management (CRUD operations)
- Password hashing and verification
- Security stamp management
- Built-in by ASP.NET Core

**ApplicationDbContext** - Persistence layer
- Entity Framework Core DbContext
- Identity table mappings (AspNetUsers, etc.)
- Already configured with SQLite

---

## 2. Key Design Decisions

### Decision 1: Controller-Based vs Minimal API

**Choice:** Use Controller-based approach with `[ApiController]` attribute

**Rationale:**
- Better organization for authentication logic
- Built-in model validation via `[ApiController]`
- Easier to apply attributes for documentation (Swagger)
- Standard pattern that most .NET developers expect
- More maintainable as API grows

**Trade-off:** Slightly more boilerplate than Minimal API, but we gain type safety and structure

**Alternative Considered:** Minimal API (like the WeatherForecast endpoint) - Rejected because authentication logic deserves proper structure and validation

---

### Decision 2: Service Layer Pattern

**Choice:** Create `IAuthService` interface with `AuthService` implementation

**Rationale:**
- Separation of concerns: HTTP logic stays in controller, business logic in service
- Easier to unit test (can mock IAuthService)
- Reusable token generation logic
- Follows SOLID principles (Single Responsibility, Dependency Inversion)
- Standard enterprise pattern

**Trade-off:** Extra abstraction layer adds one more file, but we gain testability and maintainability

**Alternative Considered:** Put all logic in controller - Rejected because it violates SRP and makes testing harder

---

### Decision 3: DTO Pattern for Requests/Responses

**Choice:** Create separate DTO classes for register/login requests and responses

**Rationale:**
- Never expose Identity's `IdentityUser` directly to API consumers
- Apply data annotations for validation (`[Required]`, `[EmailAddress]`, etc.)
- Control exactly what data flows in and out
- API versioning flexibility (can change DTOs without changing domain models)
- Security: prevent mass assignment vulnerabilities

**Trade-off:** More classes to maintain, but we gain security and API contract stability

**Alternative Considered:** Use IdentityUser directly - Rejected due to security concerns and tight coupling

---

### Decision 4: Symmetric Key (HS256) for JWT Signing

**Choice:** Use HMAC-SHA256 (HS256) with a symmetric secret key

**Rationale:**
- Simple to configure (single secret key)
- Adequate for single-server MVP
- Fast token generation and validation
- Already configured in Program.cs
- Industry standard for internal APIs

**Trade-off:** All servers need the same secret (not ideal for multi-server), but we're single-server

**Alternative Considered:** Asymmetric keys (RS256) - Deferred to when we scale to multiple services

---

### Decision 5: SQLite for MVP

**Choice:** Continue using SQLite (already configured)

**Rationale:**
- Zero configuration required
- File-based database (todoapi.db) - easy backups
- Perfect for development and small deployments
- Entity Framework makes migration to PostgreSQL trivial later
- Supports all Identity features we need

**Trade-off:** Not ideal for high concurrency (>100 concurrent users), but acceptable for MVP

**Alternative Considered:** PostgreSQL - Overkill for MVP, adds deployment complexity

---

### Decision 6: No Refresh Tokens in V1

**Choice:** Defer refresh token implementation to V2

**Rationale:**
- PRD marks refresh tokens as "P2 Could Have"
- Keeps MVP simple and focused
- 15-minute expiration is acceptable for initial release
- Can add later without breaking existing endpoints
- Users can simply re-login

**Trade-off:** Slightly worse UX (re-login every 15 min), but we ship faster

**Alternative Considered:** Implement refresh tokens now - Rejected to reduce scope and complexity

---

## 3. API Design

### 3.1 POST /api/auth/register

**Purpose:** Create a new user account

**Request:**
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response (201 Created):**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "message": "User registered successfully"
}
```

**Error Response (400 Bad Request - Validation):**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "errors": {
    "Email": ["The Email field is required.", "The Email field is not a valid e-mail address."],
    "Password": ["The Password field is required.", "Password must be at least 8 characters long."]
  }
}
```

**Error Response (409 Conflict - Duplicate Email):**
```http
HTTP/1.1 409 Conflict
Content-Type: application/json

{
  "message": "User with this email already exists"
}
```

**Validation Rules:**
- Email: Required, valid email format, unique (case-insensitive)
- Password: Required, 8+ chars, uppercase, lowercase, digit

---

### 3.2 POST /api/auth/login

**Purpose:** Authenticate user and return JWT token

**Request:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response (200 OK):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJqdGkiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3Mzg1MDU3MDAsImlhdCI6MTczODUwNDgwMCwiaXNzIjoiVG9kb0FwaSIsImF1ZCI6IlRvZG9BcGkifQ.signature",
  "expiresAt": "2026-02-02T13:15:00Z"
}
```

**Error Response (401 Unauthorized):**
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "message": "Invalid email or password"
}
```

**Error Response (400 Bad Request - Validation):**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "errors": {
    "Email": ["The Email field is required."],
    "Password": ["The Password field is required."]
  }
}
```

**Validation Rules:**
- Email: Required
- Password: Required

---

### 3.3 GET /weatherforecast (Protected Endpoint)

**Purpose:** Example protected endpoint (already exists, just test it works with JWT)

**Request:**
```http
GET /weatherforecast
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "date": "2026-02-03",
    "temperatureC": 15,
    "temperatureF": 59,
    "summary": "Mild"
  }
]
```

**Error Response (401 Unauthorized - No Token):**
```http
HTTP/1.1 401 Unauthorized
```

**Error Response (401 Unauthorized - Invalid/Expired Token):**
```http
HTTP/1.1 401 Unauthorized
```

---

## 4. Data Models

### 4.1 Database Schema

**Good news:** ASP.NET Core Identity provides all tables we need. No custom schema required.

**Identity Tables (Auto-Generated by EF Migration):**

```sql
-- AspNetUsers: Core user table
CREATE TABLE AspNetUsers (
    Id TEXT PRIMARY KEY,
    UserName TEXT,
    NormalizedUserName TEXT UNIQUE,
    Email TEXT,
    NormalizedEmail TEXT UNIQUE,
    EmailConfirmed INTEGER,
    PasswordHash TEXT,
    SecurityStamp TEXT,
    ConcurrencyStamp TEXT,
    PhoneNumber TEXT,
    PhoneNumberConfirmed INTEGER,
    TwoFactorEnabled INTEGER,
    LockoutEnd TEXT,
    LockoutEnabled INTEGER,
    AccessFailedCount INTEGER
);

-- AspNetRoles: Roles (not used in MVP, but created by Identity)
CREATE TABLE AspNetRoles (
    Id TEXT PRIMARY KEY,
    Name TEXT,
    NormalizedName TEXT UNIQUE,
    ConcurrencyStamp TEXT
);

-- AspNetUserRoles: User-Role mapping
CREATE TABLE AspNetUserRoles (
    UserId TEXT NOT NULL,
    RoleId TEXT NOT NULL,
    PRIMARY KEY (UserId, RoleId),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id),
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id)
);

-- Additional Identity tables: AspNetUserClaims, AspNetUserLogins, AspNetUserTokens, AspNetRoleClaims
```

**Key Points:**
- We use default `IdentityUser` (no custom fields needed for MVP)
- Email is indexed and unique (case-insensitive via NormalizedEmail)
- PasswordHash uses PBKDF2 with HMAC-SHA256, 10,000 iterations
- SecurityStamp invalidates tokens when password changes

---

### 4.2 DTOs (Data Transfer Objects)

**RegisterRequest.cs:**
```csharp
namespace TodoApi.Models.DTOs;

using System.ComponentModel.DataAnnotations;

public class RegisterRequest
{
    [Required(ErrorMessage = "Email is required")]
    [EmailAddress(ErrorMessage = "Email format is invalid")]
    [MaxLength(256, ErrorMessage = "Email cannot exceed 256 characters")]
    public string Email { get; set; } = string.Empty;

    [Required(ErrorMessage = "Password is required")]
    [MinLength(8, ErrorMessage = "Password must be at least 8 characters")]
    [MaxLength(128, ErrorMessage = "Password cannot exceed 128 characters")]
    public string Password { get; set; } = string.Empty;
}
```

**LoginRequest.cs:**
```csharp
namespace TodoApi.Models.DTOs;

using System.ComponentModel.DataAnnotations;

public class LoginRequest
{
    [Required(ErrorMessage = "Email is required")]
    [EmailAddress(ErrorMessage = "Email format is invalid")]
    public string Email { get; set; } = string.Empty;

    [Required(ErrorMessage = "Password is required")]
    public string Password { get; set; } = string.Empty;
}
```

**LoginResponse.cs:**
```csharp
namespace TodoApi.Models.DTOs;

public class LoginResponse
{
    public string Token { get; set; } = string.Empty;
    public DateTime ExpiresAt { get; set; }
}
```

**ErrorResponse.cs:**
```csharp
namespace TodoApi.Models.DTOs;

public class ErrorResponse
{
    public string? Message { get; set; }
    public Dictionary<string, string[]>? Errors { get; set; }
}
```

---

## 5. Component Structure

### 5.1 File Organization

```
TodoApi/
├── Controllers/
│   └── AuthController.cs          # NEW: Registration & login endpoints
├── Services/
│   ├── IAuthService.cs            # NEW: Auth service interface
│   └── AuthService.cs             # NEW: JWT token generation
├── Models/
│   └── DTOs/
│       ├── RegisterRequest.cs     # NEW: Registration request
│       ├── LoginRequest.cs        # NEW: Login request
│       ├── LoginResponse.cs       # NEW: Login response with token
│       └── ErrorResponse.cs       # NEW: Standardized error response
├── Data/
│   └── ApplicationDbContext.cs    # EXISTS: No changes needed
├── Configuration/
│   └── JwtSettings.cs             # EXISTS: No changes needed
├── Migrations/
│   └── [timestamp]_InitialCreate.cs # NEW: EF Core migration for Identity tables
├── Program.cs                     # EXISTS: Add AuthService registration
├── appsettings.json               # EXISTS: JWT SecretKey via User Secrets
├── TodoApi.csproj                 # EXISTS: All packages already installed
└── todoapi.db                     # NEW: SQLite database file (created by migration)
```

---

### 5.2 IAuthService Interface

```csharp
namespace TodoApi.Services;

using TodoApi.Models.DTOs;

public interface IAuthService
{
    /// <summary>
    /// Registers a new user with the provided email and password.
    /// </summary>
    /// <param name="email">User's email address</param>
    /// <param name="password">User's password</param>
    /// <returns>
    /// Success: (true, null)
    /// Failure: (false, error message)
    /// </returns>
    Task<(bool Succeeded, string? ErrorMessage)> RegisterUserAsync(string email, string password);

    /// <summary>
    /// Authenticates a user and generates a JWT token.
    /// </summary>
    /// <param name="email">User's email address</param>
    /// <param name="password">User's password</param>
    /// <returns>
    /// Success: (LoginResponse with token, null)
    /// Failure: (null, error message)
    /// </returns>
    Task<(LoginResponse? Response, string? ErrorMessage)> LoginUserAsync(string email, string password);
}
```

---

### 5.3 AuthService Implementation

```csharp
namespace TodoApi.Services;

using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using TodoApi.Configuration;
using TodoApi.Models.DTOs;

public class AuthService : IAuthService
{
    private readonly UserManager<IdentityUser> _userManager;
    private readonly SignInManager<IdentityUser> _signInManager;
    private readonly JwtSettings _jwtSettings;

    public AuthService(
        UserManager<IdentityUser> userManager,
        SignInManager<IdentityUser> signInManager,
        IOptions<JwtSettings> jwtSettings)
    {
        _userManager = userManager;
        _signInManager = signInManager;
        _jwtSettings = jwtSettings.Value;
    }

    public async Task<(bool Succeeded, string? ErrorMessage)> RegisterUserAsync(string email, string password)
    {
        // Check if user already exists (case-insensitive)
        var existingUser = await _userManager.FindByEmailAsync(email);
        if (existingUser != null)
        {
            return (false, "User with this email already exists");
        }

        // Create new user
        var user = new IdentityUser
        {
            UserName = email,
            Email = email
        };

        var result = await _userManager.CreateAsync(user, password);

        if (result.Succeeded)
        {
            return (true, null);
        }

        // Aggregate Identity errors into a single message
        var errors = string.Join("; ", result.Errors.Select(e => e.Description));
        return (false, errors);
    }

    public async Task<(LoginResponse? Response, string? ErrorMessage)> LoginUserAsync(string email, string password)
    {
        // Find user by email
        var user = await _userManager.FindByEmailAsync(email);
        if (user == null)
        {
            return (null, "Invalid email or password");
        }

        // Verify password
        var result = await _signInManager.CheckPasswordSignInAsync(user, password, lockoutOnFailure: false);
        if (!result.Succeeded)
        {
            return (null, "Invalid email or password");
        }

        // Generate JWT token
        var token = GenerateJwtToken(user);
        var expiresAt = DateTime.UtcNow.AddMinutes(_jwtSettings.ExpirationMinutes);

        var response = new LoginResponse
        {
            Token = token,
            ExpiresAt = expiresAt
        };

        return (response, null);
    }

    private string GenerateJwtToken(IdentityUser user)
    {
        var claims = new List<Claim>
        {
            new Claim(JwtRegisteredClaimNames.Sub, user.Id),
            new Claim(JwtRegisteredClaimNames.Email, user.Email!),
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new Claim(JwtRegisteredClaimNames.Iat, DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString(), ClaimValueTypes.Integer64)
        };

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_jwtSettings.SecretKey));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: _jwtSettings.Issuer,
            audience: _jwtSettings.Audience,
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(_jwtSettings.ExpirationMinutes),
            signingCredentials: credentials
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
```

**Key Implementation Notes:**
- `CheckPasswordSignInAsync` verifies password without signing the user in (no cookie needed)
- JWT token includes standard claims: sub, email, jti, iat (per PRD)
- Token expiration uses configured `ExpirationMinutes` (15 minutes)
- Error messages are user-friendly without leaking implementation details
- Uses async/await throughout for scalability

---

### 5.4 AuthController

```csharp
namespace TodoApi.Controllers;

using Microsoft.AspNetCore.Mvc;
using TodoApi.Models.DTOs;
using TodoApi.Services;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly IAuthService _authService;
    private readonly ILogger<AuthController> _logger;

    public AuthController(IAuthService authService, ILogger<AuthController> logger)
    {
        _authService = authService;
        _logger = logger;
    }

    /// <summary>
    /// Registers a new user account.
    /// </summary>
    /// <param name="request">Registration details (email and password)</param>
    /// <returns>201 Created on success, 400/409 on failure</returns>
    [HttpPost("register")]
    [ProducesResponseType(StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status409Conflict)]
    public async Task<IActionResult> Register([FromBody] RegisterRequest request)
    {
        // Model validation happens automatically via [ApiController]
        if (!ModelState.IsValid)
        {
            var errors = ModelState
                .Where(x => x.Value?.Errors.Count > 0)
                .ToDictionary(
                    kvp => kvp.Key,
                    kvp => kvp.Value!.Errors.Select(e => e.ErrorMessage).ToArray()
                );

            return BadRequest(new ErrorResponse { Errors = errors });
        }

        var (succeeded, errorMessage) = await _authService.RegisterUserAsync(request.Email, request.Password);

        if (succeeded)
        {
            _logger.LogInformation("User registered successfully: {Email}", request.Email);
            return CreatedAtAction(nameof(Register), new { message = "User registered successfully" });
        }

        // Check if duplicate email
        if (errorMessage?.Contains("already exists") == true)
        {
            _logger.LogWarning("Registration failed - duplicate email: {Email}", request.Email);
            return Conflict(new ErrorResponse { Message = errorMessage });
        }

        // Other validation errors (password complexity, etc.)
        _logger.LogWarning("Registration failed: {Error}", errorMessage);
        return BadRequest(new ErrorResponse { Message = errorMessage });
    }

    /// <summary>
    /// Authenticates a user and returns a JWT token.
    /// </summary>
    /// <param name="request">Login credentials (email and password)</param>
    /// <returns>200 OK with token on success, 401 on failure</returns>
    [HttpPost("login")]
    [ProducesResponseType(typeof(LoginResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        // Model validation happens automatically via [ApiController]
        if (!ModelState.IsValid)
        {
            var errors = ModelState
                .Where(x => x.Value?.Errors.Count > 0)
                .ToDictionary(
                    kvp => kvp.Key,
                    kvp => kvp.Value!.Errors.Select(e => e.ErrorMessage).ToArray()
                );

            return BadRequest(new ErrorResponse { Errors = errors });
        }

        var (response, errorMessage) = await _authService.LoginUserAsync(request.Email, request.Password);

        if (response != null)
        {
            _logger.LogInformation("User logged in successfully: {Email}", request.Email);
            return Ok(response);
        }

        _logger.LogWarning("Login failed for email: {Email}", request.Email);
        return Unauthorized(new ErrorResponse { Message = errorMessage });
    }
}
```

**Key Implementation Notes:**
- `[ApiController]` provides automatic model validation
- Logging for security audit trail (success/failure) without logging passwords
- Proper HTTP status codes: 201 Created, 400 Bad Request, 401 Unauthorized, 409 Conflict
- OpenAPI attributes for Swagger documentation
- Error responses use standardized `ErrorResponse` DTO

---

### 5.5 Program.cs Changes

**Add AuthService registration to DI container:**

```csharp
// Add this line after builder.Services.AddAuthorization();
builder.Services.AddScoped<IAuthService, AuthService>();

// Also add controllers (if not already present)
builder.Services.AddControllers();

// And map controllers after app.UseAuthorization();
app.MapControllers();
```

**Complete Program.cs snippet showing changes:**

```csharp
// ... existing code ...

builder.Services.AddAuthorization();

// NEW: Register AuthService
builder.Services.AddScoped<IAuthService, AuthService>();

// NEW: Register controllers
builder.Services.AddControllers();

var app = builder.Build();

// ... existing middleware ...

app.UseAuthentication();
app.UseAuthorization();

// ... existing WeatherForecast endpoint ...

// NEW: Map controllers
app.MapControllers();

app.Run();
```

---

## 6. Security Considerations

### 6.1 Password Security

**Already Implemented:**
- ASP.NET Core Identity uses PBKDF2 with HMAC-SHA256
- 10,000 iterations (default, secure for current standards)
- Unique salt per password
- Complexity requirements configured in Program.cs

**Additional Measures:**
- MaxLength validation (128 chars) to prevent DoS attacks
- Password not logged anywhere
- Password not returned in any API response

---

### 6.2 JWT Secret Key Protection

**Configuration Strategy:**

**Development:**
```bash
# Store in User Secrets (never in source control)
dotnet user-secrets set "Jwt:SecretKey" "your-super-secret-key-at-least-32-characters-long-for-hs256"
```

**Production:**
- Use environment variables or Azure Key Vault
- Minimum 32 characters (256 bits for HS256)
- Rotate periodically (every 90 days recommended)

**Security Checklist:**
- [ ] Never commit SecretKey to source control
- [ ] .gitignore includes appsettings.Development.json and secrets.json
- [ ] User Secrets configured (already has UserSecretsId in .csproj)
- [ ] Production uses secure configuration provider

---

### 6.3 Input Validation

**Defense in Depth:**

**Layer 1: Data Annotations** (DTOs)
- `[Required]`, `[EmailAddress]`, `[MinLength]`, `[MaxLength]`
- Automatic validation via `[ApiController]`

**Layer 2: Identity Validation**
- UserManager enforces email uniqueness
- Password complexity requirements
- Email format validation

**Layer 3: Entity Framework**
- Parameterized queries (prevents SQL injection)
- Type safety

**Layer 4: JWT Middleware**
- Token signature validation
- Expiration check (no clock skew)
- Issuer and audience validation

---

### 6.4 HTTPS Enforcement

**Already Implemented:**
- `app.UseHttpsRedirection()` in Program.cs
- Redirects HTTP to HTTPS automatically

**Production Checklist:**
- [ ] Valid SSL/TLS certificate
- [ ] HSTS (HTTP Strict Transport Security) header
- [ ] Disable HTTP endpoint entirely

---

### 6.5 Rate Limiting (Future Enhancement)

**Not Implemented in MVP** - Documented for V2

**Recommendation:**
- Use ASP.NET Core 7+ built-in rate limiting middleware
- Limit login attempts: 5 requests per minute per IP
- Limit registration: 3 requests per hour per IP
- Prevents brute force and enumeration attacks

---

### 6.6 Security Headers (Future Enhancement)

**Not Implemented in MVP** - Documented for V2

**Recommendation:**
```csharp
// Add security headers middleware
app.Use(async (context, next) =>
{
    context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Add("X-Frame-Options", "DENY");
    context.Response.Headers.Add("X-XSS-Protection", "1; mode=block");
    context.Response.Headers.Add("Referrer-Policy", "no-referrer");
    await next();
});
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

**Test Project:** `TodoApi.Tests` (to be created)

**AuthService Tests:**
```csharp
[Fact]
public async Task RegisterUserAsync_WithValidData_ReturnsSuccess()
{
    // Arrange: Mock UserManager
    // Act: Call RegisterUserAsync
    // Assert: Succeeded = true
}

[Fact]
public async Task RegisterUserAsync_WithDuplicateEmail_ReturnsError()
{
    // Arrange: Mock UserManager to return existing user
    // Act: Call RegisterUserAsync
    // Assert: Succeeded = false, ErrorMessage contains "already exists"
}

[Fact]
public async Task LoginUserAsync_WithValidCredentials_ReturnsToken()
{
    // Arrange: Mock UserManager and SignInManager
    // Act: Call LoginUserAsync
    // Assert: Response not null, Token not empty
}

[Fact]
public async Task LoginUserAsync_WithInvalidPassword_ReturnsError()
{
    // Arrange: Mock CheckPasswordSignInAsync to return failure
    // Act: Call LoginUserAsync
    // Assert: Response = null, ErrorMessage = "Invalid email or password"
}

[Fact]
public void GenerateJwtToken_CreatesValidToken()
{
    // Arrange: Create test user
    // Act: Call GenerateJwtToken (via reflection or public wrapper)
    // Assert: Token can be parsed, contains correct claims
}
```

**Coverage Target:** 80% for AuthService

---

### 7.2 Integration Tests

**Test Project:** `TodoApi.IntegrationTests` (to be created)

**AuthController Tests:**
```csharp
[Fact]
public async Task Register_WithValidData_Returns201Created()
{
    // Arrange: Create test client with in-memory database
    var client = _factory.CreateClient();
    var request = new RegisterRequest { Email = "test@example.com", Password = "Test123!" };

    // Act
    var response = await client.PostAsJsonAsync("/api/auth/register", request);

    // Assert
    Assert.Equal(HttpStatusCode.Created, response.StatusCode);
}

[Fact]
public async Task Register_WithDuplicateEmail_Returns409Conflict()
{
    // Arrange: Register user first
    // Act: Try to register same email again
    // Assert: 409 Conflict
}

[Fact]
public async Task Login_WithValidCredentials_Returns200WithToken()
{
    // Arrange: Register user first
    // Act: Login with same credentials
    // Assert: 200 OK, response contains token and expiresAt
}

[Fact]
public async Task Login_WithInvalidPassword_Returns401Unauthorized()
{
    // Arrange: Register user
    // Act: Login with wrong password
    // Assert: 401 Unauthorized
}

[Fact]
public async Task WeatherForecast_WithValidToken_Returns200()
{
    // Arrange: Register and login to get token
    // Act: Call /weatherforecast with Authorization: Bearer {token}
    // Assert: 200 OK, weather data returned
}

[Fact]
public async Task WeatherForecast_WithoutToken_Returns401()
{
    // Arrange: Create client without token
    // Act: Call /weatherforecast
    // Assert: 401 Unauthorized
}

[Fact]
public async Task WeatherForecast_WithExpiredToken_Returns401()
{
    // Arrange: Create token with past expiration (mock time)
    // Act: Call /weatherforecast
    // Assert: 401 Unauthorized
}
```

**Coverage Target:** All critical paths and edge cases

---

### 7.3 Manual Testing Checklist

**Registration:**
- [ ] Valid registration succeeds (201 Created)
- [ ] Missing email returns 400 Bad Request
- [ ] Invalid email format returns 400 Bad Request
- [ ] Short password (<8 chars) returns 400 Bad Request
- [ ] Password without uppercase returns 400 Bad Request
- [ ] Password without lowercase returns 400 Bad Request
- [ ] Password without digit returns 400 Bad Request
- [ ] Duplicate email returns 409 Conflict
- [ ] Very long password (>128 chars) returns 400 Bad Request

**Login:**
- [ ] Valid credentials return 200 OK with token
- [ ] Invalid email returns 401 Unauthorized
- [ ] Invalid password returns 401 Unauthorized
- [ ] Missing fields return 400 Bad Request
- [ ] Token includes correct claims (sub, email, jti, exp, iat, iss, aud)
- [ ] Token expires after 15 minutes

**Protected Endpoint:**
- [ ] Valid token allows access to /weatherforecast
- [ ] Missing token returns 401 Unauthorized
- [ ] Invalid token returns 401 Unauthorized
- [ ] Expired token returns 401 Unauthorized
- [ ] Malformed token returns 401 Unauthorized

---

## 8. Implementation Steps

### Step 1: Database Migration

**Purpose:** Create Identity tables in SQLite database

**Tasks:**
1. Run EF Core migration command:
   ```bash
   dotnet ef migrations add InitialIdentitySetup --project TodoApi --output Data/Migrations
   ```
2. Apply migration to create database:
   ```bash
   dotnet ef database update --project TodoApi
   ```
3. Verify todoapi.db file created
4. Verify AspNetUsers table exists (can use SQLite browser)

**Acceptance Criteria:**
- [ ] Migration file created in Data/Migrations/
- [ ] todoapi.db file exists in project root
- [ ] AspNetUsers table exists with expected schema
- [ ] No errors during migration

**Time Estimate:** 30 minutes

---

### Step 2: Configure JWT Secret Key

**Purpose:** Store JWT secret key securely using User Secrets

**Tasks:**
1. Generate secure secret key (minimum 32 characters):
   ```bash
   # Example: use random generator or password manager
   # Must be at least 32 characters for HS256 security
   ```
2. Store in User Secrets:
   ```bash
   dotnet user-secrets set "Jwt:SecretKey" "your-generated-secret-key-minimum-32-chars" --project TodoApi
   ```
3. Verify secret is stored:
   ```bash
   dotnet user-secrets list --project TodoApi
   ```
4. Document production configuration approach (environment variables)

**Acceptance Criteria:**
- [ ] Secret key is at least 32 characters long
- [ ] Secret stored in User Secrets (not in appsettings.json)
- [ ] Secret not committed to source control
- [ ] `dotnet user-secrets list` shows Jwt:SecretKey

**Time Estimate:** 15 minutes

---

### Step 3: Create DTOs

**Purpose:** Define request/response contracts with validation

**Tasks:**
1. Create `Models/DTOs/` directory
2. Create `RegisterRequest.cs` with validation attributes
3. Create `LoginRequest.cs` with validation attributes
4. Create `LoginResponse.cs`
5. Create `ErrorResponse.cs` for standardized errors

**Files to Create:**
- TodoApi/Models/DTOs/RegisterRequest.cs
- TodoApi/Models/DTOs/LoginRequest.cs
- TodoApi/Models/DTOs/LoginResponse.cs
- TodoApi/Models/DTOs/ErrorResponse.cs

**Acceptance Criteria:**
- [ ] All DTOs compile without errors
- [ ] RegisterRequest has email and password validation
- [ ] LoginRequest has required field validation
- [ ] LoginResponse has Token and ExpiresAt properties
- [ ] ErrorResponse supports Message and Errors dictionary

**Time Estimate:** 45 minutes

**Code:** See Section 4.2 for complete implementations

---

### Step 4: Implement AuthService

**Purpose:** Business logic for registration, login, and JWT generation

**Tasks:**
1. Create `Services/` directory
2. Create `IAuthService.cs` interface
3. Create `AuthService.cs` implementation:
   - Implement `RegisterUserAsync` method
   - Implement `LoginUserAsync` method
   - Implement `GenerateJwtToken` private method
4. Add XML documentation comments

**Files to Create:**
- TodoApi/Services/IAuthService.cs
- TodoApi/Services/AuthService.cs

**Acceptance Criteria:**
- [ ] IAuthService interface defines contract
- [ ] AuthService implements IAuthService
- [ ] RegisterUserAsync creates users via UserManager
- [ ] LoginUserAsync validates credentials and generates token
- [ ] GenerateJwtToken creates valid JWT with correct claims
- [ ] All methods use async/await
- [ ] Error handling returns user-friendly messages

**Time Estimate:** 2 hours

**Code:** See Section 5.2 and 5.3 for complete implementations

---

### Step 5: Implement AuthController

**Purpose:** HTTP endpoints for registration and login

**Tasks:**
1. Create `Controllers/` directory (if not exists)
2. Create `AuthController.cs`:
   - Add `[ApiController]` and `[Route]` attributes
   - Implement POST /api/auth/register
   - Implement POST /api/auth/login
   - Add proper HTTP status codes
   - Add OpenAPI documentation attributes
   - Add logging (success/failure without passwords)
3. Handle model validation errors

**Files to Create:**
- TodoApi/Controllers/AuthController.cs

**Acceptance Criteria:**
- [ ] Controller inherits from ControllerBase
- [ ] Register endpoint returns 201/400/409 as appropriate
- [ ] Login endpoint returns 200/400/401 as appropriate
- [ ] Model validation errors return structured ErrorResponse
- [ ] Logging captures auth events without sensitive data
- [ ] OpenAPI attributes present for Swagger docs

**Time Estimate:** 1.5 hours

**Code:** See Section 5.4 for complete implementation

---

### Step 6: Update Program.cs

**Purpose:** Register services and enable controllers

**Tasks:**
1. Add `builder.Services.AddScoped<IAuthService, AuthService>();`
2. Add `builder.Services.AddControllers();` (if not present)
3. Add `app.MapControllers();` after UseAuthorization()
4. Verify middleware order: HTTPS → Authentication → Authorization

**Files to Modify:**
- TodoApi/Program.cs

**Acceptance Criteria:**
- [ ] IAuthService registered in DI container
- [ ] Controllers are registered
- [ ] Controllers are mapped
- [ ] Middleware order is correct
- [ ] Application compiles without errors

**Time Estimate:** 15 minutes

**Code:** See Section 5.5 for exact changes

---

### Step 7: Manual Testing

**Purpose:** Verify all endpoints work as expected

**Tasks:**
1. Start application: `dotnet run --project TodoApi`
2. Test registration with Postman/curl:
   - Valid registration
   - Invalid email format
   - Weak password
   - Duplicate email
3. Test login with Postman/curl:
   - Valid credentials
   - Invalid password
   - Non-existent user
4. Test protected endpoint:
   - With valid token (copy from login response)
   - Without token
   - With malformed token
5. Verify token claims using jwt.io

**Tools:**
- Postman collection (create one)
- curl commands
- jwt.io for token inspection

**Acceptance Criteria:**
- [ ] Can register new user
- [ ] Validation errors return proper messages
- [ ] Can login and receive token
- [ ] Token works with /weatherforecast
- [ ] Token expires after 15 minutes
- [ ] All manual test checklist items pass (Section 7.3)

**Time Estimate:** 1.5 hours

---

### Step 8: Write Tests

**Purpose:** Automated test coverage for reliability

**Tasks:**
1. Create test project: `dotnet new xunit -n TodoApi.Tests`
2. Add project reference to TodoApi
3. Install testing packages (Moq, Microsoft.AspNetCore.Mvc.Testing)
4. Write unit tests for AuthService (5-7 tests)
5. Write integration tests for AuthController (7-10 tests)
6. Run tests: `dotnet test`
7. Verify coverage using dotnet-coverage or similar

**Files to Create:**
- TodoApi.Tests/TodoApi.Tests.csproj
- TodoApi.Tests/Services/AuthServiceTests.cs
- TodoApi.Tests/Controllers/AuthControllerTests.cs
- TodoApi.Tests/IntegrationTests/AuthEndpointTests.cs

**Acceptance Criteria:**
- [ ] Unit tests pass (green)
- [ ] Integration tests pass (green)
- [ ] Code coverage ≥ 80% for AuthService
- [ ] All critical paths tested
- [ ] Edge cases covered (invalid input, etc.)

**Time Estimate:** 3 hours

**Note:** Can be done in parallel with Step 7 or after

---

### Step 9: Documentation

**Purpose:** API documentation and developer guides

**Tasks:**
1. Verify Swagger UI works: https://localhost:7xxx/swagger
2. Test all endpoints in Swagger UI
3. Add code comments where logic is complex
4. Create POSTMAN collection (optional but recommended)
5. Update README with:
   - How to configure JWT secret
   - How to run migrations
   - How to test endpoints

**Acceptance Criteria:**
- [ ] Swagger UI displays auth endpoints
- [ ] API responses match PRD specifications
- [ ] README includes setup instructions
- [ ] Code is well-commented

**Time Estimate:** 1 hour

---

## 9. Deployment Plan

### 9.1 Pre-Deployment Checklist

**Configuration:**
- [ ] JWT SecretKey configured in production (environment variable or Key Vault)
- [ ] SecretKey is minimum 32 characters
- [ ] Connection string points to production database (or keep SQLite for MVP)
- [ ] HTTPS certificate is valid
- [ ] appsettings.Production.json reviewed (no secrets!)

**Code Quality:**
- [ ] All tests passing
- [ ] No compiler warnings
- [ ] Code reviewed by peer
- [ ] Security scan completed (dependency check)

**Database:**
- [ ] Migrations applied to production database
- [ ] Database backup taken (if not first deploy)
- [ ] Connection tested

---

### 9.2 Deployment Steps

**Option 1: Deploy to Azure App Service**
```bash
# 1. Publish application
dotnet publish -c Release -o ./publish

# 2. Create deployment package
cd publish
zip -r ../todoapi.zip *

# 3. Deploy to Azure
az webapp deployment source config-zip \
  --resource-group <resource-group> \
  --name <app-name> \
  --src ../todoapi.zip

# 4. Configure environment variables
az webapp config appsettings set \
  --resource-group <resource-group> \
  --name <app-name> \
  --settings Jwt__SecretKey="<production-secret>"

# 5. Verify deployment
curl https://<app-name>.azurewebsites.net/weatherforecast
```

**Option 2: Deploy to Docker Container**
```dockerfile
# Dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY ["TodoApi/TodoApi.csproj", "TodoApi/"]
RUN dotnet restore "TodoApi/TodoApi.csproj"
COPY . .
WORKDIR "/src/TodoApi"
RUN dotnet build "TodoApi.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "TodoApi.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "TodoApi.dll"]
```

```bash
# Build and run
docker build -t todoapi:latest .
docker run -d -p 8080:80 -e "Jwt__SecretKey=<secret>" todoapi:latest
```

---

### 9.3 Verification Steps

**Post-Deployment:**
1. Test registration: `POST https://<production-url>/api/auth/register`
2. Test login: `POST https://<production-url>/api/auth/login`
3. Test protected endpoint: `GET https://<production-url>/weatherforecast` with token
4. Verify Swagger UI: `https://<production-url>/swagger`
5. Check application logs for errors
6. Monitor first 100 requests

**Success Criteria:**
- [ ] Registration endpoint returns 201 for valid input
- [ ] Login endpoint returns 200 with token
- [ ] Protected endpoint returns 200 with valid token
- [ ] Protected endpoint returns 401 without token
- [ ] No errors in application logs
- [ ] Response times < 500ms (p95)

---

### 9.4 Rollback Plan

**If deployment fails or issues found in production:**

**Option 1: Rollback to previous version**
```bash
# Azure App Service
az webapp deployment slot swap \
  --resource-group <resource-group> \
  --name <app-name> \
  --slot staging \
  --target-slot production

# Or restore previous deployment
az webapp deployment list \
  --resource-group <resource-group> \
  --name <app-name>

az webapp deployment restore \
  --resource-group <resource-group> \
  --name <app-name> \
  --deployment-id <previous-deployment-id>
```

**Option 2: Docker rollback**
```bash
# Pull previous image version
docker pull todoapi:previous-version

# Stop current container
docker stop <container-id>

# Start previous version
docker run -d -p 8080:80 -e "Jwt__SecretKey=<secret>" todoapi:previous-version
```

**Database Rollback:**
- Identity tables are schema-only (no data loss risk in MVP)
- If migration issues: `dotnet ef database update <previous-migration>`
- Keep database backup before migrations

**Rollback Decision Criteria:**
- Critical security vulnerability discovered
- >50% of auth requests failing
- Data corruption or loss
- Performance degradation >500% (p95)

**Communication:**
1. Notify team immediately
2. Post status update (status page or Slack)
3. Execute rollback
4. Post-mortem after resolution

---

## 10. Risk Assessment

### Risk 1: JWT Secret Key Exposure

**Probability:** Low
**Impact:** Critical (all tokens can be forged)

**Mitigation:**
- Use User Secrets for development
- Use secure configuration for production (Azure Key Vault, AWS Secrets Manager)
- .gitignore includes secrets files
- Code review checks for hardcoded secrets
- Rotate keys every 90 days

**Detection:**
- Security scan in CI/CD pipeline
- Manual code review
- Secret scanning tools (GitHub secret scanning, GitGuardian)

**Response:**
- Immediately rotate key
- Invalidate all existing tokens (users must re-login)
- Security audit to find breach source

---

### Risk 2: SQL Injection

**Probability:** Very Low (EF Core parameterizes queries)
**Impact:** High (database compromise)

**Mitigation:**
- Entity Framework Core parameterizes all queries
- No raw SQL in codebase
- Input validation at API boundary

**Detection:**
- Security testing (OWASP ZAP, SQLMap)
- Code review

**Response:**
- Patch immediately
- Audit database for unauthorized access
- Review all database queries

---

### Risk 3: Brute Force Login Attacks

**Probability:** Medium (common attack)
**Impact:** Medium (account compromise)

**Mitigation (Not in MVP, but documented for V2):**
- Rate limiting (5 requests/minute per IP)
- Account lockout after failed attempts (Identity supports this)
- CAPTCHA for repeated failures
- Monitoring and alerting

**Detection:**
- Monitor failed login attempts in logs
- Alert on >10 failed attempts from single IP

**Response:**
- Enable account lockout
- Implement rate limiting
- Block offending IPs

---

### Risk 4: Token Expiration Too Short/Long

**Probability:** Low
**Impact:** Low (UX issue or security issue)

**Current Setting:** 15 minutes (per PRD)

**Mitigation:**
- 15 minutes is reasonable for MVP
- Can be adjusted via configuration (no code change)
- Refresh tokens planned for V2

**Detection:**
- User feedback
- Analytics on re-login frequency

**Response:**
- Adjust `Jwt:ExpirationMinutes` in configuration
- Implement refresh tokens (V2)

---

### Risk 5: SQLite Performance Degradation

**Probability:** Medium (if user base grows unexpectedly)
**Impact:** Medium (slow response times)

**Mitigation:**
- SQLite acceptable for <1,000 concurrent users
- Entity Framework makes migration to PostgreSQL straightforward
- Monitor response times

**Detection:**
- Response time monitoring (>500ms p95 is red flag)
- Database lock errors in logs

**Response:**
- Migrate to PostgreSQL or SQL Server
- Change connection string
- Run EF migrations for new database
- Near-zero code changes required

---

### Risk 6: Password Complexity Too Weak/Strong

**Probability:** Low
**Impact:** Low (UX or security issue)

**Current Settings:**
- 8+ characters
- Uppercase, lowercase, digit
- No special characters required

**Mitigation:**
- Settings are configurable in Program.cs
- Can be adjusted without code changes
- PRD requirements are reasonable

**Detection:**
- Security audit
- User feedback

**Response:**
- Adjust Identity options in Program.cs
- Users may need to reset passwords if strengthened

---

## 11. Performance Considerations

### 11.1 Expected Performance

**Registration:**
- Database write: ~10-50ms
- Password hashing (PBKDF2): ~50-100ms
- Total: ~100-200ms (p95)

**Login:**
- Database read: ~5-20ms
- Password verification: ~50-100ms
- JWT generation: ~1-5ms
- Total: ~100-200ms (p95)

**Protected Endpoint (token validation):**
- JWT validation: ~1-5ms (in-memory)
- Business logic: depends on endpoint
- Total overhead: ~5-10ms

**Bottlenecks:**
- Password hashing (intentionally slow for security)
- Database I/O (SQLite is file-based)

---

### 11.2 Optimization Opportunities (Future)

**Not Implemented in MVP** - Documented for V2

1. **Response Caching**
   - Cache public endpoints (not auth endpoints)
   - Use `[ResponseCache]` attribute

2. **Connection Pooling**
   - EF Core does this by default
   - Monitor connection pool exhaustion

3. **Async All The Way**
   - Already using async/await throughout
   - No blocking calls (good!)

4. **Database Indexing**
   - Identity creates indexes on Email automatically
   - Monitor query performance with EF logging

5. **Redis for Session Management** (if adding refresh tokens)
   - Fast in-memory token storage
   - Distributed cache for multi-server

---

## 12. Timeline Estimate

### Task Breakdown

| Task | Time Estimate | Dependencies |
|------|---------------|--------------|
| 1. Database Migration | 30 min | None |
| 2. Configure JWT Secret | 15 min | Task 1 |
| 3. Create DTOs | 45 min | None |
| 4. Implement AuthService | 2 hours | Task 3 |
| 5. Implement AuthController | 1.5 hours | Task 3, 4 |
| 6. Update Program.cs | 15 min | Task 4, 5 |
| 7. Manual Testing | 1.5 hours | Task 6 |
| 8. Write Tests | 3 hours | Task 5 (can overlap) |
| 9. Documentation | 1 hour | Task 7 |

**Total Development Time:** ~10.5 hours

**Recommended Schedule:**
- Day 1 Morning: Tasks 1-3 (1.5 hours)
- Day 1 Afternoon: Task 4 (2 hours)
- Day 2 Morning: Tasks 5-6 (2 hours)
- Day 2 Afternoon: Task 7 (1.5 hours)
- Day 3: Task 8-9 (4 hours)

**Buffer:** Add 25% contingency = ~13 hours total

**Calendar Time:** 2-3 days for single developer

---

## 13. Dependencies

### Internal Dependencies

**Already Satisfied:**
- ASP.NET Core 9.0 project structure
- NuGet packages installed (Identity, JwtBearer, EF Core, Sqlite)
- Program.cs configured with Identity and JWT
- ApplicationDbContext set up
- JwtSettings configuration class
- User Secrets configured (UserSecretsId in .csproj)

**To Be Created:**
- Database migrations
- AuthService and IAuthService
- AuthController
- DTOs

### External Dependencies

**All NuGet packages already installed:**
- Microsoft.AspNetCore.Identity.EntityFrameworkCore 9.0.0
- Microsoft.AspNetCore.Authentication.JwtBearer 9.0.0
- Microsoft.EntityFrameworkCore.Sqlite 9.0.0
- Microsoft.EntityFrameworkCore.Design 9.0.0

**Development Tools Required:**
- .NET 9.0 SDK
- dotnet ef tool (for migrations)
  ```bash
  dotnet tool install --global dotnet-ef
  ```

### Environmental Dependencies

**Development:**
- User Secrets for JWT key
- SQLite (no installation needed, file-based)
- HTTPS certificate: `dotnet dev-certs https --trust`

**Production:**
- Secure configuration provider (Azure Key Vault, AWS Secrets Manager, or environment variables)
- SQLite file with write permissions (or PostgreSQL for scale)
- Valid SSL/TLS certificate

---

## 14. Success Criteria

### Functional Success

- [ ] User can register with valid email and password
- [ ] Registration fails appropriately for invalid input
- [ ] User can login and receive JWT token
- [ ] Token contains correct claims (sub, email, jti, exp, iat, iss, aud)
- [ ] Token expires after 15 minutes
- [ ] User can access protected endpoint with valid token
- [ ] Access denied (401) without token or with expired token
- [ ] Validation errors are clear and user-friendly
- [ ] Duplicate email registration returns 409 Conflict

### Technical Success

- [ ] All endpoints return correct HTTP status codes
- [ ] Password hashing is secure (Identity default PBKDF2)
- [ ] JWT tokens are properly signed with HS256
- [ ] Database migrations run successfully
- [ ] No sensitive data in logs or error messages
- [ ] Code follows SOLID principles
- [ ] Service layer properly separated from controller
- [ ] DTOs used for all request/response contracts

### Quality Metrics

- [ ] Unit tests for AuthService pass (80% coverage)
- [ ] Integration tests for AuthController pass
- [ ] All manual test checklist items pass
- [ ] API documentation (Swagger) is complete
- [ ] Zero critical security vulnerabilities
- [ ] Code reviewed by peer
- [ ] Performance: registration < 500ms (p95)
- [ ] Performance: login < 200ms (p95)

### Security Metrics

- [ ] JWT secret stored securely (User Secrets, not in code)
- [ ] Passwords never logged
- [ ] HTTPS enforced
- [ ] Input validation at API boundary
- [ ] SQL injection not possible (EF parameterization)
- [ ] Token signature validated on every request
- [ ] Token expiration enforced (zero clock skew)

---

## 15. Open Questions

### Q1: Should we add email confirmation before allowing login?

**Decision:** No, deferred to V2 (PRD marks as P2 "Could Have")

**Rationale:**
- Adds complexity (email service, confirmation flow, UI)
- Not critical for MVP
- Can be added later without breaking changes

**Action:** Document as V2 feature

---

### Q2: Should we implement refresh tokens in V1?

**Decision:** No, deferred to V2 (PRD marks as P2 "Could Have")

**Rationale:**
- Increases implementation time by ~50%
- 15-minute expiration is acceptable for MVP
- Users can re-login (UX hit, but acceptable for early stage)
- Can be added later as separate endpoint

**Action:** Document refresh token architecture in V2 plan

---

### Q3: Should we add rate limiting for auth endpoints?

**Decision:** No, deferred to V2

**Rationale:**
- ASP.NET Core 7+ has built-in rate limiting, but adds complexity
- Low risk for MVP (private testing, small user base)
- Should absolutely add before public launch

**Action:** Document rate limiting strategy for V2

---

### Q4: What about user roles and permissions?

**Decision:** Not needed for MVP

**Rationale:**
- PRD states "Role-Based Authorization - Infrastructure exists, but no roles defined for MVP"
- Identity already supports roles (AspNetRoles table will be created)
- No business requirements for roles yet
- Easy to add later via `[Authorize(Roles = "Admin")]`

**Action:** Defer to when product requirements include role-based features

---

## 16. Future Enhancements (V2 and Beyond)

### High Priority (V2)

1. **Refresh Tokens**
   - 7-day expiration
   - Separate table for refresh token storage
   - POST /api/auth/refresh endpoint
   - Rotate on use (security best practice)

2. **Email Confirmation**
   - Send confirmation email on registration
   - Verify email before login
   - Resend confirmation endpoint

3. **Password Reset**
   - POST /api/auth/forgot-password
   - Email password reset link
   - POST /api/auth/reset-password with token

4. **Rate Limiting**
   - 5 login attempts per minute per IP
   - 3 registration attempts per hour per IP
   - ASP.NET Core built-in middleware

### Medium Priority (V3)

5. **Two-Factor Authentication (2FA)**
   - TOTP (Time-based One-Time Password)
   - SMS or email verification codes
   - Identity supports this

6. **Account Lockout**
   - Lock account after N failed login attempts
   - Identity has built-in support
   - Currently disabled in Program.cs

7. **Audit Logging**
   - Comprehensive auth event logging
   - Login/logout tracking
   - Token issuance and revocation
   - Store in separate audit table

8. **Security Headers Middleware**
   - X-Content-Type-Options
   - X-Frame-Options
   - X-XSS-Protection
   - HSTS

### Low Priority (Future)

9. **OAuth/Social Login**
   - Google Sign-In
   - Microsoft Account
   - GitHub
   - Third-party OAuth providers

10. **Role-Based Access Control (RBAC)**
    - Define roles (Admin, User, etc.)
    - Role-based endpoint authorization
    - Claims-based authorization for fine-grained control

11. **Multi-Tenancy**
    - Tenant isolation
    - Tenant-specific databases or schemas
    - Tenant claim in JWT

12. **Database Migration to PostgreSQL**
    - When SQLite performance becomes bottleneck
    - Change connection string
    - Run EF migrations
    - Zero code changes required

---

## 17. Appendix: Code Examples

### Example JWT Token (Decoded)

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "user@example.com",
    "jti": "550e8400-e29b-41d4-a716-446655440000",
    "exp": 1738505700,
    "iat": 1738504800,
    "iss": "TodoApi",
    "aud": "TodoApi"
  },
  "signature": "HMACSHA256(...)"
}
```

**Encoded Token:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJqdGkiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3Mzg1MDU3MDAsImlhdCI6MTczODUwNDgwMCwiaXNzIjoiVG9kb0FwaSIsImF1ZCI6IlRvZG9BcGkifQ.HMACSHA256_SIGNATURE
```

---

### Example Postman Collection

```json
{
  "info": {
    "name": "TodoApi Authentication",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Register User",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "url": "https://localhost:7000/api/auth/register",
        "body": {
          "mode": "raw",
          "raw": "{\"email\":\"test@example.com\",\"password\":\"Test123!\"}"
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "url": "https://localhost:7000/api/auth/login",
        "body": {
          "mode": "raw",
          "raw": "{\"email\":\"test@example.com\",\"password\":\"Test123!\"}"
        }
      }
    },
    {
      "name": "Weather Forecast (Protected)",
      "request": {
        "method": "GET",
        "header": [
          {"key": "Authorization", "value": "Bearer {{token}}"}
        ],
        "url": "https://localhost:7000/weatherforecast"
      }
    }
  ]
}
```

---

### Example curl Commands

**Register:**
```bash
curl -X POST https://localhost:7000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

**Login:**
```bash
curl -X POST https://localhost:7000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

**Protected Endpoint:**
```bash
TOKEN="your-jwt-token-here"
curl -X GET https://localhost:7000/weatherforecast \
  -H "Authorization: Bearer $TOKEN"
```

---

## 18. Conclusion

This technical plan provides a comprehensive blueprint for implementing JWT authentication in TodoApi. The infrastructure is already in place, which significantly reduces implementation risk and time.

**Key Strengths:**
- Well-defined architecture with clear separation of concerns
- Battle-tested technologies (ASP.NET Core Identity, JWT)
- Security-first approach
- Comprehensive testing strategy
- Clear implementation steps with acceptance criteria

**Architect's Recommendation:**
Approve this plan and proceed with implementation. The approach is pragmatic, secure, and maintainable. We're using boring, proven solutions that work.

**Next Steps:**
1. Human approval of this plan
2. Engineer picks up Task 1 (Database Migration)
3. Follow implementation steps sequentially
4. Architect available for technical questions

**Estimated Delivery:**
- Implementation: 2-3 days
- Testing: 1 day
- Total: 3-4 calendar days

---

**Plan Status:** Ready for Approval
**Author:** architect
**Date:** 2026-02-02
**Version:** 1.0

---

## Approval

**Architect:** ✅ Plan created, ready for review
**Human:** ⏸️  Awaiting approval
**Engineer:** ⏸️  Will be assigned after approval

---

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-02-02 | 1.0 | architect | Initial technical plan created |
