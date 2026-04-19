from django.shortcuts import render, redirect
from django.http import request, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee, Medicines, Customers
import traceback
# Create your views here.
def register(request):
    return render(request, 'medflowapp/register.html')

def login(request):
    return render(request, 'medflowapp/login.html')

def dashboard(request):
    if request.session.get('userId'):
        return render(request, 'medflowapp/dashboard.html')
    else:
        redirect('/')

def medicine(request):
    medicines = Medicines.objects.all()
    return render(request, 'medflowapp/medicine_section.html', {"medicines": medicines})

def pos_billing(request):
    return render(request, 'medflowapp/POS_section.html')

def inventory(request):
    return render(request, 'medflowapp/inventory.html')

def purchases(request):
    return render(request, 'medflowapp/purchases_section.html')

def reports_section(request):
    return render(request, 'medflowapp/report_section.html')

@csrf_exempt
def register_user(request):
    # user = Employee(name = request.POST['name'], email=request.POST['email'], role = request.POST['role'], employee_ID=request.POST['emp_id'], password = request.POST['password'])
    # user.save()
    data = request.POST.dict()
    print(data, '...........')
    Employee.objects.create(name = data['name'], email=data['email'], role=data['role'], employee_ID=data['emp_id'],password=data['password'])
    return JsonResponse({"status":200})

@csrf_exempt
def login_user(request):
    try:
        login_credentials = request.POST.dict()
        print(login_credentials)
        if Employee.objects.filter(email=login_credentials['email'], password=login_credentials['password']).exists():
            obj = Employee.objects.filter(email=login_credentials['email'], password=login_credentials['password']).last()
            print(obj,'///////////////')
            request.session['userId'] = obj.id
            return JsonResponse({"status": 200})
        else:
            return JsonResponse({"status": 403})
    except:

        traceback.print_exc()

@csrf_exempt
def add_medicine(request):
    data = request.POST.dict()
    print(data)
    Medicines.objects.create(medicine_name = data['medicine_name'], expiry_date=data['expiry_date'], med_category=data['category'], stock_status=data['stock_status'], price=data['price'], quantity=data['quantity'])
    return JsonResponse({'status': 200})

@csrf_exempt
def delete_medicine(request):
    data=request.POST.dict()
    med_ID = Medicines.objects.get(id=data['medicine_ID'])
    med_ID.delete()
    return JsonResponse({"status": 200})

def update_medicine_page(request, medicineid):
    medicine_ID = Medicines.objects.get(id=medicineid)
    print(f"Medicine ID : {medicine_ID}")
    return render(request, 'medflowapp/update_medicine.html', {"medicine_ID":medicine_ID})
    
@csrf_exempt
def update_med_info(request):
    try:
        data=request.POST.dict()
        print(f"data: {data}")
        medicine = Medicines.objects.get(id=data['med_ID'])
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
    Customers.objects.create(customer_name=data['customer_name'], customer_phone=data['phone_number'])
    return JsonResponse({"status":200})
