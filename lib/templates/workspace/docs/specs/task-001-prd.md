# Product Requirements Document: JWT Authentication for TodoApi

**Task ID:** task-001
**Priority:** P1
**Created:** 2026-02-02
**Status:** Awaiting Approval

---

## Problem Statement

TodoApi currently has JWT authentication infrastructure configured (Identity, JWT Bearer, DbContext) but lacks the critical authentication endpoints that users need to register, login, and obtain JWT tokens. Without these endpoints, users cannot authenticate and the protected `/weatherforecast` endpoint is inaccessible.

**Who is affected:** All users of the TodoApi
**Impact:** Cannot use the API - authentication is completely non-functional
**Why now:** P0 blocker - core functionality required before any feature development can proceed

---

## User Stories

### Story 1: User Registration
**As a** new user
**I want to** register with my email and password
**So that** I can create an account and access the TodoApi

**Acceptance Criteria:**
- User can POST to `/api/auth/register` with email and password
- Password must meet complexity requirements: 8+ chars, uppercase, lowercase, digit
- Email must be valid format and unique
- Returns 201 Created with success message on success
- Returns 400 Bad Request with validation errors if input invalid
- Returns 409 Conflict if email already exists
- User account is created in database using ASP.NET Core Identity

### Story 2: User Login
**As a** registered user
**I want to** login with my email and password
**So that** I receive a JWT token to access protected endpoints

**Acceptance Criteria:**
- User can POST to `/api/auth/login` with email and password
- Returns 200 OK with JWT token on successful authentication
- Token expires after 15 minutes (per configuration)
- Token includes standard claims: sub (userId), email, jti (token ID), exp, iat
- Returns 401 Unauthorized if credentials invalid
- Returns 400 Bad Request if input malformed

### Story 3: Access Protected Endpoint
**As an** authenticated user
**I want to** call protected endpoints with my JWT token
**So that** I can use the API functionality

**Acceptance Criteria:**
- User can call `/weatherforecast` with valid JWT in Authorization header (Bearer scheme)
- Returns 200 OK with weather forecast data if token valid
- Returns 401 Unauthorized if token missing, expired, or invalid
- Token validation uses configured settings (issuer, audience, signing key)
- No clock skew - exact expiration enforcement

---

## Functional Requirements

### Must Have (P0)

#### FR1: User Registration Endpoint
- **Endpoint:** `POST /api/auth/register`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePass123"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "message": "User registered successfully"
  }
  ```
- **Response (400 Bad Request):**
  ```json
  {
    "errors": {
      "Email": ["Email is required", "Email format is invalid"],
      "Password": ["Password must be at least 8 characters"]
    }
  }
  ```
- **Response (409 Conflict):**
  ```json
  {
    "message": "User with this email already exists"
  }
  ```

#### FR2: User Login Endpoint
- **Endpoint:** `POST /api/auth/login`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePass123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2026-02-02T13:15:00Z"
  }
  ```
- **Response (401 Unauthorized):**
  ```json
  {
    "message": "Invalid email or password"
  }
  ```

#### FR3: JWT Token Structure
- **Algorithm:** HS256 (HMAC with SHA-256)
- **Standard Claims:**
  - `sub`: User ID (from Identity)
  - `email`: User email
  - `jti`: Unique token identifier (prevents replay)
  - `exp`: Expiration timestamp (Unix)
  - `iat`: Issued at timestamp (Unix)
  - `iss`: Issuer from configuration
  - `aud`: Audience from configuration
- **Expiration:** 15 minutes from issuance
- **No custom claims** in initial release

#### FR4: Password Requirements
Per existing Identity configuration:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- Special characters NOT required (intentional for usability)

#### FR5: Email Requirements
- Must be valid email format (standard RFC 5322)
- Must be unique across all users
- Case-insensitive matching (user@example.com = USER@example.com)

### Should Have (P1)

#### FR6: Input Validation Error Details
- Specific field-level validation errors
- Clear, user-friendly error messages
- HTTP 400 for validation failures

#### FR7: Rate Limiting Consideration
- Document rate limiting as future enhancement
- Out of scope for initial release but architecture should support adding it

### Could Have (P2)

#### FR8: Refresh Token Support
- Long-lived refresh tokens (7 days)
- Separate endpoint for token refresh
- Deferred to post-MVP (mentioned in history as P1, but moving to P2 for MVP focus)

#### FR9: Email Confirmation
- Require email verification before login
- Send confirmation emails
- Deferred to post-MVP

---

## Non-Functional Requirements

### NFR1: Security
- **JWT Secret Key:** Must be stored in User Secrets (development) and secure configuration (production)
- **Password Hashing:** ASP.NET Core Identity default (PBKDF2 with HMAC-SHA256, 10000 iterations)
- **HTTPS Only:** All authentication endpoints require HTTPS (except localhost development)
- **Token Signing:** Symmetric key (HS256) - adequate for single-server MVP
- **No Sensitive Data in Tokens:** Only necessary claims (user ID, email) - no passwords or sensitive PII

### NFR2: Performance
- **Registration Response Time:** < 500ms (p95)
- **Login Response Time:** < 200ms (p95)
- **Database:** SQLite for MVP (already configured) - acceptable for small user base
- **Token Generation:** < 50ms (in-memory operation)

### NFR3: Usability
- **Clear Error Messages:** User-friendly, not exposing internal details
- **Standard HTTP Status Codes:** Proper use of 200, 201, 400, 401, 409
- **API Documentation:** OpenAPI/Swagger schema for all endpoints

### NFR4: Reliability
- **Error Handling:** All endpoints must handle exceptions gracefully
- **Database Transactions:** Use Identity's built-in transaction handling
- **Logging:** Log authentication attempts (success/failure) without logging passwords

---

## Technical Considerations

### Current State Analysis
**Already Implemented:**
- ASP.NET Core Identity configured with IdentityUser
- JWT Bearer authentication middleware configured
- ApplicationDbContext with Identity tables
- JwtSettings configuration class
- Password complexity requirements
- Protected endpoint example (/weatherforecast)
- SQLite database configured

**Missing (What We're Building):**
- Authentication controller with register/login endpoints
- JWT token generation service
- Request/response DTOs (Data Transfer Objects)
- Input validation attributes
- Error response standardization
- Database migrations for Identity tables

### Architecture Decisions

#### Decision 1: Minimal API vs Controllers
**Choice:** Use Controllers (ASP.NET Core Web API pattern)
**Rationale:**
- Better organization for authentication logic
- Easier to apply attributes (validation, authorization)
- Standard pattern for API development
- Matches industry best practices for auth endpoints

#### Decision 2: Service Layer
**Choice:** Create AuthService for token generation
**Rationale:**
- Separate concerns: Controller handles HTTP, Service handles business logic
- Easier to unit test
- Reusable token generation logic
- Follows SOLID principles

#### Decision 3: DTO Pattern
**Choice:** Use separate DTOs for requests/responses
**Rationale:**
- Don't expose Identity entities directly
- Control exactly what data flows in/out
- Apply data annotations for validation
- API versioning flexibility

---

## Edge Cases and Error Handling

### Edge Case 1: Concurrent Registration
**Scenario:** Two users try to register same email simultaneously
**Handling:** Database unique constraint + 409 Conflict response
**Test:** Verify second request fails gracefully

### Edge Case 2: Token Expiration During Request
**Scenario:** Token valid when request starts, expires during processing
**Handling:** Middleware validates at request start - should fail gracefully
**Test:** Mock time to test exact expiration boundary

### Edge Case 3: Invalid JWT Format
**Scenario:** Client sends malformed token (not JWT format)
**Handling:** Middleware returns 401 Unauthorized
**Test:** Send garbage string as Bearer token

### Edge Case 4: SQL Injection Attempts
**Scenario:** Malicious email/password with SQL commands
**Handling:** Entity Framework parameterizes queries - no action needed
**Test:** Attempt login with email "admin' OR '1'='1"

### Edge Case 5: Empty/Whitespace Input
**Scenario:** User submits empty or whitespace-only email/password
**Handling:** Model validation returns 400 Bad Request
**Test:** POST with empty strings, null values, spaces

### Edge Case 6: Very Long Passwords
**Scenario:** User submits 10,000 character password
**Handling:** Add MaxLength validation (e.g., 128 chars) to prevent DoS
**Test:** Submit extremely long password string

---

## Dependencies

### Internal Dependencies
- TodoApi project structure (already exists)
- ApplicationDbContext (already exists)
- JwtSettings configuration (already exists)
- User Secrets for JWT key (needs configuration)

### External Dependencies
- **NuGet Packages** (all already installed):
  - Microsoft.AspNetCore.Identity.EntityFrameworkCore 9.0.0
  - Microsoft.AspNetCore.Authentication.JwtBearer 9.0.0
  - Microsoft.EntityFrameworkCore.Sqlite 9.0.0
  - Microsoft.EntityFrameworkCore.Design 9.0.0

### Environmental Dependencies
- SQLite database file (todoapi.db) - created via migrations
- JWT secret key in User Secrets - needs setup
- HTTPS certificate for development (dotnet dev-certs)

---

## Out of Scope

### Explicitly NOT Included
1. **Refresh Tokens** - Deferred to v2
2. **Email Confirmation** - Deferred to v2
3. **Password Reset** - Deferred to v2
4. **Two-Factor Authentication (2FA)** - Deferred to v2
5. **OAuth/Social Login** - Deferred to future
6. **Role-Based Authorization** - Infrastructure exists, but no roles defined for MVP
7. **Rate Limiting** - Deferred to v2 (infrastructure-level concern)
8. **Account Lockout** - Identity supports it, but not configuring in MVP
9. **Audit Logging** - Basic logging only, no comprehensive audit trail
10. **Multi-Tenancy** - Single tenant application

---

## Success Metrics

### Functional Success
- [ ] User can register with valid email/password
- [ ] User receives appropriate error for invalid registration
- [ ] User can login and receive JWT token
- [ ] User can access protected endpoint with valid token
- [ ] User receives 401 for expired/invalid tokens

### Technical Success
- [ ] All endpoints return correct HTTP status codes
- [ ] Password hashing is secure (Identity default)
- [ ] JWT tokens are properly signed and validated
- [ ] Database migrations run successfully
- [ ] No sensitive data in logs or error messages

### Quality Metrics
- [ ] Unit tests for AuthService (token generation)
- [ ] Integration tests for auth endpoints
- [ ] API documentation (Swagger) is complete
- [ ] Zero critical security vulnerabilities (OWASP Top 10)

---

## Implementation Notes for Architect

### File Structure Recommendation
```
TodoApi/
├── Controllers/
│   └── AuthController.cs          # NEW: Registration and login endpoints
├── Services/
│   ├── IAuthService.cs            # NEW: Interface for auth service
│   └── AuthService.cs             # NEW: JWT token generation
├── Models/
│   ├── DTOs/
│   │   ├── RegisterRequest.cs     # NEW: Registration request DTO
│   │   ├── LoginRequest.cs        # NEW: Login request DTO
│   │   ├── LoginResponse.cs       # NEW: Login response DTO
│   │   └── ErrorResponse.cs       # NEW: Standard error response
├── Data/
│   └── ApplicationDbContext.cs    # EXISTS: No changes needed
├── Configuration/
│   └── JwtSettings.cs             # EXISTS: No changes needed
└── Program.cs                     # EXISTS: Add service registrations
```

### Key Tasks for Technical Plan
1. Create database migration for Identity tables
2. Implement AuthService with token generation logic
3. Create DTOs with validation attributes
4. Implement AuthController with register/login endpoints
5. Add IAuthService registration to DI container
6. Configure User Secrets for JWT key
7. Add error handling middleware (optional enhancement)
8. Write unit and integration tests

---

## Risk Assessment

### High Risk
**Risk:** JWT secret key exposed in source control
**Mitigation:** Use User Secrets (dev) and environment variables (prod), .gitignore secrets
**Owner:** DevOps + Engineer

### Medium Risk
**Risk:** Poor password requirements lead to weak passwords
**Mitigation:** Current requirements (8 chars, mixed case, digit) are reasonable
**Owner:** PM (requirements defined above)

### Low Risk
**Risk:** SQLite performance issues with many users
**Mitigation:** SQLite acceptable for MVP (<10k users), migration path to PostgreSQL documented
**Owner:** Architect (technical plan should note migration path)

---

## Approval

**PM:** Awaiting human approval
**Architect:** Pending (after PM approval)
**Security:** Pending (after implementation, pre-deployment)

---

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-02-02 | 1.0 | pm | Initial PRD creation |

---

## Appendix: JWT Token Example

```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "user@example.com",
  "jti": "550e8400-e29b-41d4-a716-446655440000",
  "exp": 1738505700,
  "iat": 1738504800,
  "iss": "TodoApi",
  "aud": "TodoApi"
}

Signature:
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

**Note:** Actual tokens are base64url-encoded and dot-separated. Example above shows decoded structure for clarity.
