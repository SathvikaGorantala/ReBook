from django.shortcuts import render
from .forms import SellForm
from django.contrib.auth.models import User
from .models import Description, Wishlist, Transaction, Review
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

# Create your views here.
class SellCreateView(LoginRequiredMixin,CreateView):
    model = Description
    fields = ['book_name', 'edition', 'category', 'location', 'price', 'phone', 'book_image']
    template_name = 'main/sell.html'  # Specify the template

    def form_valid(self, form):
        form.instance.seller=self.request.user
        return super().form_valid(form)

class SellUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Description
    fields = ['book_name', 'edition', 'category', 'location', 'price', 'phone', 'book_image']
    template_name = 'main/sell.html'  # Specify the template

    def form_valid(self, form):
        form.instance.seller=self.request.user
        return super().form_valid(form)

    def test_func(self):
        desc=self.get_object()
        if self.request.user==desc.seller:
            return True
        return False



def SellBooks(request):
    u=User.objects.get(id=request.user.id)
    u.save()
    if request.method=='POST':
        form=SellForm(request.POST,request.FILES)
        if form.is_valid():
            print('form is valid')
            form.save()




    elif request.method=='GET':
        form=SellForm()
    context={
        'form':form


    }
    return render(request,'main/sell.html',context)

def BuyBooks(request):
    u=User.objects.all()
    desc=Description.objects.all()
    return render(request,'main/buy.html',{'desc':desc,'u':u})




class BuyListView(ListView):
    model = Description
    template_name = 'main/buy.html'
    context_object_name = 'desc'

    def get_queryset(self):
        # Filter to show only the available books
        return Description.objects.filter(status='available')

from django.db.models import Avg


class BuyDetailView(DetailView):
    model = Description

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch reviews for the specific book
        reviews = Review.objects.filter(transaction__book=self.object)
        context['reviews'] = reviews
        
        # Calculate average rating
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        context['average_rating'] = average_rating if average_rating is not None else 0  # Handle case with no reviews
        
        return context

class SellDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Description
    success_url = '/begin/'


    def test_func(self):
        desc = self.get_object()
        if self.request.user == desc.seller:
            return True
        return False






def DetailofBooks(request,user_id):
    obj=get_object_or_404(User,id=user_id)
    desc = get_object_or_404(Description,id=user_id)
    return render(request,'main/description_detail.html',{'desc':desc,'obj':obj})


def searchbooks(request):
    query=request.GET['query']
    books=Description.objects.filter(book_name__icontains=query)
    return render(request,'main/searchbooks.html',{'desc':books})


from django.contrib import messages
@login_required
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Description, id=book_id)
    
    # Check if the book is already in the user's wishlist
    if Wishlist.objects.filter(user=request.user, book=book).exists():
        messages.info(request, 'This book is already in your wishlist.')
    else:
        # Add the book to the wishlist
        Wishlist.objects.create(user=request.user, book=book)
        messages.success(request, 'Book added to your wishlist!')
    
    return redirect('main:detail', pk=book_id)



@login_required
def view_wishlist(request):
    # Fetch all books in the user's wishlist
    wishlist_books = Wishlist.objects.filter(user=request.user).select_related('book')
    context = {'title':"My Wishlist",
               'books': wishlist_books
               }
    return render(request, 'main/wishlist.html', context)

@login_required
def view_myBooks(request):
    # Fetch all books in the user's wishlist
    books = Description.objects.filter(seller=request.user)
    context = {'title':"Books I have posted",
               'desc': books
               }
    return render(request, 'main/mybooks.html', context)




from django.utils import timezone


@login_required
def mark_as_sold(request, book_id):
    book = get_object_or_404(Description, id=book_id)
    wishlist_users = Wishlist.objects.filter(book=book)

    if request.method == 'POST':
        buyer_id = request.POST.get('buyer_id')
        buyer = get_object_or_404(User, id=buyer_id)

        # Create Transaction
        Transaction.objects.create(book=book, buyer=buyer, date=timezone.now().date())

        # Remove the book from other users' wishlists
        Wishlist.objects.filter(book=book).exclude(user=buyer).delete()

        # Add success message
        messages.success(request, f'Transaction successful! Book sold to {buyer.username}.')

        return redirect('main:detail', pk=book.id)  # Redirect back to book detail page

    return render(request, 'main/mark_as_sold.html', {
        'book': book,
        'wishlist_users': wishlist_users,
    })


@login_required
def transaction_history(request):
    # Transactions where the user is the buyer
    bought_books = Transaction.objects.filter(buyer=request.user)
    
    # Transactions where the user is the seller (i.e., books they've sold)
    sold_books = Transaction.objects.filter(book__seller=request.user)

    return render(request, 'main/transaction_history.html', {
        'bought_books': bought_books,
        'sold_books': sold_books,
    })


@login_required
def add_review(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Get the transaction for the current user
        transaction = get_object_or_404(Transaction, id=transaction_id, buyer=request.user)

        # Check if a review already exists for this transaction
        review, created = Review.objects.get_or_create(transaction=transaction, user = transaction.book.seller, rating = rating)

        # Only allow updating if the review doesn't exist yet
        if not created:
            messages.error(request, 'You can only leave one review per transaction.')
            return redirect('main:transaction_history')

        # Set the user to be the author of the book being reviewed
        print(transaction.book.seller )
        # review.user = transaction.book.seller  # The seller is the user being reviewed
        # review.rating = rating
        review.comment = comment
        review.save()

        messages.success(request, 'Your review has been submitted successfully.')
        return redirect('main:transaction_history')  # Redirect back to transaction history
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('main:transaction_history')
