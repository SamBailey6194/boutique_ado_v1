from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from products.models import Product


# Create your views here.
def view_bag(request):
    """ Render shopping bag """
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """
    Add a quantity of the specified product to the shopping bag.
    Handles products with and without sizes and displays messages.
    """
    product = Product.objects.get(pk=item_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1  # Fallback in case of invalid input

    redirect_url = request.POST.get('redirect_url', '/')
    size = request.POST.get('product_size', None)
    item_id = str(item_id)  # Ensure session consistency

    bag = request.session.get('bag', {})

    # Defensive check: quantity must be between 1 and 99
    if quantity < 1 or quantity > 99:
        messages.error(
            request,
            f'Invalid quantity for {product.name}. '
            'Must be between 1 and 99.'
            )
        return redirect(redirect_url)

    # Products with sizes
    if product.has_sizes and size:
        if item_id not in bag:
            bag[item_id] = {'items_by_size': {}}
            messages.info(
                request,
                f'Created new entry for {product.name} in '
                'your bag.'
                )

        current_qty = bag[item_id]['items_by_size'].get(size, 0)
        if current_qty:
            bag[item_id]['items_by_size'][size] += quantity
            messages.success(
                request,
                f'Updated size {size.upper()} {product.name} quantity to '
                f'{bag[item_id]["items_by_size"][size]}'
            )
        else:
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(
                request,
                f'Added size {size.upper()} '
                f'{product.name} to your bag'
                )

        if bag[item_id]['items_by_size'][size] > 10:
            messages.warning(
                request,
                'You have added a large quantity of size '
                f'{size.upper()} {product.name}.'
                )

    # Products without sizes
    else:
        if item_id in bag and isinstance(bag[item_id], int):
            bag[item_id] += quantity
            messages.success(
                request,
                f'Updated {product.name} quantity to '
                f'{bag[item_id]}'
                )
            messages.info(
                request,
                f'{product.name} now has {bag[item_id]} in '
                'your bag.'
                )

            if bag[item_id] > 10:
                messages.warning(
                    request,
                    f'You have added a large quantity of '
                    f'{product.name}.'
                    )
        else:
            bag[item_id] = quantity
            messages.success(request, f'Added {product.name} to your bag!')
            messages.info(
                request,
                f'{product.name} was not previously in your '
                'bag, now added.'
                )

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
