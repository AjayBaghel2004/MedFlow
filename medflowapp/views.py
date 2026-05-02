from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.http import request, JsonResponse
from django.db import transaction
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from .models import Employee, Medicine, Customer
import traceback
# Create your views here.
def register(request):
    return render(request, 'medflowapp/register.html')

def login(request):
    return render(request, 'medflowapp/login.html')

@login_required(login_url='/login/')
def dashboard(request):
    total_medicines = Medicine.objects.count() #Total Medicines in inventory
    low_stock_count = Medicine.objects.filter(quantity__lt=10).count()
    today = timezone.now().date() # today sales revenue
    today_sales = Sale.objects.filter(created_at__date = today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    next_month = today + timezone.timedelta(days=30)
    #expiring Soon  in the nxt 30 days
    expiring_soon = Medicine.objects.filter(expiry_date__range = [today, next_month]).count()
    # Recent critical alerts
    critical_medicines = Medicine.objects.filter(quantity__lt=5)[:5]

    context = {
        "total_medicines":total_medicines,
        "low_stock_count":low_stock_count,
        "today_sales":today_sales,
        "expiring_soon": expiring_soon,
        "critical_medicines":critical_medicines,
    }

    #weekly sales data for Chart
    last_7_days =[]
    sales_data = []
    today = timezone.now().date()
    for i in range(6,-1,-1):
        day = today - timedelta(days=i)
        last_7_days.append(day.strftime("%a"))
        # Sum total_amount for all sales on this specific day
        daily_total = Sale.objects.filter(created_at__date=day).aggregate(Sum("total_amount"))['total_amount__sum'] or 0
        sales_data.append(float(daily_total))

        context.update({
            "chart_labels":last_7_days,
            "chart_data":sales_data,
        })

    return render(request, "medflowapp/dashboard.html", context)

def medicine(request):
    medicines = Medicine.objects.all()
    return render(request, 'medflowapp/medicine_section.html', {"medicines": medicines})

def pos_billing(request):
    customer_details = Customer.objects.all()
    medicine = Medicine.objects.all()
    return render(request, 'medflowapp/POS_section.html', {"customer_details":customer_details , "medicine":medicine})

def inventory(request):
    return render(request, 'medflowapp/inventory.html')

def purchases(request):
    return render(request, 'medflowapp/purchases_section.html')

def reports_section(request):
    return render(request, 'medflowapp/report_section.html')

def register_user(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            email= request.POST.get('email')
            role = request.POST.get('role')
            password = request.POST.get('password')
            # Validation: Ensure email is unique
            if Employee.objects.filter(email=email).exists():
                return JsonResponse({"status": 400 , "message":"Email already Registered"})
            user = Employee.objects.create_user(
                username = email,
                email=email,
                password=password,
                first_name = name,
                role=role,
            )
            return JsonResponse({"status":200 , "message":"Account Created Successfully"})
        except Exception as e:
            return JsonResponse({"status": 500, "message":str(e)})

@csrf_exempt
def login_user(request):
    if request.method=="POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        #Django`s authenticate function handles the hashed password comparison
        user = authenticate(request, username=email, password=password)
        if user is not None:
            #This Creates the session and logs the user in properly
            auth_login(request user)
            return JsonResponse({"status": 200})
        else:
            return JsonResponse({"status":403, "message": "Invalid Credentials"})

@csrf_exempt
def add_medicine(request):
    data = request.POST.dict()
    print(data)
    Medicine.objects.create(medicine_name = data['medicine_name'], expiry_date=data['expiry_date'], med_category=data['category'], price=data['price'], quantity=data['quantity'])
    return JsonResponse({'status': 200})

@csrf_exempt
def delete_medicine(request):
    data=request.POST.dict()
    med_ID = Medicine.objects.get(id=data['medicine_ID'])
    med_ID.delete()
    return JsonResponse({"status": 200})

def update_medicine_page(request, medicineid):
    medicine_ID = Medicine.objects.get(id=medicineid)
    print(f"Medicine ID : {medicine_ID}")
    return render(request, 'medflowapp/update_medicine.html', {"medicine_ID":medicine_ID})
    
@csrf_exempt
def update_med_info(request):
    try:
        data=request.POST.dict()
        print(f"data: {data}")
        medicine = Medicine.objects.get(id=data['med_ID'])
        medicine.price = data['price']
        medicine.quantity=data['quantity']
        medicine.expiry_date=data['expiry_date']
        medicine.stock_status=data['stock_status']
        medicine.save()
        return JsonResponse({"status":200})
    except:
        import traceback
        traceback.print_exc()

@csrf_exempt
def add_customer(request):
    data=request.POST.dict()
    print(f"Customer Data : {data}")
    Customer.objects.create(customer_name=data['customer_name'], customer_phone=data['phone_number'])
    return JsonResponse({"status":200})

@csrf_exempt
def remove_customer(request):
    data=request.POST.dict()
    customer_ID = Customer.objects.get(id=data['customer_ID'])
    customer_ID.delete()
    return JsonResponse({"status":200})

@transaction.atomic
def complete_sale_view(request):
    if request.method =='POST':
        data = json.loads(request.body)
        #1.Get or set Customer
        cus_ID = data.get('customer_id')
        customer = Customer.objects.filter9(id=cus_ID).first() if cus_ID else None

        #2. create Sale
        sale = Sale.objects.create(
            customer=customer,
            user=request.user,
            subtotal=data['subtotal'],
            gst_amount=data['gst'],
            total_amount=data['total']
        )
        #3. Create sale Items and Reduce Stock
        for item in data['items']:
            medicine=Medicine.objects.get(medicine_name=item['name'])
            #Stock check
            if medicine.quantity < item['qty']:
                transaction.set_rollback(True)
                return JsonResponse({"status": "error", "message":f"Low stock for {medicine.medicine_name}"},status=400)
            
            SaleItem.objects.create(
                medicine_ID=medicine,
                sale_ID=sale,
                quantity_sold=item['qty'],
                unit_price=item['price'],
                total_price=item['total']
            )
            #Deduct Inventory
            medicine.quantity -= int(item['qty'])
            medicine.save()
        return JsonResponse({"status":"success", "invoice": sale.id})