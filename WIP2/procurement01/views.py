from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, inlineformset_factory
from django.http import JsonResponse
from django.template.loader import render_to_string
import json 
from django.db import transaction 
from django.forms.models import model_to_dict
from collections import OrderedDict
from django.http import HttpResponse 





from .models import SKU, Company, RFP, GeneralQuestion, RFP_SKUs,SKUSpecificQuestion
from .forms import SKUForm, SupplierForm, RFPBasicForm, SKUSearchForm, GeneralQuestionForm, RFP_SKUForm, RFPForm, SKUSpecificQuestionForm



def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # If user is already logged in, redirect to dashboard

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard after login
    else:
        form = AuthenticationForm()

    return render(request, 'procurement01/login.html', {'form': form})



@login_required
def dashboard_view(request):
    return render(request, 'procurement01/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# View to list all SKUs
@login_required
def sku_list_view(request):
    skus = SKU.objects.all()
    return render(request, 'procurement01/sku_list.html', {'skus': skus})

# View to see details of a single SKU
@login_required
def sku_detail_view(request, sku_id):
    sku = get_object_or_404(SKU, id=sku_id)
    return render(request, 'procurement01/sku_detail.html', {'sku': sku})

# view to create new skus
@login_required
def sku_create_view(request):
    if request.method == 'POST':
        form = SKUForm(request.POST)
        if form.is_valid():
            sku = form.save(commit=False)  # Don't save to the database yet
            sku.company = request.user.company  # Set the company to the logged-in user's company
            sku.save()  # Now save to the database
            return redirect('sku_list')
    else:
        form = SKUForm()

    return render(request, 'procurement01/sku_form.html', {'form': form})

@login_required
def supplier_list_view(request):
    # Ensure the logged-in user is a procurer
    if request.user.is_procurer:
        procurer_company = request.user.company
        suppliers = Company.objects.filter(procurer=procurer_company)
        return render(request, 'procurement01/supplier_list.html', {'suppliers': suppliers})
    else:
        return render(request, 'procurement01/access_denied.html')
    

@login_required
def create_supplier_view(request):
    if not request.user.is_procurer:
        return render(request, 'procurement01/access_denied.html')  # Only procurers can create suppliers

    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save(procurer=request.user.company)  # Assign the supplier to the logged-in procurer's company
            return redirect('supplier_list')  # Redirect to the supplier list page after creating the supplier
    else:
        form = SupplierForm()

    return render(request, 'procurement01/supplier_form.html', {'form': form})

@login_required
# Step 1: Create RFP (Title and Description)
def create_rfp_step1(request):
    if request.method == 'POST':
        form = RFPBasicForm(request.POST)
        if form.is_valid():
            rfp = form.save()
            # After saving the title and description, redirect to step 2
            return redirect('create_rfp_step2', rfp_id=rfp.id)
    else:
        form = RFPBasicForm()

    return render(request, 'procurement01/create_rfp_step1.html', {'form': form})


@login_required
def search_skus(request):
    query = request.GET.get('query', '')
    company = request.user.company

    # Only proceed with the search if there is a query
    if query:
        skus = SKU.objects.filter(company=company, name__icontains=query)
        sku_data = [{'id': sku.id, 'name': sku.name, 'sku_code': sku.sku_code} for sku in skus]
    else:
        sku_data = []  # Return an empty list if there is no query

    return JsonResponse(sku_data, safe=False)




RFP_SKUFormSet = inlineformset_factory(RFP, RFP_SKUs, fields=('sku',), extra=1)


@login_required
def create_rfp_step2(request, rfp_id):
    rfp = get_object_or_404(RFP, id=rfp_id)

    if request.method == 'POST':
        sku_ids = request.POST.getlist('skus[]')
        extra_columns_data = request.POST.get('extra_columns_data')
        extra_columns_json = json.loads(extra_columns_data) if extra_columns_data else []

        for sku_data in extra_columns_json:
            sku_id = sku_data['sku_id']
            sku = get_object_or_404(SKU, id=sku_id)
            rfp_sku = RFP_SKUs.objects.create(rfp=rfp, sku=sku)

            # Convert dataArray back into a dictionary, maintaining order
            data_ordered = OrderedDict(sku_data['data'])
            rfp_sku.set_extra_data(data_ordered)

            rfp_sku.save()

        return redirect('create_rfp_step3', rfp_id=rfp.id)

    sku_search_form = SKUSearchForm()

    return render(request, 'procurement01/create_rfp_step2.html', {
        'rfp': rfp,
        'sku_search_form': sku_search_form,
    })



@login_required
def create_rfp_step3(request, rfp_id):
    # Get the RFP instance
    rfp = get_object_or_404(RFP, id=rfp_id)

    # Create a formset for handling multiple GeneralQuestion instances
    GeneralQuestionFormSet = modelformset_factory(GeneralQuestion, form=GeneralQuestionForm, extra=1, can_delete=True)

    # If the form is submitted
    if request.method == 'POST':
        formset = GeneralQuestionFormSet(request.POST, queryset=GeneralQuestion.objects.filter(rfp=rfp))

        # Validate the formset
        if formset.is_valid():
            # Process each form in the formset
            instances = formset.save(commit=False)
            for instance in instances:
                # Link the question to the RFP
                instance.rfp = rfp
                instance.save()  # Save the instance to the database
            
            # Delete any questions marked for deletion
            for deleted_instance in formset.deleted_objects:
                deleted_instance.delete()
            
            # After saving, redirect to the next step (Step 4)
            return redirect('create_rfp_step4', rfp_id=rfp.id)
            

    # If the form is not submitted, display the existing questions
    else:
        formset = GeneralQuestionFormSet(queryset=GeneralQuestion.objects.filter(rfp=rfp))

    return render(request, 'procurement01/create_rfp_step3.html', {
        'rfp': rfp,
        'formset': formset,
    })


@login_required
def create_rfp_step4(request, rfp_id):
    # Get the RFP instance
    rfp = get_object_or_404(RFP, id=rfp_id)
    
    # Fetch all RFP_SKUs associated with this RFP
    rfp_skus = RFP_SKUs.objects.filter(rfp=rfp)

    # Process SKUs to pass to the template
    processed_skus = []
    extra_columns = []

    for rfp_sku in rfp_skus:
        extra_data = rfp_sku.get_extra_data()
        if not extra_columns:
            extra_columns = list(extra_data.keys())  # Store the keys only once from the first SKU
            print(extra_data)
            print(extra_columns)
        processed_skus.append({
            'sku_id': rfp_sku.id,
            'sku_name': rfp_sku.sku.name,
            'extra_data': extra_data,
        })
        print(processed_skus)

    # Handle form submission
    if request.method == 'POST':
        # Retrieve the JSON data for sku_specific_data from the form
        sku_specific_data = request.POST.get('sku_specific_data')
        questions_data = json.loads(sku_specific_data) if sku_specific_data else []

        # Clear any existing SKU-specific questions for this RFP to prevent duplicates
        SKUSpecificQuestion.objects.filter(rfp=rfp).delete()

        # Save each question once for this RFP
        for question_data in questions_data:
            SKUSpecificQuestion.objects.create(
                rfp=rfp,
                question=question_data['question'],
                question_type=question_data['question_type']
            )

        # Redirect to the next step
        print("Form submitted successfully, data saved to DB")
        return HttpResponse("Form submitted successfully, data saved to DB") 

    # Pass context to the template
    context = {
        'rfp': rfp,
        'extra_columns': extra_columns,
        'processed_skus': processed_skus,
        'question_types': SKUSpecificQuestion.QUESTION_TYPES,
    }
    return render(request, 'procurement01/create_rfp_step4.html', context)


@login_required
def view_rfp_skus(request, rfp_id):
    rfp = get_object_or_404(RFP, id=rfp_id)
    rfp_skus = RFP_SKUs.objects.filter(rfp=rfp)
    
    processed_skus = []
    extra_columns = []

    for rfp_sku in rfp_skus:
        extra_data = rfp_sku.get_extra_data()  # This should return the JSON data in the original order
        print(extra_data)
        if not extra_columns:
            # Collect columns based on the first SKU's extra data keys in order
            extra_columns = list(extra_data.keys())
            print(extra_columns)
        processed_skus.append({
            'sku_name': rfp_sku.sku.name,
            'extra_data': extra_data,
        })
        print(processed_skus)
    
    context = {
        'rfp': rfp,
        'extra_columns': extra_columns,
        'processed_skus': processed_skus,
    }
    print(context)
    return render(request, 'procurement01/view_rfp_skus.html', context)


    

@login_required
def rfp_list_view(request):
    rfps = RFP.objects.all()  # You might want to filter by the user's company if needed
    return render(request, 'procurement01/rfp_list.html', {'rfps': rfps})