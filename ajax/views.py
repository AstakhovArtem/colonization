import json
from django import http
from django.contrib.auth.decorators import login_required
from django.core import serializers
from game.models import Unit, Player, create_unit, Settlement, UNIT_TYPE, create_settlement,\
    SETTLEMENT_TYPE, check_margins, get_game_map, get_active_game, get_player


def load_units(request):
    units = get_player(request.user).unit_set.all()
    data = serializers.serialize('json', units, use_natural_keys=True)
    return http.HttpResponse(data, content_type='application/json')


def load_settlements(request):
    settlements = get_player(request.user).settlement_set.all()
    data = serializers.serialize('json', settlements, use_natural_keys=True)
    return http.HttpResponse(data, content_type='application/json')


@login_required
def load_player(request):
    player = Player.objects.filter(user=request.user)
    data = serializers.serialize('json', player, use_natural_keys=True)
    return http.HttpResponse(data, content_type='application/json')


def move_unit(request):
    pk = int(request.GET['pk'])
    unit = Unit.objects.get(pk=pk)
    if not unit.active:
        return http.HttpResponseBadRequest()
    left = int(request.GET['left'])
    top = int(request.GET['top'])
    unit.left = left
    unit.top = top
    unit.active = False
    unit.save()
    unit = Unit.objects.filter(pk=pk)
    data = serializers.serialize('json', unit, use_natural_keys=True)
    return http.HttpResponse(data, content_type='application/json')


def finish_stroke(request):
    player = Player.objects.filter(user=request.user).first()
    player.active = False
    player.save()
    Unit.objects.filter(player=player).update(active=False)
    Settlement.objects.filter(player=player).update(active=False)

    active_game = get_active_game(user=request.user)
    opponent = Player.objects.filter(game=active_game).exclude(user=request.user).first()
    opponent.increase_money_for_day()
    opponent.active = True
    opponent.save()
    Unit.objects.filter(player=opponent).update(active=True)
    Settlement.objects.filter(player=opponent).update(active=True)

    return http.HttpResponse()


def buy_unit(request):
    settlement = Settlement.objects.get(pk=int(request.GET['settlement_pk']))
    if not settlement.active:
        return http.HttpResponseBadRequest()

    player = Player.objects.filter(user=request.user).first()
    unit_type = int(request.GET['type'])
    money = player.money
    cost = UNIT_TYPE[unit_type]['cost']

    if money < cost:
        return http.HttpResponseBadRequest()

    player.money = money - cost
    game_map = get_game_map(request.user)
    unit = create_unit(game_map, settlement.left, settlement.top, player, unit_type, False)
    settlement.active = False
    settlement.save()
    player.save()
    unit_set = Unit.objects.filter(pk=unit.pk)
    data = serializers.serialize('json', unit_set, use_natural_keys=True)
    return http.HttpResponse(data, content_type='application/json')


def upgrade_settlement(request):
    settlement = Settlement.objects.get(pk=int(request.GET['settlement_pk']))
    if not settlement.active:
        return http.HttpResponseBadRequest()

    player = Player.objects.filter(user=request.user).first()
    settlement_type = int(request.GET['type'])
    money = player.money
    settlement_cost = 25

    if money < settlement_cost or settlement_type > len(SETTLEMENT_TYPE):
        return http.HttpResponseBadRequest()

    player.money = money - settlement_cost
    settlement.settlement_type = settlement_type
    settlement.active = False
    settlement.save()
    player.save()
    settlement_set = Settlement.objects.filter(pk=settlement.pk)
    data = serializers.serialize('json', settlement_set, use_natural_keys=True)
    return http.HttpResponse(data, content_type='application/json')


def check_settlement_active(request):
    settlement = Settlement.objects.get(pk=int(request.GET['pk']))
    return http.HttpResponse(json.dumps({'active': settlement.active}), mimetype="application/json")


def check_settlements_margins(request):
    unit = Unit.objects.get(pk=int(request.GET['pk']))
    return http.HttpResponse(json.dumps({'available': check_margins(get_game_map(request.user), unit.left, unit.top)}),
                             mimetype="application/json")


def create_colony(request):
    settlers_type = 1
    unit = Unit.objects.get(pk=int(request.GET['pk']))
    if not unit and unit.unit_type == settlers_type:
        return http.HttpResponseBadRequest

    if not check_margins(get_game_map(request.user), unit.left, unit.top):
        return http.HttpResponseBadRequest

    colony_type = 1
    settlement = create_settlement(unit.map, unit.left, unit.top, unit.player, colony_type, False)
    Unit.objects.filter(pk=unit.pk).delete()
    settlement = Settlement.objects.filter(pk=settlement.pk)
    data = serializers.serialize('json', settlement, use_natural_keys=True)
    return http.HttpResponse(data, content_type='application/json')