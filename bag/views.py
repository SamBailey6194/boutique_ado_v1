from django.shortcuts import render, redirect
from products.models import Product


# Create your views here.
def view_bag(request):
    """
    A view to render shopping bag
    """
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """
    Add a quantity of the specified product to the shopping bag.
    Handles products with and without sizes.
    """
    product = Product.objects.get(pk=item_id)
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url', '/')
    size = request.POST.get('product_size', None)

    # Ensure item_id is always a string for session consistency
    item_id = str(item_id)

    # Get existing bag or initialize new one
    bag = request.session.get('bag', {})

    if product.has_sizes and size:
        # Product has sizes
        if item_id not in bag:
            bag[item_id] = {'items_by_size': {}}

        # Merge/add quantity for this size
        current_qty = bag[item_id]['items_by_size'].get(size, 0)
        bag[item_id]['items_by_size'][size] = current_qty + quantity
    else:
        # Product without sizes
        if item_id in bag and isinstance(bag[item_id], int):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity

    # Debug: print bag contents
    print("Bag before saving:", bag)

    request.session['bag'] = bag
    return redirect(redirect_url)
