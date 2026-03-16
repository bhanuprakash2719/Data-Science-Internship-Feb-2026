from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

# -------------------------------
# PRODUCTS DATABASE
# -------------------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 299, "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True},
]

# -------------------------------
# CART + ORDERS
# -------------------------------
cart = []
orders = []
order_counter = 1


# -------------------------------
# MODELS
# -------------------------------
class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


# -------------------------------
# HELPER FUNCTION
# -------------------------------
def calculate_total(product, quantity):
    return product["price"] * quantity


# -------------------------------
# ADD TO CART
# -------------------------------
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    # find product
    product = None
    for p in products:
        if p["id"] == product_id:
            product = p
            break

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # check stock
    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )

    # check if already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_total(product, item["quantity"])

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    # new item
    subtotal = calculate_total(product, quantity)

    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


# -------------------------------
# VIEW CART
# -------------------------------
@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


# -------------------------------
# REMOVE FROM CART
# -------------------------------
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)

            return {
                "message": "Item removed from cart",
                "removed_item": item
            }

    raise HTTPException(status_code=404, detail="Item not found in cart")


# -------------------------------
# CHECKOUT
# -------------------------------
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    global order_counter

    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    created_orders = []
    grand_total = 0

    for item in cart:
        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "delivery_address": data.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }

        orders.append(order)
        created_orders.append(order)

        grand_total += item["subtotal"]
        order_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": created_orders,
        "grand_total": grand_total
    }


# -------------------------------
# VIEW ORDERS
# -------------------------------
@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }