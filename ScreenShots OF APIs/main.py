from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to SpeedRide Car Rentals"}



cars = [
    {"id": 1, "model": "Swift", "brand": "Maruti", "type": "Hatchback", "price_per_day": 1500, "fuel_type": "Petrol", "is_available": True},
    {"id": 2, "model": "City", "brand": "Honda", "type": "Sedan", "price_per_day": 2500, "fuel_type": "Petrol", "is_available": True},
    {"id": 3, "model": "Creta", "brand": "Hyundai", "type": "SUV", "price_per_day": 3000, "fuel_type": "Diesel", "is_available": True},
    {"id": 4, "model": "Fortuner", "brand": "Toyota", "type": "Luxury", "price_per_day": 6000, "fuel_type": "Diesel", "is_available": False},
    {"id": 5, "model": "Nexon", "brand": "Tata", "type": "SUV", "price_per_day": 2800, "fuel_type": "Electric", "is_available": True},
    {"id": 6, "model": "i20", "brand": "Hyundai", "type": "Hatchback", "price_per_day": 1800, "fuel_type": "Petrol", "is_available": True},
    {"id": 7, "model": "M430D Competition", "brand": "BMW", "type": "Luxury", "price_per_day": 7000, "fuel_type": "Diesel", "is_available": True},
    {"id": 8, "model": "Audi RS5", "brand": "Audi", "type": "Hatchback", "price_per_day": 5000, "fuel_type": "Petrol", "is_available": True},
    {"id": 9, "model": "XUV700", "brand": "Mahindra", "type": "SUV", "price_per_day": 4000, "fuel_type": "Diesel", "is_available": False},
    {"id": 10, "model": "Seltos", "brand": "kia", "type": "Hatchback", "price_per_day": 3000, "fuel_type": "Petrol", "is_available": True},]


# -------------------- Q3: GET ALL CARS --------------------

@app.get("/cars")
def get_cars():
    available = len([c for c in cars if c["is_available"]])
    return {"total": len(cars), "available_count": available, "cars": cars}


# -------------------- Q5: SUMMARY --------------------

@app.get("/cars/summary")
def cars_summary():
    total = len(cars)
    available = len([c for c in cars if c["is_available"]])

    type_count = {}
    fuel_count = {}

    for car in cars:
        type_count[car["type"]] = type_count.get(car["type"], 0) + 1
        fuel_count[car["fuel_type"]] = fuel_count.get(car["fuel_type"], 0) + 1

    cheapest = min(cars, key=lambda x: x["price_per_day"])
    expensive = max(cars, key=lambda x: x["price_per_day"])

    return {
        "total_cars": total,
        "available_count": available,
        "type_breakdown": type_count,
        "fuel_type_breakdown": fuel_count,
        "most_expensive_car": expensive,
        "cheapest_car": cheapest,
        
    }

# -------------------- Q10: FILTER --------------------


@app.get("/cars/filter")
def filter_cars(type: Optional[str] = None, brand: Optional[str] = None,
                fuel_type: Optional[str] = None, max_price: Optional[int] = None,
                is_available: Optional[bool] = None):
    result = cars

    if type:
        result = [c for c in result if c["type"].lower() == type.lower()]
    if brand:
        result = [c for c in result if c["brand"].lower() == brand.lower()]
    if fuel_type:
        result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]
    if max_price:
        result = [c for c in result if c["price_per_day"] <= max_price]
    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]

    return {"cars": result, "count": len(result)}

@app.get("/cars/sort")
def sort_cars(
    sort_by: str = "price_per_day",
    order: str = "asc"
):
  
    allowed_fields = ["price_per_day", "brand", "type"]

    if sort_by not in allowed_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Allowed: {allowed_fields}"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="order must be 'asc' or 'desc'"
        )

    reverse = True if order == "desc" else False

    sorted_cars = sorted(cars, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_cars),
        "cars": sorted_cars
    }
@app.get("/cars/page")
def paginate_cars(page: int = 1, limit: int = 3):


    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="page and limit must be greater than 0"
        )

    total = len(cars)

    
    start = (page - 1) * limit
    end = start + limit


    if start >= total:
        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "cars": []
        }

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "cars": cars[start:end]
    }
# -------------------- Q4: RENTALS --------------------


rentals = []
rental_counter = 1

@app.get("/rentals")
def get_rentals():
    return {"total": len(rentals), "rentals": rentals}


# -------------------- Q6: MODEL --------------------

class RentalRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    car_id: int = Field(..., gt=0)
    days: int = Field(..., gt=0, le=30)
    license: str = Field(..., min_length=5)
    driver_required: str = "Self"   # self or driver
    insurance: bool = False


# -------------------- HELPERS --------------------


def find_car(car_id: int):
    for car in cars:
        if car["id"] == car_id:
            return car
    return None


def calculate_rental_cost(price_per_day, days, insurance, driver_required):
    base_cost = price_per_day * days

    discount = 0
    if days >= 15:
        discount = 0.25 * base_cost
    elif days >= 7:
        discount = 0.15 * base_cost  

    insurance_cost = 500 * days if insurance else 0


    if driver_required == "Driver":
        driver_cost = 800 * days
    else:
        driver_cost = 0

    total = base_cost - discount + insurance_cost + driver_cost

    return {
        "base_cost": base_cost,
        "discount": discount,
        "insurance_cost": insurance_cost,
        "driver_cost": driver_cost,
        "total_cost": total
    }


# -------------------- CREATE RENTAL --------------------

@app.post("/rentals")
#def create_rental(request: RentalRequest):
def create_rental(data: RentalRequest):
    global rental_counter

    #car = find_car(request.car_id)
    car = find_car(data.car_id)

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    if not car["is_available"]:
        raise HTTPException(status_code=400, detail="Car not available")

    # mark unavailable
    car["is_available"] = False

    #cost = calculate_rental_cost(
        #car["price_per_day"],
        #request.days,
        #request.insurance,
        #request.driver_required)
    cost = calculate_rental_cost(
        car["price_per_day"],
        data.days,
        data.insurance,
        data.driver_required)
    

    #rental = {
        #"rental_id": rental_counter,
        #"customer_name": request.customer_name,
        #"license": request.license,
        #"car_model": car["model"],
        #"car_brand": car["brand"],
        #"days": request.days,
        #"insurance": request.insurance,
        #"driver_required": request.driver_required,
        #"driver_cost": cost["driver_cost"],
        #"base_cost": cost["base_cost"],
        #"discount": cost["discount"],
        #"insurance_cost": cost["insurance_cost"],
        #"total_cost": cost["total_cost"],
        #"car_available": car["is_available"],
        #"status": "active"}
    rental = {
        #"status": "Car Returned",
        "rental_id": rental_counter,
         "car_id": car["id"],
        "customer_name": data.customer_name,
        "license": data.license,
        "car_model": car["model"],
        "car_brand": car["brand"],
        "days": data.days,
        "insurance": data.insurance,
        "driver_required": data.driver_required,
        "driver_cost": cost["driver_cost"],
        "base_cost": cost["base_cost"],
        "discount": cost["discount"],
        "insurance_cost": cost["insurance_cost"],
        "total_cost": cost["total_cost"],
        "car_available": car["is_available"],
        "status": "active"}
    

    rentals.append(rental)
    car["is_available"] = False
    rental_counter += 1

    return rental


# -------------------- Q11: ADD CAR --------------------

class NewCar(BaseModel):
    model: str
    brand: str
    type: str
    price_per_day: int
    fuel_type: str
    is_available: bool = True


@app.post("/cars",status_code=201)
def add_car(car: NewCar, response: Response):
    for c in cars:
        if c["model"].lower() == car.model.lower():
            raise HTTPException(201, "Car already exists")

    new = car.dict()
    new["id"] = len(cars) + 1
    cars.append(new)

    response.status_code = 201
    return new


# -------------------- Q12: UPDATE --------------------

@app.put("/cars/{car_id}")
def update_car(car_id: int, price_per_day: int = None, is_available: bool = None):
    car = find_car(car_id)

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    if price_per_day is not None:
        car["price_per_day"] = price_per_day

    if is_available is not None:
        car["is_available"] = is_available

    return car



# -------------------- Q13: DELETE --------------------

@app.delete("/cars/{car_id}")
def delete_car(car_id: int):

    #car = next((c for c in cars if c["id"] == car_id), None)
    car = find_car(car_id)


    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    for r in rentals:
        if r.get("car_id") == car_id and r.get("status") == "active":
            raise HTTPException(
                status_code=400,
                detail="CannoT Delete Car is Rented in active status"
            )

    cars.remove(car)

    #return {"message": "Deleted", "car": car["model"]}

    return {"message": "Deleted", "car": car["model"]}


# -------------------- Q14: CART --------------------


cart = []
def find_rental(rental_id: int):
    for r in rentals:
        if r["rental_id"] == rental_id:
            return r
    return None
@app.post("/return/{rental_id}")
def return_car(rental_id: int):

    rental = find_rental(rental_id)

    if rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")

  
    if "status" not in rental:
        raise HTTPException(status_code=500, detail="Invalid rental data")

    if rental["status"] == "returned":
        raise HTTPException(status_code=400, detail="Car already returned")

    car_id = rental.get("car_id")
    if car_id is None:
        raise HTTPException(
            status_code=500,
            detail="car_id missing in rental (fix rental creation)"
        )

    car = find_car(car_id)

    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

   
    rental["status"] = "Car Returned"
    car["is_available"] = True
    rental["car_available"] = True

    return rental


# -------------------- Q15: CHECKOUT -------------------


@app.get("/rentals/active")
def get_active_rentals():
    active = [r for r in rentals if r.get("status") == "active"]
    return {
        "total": len(active),
        "rentals": active
    }
@app.get("/rentals/by-car/{car_id}")
def rentals_by_car(car_id: int):
    car = find_car(car_id)

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    result = [r for r in rentals if r.get("car_id") == car_id]

    return {
        "car_id": car_id,
        "total": len(result),
        "rentals": result
    }
@app.get("/cars")
def get_cars():
    return {"total": len(cars), "cars": cars}


@app.get("/cars/search")  
def search_cars(keyword: str):
    keyword = keyword.lower()

    result = [
        c for c in cars
        if keyword in c["model"].lower()
        or keyword in c["brand"].lower()
        or keyword in c["type"].lower()
    ]

    return {
        "keyword": keyword,
        "total_found": len(result),
        "cars": result
    }
@app.get("/cars/unavailable")
def get_unavailable_cars():
    result = [c for c in cars if not c["is_available"]]

    return {
        "total": len(result),
        "cars": result
    }

    
# -------------------- Q20: BROWSE --------------------

@app.get("/cars/browse")
def browse_cars(
    keyword: Optional[str] = None,
    type: Optional[str] = None,
    fuel_type: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None,
    sort_by: str = "price_per_day",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = cars
    # -SEARCH 
    if keyword:
        k = keyword.lower()
        result = [
            c for c in result
            if k in c["model"].lower()
            or k in c["brand"].lower()
            or k in c["type"].lower()
        ]

    # Filter


    if type:
        result = [c for c in result if c["type"].lower() == type.lower()]

    if fuel_type:
        result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]

    if max_price:
        result = [c for c in result if c["price_per_day"] <= max_price]

    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]

    
    # ----------------Sort----------------
    
    allowed_sort = ["price_per_day", "brand", "type"]

    if sort_by not in allowed_sort:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Allowed: {allowed_sort}"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="order must be 'asc' or 'desc'"
        )

    reverse = order == "desc"
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)



    # ----------------Pagination FOr Car ----------------


    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="page and limit must be greater than 0"
        )

    total = len(result)
    start = (page - 1) * limit
    end = start + limit

    paginated = result[start:end]    
    return {
        "sorting": {
            "sort_by": sort_by,
            "order": order,
            "Page":page,
            "Total_Page":total,
            "Limit":limit
        },
        "cars": paginated}

    
# -------------------- Q19: RENTAL SEARCH --------------------

@app.get("/rentals/search")
def search_rentals(name: str):
    keyword = name.lower()

    result = [
        r for r in rentals
        if keyword in r["customer_name"].lower()
    ]

    return {
        "keyword": name,
        "total_found": len(result),
        "rentals": result
    }

@app.get("/rentals/sort")
def sort_rentals(
    sort_by: str = "total_cost",
    order: str = "asc"
):
    allowed = ["total_cost", "days"]

    if sort_by not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Allowed: {allowed}"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="order must be 'asc' or 'desc'"
        )

    reverse = order == "desc"

    sorted_list = sorted(rentals, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_list),
        "rentals": sorted_list
    }

@app.get("/rentals/page")
def paginate_rentals(page: int = 1, limit: int = 3):

    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="page and limit must be greater than 0"
        )

    total = len(rentals)
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "rentals": rentals[start:end]
    }
@app.get("/cars/{car_id}")
def get_car(car_id: int):
    car = next((c for c in cars if c["id"] == car_id), None)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car
