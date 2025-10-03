from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Product

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
# from .models import User
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order

def login_page(request):
    if request.method=="POST":   #1
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)  #using inbuilt login() for session creation it will act like cookies
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')
    return render(request,'login_page.html')

def chunk_products(products, chunk_size=6):
    """Splits the list into chunks of `chunk_size`"""
    return [products[i:i + chunk_size] for i in range(0, len(products), chunk_size)]

def home(request):
    fashion_products = Product.objects.filter(category='fashion')
    electronics_products = Product.objects.filter(category='electronics')
    home_products = Product.objects.filter(category='home')
    others_products = Product.objects.filter(category__in=['others', '', None])


    context = {
        'fashion_rows': chunk_products(list(fashion_products)),
        'electronics_rows': chunk_products(list(electronics_products)),
        'home_rows': chunk_products(list(home_products)),
        'others_rows': chunk_products(list(others_products)),
    }

    return render(request, 'home.html', context)


def signin(request):
    if request.user.is_authenticated:      #1
        messages.warning(request,"you are already logged in ,click login")
        return redirect('home')
    
    if request.method=="POST":             #2
        username=request.POST['username']
        password=request.POST['password']

        if User.objects.filter(username=username).exists():  #here-- User -- it is the in built model name.
            messages.error(request,"username already taken")
            return redirect('signin')

        user=User()           #it is manual data storing and we can store it by inbuilt way------user=User.objects.create_user(username=username,password=password)
        user.username=username #in the deafult models,the field name is starts with small letter only
        user.set_password(password) #if use dont want to hash the password you can write like--- user.password =password

        user.save()
        login(request,user)
        return redirect('home')

    return render(request,'signin_page.html')

def is_staff_user(user):    #used to check the admin to allow for add data
    return user.is_staff

@user_passes_test(is_staff_user)
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        stock = request.POST.get('stock')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        if name and price and description and stock and category:
            Product.objects.create(
                name=name,
                price=price,
                description=description,
                stock=stock,
                category=category,
                image=image
            )
            return redirect('home')

    return render(request, 'add_product.html')



def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

def place_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        
        if quantity <= 0 or quantity > product.stock:
            return render(request, 'product_detail.html', {
                'product': product,
                'error': 'Invalid quantity selected.'
            })
        
        Order.objects.create(product=product, quantity=quantity)

        product.stock -= quantity
        product.save()
        
        return redirect('home') 
    
    return redirect('product_detail', product_id=product.id)
