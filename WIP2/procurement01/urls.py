from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('skus/', views.sku_list_view, name='sku_list'),
    path('skus/<int:sku_id>/', views.sku_detail_view, name='sku_detail'),
    path('skus/new/', views.sku_create_view, name='sku_create'),

    path('suppliers/', views.supplier_list_view, name='supplier_list'),
    path('suppliers/create/', views.create_supplier_view, name='create_supplier'),

    path('rfp/create/step1/', views.create_rfp_step1, name='create_rfp_step1'),
    path('rfp/create/step2/<int:rfp_id>/', views.create_rfp_step2, name='create_rfp_step2'),
    path('search_skus/', views.search_skus, name='search_skus'),  # Add this line
    
    path('rfp/create/step3/<int:rfp_id>/', views.create_rfp_step3, name='create_rfp_step3'),
    path('rfp/create/step4/<int:rfp_id>/', views.create_rfp_step4, name='create_rfp_step4'),
    
    path('rfps/', views.rfp_list_view, name='rfp_list'),



]
