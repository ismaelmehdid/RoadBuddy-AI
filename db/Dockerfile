FROM postgres:16

# Environment variables for PostgreSQL configuration
ENV POSTGRES_DB=telegram_bot
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Expose PostgreSQL port
EXPOSE 5432

# Add custom PostgreSQL configuration
COPY postgresql.conf /etc/postgresql/postgresql.conf

# Use custom configuration
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
