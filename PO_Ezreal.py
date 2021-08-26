"""
 ______  ______   __   __   ______   __  __   ______
/\  == \/\  __ \ /\ "-.\ \ /\  ___\ /\ \_\ \ /\  ___\
\ \  _-/\ \ \/\ \\ \ \-.  \\ \ \____\ \  __ \\ \  __\
 \ \_\   \ \_____\\ \_\\"\_\\ \_____\\ \_\ \_\\ \_____\
  \/_/    \/_____/ \/_/ \/_/ \/_____/ \/_/\/_/ \/_____/


Changelog :

v0.1 Initial release

v0.2 Fixed Q / W order

v0.3 Added Q Last Hit

v0.31 Set correct hit chance

v0.4 Added R max range, Fixed crash at start

v0.5 Imporved overall logic, Fixed cast on evade

v0.51 Fixed mistake on R range

v0.6 Fixed a bug with settings usage, Made compatible with pred changes

TO DO:

E handler

"""

from valkyrie import *
from PO_Prediction import *
from helpers.targeting import TargetSelector, TargetSet
from helpers.flags import EvadeFlags, Orbwalker
from helpers.spells import Slot
from helpers.damages import *
import time

target_selector = TargetSelector(0, TargetSet.Champion)


q_combo = True
q_harass = True
q_combo_hitchance = HitChance.Medium
q_harass_hitchance = HitChance.High
q_range = 1200
q_speed = 2000
q_delay = 0.25
q_width = 120
q_last_hit = True
q_stack = True
q_min_mana = 30

w_combo = True
w_focus = True
w_combo_hitchance = HitChance.Medium
w_range = 1200
w_speed = 1700
w_delay = 0.25
w_width = 160

r_combo = True
r_min_dist = 900
r_use_max_dist = True
r_max_dist = 3000
r_combo_hitchance = HitChance.High
r_combo_hitcount = 3
r_width = 320
r_speed = 2000
r_delay = 1

include_clones = False
stack_items = [3004, 3070, 3003]
w_debuff = 'ezrealwattach'


def valkyrie_menu(ctx: Context):
    global w_focus, r_use_max_dist, r_max_dist, q_min_mana, q_last_hit, q_stack, r_combo_hitcount, r_combo, r_min_dist, r_combo_hitchance, include_clones, q_combo, q_harass, w_combo, q_combo_hitchance, q_harass_hitchance, w_combo_hitchance
    ui = ctx.ui

    ui.text("Ponche Ezreal v0.6")
    ui.separator()

    include_clones = ui.checkbox('Include clones', include_clones)
    ui.help("Training dummy are considered as clones")
    ui.separator()

    if ui.beginmenu("Q"):
        q_combo = ui.checkbox('Combo', q_combo)
        q_combo_hitchance = ui.sliderenum(
            "Harass - Hit Chance", HitChance.GetHitChanceName(q_combo_hitchance), q_combo_hitchance, 2)
        ui.separator()
        q_harass = ui.checkbox('Harass', q_harass)
        q_harass_hitchance = ui.sliderenum(
            "Combo - Hit Chance", HitChance.GetHitChanceName(q_harass_hitchance), q_harass_hitchance, 2)
        ui.separator()
        w_focus = ui.checkbox('Q on W', w_focus)
        ui.help("Target enemies with W debuff")
        ui.separator()
        q_last_hit = ui.checkbox('Last Hit', q_last_hit)
        q_stack = ui.checkbox('Only to stack Manamune', q_stack)
        q_min_mana = ui.sliderint(
            "Min. Mana %", q_min_mana, 0, 100)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("W"):
        w_combo = ui.checkbox('Combo', w_combo)
        w_combo_hitchance = ui.sliderenum(
            "Combo - Hit Chance", HitChance.GetHitChanceName(w_combo_hitchance), w_combo_hitchance, 2)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("R"):
        r_combo = ui.checkbox('Combo', r_combo)
        r_min_dist = ui.sliderint(
            "Min. Distance to enemies", r_min_dist, 0, 1500)
        r_use_max_dist = ui.checkbox('Use Max. Distance', r_use_max_dist)
        r_max_dist = ui.sliderint(
            "Max. Distance to enemies", r_max_dist, 0, 4500)
        r_combo_hitchance = ui.sliderenum(
            "Hit Chance", HitChance.GetHitChanceName(r_combo_hitchance), r_combo_hitchance, 2)
        r_combo_hitcount = ui.sliderint(
            "Min. Count to hit", r_combo_hitcount, 1, 5)
        ui.endmenu()


def valkyrie_on_load(ctx: Context):
    global w_focus, r_use_max_dist, r_max_dist, q_min_mana, q_last_hit, q_stack, r_combo_hitcount, r_combo, r_min_dist, r_combo_hitchance, include_clones, q_combo, q_harass, w_combo, q_combo_hitchance, q_harass_hitchance, w_combo_hitchance
    cfg = ctx.cfg

    include_clones = cfg.get_bool('include_clones', include_clones)

    q_combo = cfg.get_bool('q_combo', q_combo)
    q_combo_hitchance = cfg.get_int('q_combo_hitchance', q_combo_hitchance)
    q_harass = cfg.get_bool('q_harass', q_harass)
    q_harass_hitchance = cfg.get_int('q_harass_hitchance', q_harass_hitchance)
    w_focus = cfg.get_bool('w_focus', w_focus)
    q_last_hit = cfg.get_bool('q_last_hit', q_last_hit)
    q_stack = cfg.get_bool('q_stack', q_stack)
    q_min_mana = cfg.get_int('q_min_mana', q_min_mana)

    w_combo = cfg.get_bool('w_combo', w_combo)
    w_combo_hitchance = cfg.get_int('w_combo_hitchance', w_combo_hitchance)

    r_combo = cfg.get_bool('r_combo', r_combo)
    r_min_dist = cfg.get_int('r_min_dist', r_min_dist)
    r_use_max_dist = cfg.get_bool('r_use_max_dist', r_use_max_dist)
    r_max_dist = cfg.get_int('r_max_dist', r_max_dist)
    r_combo_hitcount = cfg.get_int('r_combo_hitcount', r_combo_hitcount)
    r_combo_hitchance = cfg.get_int('r_combo_hitchance', r_combo_hitchance)


def valkyrie_on_save(ctx: Context):
    cfg = ctx.cfg

    cfg.set_bool('include_clones', include_clones)

    cfg.set_bool('q_combo', q_combo)
    cfg.set_int('q_combo_hitchance', q_combo_hitchance)
    cfg.set_bool('q_harass', q_harass)
    cfg.set_int('q_harass_hitchance', q_harass_hitchance)
    cfg.set_bool('w_focus', w_focus)
    cfg.set_bool('q_last_hit', q_last_hit)
    cfg.set_bool('q_stack', q_stack)
    cfg.set_int('q_min_mana', q_min_mana)

    cfg.set_bool('w_combo', w_combo)
    cfg.set_int('w_combo_hitchance', w_combo_hitchance)

    cfg.set_bool('r_combo', r_combo)
    cfg.set_int('r_min_dist', r_min_dist)
    cfg.set_bool('r_use_max_dist', r_use_max_dist)
    cfg.set_int('r_max_dist', r_max_dist)
    cfg.set_int('r_combo_hitcount', r_combo_hitcount)
    cfg.set_int('r_combo_hitchance', r_combo_hitchance)


def q_cast(ctx: Context, target: UnitObj, hitchance: HitChance):
    player = ctx.player
    q_spell = player.spells[Slot.Q]

    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), True, q_delay, q_width, speed=q_speed, range=q_range, type=SkillshotType.SkillshotLine, collision=True, collisionableObjects=[CollisionableObjects.Minions, CollisionableObjects.Jungles, CollisionableObjects.Enemies])
    output = Prediction.GetPrediction(input)

    if output.HitChance >= hitchance:
        return ctx.cast_spell(q_spell, output.CastPosition)

    return False


def w_cast(ctx: Context, target: UnitObj, hitchance: HitChance):
    player = ctx.player
    w_spell = player.spells[Slot.W]

    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), True, w_delay, w_width, speed=w_speed, range=w_range, type=SkillshotType.SkillshotLine, collision=True, collisionableObjects=[CollisionableObjects.Enemies])
    output = Prediction.GetPrediction(input)

    if output.HitChance >= hitchance:
        return ctx.cast_spell(w_spell, output.CastPosition)

    return False


def r_cast_aoe(ctx: Context, target: UnitObj, enemies: list[ChampionObj], hitchance: HitChance):
    player = ctx.player
    r_spell = player.spells[Slot.R]

    for enemy in enemies:
        if enemy.pos.distance(player.pos) < r_min_dist:
            return False

    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), True, r_delay, r_width, range=r_max_dist if r_use_max_dist else hugeValue, speed=r_speed, type=SkillshotType.SkillshotLine, collision=False)
    output = AoePrediction.GetPrediction(input)

    if output.HitChance >= hitchance and output.AoeTargetsHitCount >= r_combo_hitcount:
        return ctx.cast_spell(r_spell, output.CastPosition)

    return False


def is_under_w(target: ChampionObj) -> bool:
    return target.has_buff(w_debuff)


def get_enemies_under_w(enemies: list[ChampionObj]) -> list[ChampionObj]:
    result = []

    for enemy in enemies:
        if is_under_w(enemy):
            result.append(enemy)

    return result


def combo_handler(ctx: Context, enemies: list[ChampionObj]):
    player = ctx.player
    q_spell = player.spells[Slot.Q]
    w_spell = player.spells[Slot.W]
    r_spell = player.spells[Slot.R]

    if r_combo and player.can_cast_spell(r_spell):
        in_range = Utility.GetInRange(
            player.pos, enemies, r_max_dist if r_use_max_dist else hugeValue)
        target = target_selector.get_target(ctx, in_range)
        if target and r_cast_aoe(ctx, target, enemies, r_combo_hitchance):
            return True

    in_range = Utility.GetInRange(player.pos, enemies, w_range)
    target = target_selector.get_target(ctx, in_range)
    if target and w_combo and player.can_cast_spell(w_spell) and w_cast(ctx, target, w_combo_hitchance):
        return True

    if target and q_combo and (not w_combo or not player.can_cast_spell(w_spell)) and player.can_cast_spell(q_spell):
        if w_focus:
            if is_under_w(target) and q_cast(ctx, target, q_combo_hitchance):
                return True
            under_w = get_enemies_under_w(in_range)
            for enemy in under_w:
                if q_cast(ctx, enemy, q_combo_hitchance):
                    return True
        if q_cast(ctx, target, q_combo_hitchance):
            return True

    return False


def harass_handler(ctx: Context, enemies: list[ChampionObj]):
    player = ctx.player
    q_spell = player.spells[Slot.Q]

    if not q_harass or not player.can_cast_spell(q_spell):
        return False

    in_range = Utility.GetInRange(player.pos, enemies, q_range)
    target = target_selector.get_target(ctx, in_range)

    if target and q_cast(ctx, target, q_harass_hitchance):
        return

    for enemy in in_range:
        if q_cast(ctx, enemy, q_harass_hitchance):
            return True

    return False


def get_item_to_stack(player: ChampionObj):
    for item_id in stack_items:
        item = player.get_item(item_id)
        if item:
            return item

    return None


def lasthit_handler(ctx: Context, minions: list[MinionObj]):
    player = ctx.player
    q_spell = player.spells[Slot.Q]

    if not q_last_hit or not player.can_cast_spell(q_spell):
        return False

    if player.mana * 100 / player.max_mana < q_min_mana:
        return False

    item = get_item_to_stack(player)

    if q_stack and (not item or not item.active or not item.active.ready_at < ctx.time):
        return False

    q_dmg = MixedDamage(calculate_raw_spell_dmg(player, q_spell))

    input = PredictionInput(player, player.pos.clone(), player.pos.clone(), True, q_delay, q_width, speed=q_speed, range=q_range,
                            type=SkillshotType.SkillshotLine, collision=True, collisionableObjects=[CollisionableObjects.Minions, CollisionableObjects.Enemies])

    for minion in minions:
        q_real_dmg = q_dmg.calc_against(ctx, player, minion)
        if minion.health <= q_real_dmg and minion.health * 100 / minion.max_health > 6:
            input.Unit = minion
            output = Prediction.GetPrediction(input)
            if output.HitChance >= HitChance.Medium:
                return ctx.cast_spell(q_spell, output.CastPosition)


def is_casting(player: ChampionObj):
    return player.curr_casting and player.curr_casting.remaining > 0


def valkyrie_exec(ctx: Context):
    player = ctx.player

    if player.dead or is_casting(player) or Orbwalker.Attacking or player.recalling or EvadeFlags.EvadeEndTime > time.time():
        return

    if include_clones:
        enemies = ctx.champs.enemy_to(
            player).targetable().get()
    else:
        enemies = ctx.champs.enemy_to(
            player).targetable().not_clone().get()
    minions = ctx.minions.enemy_to(
        player).targetable().near(player, q_range).get()

    is_combo = Orbwalker.CurrentMode == Orbwalker.ModeKite

    if len(enemies) > 0:
        if is_combo:
            combo_handler(ctx, enemies)
            return
        else:
            if harass_handler(ctx, enemies):
                return

    if not is_combo and len(minions) > 0:
        lasthit_handler(ctx, minions)
