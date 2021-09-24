def authenticated(session):
    return session.get("id") or session.get("idAdmin")

#buscar alternativa mas segura
