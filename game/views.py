import json
from django import http
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.core import serializers
from django.contrib.auth import authenticate, login
from game.forms import RegisterForm
from game.models import Game, Unit, create_game, Player, create_unit, Settlement, Map, UNIT_TYPE, create_settlement,\
    SETTLEMENT_TYPE, check_margins


def game(request):
    if not Game.objects.all().count():
        create_game('ilya')

    if request.user.is_active:
        return render(request, 'game/game.html', {'username': request.user.username})
    return render(request, 'game/game.html')


def login(request):
    return render(request, 'game/login.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'game/game.html')
        else:
            errors = ["There is an error"]
            return render(request, 'game/register.html', {'form':  UserCreationForm(), 'errors': errors})
    else:
        return render(request, 'game/register.html', {'form':  UserCreationForm()})


def load_units(request):
    units = Game.objects.get(pk=1).map_set.all()[0].unit_set.all()
    data = serializers.serialize('json', units, use_natural_keys=True)
    return http.HttpResponse(data, content_type='application/json')


def load_settlements(request):
    settlements = Game.objects.get(pk=1).map_set.all()[0].settlement_set.all()
    data = serializers.serialize('json', settlements, use_natural_keys=True)
    return http.HttpResponse(data, content_type='application/json')


def load_player(request):
    pk = int(request.GET['pk'])
    player = Game.objects.get(pk=1).player_set.filter(pk=pk)
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
    player_pk = int(request.GET['player'])
    player = Player.objects.get(pk=player_pk)
    player.increase_money_for_day()
    player.save()
    Unit.objects.filter(player=player_pk).update(active=True)
    Settlement.objects.filter(player=player_pk).update(active=True)
    return http.HttpResponse()


def buy_unit(request):
    settlement = Settlement.objects.get(pk=int(request.GET['settlement_pk']))
    if not settlement.active:
        return http.HttpResponseBadRequest()

    player = Player.objects.get(pk=int(request.GET['player']))
    unit_type = int(request.GET['type'])
    money = player.money
    cost = UNIT_TYPE[unit_type]['cost']

    if money < cost:
        return http.HttpResponseBadRequest()

    player.money = money - cost
    game_map = Map.objects.get(pk=int(request.GET['map']))
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

    player = Player.objects.get(pk=int(request.GET['player']))
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
    return http.HttpResponse(json.dumps({'available': check_margins(unit.left, unit.top)}),
                             mimetype="application/json")


def create_colony(request):
    settlers_type = 1
    unit = Unit.objects.get(pk=int(request.GET['pk']))
    if not unit and unit.unit_type == settlers_type:
        return http.HttpResponseBadRequest

    if not check_margins(unit.left, unit.top):
        return http.HttpResponseBadRequest

    colony_type = 1
    settlement = create_settlement(unit.map, unit.left, unit.top, unit.player, colony_type, False)
    Unit.objects.filter(pk=unit.pk).delete()
    settlement = Settlement.objects.filter(pk=settlement.pk)
    data = serializers.serialize('json', settlement, use_natural_keys=True)
    return http.HttpResponse(data, content_type='application/json')