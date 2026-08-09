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
                    │                            │
                    │        AuthService         │
                    │        UserService         │
                    │                            │
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

 SQLUnitOfWork          SQLRepositories          PasetoTokenProvider
                            (User / Session)

                SQL Mapper  Identity Map    Snapshot

                      Argon2PasswordHasher

                            SQL Database


┌──────────────────────────────┐
│          Login Flow          │
└──────────────────────────────┘

Client
  │
  │ username + password
  ▼
AuthService
  │
  ├── UnitOfWork.begin()
  ├── UserRepository.get(username)
  ├── PasswordHasher.verify()
  ├── Session.create()
  ├── TokenProvider.issue()
  ├── PasswordHasher.hash(refresh_token)
  ├── Session.rotate_refresh_token(refresh_token_hash)
  ├── SessionRepository.add()
  └── UnitOfWork.commit()
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
AuthService
  │
  ├── UnitOfWork.begin()
  ├── TokenProvider.verify_refresh()
  ├── SessionRepository.get(session_id)
  ├── PasswordHasher.verify(refresh_token, refresh_token_hash)
  ├── TokenProvider.issue()
  ├── PasswordHasher.hash(new_refresh_token)
  ├── Session.rotate_refresh_token(new_refresh_token_hash)
  └── UnitOfWork.commit()
          │
          ├── New Access Token
          └── New Refresh Token
  
Before refresh

Session
-------------------------
session_id = 123
username = john
refresh_hash = H1
revoked = false


After refresh

Session
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
  │ refresh token
  ▼
AuthService
  │
  ├── UnitOfWork.begin()
  ├── TokenProvider.verify_refresh()
  ├── SessionRepository.get(session_id)
  ├── Session.revoke()
  └── UnitOfWork.commit()
  
  
┌──────────────────────────────┐
│       Create User Flow       │
└──────────────────────────────┘

CLI / API
  │
  │ username + password
  ▼
UserService
  │
  ├── UnitOfWork.begin()
  ├── UserRepository.user_exists()
  ├── PasswordHasher.hash()
  ├── User.create()
  ├── UserRepository.add()
  └── UnitOfWork.commit()
          │
          ├── User ID
          └── Username
          
          
┌──────────────────────────────┐
│       Disable User Flow      │
└──────────────────────────────┘

CLI / API
  │
  │ username
  ▼
UserService
  │
  ├── UnitOfWork.begin()
  ├── UserRepository.get(username)
  ├── User.disable()
  ├── SessionRepository.revoke_all(user.user_id)
  └── UnitOfWork.commit()          
          
          
┌──────────────────────────────┐
│     Change Password Flow     │
└──────────────────────────────┘

CLI / API
  │
  │ username + old password + new password
  ▼
UserService
  │
  ├── UnitOfWork.begin()
  ├── UserRepository.get(username)
  ├── PasswordHasher.verify(old password)
  ├── PasswordHasher.hash(new password)
  ├── User.change_password()
  └── UnitOfWork.commit()
  

                    Domain Models
                    
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