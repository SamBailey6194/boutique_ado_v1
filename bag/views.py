from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from products.models import Product


# Create your views here.
def view_bag(request):
    """ Render shopping bag """
    bag = request.session.get('bag', {})
    bag_items = []

    total = 0

    for item_id, item_data in bag.items():
        product = get_object_or_404(Product, pk=item_id)

        if product.has_sizes:
            for size, quantity in item_data.get('items_by_size', {}).items():
                subtotal = product.price * quantity
                total += subtotal
                bag_items.append({
                    'item_id': item_id,
                    'product': product,
                    'quantity': quantity,
                    'size': size,
                    'subtotal': subtotal
                })
        else:
            quantity = item_data if isinstance(item_data, int) else 0
            subtotal = product.price * quantity
            total += subtotal
            bag_items.append({
                'item_id': item_id,
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

    context = {
        'bag_items': bag_items,
        'total': total,
        'delivery': 0,  # or calculate delivery
        'grand_total': total,  # total + delivery
    }
    return render(request, 'bag/bag.html', context)


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


def adjust_bag(request, item_id):
    """ Adjust quantity of an item in the bag via AJAX """
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity', 1))
    size = request.POST.get('product_size', None)
    item_id = str(item_id)

    bag = request.session.get('bag', {})

    if product.has_sizes and size:
        if item_id in bag and 'items_by_size' in bag[item_id]:
            if quantity > 0:
                bag[item_id]['items_by_size'][size] = quantity
            else:
                bag[item_id]['items_by_size'].pop(size)
                if not bag[item_id]['items_by_size']:
                    bag.pop(item_id)
    else:
        if quantity > 0:
            bag[item_id] = quantity
        else:
            bag.pop(item_id, None)

    request.session['bag'] = bag
    return redirect(reverse('bag:view_bag'))


def remove_from_bag(request, item_id):
    """ Remove the item from the shopping bag """
    try:
        item_id = str(item_id)
        bag = request.session.get('bag', {})

        # Accept either 'size' or 'product_size' from POST
        size = request.POST.get('size') or request.POST.get('product_size')

        if size:
            if item_id in bag and 'items_by_size' in bag[item_id]:
                bag[item_id]['items_by_size'].pop(size, None)
                if not bag[item_id]['items_by_size']:
                    bag.pop(item_id, None)
        else:
            bag.pop(item_id, None)

        print("Debug: Item removed from bag after click")

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception:
        return HttpResponse(status=500)
