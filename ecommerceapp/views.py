from django.shortcuts import render, redirect, get_object_or_404
from ecommerceapp.models import Contact, Product, OrderUpdate, Orders
from django.contrib import messages
from math import ceil
from ecommerceapp import keys
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum

MERCHANT_KEY = keys.MK

# Home Page
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds}
    return render(request, "index.html", params)

# Contact Form
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        desc = request.POST.get("desc")
        pnumber = request.POST.get("pnumber")
        myquery = Contact(name=name, email=email, desc=desc, phonenumber=pnumber)
        myquery.save()
        messages.info(request, "We will get back to you soon..")
        return render(request, "contact.html")
    return render(request, "contact.html")

# About Page
def about(request):
    return render(request, "about.html")

# Checkout Page
def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        Order = Orders(items_json=items_json, name=name, amount=amount, email=email, address1=address1,
                       address2=address2, city=city, state=state, zip_code=zip_code, phone=phone)
        Order.save()
        update = OrderUpdate(order_id=Order.order_id, update_desc="The order has been placed")
        update.save()

        id = Order.order_id
        oid = str(id) + "ShopyCart"
        param_dict = {
            'MID': keys.MID,
            'ORDER_ID': oid,
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'paytm.html', {'param_dict': param_dict})

    return render(request, 'checkout.html')

# Handle Payment Response
@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            a = response_dict['ORDERID']
            b = response_dict['TXNAMOUNT']
            rid = a.replace("ShopyCart", "")
            filter2 = Orders.objects.filter(order_id=rid)
            for post1 in filter2:
                post1.oid = a
                post1.amountpaid = b
                post1.paymentstatus = "PAID"
                post1.save()
        else:
            print('Order was not successful because ' + response_dict['RESPMSG'])
    return render(request, 'paymentstatus.html', {'response': response_dict})

# Modified User Profile
def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    currentuser = request.user.username
    items = Orders.objects.filter(email=currentuser)
    rid = None

    for i in items:
        myid = i.oid
        if myid:
            try:
                rid_candidate = myid.replace("ShopyCart", "")
                rid = int(rid_candidate)
                break  # Use the first valid one
            except (ValueError, AttributeError):
                continue

    status = OrderUpdate.objects.filter(order_id=rid) if rid else []
    context = {"items": items, "status": status}
    return render(request, "profile.html", context)

# New: Search Function
def search_products(request):
    query = request.GET.get('query', '')
    products = []

    if query:
        products = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(category__icontains=query) |
            Q(subcategory__icontains=query)
        )

    return render(request, 'search_results.html', {'products': products, 'query': query})

# Add to Cart
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
        messages.success(request, f"{product.product_name} added to cart!")
    return redirect(request.META.get('HTTP_REFERER', '/'))
