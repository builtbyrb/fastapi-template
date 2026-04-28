# SERVICES_DECISION_MATRIX.md

This document serves as a reference guide for technological choices in freelance projects. It provides a framework to quickly arbitrate between **Control (DIY/Self-hosted)** and **Velocity (Managed/BaaS)**.

### A. Database
*Goal: Data persistence and business integrity.*

| Option | Type | Pros | Cons | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Option A** | Self-Hosted (Postgres + Docker) | Full control, zero licensing/usage cost, portable. | You manage backups, maintenance, and failover. | Production-grade (Sovereign) |
| **Option B** | Cloud Provider Managed (e.g. Azure DB) | Automated backups, high security compliance. | Monthly recurring costs, vendor lock-in. | Production-grade (Corporate/Enterprise) |
| **Option C** | BaaS Managed (Supabase/AWS RDS) | Dashboard UI, High Availability, "Set and forget". | Costs scale quickly, vendor lock-in. | MVP / Rapid development |

**Verdict:** - Choose **Option A** for the "Sovereign" approach: Maximum control, predictable fixed costs, and total data privacy. Ideal for long-term production apps where you act as the Infrastructure Manager.
- Choose **Option B** when the client has specific compliance requirements (Corporate policy).
- Choose **Option C** for rapid prototyping (MVP) or when the client explicitly asks to offload infrastructure management.

### B. Authentication
*Goal: Secure access management, identity verification, and RBAC.*

| Option | Type | Pros | Cons | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Option A** | Custom (JWT + SQL + Argon2) | Full control, zero external dependency, free, 100% portable. | Requires writing boilerplate (token logic, reset flows). | Production-grade (Sovereign) |
| **Option B** | Managed (Supabase Auth / Auth0) | Instant setup, Social Login/SSO, Magic Links. | Vendor lock-in, costs scale with users, remote dependency. | MVP / Fast Time-to-Market |

**Verdict:** - Choose **Option A** for the "Sovereign" approach: You own the user data and the entire auth logic. Perfect for long-term production apps where data privacy and decoupling are critical. Since you use Hexagonal Architecture, this implementation is just an `AuthAdapter`.
- Choose **Option B** only if the client has extreme short-term deadlines or requires complex social login/SSO integration that would take too much time to build custom (though it can be migrated later).

### C. Storage
*Goal: Managing user-generated assets, documents, and media files.*

| Option | Type | Pros | Cons | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Option A** | Self-Hosted (MinIO) | S3-compatible, total privacy, zero egress fees, portable. | You manage the volume size and hardware backups. | Production-grade (Sovereign) |
| **Option B** | Cloud Provider (R2 / S3) | Infinite scalability, global CDN performance, zero maintenance. | Recurring monthly fees, vendor lock-in, IAM complexity. | High-traffic / Public assets |

**Verdict:** - Choose **Option A** for the "Sovereign" approach: Keep your data on your own infrastructure. It is S3-compatible, meaning your code uses the *exact same* SDK regardless of the backend. It's the best way to keep costs fixed and data 100% under your control.
- Choose **Option B** only when the application reaches a scale where serving media directly from your VPS (via MinIO) creates bandwidth bottlenecks. Even then, your code remains untouched because of the S3-compatible interface.

### D. Backups (Disaster Recovery)
*Goal: Ensure business continuity and prevent data loss.*

| Option | Type | Pros | Cons | Risk Level |
| :--- | :--- | :--- | :--- | :--- |
| **Option A** | Local Redundancy (DB to MinIO) | Instant/Free, easy to setup. | Single point of failure: If the server fails, backups are lost. | High (Critical) |
| **Option B** | Sovereign + Remote (MinIO to Cloud) | Follows 3-2-1 rule, highly resilient, disaster-proof. | Requires setting up a sync task (e.g., Rclone). | Low (Safe) |

**Verdict:** - Choose **Option A** only for non-critical development environments. It is effectively a "snapshot" and not a real backup solution.
- Choose **Option B** for all production applications. It is your professional standard:
    1. Dump DB to local MinIO.
    2. Sync the entire MinIO bucket (files + dumps) to an offsite location (e.g., Backblaze B2, AWS S3, or any Cloud provider) via Rclone.
    
This approach guarantees that even if your entire infrastructure is destroyed (fire, theft, server hardware failure), you can fully restore the application on a new server in minutes.

### E. Email & Notifications
*Goal: Transactional emails, marketing newsletters, and user alerts.*

| Option | Type | Pros | Cons | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Option A** | Sovereign Logic (Listmonk + SMTP Relay) | Full control of data/templates, low cost, portable. | Requires managing SMTP credentials/DNS (SPF/DKIM). | Production-grade |
| **Option B** | Fully Managed (Resend / SendGrid / AWS SES) | Extremely high deliverability, zero maintenance. | Expensive, heavy vendor lock-in, data privacy loss. | MVP / High volume |

**Verdict:** - Choose **Option A** for the "Sovereign" approach: Host **Listmonk** (or your own notification service) in Docker. Connect it to a professional SMTP relay (like AWS SES or a similar reputable provider). You keep your subscriber lists and email templates under your control, but you outsource the "deliverability" to an expert so your emails don't go to spam.
- Choose **Option B** if you need complex analytics, pre-built high-level dashboards, or have zero time to manage SMTP configurations.

### F. Infrastructure & Deployment
*Goal: Application availability, monitoring, and SSL management.*

| Option | Type | Pros | Cons | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Option A** | Manual VPS (Docker Compose) | No extra layer, full control, minimal resources. | High overhead for SSH/Logs/Deploy management. | Minimalist |
| **Option B** | Orchestrated (Coolify + Docker Compose) | GitOps, UI/Logs convenience + Total file control. | Slight extra resource usage. | Default Standard |

**Verdict:** - Choose **Option B**. Treat your `docker-compose.yml` as the "Source of Truth" for all configurations (networks, services, Traefik, volumes). Use Coolify solely as an orchestrator to manage container lifecycles, view logs, and trigger deployments. This ensures you maintain full technical control via your own files while benefiting from a modern dashboard interface.