# Auth JWT

Rotas:

- `POST /api/auth/login`
- `GET /api/auth/me`

Login usa email e senha locais. O JWT contem:

- `sub`
- `role`
- `store_id`
- `exp`

Roles permitidas no MVP:

- `admin`
- `manager`
- `salesperson`

Nao ha refresh token, reset de senha ou provedor externo de auth no MVP.
