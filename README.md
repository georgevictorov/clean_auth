# Authentication Service

Authentication service for user authentication, session management, token issuance, and public key discovery.

## Architecture

```text
Client
  │
  ├── Flask API
  └── CLI
        │
        ▼
Application Layer
  │
  ├── AuthService
  ├── UserService
  └── KeyService
        │
        ├── UnitOfWork
        ├── TokenProvider
        ├── PasswordHasher
        └── PaserkProvider
                │
                ▼
           KeyProvider
                │
                ▼
         Ed25519 key pair
```

```text
Infrastructure
  │
  ├── SQLUnitOfWork
  ├── SQLRepositories
  ├── PasetoTokenProvider
  ├── PaserkProvider
  ├── FileKeysPairProvider
  └── Argon2PasswordHasher
        │
        ▼
    PostgreSQL
```

## Main Components

| Component        | Responsibility                               |
|------------------|----------------------------------------------|
| `AuthService`    | Authentication and session lifecycle         |
| `UserService`    | User creation and management                 |
| `KeyService`     | Public key discovery                         |
| `UnitOfWork`     | Transaction management                       |
| `TokenProvider`  | Issue and verify tokens                      |
| `PasswordHasher` | Hash and verify passwords                    |
| `KeyProvider`    | Provide Ed25519 keys                         |
| `PaserkProvider` | Convert public keys to PASERK representation |

## Authentication

```text
Client
  → Flask API
  → AuthService
  → Load user
  → Verify password
  → Create session
  → Issue access + refresh tokens
  → Store refresh token hash
  → Commit
```

## Refresh

```text
Client
  → Flask API
  → AuthService
  → Verify refresh token
  → Load session
  → Verify refresh token hash
  → Rotate refresh token
  → Issue new tokens
  → Commit
```

```text
refresh_hash: H1 → H2
```

## Logout

```text
Client
  → Flask API
  → AuthService
  → Load session
  → Revoke session
  → Commit
```

## Public Key Discovery

```text
External Service
  → GET /.well-known/paserk.json
  → KeyService
  → PaserkProvider
  → KeyProvider
  → Public Ed25519 key
  → PASERK
```

```json
{
  "keys": [
    {
      "kid": "auth-key-01...",
      "paserk": "k4.public.A2x4..."
    }
  ]
}
```

## User Management

### Create User

```text
CLI / API
  → UserService
  → Check user
  → Hash password
  → Create user
  → Persist
  → Commit
```

### Disable User

```text
CLI / API
  → UserService
  → Load user
  → Disable user
  → Revoke sessions
  → Commit
```

### Change Password

```text
CLI / API
  → UserService
  → Load user
  → Verify current password
  → Hash new password
  → Update user
  → Commit
```

## Domain Models

```text
User
----
user_id
username
password_hash
version
disabled


Session
-------
session_id
user_id
refresh_token_hash
created_at
expires_at
version
revoked
```
