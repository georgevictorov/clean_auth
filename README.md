``` 
                        Authentication Service


        ┌─────────────────────┐     ┌─────────────────────┐
        │                     │     │                     │
        │      Flask API      │     │         CLI         │
        │                     │     │                     │
        │ /login              │     │ create-user         │
        │ /refresh            │     │ disable-user        │
        │ /logout             │     │ change-password     │
        │                     │     │                     │
        └──────────┬──────────┘     └──────────┬──────────┘
                   │                           │
                   └─────────────┬─────────────┘
                                 │
                                 ▼

                    ┌────────────────────────────┐
                    │      Application Layer     │
                    │                            │
                    │  LoginService              │
                    │  RefreshService            │
                    │  LogoutService             │
                    │  UserService               │
                    └──────────────┬─────────────┘
                                   │
      ┌────────────────────────────┼─────────────────────────────┐
      │                            │                             │
      ▼                            ▼                             ▼
 UnitOfWork                 TokenProvider                PasswordHasher
    Port                         Port                          Port
      │                            │                             │
      └──────────────┬─────────────┴─────────────┬───────────────┘
                     │                           │
                     ▼                           ▼

═══════════════════════════ DOMAIN ═══════════════════════════

                     User              UserSession

═══════════════════════════════════════════════════════════════

                     ▲                           ▲
                     │                           │
      ┌──────────────┴─────────────┬─────────────┴──────────────┐
      │                            │                            │
      ▼                            ▼                            ▼

 SQLiteUnitOfWork          SQLiteRepositories          JwtTokenProvider
                            (User / Session)

                SQLite Mapper       Identity Map Snapshot

                      Argon2PasswordHasher

                    SQLite Database / Key Store


┌──────────────────────────────┐
│          Login Flow          │
└──────────────────────────────┘

Client
  │
  │ username + password
  ▼
LoginService
  │
  ├── UnitOfWork.begin()
  ├── UserRepository.get(username)
  ├── PasswordHasher.verify()
  ├── UserSession.create()
  ├── SessionRepository.add()
  ├── UnitOfWork.commit()
  └── TokenProvider.issue()
          │
          ├── Access Token
          └── Refresh Token
          
          
┌──────────────────────────────┐
│         Refresh Flow         │
└──────────────────────────────┘

Client
  │
  │ refresh token
  ▼
RefreshService
  │
  ├── UnitOfWork.begin()
  ├── TokenProvider.verify()
  ├── SessionRepository.get(session_id)
  ├── verify refresh_token_hash
  ├── UserSession.rotate_refresh_token()
  ├── UnitOfWork.commit()
  └── TokenProvider.issue()
          │
          ├── New Access Token
          └── New Refresh Token
  
Before refresh

UserSession
-------------------------
session_id = 123
username = john
refresh_hash = H1
revoked = false


After refresh

UserSession
-------------------------
session_id = 123
username = john
refresh_hash = H2
revoked = false


┌──────────────────────────────┐
│          Logout Flow         │
└──────────────────────────────┘

Client
  │
  │ access / refresh token
  ▼
LogoutService
  │
  ├── UnitOfWork.begin()
  ├── TokenProvider.verify()
  ├── SessionRepository.get(session_id)
  ├── UserSession.revoke()
  └── UnitOfWork.commit()
  
  
┌──────────────────────────────┐
│       Create User Flow       │
└──────────────────────────────┘

CLI / API
  │
  │ username + password
  ▼
CreateUserService
  │
  ├── UnitOfWork.begin()
  ├── UserRepository.exists()
  ├── PasswordHasher.hash()
  ├── User.create()
  ├── UserRepository.add()
  └── UnitOfWork.commit()
  
  
┌──────────────────────────────┐
│     Change Password Flow     │
└──────────────────────────────┘

CLI / API
  │
  │ username + new password
  ▼
ChangePasswordService
  │
  ├── UnitOfWork.begin()
  ├── UserRepository.get(username)
  ├── PasswordHasher.hash()
  ├── User.change_password()
  ├── SessionRepository.revoke_all(username)
  └── UnitOfWork.commit()
  
  
┌──────────────────────────────┐
│       Disable User Flow      │
└──────────────────────────────┘

CLI / API
  │
  │ username
  ▼
DisableUserService
  │
  ├── UnitOfWork.begin()
  ├── UserRepository.get(username)
  ├── User.disable()
  ├── SessionRepository.revoke_all(username)
  └── UnitOfWork.commit()


                    Domain Models
                    
User
----
username
password_hash
disabled
version


UserSession
-----------
session_id
username
refresh_token_hash
created_at
expires_at
revoked
version
```