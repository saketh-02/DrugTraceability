from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import Product, TraceRecord, UserProfile
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from datetime import date
from django.conf import settings

def index(request):
    return render(request, 'index.html')

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_screen')
            return redirect('user_screen')
        return render(request, 'Login.html', {'data': 'Invalid login details'})
    
    return render(request, 'Login.html')

def admin_screen(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'AdminScreen.html', {'data': f"Welcome {request.user.username}"})

def user_screen(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'UserScreen.html', {'data': f"Welcome {request.user.username}"})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '')
        
        if User.objects.filter(username=username).exists():
            return render(request, 'Register.html', {'data': 'Username already exists'})
        
        user = User.objects.create_user(username=username, password=password, email=email)
        UserProfile.objects.create(user=user, ethereum_address='0x0')  # Placeholder address
        
        return render(request, 'Login.html', {'data': 'Registration successful. Please login.'})
    
    return render(request, 'Register.html')

@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('t1')
        quantity = request.POST.get('t2')
        price = request.POST.get('t3')
        description = request.POST.get('t4')
        image = request.FILES.get('t5')
        
        if Product.objects.filter(name=name).exists():
            return render(request, 'AddProduct.html', {'data': 'Product already exists'})
        
        fs = FileSystemStorage()
        if image:
            image_name = fs.save(image.name, image)
        else:
            image_name = None
        
        Product.objects.create(
            name=name,
            quantity=quantity,
            price=price,
            description=description,
            image=image_name,
            owner=request.user
        )
        
        return render(request, 'AddProduct.html', {'data': 'Product added successfully'})
    
    return render(request, 'AddProduct.html')

@login_required
def view_tracing(request):
    # Get all products with their tracing records in a single query
    products = Product.objects.prefetch_related('trace_records').all()
    
    # Add tracing history to each product
    for product in products:
        # Sort tracing records by date, newest first
        product.history = product.trace_records.all().order_by('-timestamp')
    
    context = {
        'products': products,
        'MEDIA_URL': settings.MEDIA_URL
    }
    return render(request, 'ViewTracing.html', context)

@login_required
def update_tracing(request):
    if request.method == 'POST':
        product_name = request.POST.get('t1')
        trace_type = request.POST.get('t2')
        details = request.POST.get('t3')
        
        try:
            product = Product.objects.get(name=product_name)
            TraceRecord.objects.create(
                product=product,
                trace_type=trace_type,
                details=details,
                updated_by=request.user
            )
            product.current_status = trace_type
            product.save()
            
            messages.success(request, 'Tracing details updated successfully')
            return redirect('update_tracing')
        except Product.DoesNotExist:
            messages.error(request, 'Product not found')
            return redirect('update_tracing')
    
    # For GET requests
    products = Product.objects.all()
    context = {'products': products}
    
    # If a specific product is selected for updating
    product_name = request.GET.get('pname')
    if product_name:
        try:
            selected_product = Product.objects.get(name=product_name)
            context['selected_product'] = selected_product
        except Product.DoesNotExist:
            messages.error(request, 'Selected product not found')
    
    return render(request, 'UpdateTracing.html', context)

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})
    
def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def AddProduct(request):
    if request.method == 'GET':
       return render(request, 'AddProduct.html', {})

def UpdateTracingAction(request):
    if request.method == 'GET':
        global product_name
        product_name = request.GET['pname']
        output = '<tr><td><font size="" color="black">Product&nbsp;Name</font></td>'
        output += '<td><input type="text" name="t1" style="font-family: Comic Sans MS" size="30" value='+product_name+' readonly/></td></tr>'
        context= {'data':output}
        return render(request, 'AddTracing.html', context)    

def UpdateTracing(request):
    if request.method == 'GET':
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Drug Name</font></th>'
        output+='<th><font size=3 color=black>Price</font></th>'
        output+='<th><font size=3 color=black>Quantity</font></th>'
        output+='<th><font size=3 color=black>Description</font></th>'
        output+='<th><font size=3 color=black>Image</font></th>'
        output+='<th><font size=3 color=black>Last Update Date</font></th>'
        output+='<th><font size=3 color=black>Current Tracing Info</font></th>'
        output+='<th><font size=3 color=black>Update New Tracing Info</font></th></tr>'
        readDetails("addproduct")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == 'addproduct':
                output+='<tr><td><font size=3 color=black>'+arr[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+str(arr[3])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(arr[4])+'</font></td>'
                output+='<td><img src="/static/products/'+arr[5]+'" width="200" height="200"></img></td>'
                output+='<td><font size=3 color=black>'+str(arr[6])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(arr[7])+'</font></td>'
                output+='<td><a href=\'UpdateTracingAction?pname='+arr[1]+'\'><font size=3 color=black>Click Here</font></a></td></tr>'                    
        output+="</table><br/><br/><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'UpdateTracing.html', context)              
        
    
def AddTracingAction(request):
    if request.method == 'POST':
        product_name = request.POST.get('t1', False)
        tracing_type = request.POST.get('t2', False)
        tracing_status = request.POST.get('t3', False)
        index = 0
        record = ''
        readDetails("addproduct")
        rows = details.split("\n")
        tot_qty = 0
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "addproduct":
                if arr[1] == product_name:
                    today = date.today()
                    index = i
                    record = arr[0]+"#"+arr[1]+"#"+arr[2]+"#"+arr[3]+"#"+arr[4]+"#"+arr[5]+"#"+str(today)+"#"+tracing_type+"! "+tracing_status+"\n"
                    break
        for i in range(len(rows)-1):
            if i != index:
                record += rows[i]+"\n"
        updateQuantityBlock(record)
        context= {'data':"Tracing details updated"}
        return render(request, 'AdminScreen.html', context)
          
def AddProductAction(request):
    if request.method == 'POST':
        cname = request.POST.get('t1', False)
        qty = request.POST.get('t2', False)
        price = request.POST.get('t3', False)
        desc = request.POST.get('t4', False)
        image = request.FILES['t5']
        imagename = request.FILES['t5'].name

        today = date.today()
        fs = FileSystemStorage()
        filename = fs.save('DrugTraceApp/static/products/'+imagename, image)
        
        data = "addproduct#"+cname+"#"+price+"#"+qty+"#"+desc+"#"+imagename+"#"+str(today)+"#Production State\n"
        saveDataBlockChain(data,"addproduct")
        context= {'data':"Product details saved in Blockchain"}
        return render(request, 'AddProduct.html', context)
        
   
def Signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        contact = request.POST.get('contact', False)
        email = request.POST.get('email', False)
        address = request.POST.get('address', False)
        record = 'none'
        readDetails("signup")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] == username:
                    record = "exists"
                    break
        if record == 'none':
            data = "signup#"+username+"#"+password+"#"+contact+"#"+email+"#"+address+"\n"
            saveDataBlockChain(data,"signup")
            context= {'data':'Signup process completd and record saved in Blockchain'}
            return render(request, 'Register.html', context)
        else:
            context= {'data':username+'Username already exists'}
            return render(request, 'Register.html', context)    


def UserLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        status = "Login.html"
        context= {'data':'Invalid login details'}
        if username == 'admin' and password == 'admin':
            context = {'data':"Welcome "+username}
            status = "AdminScreen.html"
        else:
            readDetails("signup")
            rows = details.split("\n")
            for i in range(len(rows)-1):
                arr = rows[i].split("#")
                if arr[0] == "signup":
                    if arr[1] == username and arr[2] == password:
                        context = {'data':"Welcome "+username}
                        status = 'UserScreen.html'
                        file = open('session.txt','w')
                        file.write(username)
                        file.close()
                        break
        return render(request, status, context)              


def ViewTracing(request):
    if request.method == 'GET':
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Drug Name</font></th>'
        output+='<th><font size=3 color=black>Price</font></th>'
        output+='<th><font size=3 color=black>Quantity</font></th>'
        output+='<th><font size=3 color=black>Description</font></th>'
        output+='<th><font size=3 color=black>Image</font></th>'
        output+='<th><font size=3 color=black>Last Update Date</font></th>'
        output+='<th><font size=3 color=black>Current Tracing Info</font></th></tr>'
        
        readDetails("addproduct")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == 'addproduct':
                output+='<tr><td><font size=3 color=black>'+arr[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+str(arr[3])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(arr[4])+'</font></td>'
                output+='<td><img src="/static/products/'+arr[5]+'" width="200" height="200"></img></td>'
                output+='<td><font size=3 color=black>'+str(arr[6])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(arr[7])+'</font></td>'                             
        output+="</table><br/><br/><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'ViewTracing.html', context)   
        
@login_required
def delete_product(request, product_id):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method')
        return redirect('view_tracing')
        
    product = get_object_or_404(Product, id=product_id)
    
    # Only allow superusers or the product owner to delete
    if request.user.is_superuser or product.owner == request.user:
        # Delete the product image if it exists
        if product.image:
            fs = FileSystemStorage()
            if fs.exists(product.image.path):
                fs.delete(product.image.path)
        
        # Delete the product
        product.delete()
        messages.success(request, f'Product "{product.name}" has been deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this product.')
    
    return redirect('view_tracing')
            
