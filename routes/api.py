from fastapi import APIRouter

router = APIRouter()

@router.get("/api/cancelorder/{orderId}")
def cancel_order(orderId):
    return {"Message": "Order successfully canceled.", "OrderID": orderId}

@router.get("/api/vieworder/{orderId}")
def view_order(orderId):
    return {"OrderID": "286234131", "OpenedDateTime": "2021-02-24T15:47:45Z", "OrderType": "Market"}

@router.get("/api/updatebalances")
def view_order():
    return {"data":[
        {'AccountID':'12345678','CashBalance':'9000'},
        {'AccountID':'12345678','CashBalance':'9000'},
        {'AccountID':'12345678','CashBalance':'9000'},
        {'AccountID':'12345678','CashBalance':'9000'},
        {'AccountID':'12345678','CashBalance':'9000'},
        {'AccountID':'12345678','CashBalance':'9000'}
        ]}