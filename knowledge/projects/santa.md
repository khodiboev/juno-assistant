# Project: Santa (VMotors) — Online Car Marketplace

## Summary
Santa is a full-stack online marketplace for new Hyundai and Kia cars aimed at the South Korean market. Buyers browse and search a vehicle catalog, like and comment on cars, and message dealers; dealers manage their own listings; admins moderate everything through an admin panel. It is Juno's largest project.
Live site: http://santacar.tech

## Origin
The project started from "Nestar", a real-estate platform template built in a teacher-led course. Juno rebuilt it module by module into a car marketplace: new domain models, new pages, a redesigned homepage and many new features. Some traces of the original template remain in naming, which he documented honestly in his code review.

## Tech stack
- Backend: NestJS monorepo with two apps — vmotors-api (the GraphQL API) and vmotors-batch (scheduled background jobs), MongoDB with Mongoose
- API: GraphQL
- Frontend: Next.js 14 (pages router), Apollo Client, Apollo reactive variables for global state (instead of Redux), MUI, SCSS, Framer Motion, next-i18next (English and Korean)
- Real-time: native WebSocket for notifications and chat
- Deployment: Ubuntu VPS, Docker, Nginx reverse proxy, custom domain santacar.tech

## Key features
- Vehicle catalog with filters (brand, fuel type, transmission) and pagination
- Vehicle detail page with optimistic "like", comments and "message the dealer"
- Three user roles: buyer, dealer (agent) and admin; dealers are promoted only by an admin
- MyPage personal dashboard with a Telegram-style real-time chat (the largest component in the project)
- Community forum with a WYSIWYG editor, FAQ and notice pages
- "Santa Assistant" — a rule-based helper chatbot (not an LLM)
- Admin panel for members, vehicles, community posts and notices
- Homepage with a 3D "orbital" carousel that respects reduced-motion settings
- English and Korean interface

## Challenges and what Juno learned
- Migrating a large codebase to a new domain step by step without breaking it
- Keeping real-time WebSocket chat and notifications working alongside the GraphQL API
- Deploying a monorepo (two backend apps plus a Next.js frontend) to a single VPS with Docker and Nginx, including DNS configuration for the domain
- Auditing his own code: his written review lists concrete issues he found (dead code, duplicated design tokens, an environment-variable bug) and which ones are the highest priority to fix
