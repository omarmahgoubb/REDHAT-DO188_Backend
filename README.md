# 🖥️ Backend - Delivery Management System

## 📖 Overview

Welcome to the **Backend** for the Delivery Management System 🚚📦!  
This service powers the core operations for **users, couriers, and admins**, including:

- 📲 User Registration & Authentication
- 📦 Order Creation, Tracking & Management
- 🚛 Courier Order Assignments & Status Updates
- 🛡️ Admin Order Monitoring & Control

This backend exposes a clean set of **RESTful APIs**, making it easy for the frontend to interact with the system. Built for **scalability, flexibility, and reliability**.

---

## 🚀 Features

### ✅ User Features
- 👤 **Register New User**: Create a new user account with email, phone, and password.
- 🔐 **User Login**: Authenticate and receive a secure token.
- 📝 **Create Order**: Submit order details including pickup, drop-off, and package info.
- 📋 **View My Orders**: Retrieve a list of the user’s orders with statuses.
- 🔎 **View Order Details**: Get full details of a specific order.
- ❌ **Cancel Order**: Cancel orders that are still pending.

### 🚚 Courier Features
- 📥 **View Assigned Orders**: See all orders assigned to the courier.
- 🔄 **Accept/Decline Order**: Accept or decline new assignments.
- 🚦 **Update Order Status**: Update status (Picked Up, In Transit, Delivered).

### 🛡️ Admin Features
- 📊 **Manage All Orders**: View all orders in a central table.
- ✍️ **Update Order Status**: Admin can change order statuses directly.
- 🗑️ **Delete Orders**: Remove any problematic orders.
- 📌 **Assign/Reassign Orders to Couriers**: Direct control over who handles which delivery.

---

## 📚 Tech Stack

| 🛠️ Technology | 📋 Description |
|---|---|
| 🐍 Python (or Node.js) | Backend Language |
| ⚙️ Flask/Express | REST API Framework |
| 🗄️ MongoDB/PostgreSQL | Database |
| 🔐 JWT | Authentication |
