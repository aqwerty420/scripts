"""
 ______  ______   __   __   ______   __  __   ______
/\  == \/\  __ \ /\ "-.\ \ /\  ___\ /\ \_\ \ /\  ___\
\ \  _-/\ \ \/\ \\ \ \-.  \\ \ \____\ \  __ \\ \  __\
 \ \_\   \ \_____\\ \_\\"\_\\ \_____\\ \_\ \_\\ \_____\
  \/_/    \/_____/ \/_/ \/_/ \/_____/ \/_/\/_/ \/_____/


Changelog :

v0.1 Initial release

v0.2 Fixed R spam, Made compatible with pred changes

"""

from valkyrie import *
from helpers.targeting import TargetSelector, TargetSet
from helpers.flags import EvadeFlags, Orbwalker
from PO_Prediction import *
from math import *
import time


target_selector = TargetSelector(0, TargetSet.Champion)
include_clones = False
disable_attack = False

q_combo = True
q_combo_hitchance = HitChance.Medium
q_name = 'XerathArcanopulseChargeUp'
q_width = 140
q_delay = 0.5
q_min_range = 735
q_max_range = 1450

w_combo = True
w_combo_hitchance = HitChance.Medium
w_range = 1000
w_width = 125
w_width_full = 275
w_delay = 0.25 + 0.5

e_combo = True
e_combo_hitchance = HitChance.Medium
e_range = 1125
e_width = 120
e_delay = 0.25
e_speed = 1400

r_auto = True
r_auto_hitchance = HitChance.Medium
r_range = 5000
r_width = 200
r_delay = 0.6
r_name = 'xerathrshots'
r_last_cast = 0

q_started_time = 0
last_r_cast = 0


def valkyrie_menu(ctx: Context):
    global r_auto_hitchance, r_auto, e_combo_hitchance, e_combo, w_combo_hitchance, w_combo, q_combo_hitchance, q_combo, disable_attack, include_clones
    ui = ctx.ui

    ui.text("Ponche Xerath v0.2")
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
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("W"):
        w_combo = ui.checkbox('Combo', w_combo)
        w_combo_hitchance = ui.sliderenum(
            "Combo - Hit Chance", HitChance.GetHitChanceName(w_combo_hitchance), w_combo_hitchance, 2)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("E"):
        e_combo = ui.checkbox('Combo', e_combo)
        e_combo_hitchance = ui.sliderenum(
            "Combo - Hit Chance", HitChance.GetHitChanceName(e_combo_hitchance), e_combo_hitchance, 2)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("R"):
        r_auto = ui.checkbox('Auto', r_auto)
        ui.help("Manual start")
        r_auto_hitchance = ui.sliderenum(
            "Hit Chance", HitChance.GetHitChanceName(r_auto_hitchance), r_auto_hitchance, 2)
        ui.endmenu()


def valkyrie_on_load(ctx: Context):
    global r_auto_hitchance, r_auto, e_combo_hitchance, e_combo, w_combo_hitchance, w_combo, q_combo_hitchance, q_combo, disable_attack, include_clones
    cfg = ctx.cfg

    include_clones = cfg.get_bool('include_clones', include_clones)
    disable_attack = cfg.get_bool('disable_attack', disable_attack)

    q_combo = cfg.get_bool('q_combo', q_combo)
    q_combo_hitchance = cfg.get_int('q_combo_hitchance', q_combo_hitchance)

    w_combo = cfg.get_bool('w_combo', w_combo)
    w_combo_hitchance = cfg.get_int('w_combo_hitchance', w_combo_hitchance)

    e_combo = cfg.get_bool('e_combo', e_combo)
    e_combo_hitchance = cfg.get_bool('e_combo_hitchance', e_combo_hitchance)

    r_auto = cfg.get_bool('r_auto', r_auto)
    r_auto_hitchance = cfg.get_int('r_auto_hitchance', r_auto_hitchance)


def valkyrie_on_save(ctx: Context):
    cfg = ctx.cfg

    cfg.set_bool('include_clones', include_clones)
    cfg.set_bool('disable_attack', disable_attack)

    cfg.set_bool('q_combo', q_combo)
    cfg.set_int('q_combo_hitchance', q_combo_hitchance)

    cfg.set_bool('w_combo', w_combo)
    cfg.set_int('w_combo_hitchance', w_combo_hitchance)

    cfg.set_bool('e_combo', e_combo)
    cfg.set_bool('e_combo_hitchance', e_combo_hitchance)

    cfg.set_bool('r_auto', r_auto)
    cfg.set_bool('r_auto_hitchance', r_auto_hitchance)


def is_casting(player: ChampionObj, buff_name: str) -> bool:
    return player.has_buff(buff_name)


def q_prepare(ctx: Context) -> bool:
    global q_started_time
    player = ctx.player
    Orbwalker.DisableAttack = True
    q_started_time = time.time()
    return ctx.start_channel(player.Q)


def q_cast(ctx: Context, target: UnitObj, hitchance: HitChance, q_range: float):
    player = ctx.player

    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), True, q_delay, q_width, range=q_range, type=SkillshotType.SkillshotLine)
    output = AoePrediction.GetPrediction(input)

    if output.HitChance >= hitchance:
        return ctx.end_channel(player.Q, output.CastPosition)

    return True


def w_cast(ctx: Context, target: UnitObj, hitchance: HitChance):
    player = ctx.player
    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), False, w_delay, w_width, range=w_range, type=SkillshotType.SkillshotCircle)
    output = AoePrediction.GetPrediction(input)

    if output.HitChance >= hitchance:
        return ctx.cast_spell(player.W, output.CastPosition)

    return False


def e_cast(ctx: Context, target: UnitObj, hitchance: HitChance):
    player = ctx.player

    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), True, e_delay, e_width, speed=e_speed, range=e_range, type=SkillshotType.SkillshotLine, collision=True, collisionableObjects=[CollisionableObjects.Minions, CollisionableObjects.Jungles, CollisionableObjects.Enemies])
    output = Prediction.GetPrediction(input)

    if output.HitChance >= hitchance:
        return ctx.cast_spell(player.E, output.CastPosition)

    return False


def r_cast(ctx: Context, target: UnitObj, hitchance: HitChance):
    global last_r_cast
    player = ctx.player

    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), False, r_delay, r_width, range=r_range, type=SkillshotType.SkillshotCircle)
    output = Prediction.GetPrediction(input)

    if output.HitChance >= hitchance:
        last_r_cast = time.time()
        return ctx.cast_spell(player.R, output.CastPosition)

    return False


def get_in_range(from_pos: Vec3, enemies: list[ChampionObj], range: float) -> list[ChampionObj]:
    result = []

    from_pos = Utility.To2D(from_pos)
    for enemy in enemies:
        if Utility.IsInRange(Utility.To2D(enemy.pos), from_pos, range):
            result.append(enemy)

    return result


def combo_handler(ctx: Context, enemies: list[ChampionObj]) -> bool:
    player = ctx.player
    q_spell = player.Q
    w_spell = player.W
    e_spell = player.E

    casting_q = is_casting(player, q_name)
    in_range = get_in_range(player.pos, enemies, w_range)
    target = target_selector.get_target(ctx, in_range)
    if target and w_combo and not casting_q and ctx.player.can_cast_spell(w_spell) and w_cast(ctx, target, w_combo_hitchance):
        return True

    in_range = get_in_range(player.pos, enemies, e_range)
    target = target_selector.get_target(ctx, in_range)
    if target and e_combo and not casting_q and ctx.player.can_cast_spell(e_spell) and e_cast(ctx, target, e_combo_hitchance):
        return True

    in_range = get_in_range(player.pos, enemies, q_max_range)
    target = target_selector.get_target(ctx, in_range)
    if q_combo and target and ctx.player.can_cast_spell(q_spell) and not casting_q and q_started_time + 1.0 < time.time():
        return q_prepare(ctx)
    elif casting_q and target:
        if time.time() - q_started_time - 0.5 > 0:
            q_range = min(q_min_range + int((time.time() -
                          q_started_time - 0.25) / 0.25) * 102.14 - 80, q_max_range)
        else:
            q_range = q_min_range
        return q_cast(ctx, target, q_combo_hitchance, q_range)

    return False


def r_handler(ctx: Context, enemies: list[ChampionObj]) -> bool:
    player = ctx.player

    if r_auto and is_casting(player, r_name):
        if last_r_cast < time.time() + 0.7:
            in_range = get_in_range(player.pos, enemies, r_range)
            target = target_selector.get_target(ctx, in_range)
            if target and player.can_cast_spell(player.R):
                r_cast(ctx, target, r_auto_hitchance)
        return True

    return False


def orbwalker_handler(player: ChampionObj):
    if not Orbwalker.DisableAttack and disable_attack:
        Orbwalker.DisableAttack = True

    if Orbwalker.DisableAttack and not disable_attack and not is_casting(player, q_name):
        Orbwalker.DisableAttack = False

    casting_r = is_casting(player, r_name)
    if not casting_r and Orbwalker.PauseUntil > time.time():
        Orbwalker.PauseUntil = 0
    if casting_r:
        Orbwalker.PauseUntil = time.time() + 1


def valkyrie_exec(ctx: Context):
    player = ctx.player

    if player.dead or Orbwalker.Attacking or player.recalling or (EvadeFlags.EvadeEndTime > time.time() and not is_casting(player, q_name)):
        return

    orbwalker_handler(player)

    if include_clones:
        enemies = ctx.champs.enemy_to(
            player).targetable().get()
    else:
        enemies = ctx.champs.enemy_to(
            player).targetable().not_clone().get()

    is_combo = Orbwalker.CurrentMode == Orbwalker.ModeKite

    if len(enemies) > 0:
        if r_handler(ctx, enemies):
            return
        if is_combo:
            combo_handler(ctx, enemies)
