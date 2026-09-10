"""
Campus Food Delivery and Order Management System
A simple console application for managing food orders
"""

import json
import os
from datetime import datetime

# data

# the predefined menu with categories (prices in Uganda Shillings)
MENU = {
    "Meals": {
        "Liver": 12000,
        "Sandwich": 10000,
        "Chicken": 8000,
        "Sausages": 5000
    },
    "Drinks": {
        "Soda": 2000,
        "Coffee": 3000,
        "Juice": 4000
    },
    "Snacks": {
        "Burger": 10000,
        "Samosas": 3000,
        "Rolex": 3000
    }
}

# available riders
RIDERS = ["Elobu", "Nafuna", "Mukisa", "Asimwe"]

# global variables
orders = []
order_counter = 1
ORDER_FILE = "orders_log.json"

# file handling

def load_orders():
    """Load existing orders from JSON file on program start"""
    global orders, order_counter
    if os.path.exists(ORDER_FILE):
        try:
            with open(ORDER_FILE, 'r') as f:
                data = json.load(f)
                orders = data.get('orders', [])
                order_counter = data.get('next_id', 1)
        except (json.JSONDecodeError, IOError):
            print("Warning: Could not read orders file. Starting fresh.")
            orders = []
            order_counter = 1
    else:
        orders = []
        order_counter = 1

def save_orders():
    """Save all orders to JSON file"""
    try:
        with open(ORDER_FILE, 'w') as f:
            json.dump({'orders': orders, 'next_id': order_counter}, f, indent=2)
    except IOError:
        print("Error: Could not save orders to file.")

# order taking

def display_menu():
    """Show the full menu with categories and prices"""
    print("\n" + "="*50)
    print("         CAMPUS FOOD MENU")
    print("="*50)
    for category, items in MENU.items():
        print(f"\n{category}:")
        for item, price in items.items():
            print(f"  {item}: UGX {price:,}")
    print("="*50)

def take_order():
    """Let user select items and quantities, return order details"""
    global order_counter
    
    display_menu()
    
    order_items = []
    subtotal = 0
    
    while True:
        print("\nEnter item name (or 'done' to finish):")
        item_name = input("> ").strip().title()
        
        if item_name.lower() == 'done':
            if order_items:
                break
            else:
                print("You must order at least one item!")
                continue
        
        # find item in menu
        found = False
        for category in MENU.values():
            if item_name in category:
                price = category[item_name]
                found = True
                break
        
        if not found:
            print(f"'{item_name}' not found on menu. Please try again.")
            continue
        
        # get quantity
        while True:
            try:
                qty = int(input(f"Quantity of {item_name}: "))
                if qty > 0:
                    break
                print("Quantity must be positive.")
            except ValueError:
                print("Please enter a valid number.")
        
        # add to order
        item_total = price * qty
        order_items.append({
            'item': item_name,
            'qty': qty,
            'price': price,
            'total': item_total
        })
        subtotal += item_total
        print(f"Added {qty}x {item_name} (UGX {item_total:,})")
    
    # get delivery distance
    while True:
        try:
            distance = float(input("\nEnter delivery distance in km: "))
            if distance >= 0:
                break
            print("Distance cannot be negative.")
        except ValueError:
            print("Please enter a valid number.")
    
    # creating an order dictionary
    order = {
        'id': order_counter,
        'items': order_items,
        'subtotal': subtotal,
        'distance': distance,
        'status': 'Pending',
        'rider': None,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    order_counter += 1
    
    return order

# delivery fee

def calculate_delivery_fee(distance):
    """Calculate delivery fee based on distance band (in UGX)"""
    if distance <= 2.0:
        return 2000
    elif distance <= 5.0:
        return 5000
    elif distance <= 10.0:
        return 8000
    else:
        return 12000

# assigning a rider

def assign_rider(order):
    """Assign a rider to a pending order"""
    if order['status'] != 'Pending':
        print(f"Order #{order['id']} is already {order['status']}")
        return False
    
    # finding the available rider (not currently assigned to active orders)
    active_riders = [o['rider'] for o in orders if o['status'] in ['Pending', 'Out for Delivery'] and o['rider']]
    available_riders = [r for r in RIDERS if r not in active_riders]
    
    if not available_riders:
        print("No riders available. Please try again later.")
        return False
    
    rider = available_riders[0]
    order['rider'] = rider
    order['status'] = 'Out for Delivery'
    print(f"Rider {rider} assigned to Order #{order['id']}")
    return True

# status management

def update_status(order):
    """Update order status (Pending → Out for Delivery → Delivered)"""
    if order['status'] == 'Pending':
        print(f"Order #{order['id']} is Pending. Assign a rider first.")
        assign_rider(order)
    
    elif order['status'] == 'Out for Delivery':
        order['status'] = 'Delivered'
        print(f"Order #{order['id']} marked as Delivered!")
        save_orders()
    
    elif order['status'] == 'Delivered':
        print(f"Order #{order['id']} is already Delivered.")
    
    else:
        print(f"Unknown status for Order #{order['id']}")

# reportings

def generate_report():
    """Generate and display daily reports"""
    if not orders:
        print("\nNo orders found.")
        return
    
    completed = [o for o in orders if o['status'] == 'Delivered']
    
    # the total revenue from completed orders
    total_revenue = sum(o['subtotal'] + calculate_delivery_fee(o['distance']) for o in completed)
    
    # finding the best selling item
    item_sales = {}
    for order in orders:
        for item in order['items']:
            name = item['item']
            if name in item_sales:
                item_sales[name] = item_sales[name] + item['qty']
            else:
                item_sales[name] = item['qty']
    
    # determine the winner
    best_item = "None"
    best_count = 0
    for item, count in item_sales.items():
        if count > best_count:
            best_count = count
            best_item = item
    best_seller = (best_item, best_count)
    
    # status counts
    status_counts = {
        'Pending': 0,
        'Out for Delivery': 0,
        'Delivered': 0
    }
    for order in orders:
        if order['status'] in status_counts:
            status_counts[order['status']] = status_counts[order['status']] + 1
    
    # display report
    print("\n" + "="*50)
    print("              DAILY REPORT")
    print("="*50)
    print(f"Total Revenue: UGX {total_revenue:,}")
    print(f"Best Selling Item: {best_item} ({best_count} units)")
    print(f"\nOrder Status:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    print("="*50)

# the main menu

def view_all_orders():
    """Display all orders with details"""
    if not orders:
        print("\nNo orders yet.")
        return
    
    print("\n" + "="*60)
    print("                   ALL ORDERS")
    print("="*60)
    for order in orders:
        print(f"\nOrder #{order['id']} | Status: {order['status']}")
        print(f"Time: {order['timestamp']}")
        print(f"Distance: {order['distance']} km")
        print("Items:")
        for item in order['items']:
            print(f"  {item['qty']}x {item['item']} @ UGX {item['price']:,} = UGX {item['total']:,}")
        fee = calculate_delivery_fee(order['distance'])
        print(f"Subtotal: UGX {order['subtotal']:,}")
        print(f"Delivery Fee: UGX {fee:,}")
        print(f"Total: UGX {order['subtotal'] + fee:,}")
        if order['rider']:
            print(f"Rider: {order['rider']}")
    print("="*60)

def main():
    """Main menu loop"""
    load_orders()
    
    while True:
        print("\n" + "="*35)
        print("  CAMPUS FOOD DELIVERY SYSTEM")
        print("="*35)
        print("1. View Menu")
        print("2. Place New Order")
        print("3. View All Orders")
        print("4. Update Order Status")
        print("5. Generate Report")
        print("6. Exit")
        print("="*35)
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == '1':
            display_menu()
        
        elif choice == '2':
            new_order = take_order()
            fee = calculate_delivery_fee(new_order['distance'])
            total = new_order['subtotal'] + fee
            print(f"\nOrder #{new_order['id']} placed!")
            print(f"Subtotal: UGX {new_order['subtotal']:,}")
            print(f"Delivery Fee: UGX {fee:,} (for {new_order['distance']} km)")
            print(f"Total: UGX {total:,}")
            orders.append(new_order)
            save_orders()
            # Auto-assign rider if available
            assign_rider(new_order)
            save_orders()
        
        elif choice == '3':
            view_all_orders()
        
        elif choice == '4':
            if not orders:
                print("\nNo orders to update.")
                continue
            try:
                order_id = int(input("Enter order ID: "))
                # Find the order by ID
                order = None
                for o in orders:
                    if o['id'] == order_id:
                        order = o
                        break
                if order:
                    update_status(order)
                    save_orders()
                else:
                    print(f"Order #{order_id} not found.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '5':
            generate_report()
        
        elif choice == '6':
            save_orders()
            print("\nThank you for using Campus Food Delivery System!")
            break
        
        else:
            print("Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()