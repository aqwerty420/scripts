"""
 ______  ______   __   __   ______   __  __   ______
/\  == \/\  __ \ /\ "-.\ \ /\  ___\ /\ \_\ \ /\  ___\
\ \  _-/\ \ \/\ \\ \ \-.  \\ \ \____\ \  __ \\ \  __\
 \ \_\   \ \_____\\ \_\\"\_\\ \_____\\ \_\ \_\\ \_____\
  \/_/    \/_____/ \/_/ \/_/ \/_____/ \/_/\/_/ \/_____/


Changelog :

v0.1 Initial release

v0.11 Set correct hit chance

v0.2 Added attack disabler

v0.3 Made compatible with pred changes

"""

from helpers.targeting import TargetSelector, TargetSet
from helpers.flags import Orbwalker
from PO_Prediction import *
from valkyrie import *

q_combo = True
q_combo_hitchance = HitChance.Medium
q_range = 850
q_delay = 0.4 + 0.25
q_width = 40

w_combo = True
w_combo_hitchance = HitChance.High
w_range = 700
w_width = 160
w_delay = 0.25

e_combo = True
e_prefer_poisoned = True
e_range = 700
e_delay = 0.125

r_combo = True
r_combo_hitchance = HitChance.High
r_min_count = 2
r_range = 825
r_delay = 0.5

disable_attack = True
fight_range = 1500
include_clones = False
poisons = ['cassiopeiaqdebuff', 'cassiopeiawpoison']

target_selector = TargetSelector(0, TargetSet.Champion)


def valkyrie_menu(ctx: Context):
    global disable_attack, include_clones, r_min_count, q_combo, q_combo_hitchance, w_combo, w_combo_hitchance, e_combo, e_prefer_poisoned, r_combo, r_combo_hitchance
    ui = ctx.ui

    ui.text("Ponche Cassiopeia 0.3")
    ui.separator()

    include_clones = ui.checkbox('Include clones', include_clones)
    ui.help("Training dummy are considered as clones")
    ui.separator()

    disable_attack = ui.checkbox('Disable Attack', disable_attack)
    ui.help("Disable Attack in Combo mode")
    ui.separator()

    if ui.beginmenu("Q"):
        q_combo = ui.checkbox('Combo', q_combo)
        q_combo_hitchance = ui.sliderenum(
            "Combo - Hit Chance", HitChance.GetHitChanceName(q_combo_hitchance), q_combo_hitchance, 2)
        ui.separator()
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("W"):
        w_combo = ui.checkbox('Combo', w_combo)
        w_combo_hitchance = ui.sliderenum(
            "Combo - Hit Chance", HitChance.GetHitChanceName(w_combo_hitchance), w_combo_hitchance, 2)
        ui.separator()
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("E"):
        e_combo = ui.checkbox('Combo', e_combo)
        e_prefer_poisoned = ui.checkbox('Focus Poisoned', e_prefer_poisoned)
        ui.separator()
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("R"):
        r_combo = ui.checkbox('Combo', r_combo)
        r_combo_hitchance = ui.sliderenum(
            "Hit Chance", HitChance.GetHitChanceName(r_combo_hitchance), r_combo_hitchance, 2)
        r_min_count = ui.sliderint(
            "Min. Count", r_min_count, 1, 5)
        ui.help("Enemies must be facing you to be included in count.")
        ui.endmenu()


def valkyrie_on_load(ctx: Context):
    global disable_attack, include_clones, r_min_count, q_combo, q_combo_hitchance, w_combo, w_combo_hitchance, e_combo, e_prefer_poisoned, r_combo, r_combo_hitchance
    cfg = ctx.cfg

    include_clones = cfg.get_bool('include_clones', include_clones)
    disable_attack = cfg.get_bool('disable_attack', disable_attack)

    q_combo = cfg.get_bool('q_combo', q_combo)
    q_combo_hitchance = cfg.get_int('q_combo_hitchance', q_combo_hitchance)

    w_combo = cfg.get_bool('w_combo', w_combo)
    w_combo_hitchance = cfg.get_int('w_combo_hitchance', w_combo_hitchance)

    e_combo = cfg.get_bool('e_combo', e_combo)
    e_prefer_poisoned = cfg.get_bool('e_prefer_poisoned', e_prefer_poisoned)

    r_combo = cfg.get_bool('r_combo', r_combo)
    r_combo_hitchance = cfg.get_int('r_combo_hitchance', r_combo_hitchance)
    r_min_count = cfg.get_int('r_min_count', r_min_count)


def valkyrie_on_save(ctx: Context):
    cfg = ctx.cfg

    cfg.set_bool('include_clones', include_clones)
    cfg.set_bool('disable_attack', disable_attack)

    cfg.set_bool('q_combo', q_combo)
    cfg.set_int('q_combo_hitchance', q_combo_hitchance)

    cfg.set_bool('w_combo', w_combo)
    cfg.set_int('w_combo_hitchance', w_combo_hitchance)

    cfg.set_bool('e_combo', e_combo)
    cfg.set_bool('e_prefer_poisoned', e_prefer_poisoned)

    cfg.set_bool('r_combo', r_combo)
    cfg.set_int('r_combo_hitchance', r_combo_hitchance)
    cfg.set_int('r_min_count', r_min_count)


def q_cast(ctx: Context, target: UnitObj, hitchance: HitChance):
    player = ctx.player
    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), False, q_delay, q_width, range=q_range, type=SkillshotType.SkillshotCircle)
    output = AoePrediction.GetPrediction(input)

    if output.HitChance >= hitchance:
        return ctx.cast_spell(player.Q, output.CastPosition)

    return False


def w_cast(ctx: Context, target: UnitObj, hitchance: HitChance):
    player = ctx.player
    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), False, w_delay, w_width, range=w_range, type=SkillshotType.SkillshotCircle)
    output = AoePrediction.GetPrediction(input)

    if output.HitChance >= hitchance:
        return ctx.cast_spell(player.W, output.CastPosition)

    return False


def is_poisoned(unit: UnitObj):
    return unit.has_buff(poisons[0]) or unit.has_buff(poisons[1])


def e_cast(ctx: Context, target: UnitObj, enemies):
    player = ctx.player

    if e_prefer_poisoned:
        if is_poisoned(target) and player.pos.distance(target.pos) < e_range:
            return ctx.cast_spell(player.E, target.pos)

        for enemy in enemies:
            if is_poisoned(enemy) and player.pos.distance(enemy.pos) < e_range:
                return ctx.cast_spell(player.E, enemy.pos)

    if player.pos.distance(target.pos) < e_range:
        return ctx.cast_spell(player.E, target.pos)


def r_cast(ctx: Context, target: UnitObj, hitchance: HitChance):
    player = ctx.player
    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), False, r_delay, range=r_range, angle=90, type=SkillshotType.SkillshotCone)
    output = AoePrediction.GetPrediction(input)

    if output.HitChance >= hitchance and output.AoeTargetsHitCount >= r_min_count:
        facing_count = 0
        for hit in output.AoeTargetsHit:
            if Utility.IsFacing(hit, player):
                facing_count += 1
        if facing_count >= r_min_count:
            return ctx.cast_spell(player.R, output.CastPosition)

    return False


def combo_handler(ctx: Context, target: UnitObj, enemies: list[ChampionObj]):
    player = ctx.player
    q_spell = player.Q
    w_spell = player.W
    e_spell = player.E
    r_spell = player.R

    if r_combo and ctx.player.can_cast_spell(r_spell) and r_cast(ctx, target, r_combo_hitchance):
        return True

    if w_combo and ctx.player.can_cast_spell(w_spell) and w_cast(ctx, target, w_combo_hitchance):
        return True

    if q_combo and ctx.player.can_cast_spell(q_spell) and q_cast(ctx, target, q_combo_hitchance):
        return True

    if e_combo and ctx.player.can_cast_spell(e_spell) and e_cast(ctx, target, enemies):
        return True

    return False


def is_casting(player: ChampionObj):
    if player.curr_casting and player.curr_casting.remaining > 0:
        return True


def valkyrie_exec(ctx: Context):
    player = ctx.player

    is_combo = Orbwalker.CurrentMode == Orbwalker.ModeKite

    if disable_attack and is_combo and not Orbwalker.DisableAttack:
        Orbwalker.DisableAttack = True
    elif Orbwalker.DisableAttack and (not is_combo or not disable_attack):
        Orbwalker.DisableAttack = False

    if player.dead or player.recalling or is_casting(player):
        return

    if include_clones:
        enemies = ctx.champs.enemy_to(
            player).targetable().near(player, fight_range).get()
    else:
        enemies = ctx.champs.enemy_to(
            player).targetable().near(player, fight_range).not_clone().get()

    if len(enemies) == 0:
        return

    target = target_selector.get_target(ctx, enemies)

    if is_combo:
        combo_handler(ctx, target, enemies)
