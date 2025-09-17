# Inventory Tracking API

A FastAPI-based CRUD application for inventory management system built by Stephen.

## Features

- **Categories Management**: Create, read, update, delete product categories
- **Suppliers Management**: Manage supplier information and contacts
- **Products Management**: Complete product lifecycle management
- **Inventory Tracking**: Real-time stock level monitoring
- **Low Stock Alerts**: Automatic identification of products needing restock

## Database Schema

The system uses MySQL with the following entities:

- Categories (One-to-Many with Products)
- Suppliers (One-to-Many with Products)
- Products (One-to-One with Inventory)
- Inventory (tracks current stock levels)
- Purchase Orders & Items (for stock management)

## Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL Server
- Git

### Installation Steps

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd inventory-tracking-api
```
