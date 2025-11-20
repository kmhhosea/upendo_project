import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Need, Donation

# Render the single-page app shell
def index(request):
    return render(request, 'core/index.html')

# Return JSON of all active needs
def api_needs(request):
    needs = Need.objects.filter(is_active=True).order_by('-created_at')
    data = []
    for n in needs:
        data.append({
            'id': n.id,
            'title': n.title,
            'description': n.description[:300],
            'amount_needed': str(n.amount_needed),
            'amount_received': str(n.amount_received),
            'contact': n.contact,
            'image_url': n.image_url,
            'created_at': n.created_at.isoformat(),
        })
    return JsonResponse({'needs': data})

# Return detail for a single need including donations
def api_need_detail(request, need_id):
    n = get_object_or_404(Need, pk=need_id)
    donations = n.donations.order_by('-created_at')[:50]
    donations_list = [
        {'donor_name': d.donor_name, 'amount': str(d.amount), 'message': d.message, 'created_at': d.created_at.isoformat()} for d in donations
    ]
    data = {
        'id': n.id,
        'title': n.title,
        'description': n.description,
        'amount_needed': str(n.amount_needed),
        'amount_received': str(n.amount_received),
        'contact': n.contact,
        'donations': donations_list,
    }
    return JsonResponse(data)

# Endpoint to handle donation POST requests.
# We simulate payment — in production you'd integrate with a payment gateway.
@require_http_methods(['POST'])
def api_donate(request, need_id):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    donor_name = payload.get('donor_name') or 'Anonymous'
    message = payload.get('message', '')
    try:
        amount = Decimal(str(payload.get('amount', '0')))
    except Exception:
        return HttpResponseBadRequest('Invalid amount')

    if amount <= 0:
        return HttpResponseBadRequest('Donation amount must be > 0')

    need = get_object_or_404(Need, pk=need_id)

    # Create donation record
    donation = Donation.objects.create(
        need=need,
        donor_name=donor_name,
        message=message,
        amount=amount,
    )

    # Update amount_received on Need atomically
    need.amount_received = Decimal(need.amount_received) + amount
    # If reached the target, we could auto-deactivate or flag.
    if need.amount_received >= need.amount_needed:
        need.is_active = False
    need.save()

    return JsonResponse({'status': 'ok', 'donation_id': donation.id, 'new_amount_received': str(need.amount_received)})

# Create a new need (for volunteers/caregivers to post)
@require_http_methods(['POST'])
def api_create_need(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    title = payload.get('title', '').strip()
    description = payload.get('description', '').strip()
    try:
        amount_needed = Decimal(str(payload.get('amount_needed', '0')))
    except Exception:
        amount_needed = Decimal('0')

    if not title or amount_needed <= 0:
        return HttpResponseBadRequest('Title and positive amount_needed required')

    need = Need.objects.create(
        title=title,
        description=description,
        amount_needed=amount_needed,
        amount_received=Decimal('0'),
        contact=payload.get('contact', ''),
        image_url=payload.get('image_url', ''),
    )

    return JsonResponse({'status': 'ok', 'need_id': need.id})

