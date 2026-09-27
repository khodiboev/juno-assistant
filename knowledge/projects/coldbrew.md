# Project: ColdBrew — Coffee Shop E-commerce

## Summary
ColdBrew is a full-stack e-commerce application for a coffee shop. Customers browse the menu, add products to a basket, place and pay for orders and track them; the shop owner manages products and users through a separate admin panel.
Live site: http://187.127.220.109:3000

## Origin
ColdBrew was built while following a teacher-led course. Juno extended and redesigned it: a new homepage, a dark coffee-themed UI, admin-panel bug fixes (file uploads, search, profile pictures) and deployment to his own server.

## Tech stack
- Backend: Node.js, Express, TypeScript, MongoDB with Mongoose, MVC architecture
- Admin panel: server-side rendered with EJS
- Authentication: JWT for customers and sessions for the admin panel
- Frontend: React 18, TypeScript, Redux Toolkit with selectors, React Context, React Router, MUI, axios
- Deployment: Ubuntu VPS with PM2

## Key features
- Product catalog with categories, search, sorting, pagination and a "Barista's Pick" section
- Product detail page with an image slider
- Basket stored in the browser
- Full order lifecycle: paused, in process and finished, with automatic updates
- Loyalty points added to the customer after payment
- User profile editing with image upload
- Admin panel for products and users

## Architecture in one example — buying a coffee
The customer opens the menu, the React app requests products from the Express REST API, adds items to the basket, places an order (the backend creates the order and its items), pays (the status changes to "process" and the user receives a point), and the admin sees the order in the EJS admin panel.

## What Juno learned
Designing a clean MVC backend, using two kinds of authentication for two audiences, and deciding when to use Redux versus React Context for global state.
