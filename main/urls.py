from django.urls import path
from .views import BuyBooks,SellBooks,BuyDetailView,BuyListView,SellCreateView,SellUpdateView,SellDeleteView,searchbooks
from . import views
app_name='main'
urlpatterns=[
    path('buy/',BuyListView.as_view(),name='buy'),
    path('sell/',SellCreateView.as_view(),name='sell'),
    path('detail/<int:pk>/',BuyDetailView.as_view(),name='detail'),
    path('detail/<int:pk>/update/',SellUpdateView.as_view(),name='update'),
    path('detail/<int:pk>/delete/',SellDeleteView.as_view(),name='delete'),
    path('search/',searchbooks,name='search'),
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add-to-wishlist'),
    path('wishlist/', views.view_wishlist, name='view-wishlist'),
    path('mybooks/', views.view_myBooks, name='view-my-books'),
    path('mark-as-sold/<int:book_id>/', views.mark_as_sold, name='mark_as_sold'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('add-review/', views.add_review, name='add_review'),


]