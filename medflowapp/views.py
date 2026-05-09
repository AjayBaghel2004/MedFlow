from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.http import request, JsonResponse
from django.db import transaction
from django.db.models import Sum, F
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from .models import *
import openpyxl
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import json
import uuid
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import traceback
from django.views.decorators.cache import cache_control
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def register(request):
    return render(request, 'medflowapp/register.html')

def login(request):
    return render(request, 'medflowapp/login.html')

@login_required(login_url='/login/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    total_medicines = Medicine.objects.count() #Total Medicines in inventory
    low_stock_count = Medicine.objects.filter(quantity__lt=10).count()
    today = timezone.now().date() # today sales revenue
    today_sales = float(Sale.objects.filter(created_at__date = today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
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

def login_user(request):
    if request.method=="POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        #Django`s authenticate function handles the hashed password comparison
        user = authenticate(request, username=email, password=password)
        if user is not None:
            #This Creates the session and logs the user in properly
            auth_login(request, user)
            return JsonResponse({"status": 200})
        else:
            return JsonResponse({"status":403, "message": "Invalid Credentials"})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_medicine(request):
    data = request.POST.dict()
    print(data)
    Medicine.objects.create(medicine_name = data['medicine_name'], expiry_date=data['expiry_date'], med_category=data['category'], price=data['price'], quantity=data['quantity'])
    return JsonResponse({'status': 200})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_medicine(request):
    data=request.POST.dict()
    med_ID = Medicine.objects.get(id=data['medicine_ID'])
    med_ID.delete()
    return JsonResponse({"status": 200})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_medicine_page(request, medicineid):
    medicine_ID = Medicine.objects.get(id=medicineid)
    print(f"Medicine ID : {medicine_ID}")
    return render(request, 'medflowapp/update_medicine.html', {"medicine_ID":medicine_ID})
    
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_med_info(request):
    try:
        data=request.POST.dict()
        print(f"data: {data}")
        medicine = Medicine.objects.get(id=data['med_ID'])
        medicine.price = data['price']
        medicine.quantity=data['quantity']
        medicine.expiry_date=data['expiry_date']
        medicine.save()
        return JsonResponse({"status":200})
    except:
        import traceback
        traceback.print_exc()


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def supplier_list(request):
    suppliers=Supplier.objects.all()
    return render(request, 'medflowapp/suppliers_section.html', {'suppliers':suppliers})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_supplier(request):
    if request.method == "POST":
        try:
            data=request.POST
            Supplier.objects.create(
                supplier_name=data.get('supplier_name'),
                supplier_contact=data.get('phone_number'),
                supplier_person=data.get('contact_person'),
                supplier_address=data.get('address')
            )
            return JsonResponse({"status":200, "message":"Supplier added successfully!"})
        except Exception as e:
            return JsonResponse({"status":500, "message":str(e)}, status=500)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_supplier(request):
    id=request.POST.dict()
    supplier = Supplier.objects.get(id=id['supplier_ID'])
    supplier.delete()
    return JsonResponse({"status":200, "message": "Supplier Deleted Successfully!"})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def purchases(request):
    suppliers = Supplier.objects.all()
    medicines = Medicine.objects.all()

    history = Purchase.objects.all().order_by('-purchase_date')

    context = {
        "supplier_details":suppliers,
        "medicine_details": medicines,
        "purchase_history":history,
    }
    return render(request, "medflowapp/purchases_section.html", context)

@transaction.atomic
def add_purchases(request):
    if request.method=="POST":
        try:
            data=request.POST
            qty=int(data.get('quantity'))
            med_id=data.get('medicine_id')
            #create the purchase Record
            purchase = Purchase.objects.create(
                supplier_id=data.get('supplier_id'),
                medicine_id=med_id,
                batch_number=data.get('batch_no'),
                quantity_received=qty,
                cost_price=data.get('cost_price'),
                purchase_date=data.get('expiry_date'),
            )
            #Update medicine inventory
            medicine = Medicine.objects.get(id=med_id)
            medicine.quantity += qty
            #Sync the expiry date with the latest batch
            medicine.expiry_date = data.get('expiry_date')
            medicine.save()

            return JsonResponse({"status":200, "message":"Stock updates Successfully!"})
        except Exception as e:
            return JsonResponse({"status":200, "message":str(e)}, status=500)



def add_customer(request):
    data=request.POST.dict()
    print(f"Customer Data : {data}")
    Customer.objects.create(customer_name=data['customer_name'], customer_phone=data['phone_number'])
    return JsonResponse({"status":200})


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
        customer = Customer.objects.filter(id=cus_ID).first() if cus_ID else None
        # generate automatic invoice number
        new_invoice_number = f"INV-{uuid.uuid4().hex[:6].upper()}"
        #2. create Sale
        sale = Sale.objects.create(
            invoice_number = new_invoice_number,
            customer=customer,
            subtotal=float(data['subtotal']),
            gst_amount=float(data['gst']),
            total_amount=float(data['total'])
        )
        #3. Create sale Items and Reduce Stock
        for item in data['items']:
            medicine=Medicine.objects.get(id=item['id'])
            #Stock check
            if medicine.quantity < item['qty']:
                transaction.set_rollback(True)
                return JsonResponse({"status": "error", "message":f"Low stock for {medicine.medicine_name}"},status=400)
            
            SaleItem.objects.create(
                medicine=medicine,
                sale=sale,
                quantity_sold=item['qty'],
                unit_price=item['price'],
                total_price=item['total']
            )
            #Deduct Inventory
            medicine.quantity -= int(item['qty'])
            medicine.save()
        return JsonResponse({"status":"success", "invoice": sale.id})

@login_required
@login_required
def reports_section(request):
    # 1. DATE FILTERING
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    sales_query = Sale.objects.all()
    if start_date and end_date:
        sales_query = sales_query.filter(created_at__date__range=[start_date, end_date])

    # 2. SUMMARY CARDS (Keep this clean and direct)
    gross_revenue = sales_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Calculate Total Cost for the filtered range
    total_cost = 0
    sale_items = SaleItem.objects.filter(sale__in=sales_query)
    for item in sale_items:
        # Use the logic that resolved your relation error
        latest_purchase = Purchase.objects.filter(medicine=item.medicine).last()
        cost = latest_purchase.cost_price if latest_purchase else 0
        total_cost += (item.quantity_sold * float(cost))

    net_profit = float(gross_revenue) - total_cost
    margin = (net_profit / float(gross_revenue) * 100) if gross_revenue > 0 else 0

    # 3. CHART DATA (The 12-month dynamic logic)
    chart_labels = []
    chart_sales = []
    chart_profits = []
    today = timezone.now().date()

    for i in range(11, -1, -1):
        month_date = today - relativedelta(months=i)
        chart_labels.append(month_date.strftime("%b %Y"))

        m_query = Sale.objects.filter(created_at__year=month_date.year, created_at__month=month_date.month)
        
        # Monthly Sales
        m_sales = m_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        chart_sales.append(float(m_sales))

        # Monthly Profit
        m_profit = 0
        m_items = SaleItem.objects.filter(sale__in=m_query)
        for mi in m_items:
            lp = Purchase.objects.filter(medicine=mi.medicine).last()
            c = lp.cost_price if lp else 0
            m_profit += (mi.quantity_sold * (float(mi.unit_price) - float(c)))
        chart_profits.append(m_profit)

    # 4. TOP SELLING ITEMS
    top_items = SaleItem.objects.filter(sale__in=sales_query).values(
        'medicine__medicine_name'
    ).annotate(
        total_units=Sum('quantity_sold')
    ).order_by('-total_units')[:3]

    context = {
        "gross_revenue": gross_revenue,
        "net_profit": net_profit,
        "margin": margin,
        "top_items": top_items,
        "chart_labels": chart_labels,
        "chart_sales": chart_sales,
        "chart_profits": chart_profits,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, 'medflowapp/report_section.html', context)

def export_sales_excel(request):
    response=HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition']='attachment; filename="Sales_Report.xlsx"'
    wb=openpyxl.Workbook()
    ws=wb.active
    ws.title="Sales Report"
    #define headers
    headers = ['Date', 'Invoice #', 'Customer', 'Subtotal', 'GST', 'Total']
    ws.append(headers)
    # Fetch Data
    sales=Sale.objects.all().order_by('-created_at')
    for sale in sales:
        ws.append([
            sale.created_at.strftime("%Y-%m-%d"),
            sale.invoice_number,
            sale.customer.customer_name if sale.customer else "Guest",
            float(sale.subtotal),
            float(sale.gst_amount),
            float(sale.total_amount)
        ])

        wb.save(response)
        return response

def export_sales_pdf(request):
    response=HttpResponse(content_type='application/pdf')
    response['content-Disposition'] = 'attachment; filename="Sales_Report.pdf"'
    p=canvas.Canvas(response, pagesize=letter)
    p.setFont('Helvetica-Bold', 16)
    p.drawString(100, 750,"MedFlow Pharmacy - Sales Report")
    p.setFont("Helvetica", 12)
    y=700
    sales = Sale.objects.all()
    for sale in sales:
        line = f"Inv: {sale.invoice_number} | Date: {sale.created_at.date()} | Total: {sale.total_amount}"
        p.drawString(100, y, line)
        y-=20
        if y < 50:
            p.showPage()
            y=750
        p.showPage()
        p.save()
        return response

def logout_user(request):
    logout(request)
    return redirect('/login/')


# def send_mail_page(request):
#     address = "ajaybaghel2459@gmail.com"
#     subject = "test mail"
#     message = "OTP verifiation 123456"

#     if address and subject and message:
#         try:
#             result = send_mail(subject, message, settings.EMAIL_HOST_USER, [address])
#             print(result,'//////////////////')
#         except Exception as e:
#             traceback.print_exc()
#     else:
#         context['result'] = 'All fields are required'
